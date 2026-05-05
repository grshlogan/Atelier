import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atelier.adapters.command import CommandExecutionError, CommandSpec, run_command


class CommandExecutorTests(unittest.TestCase):
    def test_runs_command_spec_with_args_cwd_env_and_redacted_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script = root / "echo_args.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import os
                    import sys

                    print("|".join(sys.argv[1:]))
                    print(os.environ["ATELIER_COMMAND_TEST"])
                    """
                ),
                encoding="utf-8",
            )
            spec = CommandSpec(
                executable=Path(sys.executable),
                args=[str(script), "--token", "secret-value"],
                cwd=root,
                env={"ATELIER_COMMAND_TEST": "env-seen"},
                redacted_args=[str(script), "--token", "<redacted>"],
            )

            result = run_command(spec)

            self.assertEqual(result.returncode, 0)
            self.assertIn("--token|secret-value", result.stdout)
            self.assertIn("env-seen", result.stdout)
            self.assertEqual(
                result.redacted_command,
                [str(Path(sys.executable)), str(script), "--token", "<redacted>"],
            )

    def test_nonzero_exit_raises_with_stderr_and_redacted_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script = root / "fail.py"
            script.write_text(
                "import sys\nsys.stderr.write('dependency failed\\n')\nraise SystemExit(7)\n",
                encoding="utf-8",
            )
            spec = CommandSpec(
                executable=Path(sys.executable),
                args=[str(script), "--password", "secret"],
                cwd=root,
                redacted_args=[str(script), "--password", "<redacted>"],
            )

            with self.assertRaises(CommandExecutionError) as raised:
                run_command(spec)

            self.assertEqual(raised.exception.returncode, 7)
            self.assertIn("dependency failed", raised.exception.stderr)
            self.assertNotIn("secret", " ".join(raised.exception.redacted_command))


if __name__ == "__main__":
    unittest.main()
