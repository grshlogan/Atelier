import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from atelier.gui.entry import check_gui_dependency
from atelier.workflow.graph import WorkflowEdge, WorkflowGraph, WorkflowNode, WorkflowPortRef

GUI_AVAILABLE = check_gui_dependency().available

if GUI_AVAILABLE:
    from PySide6.QtWidgets import QApplication, QGraphicsPathItem, QGraphicsRectItem

    from atelier.app.paths import AppPaths
    from atelier.gui.main_window import MainWindow
else:
    QApplication = None
    QGraphicsPathItem = None
    QGraphicsRectItem = None


@unittest.skipUnless(GUI_AVAILABLE, "PySide6 is not installed")
class WorkflowCanvasFoundationTests(unittest.TestCase):
    def test_view_model_keeps_graph_data_separate_from_visual_layout(self) -> None:
        workflow_canvas = _workflow_canvas_module()
        graph = _minimal_graph()

        view_model = workflow_canvas.build_workflow_canvas_view_model(graph)

        self.assertEqual([node.node_id for node in graph.nodes], ["video-input", "audio-extract"])
        self.assertEqual([node.node_id for node in view_model.nodes], ["video-input", "audio-extract"])
        self.assertEqual([edge.edge_id for edge in view_model.edges], ["edge-video-audio"])
        self.assertEqual(view_model.nodes[0].position, (0.0, 0.0))
        self.assertEqual(view_model.nodes[1].position, (220.0, 0.0))
        self.assertFalse(hasattr(graph.nodes[0], "position"))

    def test_canvas_renders_node_cards_and_edge_items_from_workflow_graph(self) -> None:
        workflow_canvas = _workflow_canvas_module()
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        canvas = workflow_canvas.WorkflowCanvas(
            workflow_canvas.build_workflow_canvas_view_model(_minimal_graph())
        )
        try:
            node_items = [
                item
                for item in canvas.scene().items()
                if isinstance(item, QGraphicsRectItem)
                and item.data(0) in {"video-input", "audio-extract"}
            ]
            edge_items = [
                item
                for item in canvas.scene().items()
                if isinstance(item, QGraphicsPathItem) and item.data(0) == "edge-video-audio"
            ]

            self.assertEqual({item.data(0) for item in node_items}, {"video-input", "audio-extract"})
            self.assertEqual(len(edge_items), 1)
            self.assertGreater(edge_items[0].path().length(), 0)
        finally:
            canvas.close()

    def test_select_node_updates_visual_selection_without_mutating_graph(self) -> None:
        workflow_canvas = _workflow_canvas_module()
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)
        graph = _minimal_graph()
        view_model = workflow_canvas.build_workflow_canvas_view_model(graph)
        canvas = workflow_canvas.WorkflowCanvas(view_model)
        selected_node_ids: list[str] = []
        canvas.selection_changed.connect(selected_node_ids.append)
        try:
            canvas.select_node("audio-extract")

            self.assertEqual(canvas.selected_node_id(), "audio-extract")
            self.assertEqual(selected_node_ids, ["audio-extract"])
            self.assertEqual([node.node_id for node in graph.nodes], ["video-input", "audio-extract"])
        finally:
            canvas.close()

    def test_main_window_central_view_uses_workflow_canvas_for_injected_graph(self) -> None:
        workflow_canvas = _workflow_canvas_module()
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as temp_dir:
            window = MainWindow(
                app_paths=AppPaths.for_development(Path(temp_dir)),
                workflow_graph=_minimal_graph(),
            )
            try:
                canvas = window.findChild(workflow_canvas.WorkflowCanvas, "workflow-canvas")

                self.assertIsNotNone(canvas)
                self.assertEqual(canvas.view_model().graph_id, "graph-canvas-foundation")
            finally:
                window.close()


def _workflow_canvas_module():
    try:
        from atelier.gui import workflow_canvas
    except ModuleNotFoundError as exc:
        raise AssertionError("atelier.gui.workflow_canvas module should exist") from exc
    return workflow_canvas


def _minimal_graph() -> WorkflowGraph:
    return WorkflowGraph(
        graph_id="graph-canvas-foundation",
        name="Canvas Foundation",
        nodes=[
            WorkflowNode(
                node_id="video-input",
                node_type="input.video",
                params={"label": "Video Input"},
            ),
            WorkflowNode(
                node_id="audio-extract",
                node_type="media.audio_extract",
                params={"label": "Audio Extract"},
            ),
        ],
        edges=[
            WorkflowEdge(
                edge_id="edge-video-audio",
                source=WorkflowPortRef(node_id="video-input", port_id="video"),
                target=WorkflowPortRef(node_id="audio-extract", port_id="input"),
            )
        ],
    )


if __name__ == "__main__":
    unittest.main()
