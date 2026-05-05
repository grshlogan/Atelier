from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import os
import subprocess

from pydantic import BaseModel, Field


class CommandSpec(BaseModel):
    executable: Path
    args: list[str] = Field(default_factory=list)
    cwd: Path
    env: dict[str, str] = Field(default_factory=dict)
    redacted_args: list[str] = Field(default_factory=list)
    timeout_seconds: float | None = None


class CommandResult(BaseModel):
    returncode: int
    stdout: str
    stderr: str
    redacted_command: list[str]


class CommandExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        returncode: int,
        stdout: str,
        stderr: str,
        redacted_command: list[str],
    ) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.redacted_command = redacted_command


def run_command(spec: CommandSpec, *, base_env: Mapping[str, str] | None = None) -> CommandResult:
    command = [str(spec.executable), *spec.args]
    redacted_command = [str(spec.executable), *(spec.redacted_args or spec.args)]
    process_env = {**dict(base_env or os.environ), **spec.env}
    completed = subprocess.run(
        command,
        cwd=spec.cwd,
        env=process_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=spec.timeout_seconds,
    )
    result = CommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        redacted_command=redacted_command,
    )
    if completed.returncode != 0:
        raise CommandExecutionError(
            f"command failed with exit code {completed.returncode}",
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            redacted_command=result.redacted_command,
        )
    return result
