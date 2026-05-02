CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    root_dir TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_graphs (
    graph_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    graph_json TEXT NOT NULL,
    node_count INTEGER NOT NULL DEFAULT 0,
    edge_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    name TEXT NOT NULL,
    workflow_graph_id TEXT NOT NULL REFERENCES workflow_graphs(graph_id),
    execution_plan_id TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    priority INTEGER NOT NULL DEFAULT 0,
    input_media_paths TEXT NOT NULL DEFAULT '[]',
    output_dir TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS execution_plans (
    plan_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    workflow_graph_id TEXT NOT NULL REFERENCES workflow_graphs(graph_id),
    status TEXT NOT NULL DEFAULT 'draft',
    phases_json TEXT NOT NULL DEFAULT '[]',
    conflicts_json TEXT NOT NULL DEFAULT '[]',
    hardware_snapshot TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS execution_tasks (
    task_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL REFERENCES execution_plans(plan_id),
    phase_id TEXT NOT NULL,
    lane_id TEXT NOT NULL,
    source_node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    params_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    resource_request TEXT NOT NULL DEFAULT '{}',
    resource_binding TEXT,
    runtime_request TEXT NOT NULL DEFAULT '{}',
    runtime_binding TEXT,
    failure_policy TEXT NOT NULL DEFAULT '{}',
    cache_key TEXT,
    cache_hit INTEGER NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error_code TEXT,
    error_message TEXT,
    duration_seconds REAL
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id TEXT NOT NULL REFERENCES execution_tasks(task_id),
    depends_on_task_id TEXT NOT NULL REFERENCES execution_tasks(task_id),
    PRIMARY KEY (task_id, depends_on_task_id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES execution_tasks(task_id),
    artifact_type TEXT NOT NULL,
    path TEXT NOT NULL,
    hash TEXT,
    size_bytes INTEGER,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'valid',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS task_artifacts (
    link_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES execution_tasks(task_id),
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
    role TEXT NOT NULL,
    port_id TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE (task_id, artifact_id, role, port_id)
);

CREATE TABLE IF NOT EXISTS task_events (
    event_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES execution_tasks(task_id),
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    seq INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    UNIQUE (task_id, seq)
);

CREATE TABLE IF NOT EXISTS resource_locks (
    lock_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES execution_tasks(task_id),
    device_id TEXT NOT NULL,
    lock_type TEXT NOT NULL,
    vram_mb INTEGER,
    owner_pid INTEGER,
    acquired_at TEXT NOT NULL,
    heartbeat_at TEXT,
    stale_after TEXT,
    released_at TEXT
);

CREATE TABLE IF NOT EXISTS cache_entries (
    cache_key TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    node_version TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
    params_hash TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    runtime_fingerprint TEXT NOT NULL DEFAULT '',
    model_fingerprint TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    last_hit_at TEXT,
    hit_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS presets (
    preset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general',
    description TEXT NOT NULL DEFAULT '',
    graph_json TEXT NOT NULL,
    is_builtin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runtime_components (
    component_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    kind TEXT NOT NULL,
    install_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'missing',
    hash TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    installed_at TEXT,
    last_checked_at TEXT
);

CREATE TABLE IF NOT EXISTS model_assets (
    model_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    backend TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '',
    local_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'missing',
    hash TEXT,
    size_bytes INTEGER,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS credential_refs (
    credential_ref_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    account_label TEXT NOT NULL DEFAULT '',
    purpose TEXT NOT NULL DEFAULT '',
    backend TEXT NOT NULL DEFAULT 'os',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_checked_at TEXT
);
