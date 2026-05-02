import unittest

from atelier.domain.resources import ResourceRequest, RuntimeRequest
from atelier.planning.simple import build_linear_execution_plan
from atelier.workflow.graph import WorkflowEdge, WorkflowGraph, WorkflowNode, WorkflowPortRef


class SimplePlanningTests(unittest.TestCase):
    def test_build_linear_execution_plan_preserves_edge_dependencies(self) -> None:
        graph = WorkflowGraph(
            graph_id="graph-linear",
            name="Linear Graph",
            nodes=[
                WorkflowNode(
                    node_id="node-a",
                    node_type="simulate.source",
                    resource_request=ResourceRequest(device_type="cpu"),
                    runtime_request=RuntimeRequest(components=["simulated"]),
                ),
                WorkflowNode(
                    node_id="node-b",
                    node_type="simulate.echo",
                    resource_request=ResourceRequest(device_type="cpu"),
                    runtime_request=RuntimeRequest(components=["simulated"]),
                ),
            ],
            edges=[
                WorkflowEdge(
                    edge_id="edge-a-b",
                    source=WorkflowPortRef(node_id="node-a", port_id="out"),
                    target=WorkflowPortRef(node_id="node-b", port_id="in"),
                )
            ],
        )

        plan = build_linear_execution_plan(graph, plan_id="plan-linear")

        self.assertEqual([task.source_node_id for task in plan.tasks], ["node-a", "node-b"])
        self.assertEqual(plan.tasks[0].depends_on_tasks, [])
        self.assertEqual(plan.tasks[1].depends_on_tasks, ["plan-linear-node-a-task"])

    def test_build_linear_execution_plan_rejects_empty_graph(self) -> None:
        graph = WorkflowGraph(graph_id="graph-empty", name="Empty Graph")

        with self.assertRaisesRegex(ValueError, "workflow graph has no nodes"):
            build_linear_execution_plan(graph, plan_id="plan-empty")


if __name__ == "__main__":
    unittest.main()
