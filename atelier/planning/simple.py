from __future__ import annotations

from atelier.domain.execution_plan import ExecutionPlan, ExecutionTask
from atelier.workflow.graph import WorkflowGraph


def build_linear_execution_plan(graph: WorkflowGraph, plan_id: str) -> ExecutionPlan:
    if not graph.nodes:
        raise ValueError("workflow graph has no nodes")

    task_id_by_node_id = {
        node.node_id: f"{plan_id}-{node.node_id}-task"
        for node in graph.nodes
    }
    dependencies_by_node_id: dict[str, list[str]] = {node.node_id: [] for node in graph.nodes}
    for edge in graph.edges:
        dependencies_by_node_id[edge.target.node_id].append(task_id_by_node_id[edge.source.node_id])

    tasks = [
        ExecutionTask(
            task_id=task_id_by_node_id[node.node_id],
            source_node_id=node.node_id,
            node_type=node.node_type,
            params=node.params,
            resource_request=node.resource_request,
            runtime_request=node.runtime_request,
            depends_on_tasks=dependencies_by_node_id[node.node_id],
        )
        for node in graph.nodes
    ]
    return ExecutionPlan(
        plan_id=plan_id,
        workflow_graph_id=graph.graph_id,
        tasks=tasks,
    )
