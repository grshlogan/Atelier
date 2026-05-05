from __future__ import annotations

from pathlib import Path
import subprocess

from pydantic import BaseModel, Field

from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest, RuntimeStatus
from atelier.security.package_integrity import verify_sha256


class RuntimeHealthReport(BaseModel):
    subject_id: str
    status: RuntimeStatus
    issues: list[str] = Field(default_factory=list)
    repair_hints: list[str] = Field(default_factory=list)
    checked_paths: dict[str, str] = Field(default_factory=dict)


class RuntimeHealthChecker:
    def __init__(self, data_root: str | Path) -> None:
        self.data_root = Path(data_root)

    def check_runtime(
        self,
        manifest: RuntimeManifest,
        *,
        dry_run_args: dict[str, list[str]] | None = None,
    ) -> RuntimeHealthReport:
        if manifest.status != "ready":
            return RuntimeHealthReport(
                subject_id=manifest.runtime_id,
                status=manifest.status,
                issues=[f"runtime status is {manifest.status}"],
                repair_hints=[f"Enable or repair the {manifest.component} runtime profile."],
            )

        checked_paths: dict[str, str] = {}
        missing_issues: list[str] = []
        broken_issues: list[str] = []
        for name, raw_path in manifest.component_paths.items():
            path = self._resolve_path(raw_path)
            checked_paths[name] = str(path)
            if not path.exists():
                missing_issues.append(f"missing component path: {name}")
                continue
            expected_sha256 = manifest.checksums.get(name)
            if expected_sha256 and not verify_sha256(path, expected_sha256):
                broken_issues.append(f"checksum mismatch: {name}")

        if missing_issues:
            return RuntimeHealthReport(
                subject_id=manifest.runtime_id,
                status="missing",
                issues=missing_issues,
                repair_hints=[f"Register or repair the {manifest.component} runtime path."],
                checked_paths=checked_paths,
            )
        if broken_issues:
            return RuntimeHealthReport(
                subject_id=manifest.runtime_id,
                status="broken",
                issues=broken_issues,
                repair_hints=[f"Reinstall or replace the {manifest.component} runtime component."],
                checked_paths=checked_paths,
            )
        dry_run_issues = self._run_dry_run_checks(manifest, dry_run_args or {}, checked_paths)
        if dry_run_issues:
            repair_hints = []
            for issue in dry_run_issues:
                name = issue.removeprefix("dry-run failed: ")
                repair_hints.append(f"Check the {name} runtime configuration and probe arguments.")
            return RuntimeHealthReport(
                subject_id=manifest.runtime_id,
                status="broken",
                issues=dry_run_issues,
                repair_hints=repair_hints,
                checked_paths=checked_paths,
            )
        return RuntimeHealthReport(
            subject_id=manifest.runtime_id,
            status="ready",
            checked_paths=checked_paths,
        )

    def check_model_asset(self, manifest: ModelAssetManifest) -> RuntimeHealthReport:
        if manifest.status != "ready":
            return RuntimeHealthReport(
                subject_id=manifest.model_id,
                status=manifest.status,
                issues=[f"model status is {manifest.status}"],
                repair_hints=[f"Enable or repair the {manifest.model_id} model profile."],
            )

        path = self._resolve_path(manifest.local_path)
        checked_paths = {"model": str(path)}
        if not path.exists():
            return RuntimeHealthReport(
                subject_id=manifest.model_id,
                status="missing",
                issues=[f"missing model path: {manifest.model_id}"],
                repair_hints=[f"Register or repair the {manifest.model_id} model path."],
                checked_paths=checked_paths,
            )
        if manifest.sha256 and (not path.is_file() or not verify_sha256(path, manifest.sha256)):
            return RuntimeHealthReport(
                subject_id=manifest.model_id,
                status="broken",
                issues=[f"checksum mismatch: {manifest.model_id}"],
                repair_hints=[f"Reinstall or replace the {manifest.model_id} model asset."],
                checked_paths=checked_paths,
            )
        return RuntimeHealthReport(
            subject_id=manifest.model_id,
            status="ready",
            checked_paths=checked_paths,
        )

    def _resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path
        return self.data_root / path

    def _run_dry_run_checks(
        self,
        manifest: RuntimeManifest,
        dry_run_args: dict[str, list[str]],
        checked_paths: dict[str, str],
    ) -> list[str]:
        issues: list[str] = []
        for name, args in dry_run_args.items():
            raw_executable = manifest.executable_paths.get(name) or manifest.component_paths.get(name)
            if raw_executable is None:
                issues.append(f"dry-run failed: {name}")
                continue
            executable = self._resolve_path(raw_executable)
            checked_paths[f"{name}:dry_run"] = str(executable)
            try:
                completed = subprocess.run(
                    [str(executable), *args],
                    cwd=self.data_root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                    timeout=5,
                )
            except (OSError, subprocess.TimeoutExpired):
                issues.append(f"dry-run failed: {name}")
                continue
            if completed.returncode != 0:
                issues.append(f"dry-run failed: {name}")
        return issues
