from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from atelier.domain.resources import ResourceRequest, RuntimeRequest


class WorkflowPortRef(BaseModel):
    node_id: str
    port_id: str = ""


class WorkflowEdge(BaseModel):
    edge_id: str
    source: WorkflowPortRef
    target: WorkflowPortRef


class WorkflowNode(BaseModel):
    node_id: str
    node_type: str
    params: dict[str, Any] = Field(default_factory=dict)
    resource_request: ResourceRequest = Field(default_factory=ResourceRequest)
    runtime_request: RuntimeRequest = Field(default_factory=RuntimeRequest)


class WorkflowGraph(BaseModel):
    graph_id: str
    name: str
    description: str = ""
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)
