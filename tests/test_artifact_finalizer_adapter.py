import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atelier.adapters.base import AdapterContext, AdapterExecutionError
from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.resources import ResourceRequest, RuntimeBinding, RuntimeRequest
from atelier.security.package_integrity import sha256_file

try:
    from atelier.adapters.finalize import ArtifactFinalizerAdapter
except ImportError:
    ArtifactFinalizerAdapter = None


class ArtifactFinalizerAdapterTests(unittest.TestCase):
    def test_copies_staged_artifact_to_output_dir_and_returns_final_output_artifact(self) -> None:
        self.assertIsNotNone(ArtifactFinalizerAdapter, "ArtifactFinalizerAdapter should exist")
        assert ArtifactFinalizerAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            staged = root / "staging" / "audio.wav"
            staged.parent.mkdir()
            staged.write_bytes(b"fake wav")
            output_dir = root / "exports"
            adapter = ArtifactFinalizerAdapter()

            result = adapter.run(
                AdapterContext(
                    task=_task(
                        params={
                            "input_path": str(staged),
                            "output_dir": str(output_dir),
                            "filename": "final.wav",
                            "artifact_type": "audio",
                        }
                    ),
                    runtime_binding=RuntimeBinding(runtime_id="runtime:none"),
                    work_dir=root / "work",
                )
            )

            exported = output_dir / "final.wav"
            self.assertEqual(exported.read_bytes(), b"fake wav")
            self.assertEqual(len(result.artifacts), 1)
            self.assertEqual(result.artifacts[0].artifact_type, "audio")
            self.assertEqual(result.artifacts[0].path, str(exported))
            self.assertEqual(result.metadata["role"], "final_output")
            self.assertEqual(result.metadata["source_path"], str(staged))
            self.assertEqual(result.metadata["size_bytes"], len(b"fake wav"))
            self.assertEqual(result.metadata["sha256"], sha256_file(exported))

    def test_uses_source_filename_when_filename_is_not_provided(self) -> None:
        self.assertIsNotNone(ArtifactFinalizerAdapter, "ArtifactFinalizerAdapter should exist")
        assert ArtifactFinalizerAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            staged = root / "staging" / "probe.json"
            staged.parent.mkdir()
            staged.write_text("{}", encoding="utf-8")
            output_dir = root / "exports"
            adapter = ArtifactFinalizerAdapter()

            result = adapter.run(
                AdapterContext(
                    task=_task(params={"input_path": str(staged), "output_dir": str(output_dir)}),
                    runtime_binding=RuntimeBinding(runtime_id="runtime:none"),
                    work_dir=root / "work",
                )
            )

            self.assertTrue((output_dir / "probe.json").is_file())
            self.assertEqual(result.artifacts[0].artifact_type, "video")
            self.assertEqual(result.artifacts[0].path, str(output_dir / "probe.json"))

    def test_existing_output_file_is_structured_conflict_failure(self) -> None:
        self.assertIsNotNone(ArtifactFinalizerAdapter, "ArtifactFinalizerAdapter should exist")
        assert ArtifactFinalizerAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            staged = root / "staging" / "audio.wav"
            staged.parent.mkdir()
            staged.write_bytes(b"new")
            output_dir = root / "exports"
            output_dir.mkdir()
            (output_dir / "audio.wav").write_bytes(b"existing")
            adapter = ArtifactFinalizerAdapter()

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(
                    AdapterContext(
                        task=_task(params={"input_path": str(staged), "output_dir": str(output_dir)}),
                        runtime_binding=RuntimeBinding(runtime_id="runtime:none"),
                        work_dir=root / "work",
                    )
                )

            self.assertEqual(raised.exception.error_code, "OUTPUT_CONFLICT")
            self.assertTrue(raised.exception.recoverable)
            self.assertEqual((output_dir / "audio.wav").read_bytes(), b"existing")

    def test_unsafe_filename_is_structured_permission_failure(self) -> None:
        self.assertIsNotNone(ArtifactFinalizerAdapter, "ArtifactFinalizerAdapter should exist")
        assert ArtifactFinalizerAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            staged = root / "staging" / "audio.wav"
            staged.parent.mkdir()
            staged.write_bytes(b"fake wav")
            adapter = ArtifactFinalizerAdapter()

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(
                    AdapterContext(
                        task=_task(
                            params={
                                "input_path": str(staged),
                                "output_dir": str(root / "exports"),
                                "filename": "..\\escape.wav",
                            }
                        ),
                        runtime_binding=RuntimeBinding(runtime_id="runtime:none"),
                        work_dir=root / "work",
                    )
                )

            self.assertEqual(raised.exception.error_code, "PERMISSION")
            self.assertFalse(raised.exception.recoverable)
            self.assertFalse((root / "escape.wav").exists())

    def test_missing_input_path_is_structured_failure(self) -> None:
        self.assertIsNotNone(ArtifactFinalizerAdapter, "ArtifactFinalizerAdapter should exist")
        assert ArtifactFinalizerAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            adapter = ArtifactFinalizerAdapter()

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(
                    AdapterContext(
                        task=_task(
                            params={
                                "input_path": str(root / "missing.wav"),
                                "output_dir": str(root / "exports"),
                            }
                        ),
                        runtime_binding=RuntimeBinding(runtime_id="runtime:none"),
                        work_dir=root / "work",
                    )
                )

            self.assertEqual(raised.exception.error_code, "INPUT_MISSING")
            self.assertFalse(raised.exception.recoverable)


def _task(params: dict[str, str]) -> ExecutionTask:
    return ExecutionTask(
        task_id="task-output-export",
        source_node_id="node-output-export",
        node_type="output.export",
        params=params,
        resource_request=ResourceRequest(device_type="cpu"),
        runtime_request=RuntimeRequest(),
    )


if __name__ == "__main__":
    unittest.main()
