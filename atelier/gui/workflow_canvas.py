from __future__ import annotations

from dataclasses import dataclass

from atelier.gui.entry import ensure_gui_dependency
from atelier.workflow.graph import WorkflowGraph

ensure_gui_dependency()

from PySide6.QtCore import QObject, QPointF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)


NODE_WIDTH = 160.0
NODE_HEIGHT = 84.0
NODE_GAP_X = 220.0
NODE_GAP_Y = 130.0


@dataclass(frozen=True)
class WorkflowCanvasNodeView:
    node_id: str
    node_type: str
    title: str
    position: tuple[float, float]


@dataclass(frozen=True)
class WorkflowCanvasEdgeView:
    edge_id: str
    source_node_id: str
    target_node_id: str


@dataclass(frozen=True)
class WorkflowCanvasViewModel:
    graph_id: str
    name: str
    nodes: list[WorkflowCanvasNodeView]
    edges: list[WorkflowCanvasEdgeView]


class WorkflowCanvasSelectionState(QObject):
    changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._selected_node_id: str | None = None

    def selected_node_id(self) -> str | None:
        return self._selected_node_id

    def select_node(self, node_id: str) -> None:
        if self._selected_node_id == node_id:
            return
        self._selected_node_id = node_id
        self.changed.emit(node_id)


class WorkflowCanvas(QGraphicsView):
    selection_changed = Signal(str)

    def __init__(self, view_model: WorkflowCanvasViewModel, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("workflow-canvas")
        self._view_model = view_model
        self._selection_state = WorkflowCanvasSelectionState()
        self._selection_state.changed.connect(self._apply_selection)
        self._selection_state.changed.connect(self.selection_changed)
        self._node_items: dict[str, QGraphicsRectItem] = {}
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._render_view_model()

    def selected_node_id(self) -> str | None:
        return self._selection_state.selected_node_id()

    def select_node(self, node_id: str) -> None:
        if node_id not in self._node_items:
            return
        self._selection_state.select_node(node_id)

    def view_model(self) -> WorkflowCanvasViewModel:
        return self._view_model

    def _render_view_model(self) -> None:
        self._scene.clear()
        self._node_items.clear()
        for node in self._view_model.nodes:
            self._add_node_item(node)
        for edge in self._view_model.edges:
            self._add_edge_item(edge)
        self._scene.setSceneRect(self._scene.itemsBoundingRect().adjusted(-48, -48, 48, 48))

    def _add_node_item(self, node: WorkflowCanvasNodeView) -> None:
        x, y = node.position
        rect = QGraphicsRectItem(0, 0, NODE_WIDTH, NODE_HEIGHT)
        rect.setData(0, node.node_id)
        rect.setData(1, "workflow-node-card")
        rect.setPos(x, y)
        rect.setBrush(QBrush(QColor("#172332")))
        rect.setPen(QPen(QColor("#2A3A50"), 1.5))
        rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self._scene.addItem(rect)
        self._node_items[node.node_id] = rect

        title = QGraphicsSimpleTextItem(node.title, rect)
        title.setBrush(QBrush(QColor("#F3F7FB")))
        title.setPos(14, 14)

        subtitle = QGraphicsSimpleTextItem(node.node_type, rect)
        subtitle.setBrush(QBrush(QColor("#B7C2D2")))
        subtitle.setPos(14, 40)

    def _add_edge_item(self, edge: WorkflowCanvasEdgeView) -> None:
        source = self._node_items.get(edge.source_node_id)
        target = self._node_items.get(edge.target_node_id)
        if source is None or target is None:
            return
        source_point = source.scenePos() + QPointF(NODE_WIDTH, NODE_HEIGHT / 2)
        target_point = target.scenePos() + QPointF(0, NODE_HEIGHT / 2)
        path = QPainterPath(source_point)
        mid_x = (source_point.x() + target_point.x()) / 2
        path.cubicTo(
            QPointF(mid_x, source_point.y()),
            QPointF(mid_x, target_point.y()),
            target_point,
        )
        item = QGraphicsPathItem(path)
        item.setData(0, edge.edge_id)
        item.setData(1, "workflow-edge")
        item.setPen(QPen(QColor("#9CA8B8"), 2.0))
        item.setZValue(-1)
        self._scene.addItem(item)

    def _apply_selection(self, selected_node_id: str) -> None:
        for node_id, item in self._node_items.items():
            if node_id == selected_node_id:
                item.setPen(QPen(QColor("#3B82F6"), 2.0))
                item.setBrush(QBrush(QColor("#1C2B3D")))
            else:
                item.setPen(QPen(QColor("#2A3A50"), 1.5))
                item.setBrush(QBrush(QColor("#172332")))


def build_workflow_canvas_view_model(graph: WorkflowGraph) -> WorkflowCanvasViewModel:
    return WorkflowCanvasViewModel(
        graph_id=graph.graph_id,
        name=graph.name,
        nodes=[
            WorkflowCanvasNodeView(
                node_id=node.node_id,
                node_type=node.node_type,
                title=str(node.params.get("label") or node.node_type),
                position=_default_node_position(index),
            )
            for index, node in enumerate(graph.nodes)
        ],
        edges=[
            WorkflowCanvasEdgeView(
                edge_id=edge.edge_id,
                source_node_id=edge.source.node_id,
                target_node_id=edge.target.node_id,
            )
            for edge in graph.edges
        ],
    )


def _default_node_position(index: int) -> tuple[float, float]:
    column = index % 4
    row = index // 4
    return (float(column) * NODE_GAP_X, float(row) * NODE_GAP_Y)
