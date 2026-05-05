from __future__ import annotations

import sqlite3

from atelier.app.paths import AppPaths
from atelier.app.runtime_setup import RuntimeSetupAppService
from atelier.runtime.health import RuntimeHealthChecker
from atelier.runtime.store import RuntimeStore
from atelier.storage.db import initialize_database


def create_runtime_store(paths: AppPaths) -> RuntimeStore:
    paths.ensure_data_dirs()
    return RuntimeStore(paths.data_root)


def create_runtime_setup_service(paths: AppPaths) -> RuntimeSetupAppService:
    return RuntimeSetupAppService(
        create_runtime_store(paths),
        RuntimeHealthChecker(paths.data_root),
    )


def open_app_database(paths: AppPaths) -> sqlite3.Connection:
    paths.ensure_data_dirs()
    connection = sqlite3.connect(paths.database_path)
    initialize_database(connection)
    return connection
