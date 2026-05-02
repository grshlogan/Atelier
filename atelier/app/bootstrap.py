from dataclasses import dataclass


@dataclass(frozen=True)
class AppBootstrapConfig:
    app_name: str = "Atelier"
    database_path: str | None = None
