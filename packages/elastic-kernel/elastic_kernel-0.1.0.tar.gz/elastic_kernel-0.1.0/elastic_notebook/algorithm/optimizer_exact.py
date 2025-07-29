import logging
import time

import networkx as nx
import numpy as np
from networkx.algorithms.flow import edmonds_karp

from elastic_notebook.algorithm.selector import Selector
from elastic_notebook.core.graph.cell_execution import CellExecution
from elastic_notebook.core.graph.variable_snapshot import VariableSnapshot

logger = logging.getLogger("ElasticNotebookLogger")


class OptimizerExact(Selector):
    """
    The exact optimizer constructs a flow graph and runs the min-cut algorithm to exactly find the best
    checkpointing configuration.
    """

    def __init__(self, migration_speed_bps=1):
        super().__init__(migration_speed_bps)

        # Augmented computation graph
        self.active_oes = None
        self.compute_graph = None

        # CEs required to recompute a variables last modified by a given CE.
        self.recomputation_ces = {}

        self.idx = 0

    def get_new_idx(self) -> int:
        """
        Get a new index number to add to compute graph.
        """
        idx = self.idx
        self.idx += 1
        return idx

    def dfs(self, current: str, visited: set, recompute_ces: str):
        """
        Perform DFS on the Application History Graph for finding the CEs required to recompute a variable.
        Args:
            current (str): Name of current nodeset.
            visited (set): Visited nodesets.
            recompute_ces (set): Set of CEs needing re-execution to recompute the current nodeset.
        """
        if isinstance(current, CellExecution):
            # Result is memoized
            if current in self.recomputation_ces:
                recompute_ces.update(self.recomputation_ces[current])
            else:
                recompute_ces.add(current)
                for vs in current.src_vss:
                    if vs not in self.active_vss and vs not in visited:
                        self.dfs(vs, visited, recompute_ces)

        elif isinstance(current, VariableSnapshot):
            visited.add(current)
            if current.output_ce not in recompute_ces:
                self.dfs(current.output_ce, visited, recompute_ces)

    def find_prerequisites(self):
        """
        Find the necessary (prerequisite) cell executions to rerun a cell execution.
        """
        self.active_vss = set(self.active_vss)

        for ce in self.dependency_graph.cell_executions:
            if ce.dst_vss.intersection(self.active_vss):
                recompute_ces = set()
                self.dfs(ce, set(), recompute_ces)
                self.recomputation_ces[ce] = recompute_ces

    def select_vss(self, notebook_name=None, optimizer_name=None) -> set:
        logger.info("=== OptimizerExact.select_vss started ===")
        start_time = time.time()

        logger.info("Finding prerequisites...")
        prereq_start = time.time()
        self.find_prerequisites()
        prereq_end = time.time()
        logger.info(f"Prerequisites found in {prereq_end - prereq_start:.3f} seconds")

        logger.info(f"Number of active variables: {len(self.active_vss)}")
        logger.info(
            f"Number of cell executions: {len(self.dependency_graph.cell_executions)}"
        )
        logger.info(
            f"Number of overlapping variable pairs: {len(self.overlapping_vss)}"
        )

        # Construct flow graph for computing mincut
        logger.info("Constructing flow graph...")
        graph_start = time.time()
        mincut_graph = nx.DiGraph()

        # Add source and sink to flow graph.
        mincut_graph.add_node("source")
        mincut_graph.add_node("sink")

        # Add all active VSs as nodes, connect them with the source with edge capacity equal to migration cost.
        logger.info("Adding active variables to graph...")
        for i, active_vs in enumerate(self.active_vss):
            if i % 100 == 0:
                logger.info(f"  Added {i}/{len(self.active_vss)} active variables")
            mincut_graph.add_node(active_vs)
            mincut_graph.add_edge(
                "source", active_vs, capacity=active_vs.size / self.migration_speed_bps
            )

        # Add all CEs as nodes, connect them with the sink with edge capacity equal to recomputation cost.
        logger.info("Adding cell executions to graph...")
        for i, ce in enumerate(self.dependency_graph.cell_executions):
            if i % 100 == 0:
                logger.info(
                    f"  Added {i}/{len(self.dependency_graph.cell_executions)} cell executions"
                )
            mincut_graph.add_node(ce)
            mincut_graph.add_edge(ce, "sink", capacity=ce.cell_runtime)

        # Connect each CE with its output variables and its prerequisite OEs.
        logger.info("Connecting variables to cell executions...")
        edge_count = 0
        for i, active_vs in enumerate(self.active_vss):
            if i % 100 == 0:
                logger.info(
                    f"  Processing variable {i}/{len(self.active_vss)}, edges added: {edge_count}"
                )
            for ce in self.recomputation_ces[active_vs.output_ce]:
                mincut_graph.add_edge(active_vs, ce, capacity=np.inf)
                edge_count += 1

        # Add constraints: overlapping variables must either be migrated or recomputed together.
        logger.info("Adding overlapping variable constraints...")
        for i, vs_pair in enumerate(self.overlapping_vss):
            if i % 100 == 0:
                logger.info(
                    f"  Added {i}/{len(self.overlapping_vss)} overlapping constraints"
                )
            mincut_graph.add_edge(vs_pair[0], vs_pair[1], capacity=np.inf)
            mincut_graph.add_edge(vs_pair[1], vs_pair[0], capacity=np.inf)

        # Prune CEs which produce no active variables to speedup computation.
        logger.info("Pruning cell executions with no active variables...")
        pruned_count = 0
        for ce in list(self.dependency_graph.cell_executions):
            if mincut_graph.in_degree(ce) == 0:
                mincut_graph.remove_node(ce)
                pruned_count += 1
        logger.info(f"Pruned {pruned_count} cell executions")

        graph_end = time.time()
        logger.info(
            f"Graph construction completed in {graph_end - graph_start:.3f} seconds"
        )
        logger.info(
            f"Graph stats: {mincut_graph.number_of_nodes()} nodes, {mincut_graph.number_of_edges()} edges"
        )

        # Solve min-cut with Edmonds-Karp (faster than Ford-Fulkerson)
        logger.info("=== Starting minimum cut computation ===")
        logger.info("This may take a while for large graphs...")
        mincut_start = time.time()

        cut_value, partition = nx.minimum_cut(
            mincut_graph, "source", "sink", flow_func=edmonds_karp
        )
        mincut_end = time.time()
        logger.info(f"Minimum cut completed in {mincut_end - mincut_start:.3f} seconds")
        logger.info(f"Cut value: {cut_value}")

        # Determine the replication plan from the partition.
        vss_to_migrate = set(partition[1]).intersection(self.active_vss)
        ces_to_recompute = set(partition[0]).intersection(
            self.dependency_graph.cell_executions
        )

        total_time = time.time() - start_time
        logger.info(
            f"=== OptimizerExact.select_vss completed in {total_time:.3f} seconds ==="
        )
        logger.info(f"Variables to migrate: {len(vss_to_migrate)}")
        logger.info(f"Cell executions to recompute: {len(ces_to_recompute)}")

        return vss_to_migrate, ces_to_recompute
