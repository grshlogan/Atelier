# Atelier Failure Recovery Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的失败分类、恢复动作、partial artifacts、任务恢复、崩溃恢复和用户可见失败界面。

## 1. 目标

Atelier 的失败不是只弹一个错误框。失败必须成为可观察、可诊断、可恢复的产品状态。

```text
失败点可定位
影响范围可解释
可用产物可保留
恢复动作可执行
恢复结果可追踪
```

## 2. 参考软件与取舍

### AWS Step Functions

可借鉴：

- 状态机显式建模任务失败。
- Retry 和 Catch 分开表达。
- 不同错误类型可以有不同恢复路径。

Atelier 的取舍：

- 不引入 Step Functions。
- 借鉴 `error_code -> retry/catch/recovery action` 的明确映射。

### Kubernetes Job

可借鉴：

- Job 有 backoff limit、失败策略和终止条件。
- Pod 失败不是终点，控制器根据策略决定重试或结束。

Atelier 的取舍：

- 本地 Scheduler 承担 Job controller 角色。
- retry 必须受 `failure_policy`、错误类型和用户动作限制。

### Temporal

可借鉴：

- Workflow 状态持久化，Worker 失败后可由系统恢复执行。
- Activity retry policy 明确。
- 长流程不依赖单个进程存活。

Atelier 的取舍：

- 不引入 Temporal。
- 借鉴 durable execution：SQLite 保存任务、事件、artifact 和恢复状态。

### 视频创作软件

可借鉴：

- 渲染失败后通常保留日志、缓存、部分输出和可重新排队动作。

Atelier 的取舍：

- 每个 stage 都应有 artifact 记录。
- downstream impact 必须在 Queue Monitor 中展示。

## 3. Failure Model

```python
class FailureRecord(BaseModel):
    failure_id: str
    job_id: str
    task_id: str
    node_type: str
    error_code: str
    human_message: str
    technical_reason: str
    failed_stage: str
    recoverable: bool
    affected_downstream_tasks: list[str]
    usable_artifacts: list[str]
    recovery_actions: list[RecoveryAction]
    created_at: str
```

```python
class RecoveryAction(BaseModel):
    action_id: str
    kind: Literal[
        "retry",
        "retry_with_changes",
        "resume",
        "skip",
        "fallback_node",
        "switch_runtime",
        "switch_device",
        "export_partial",
        "mark_failed"
    ]
    label_key: str
    risk_level: Literal["low", "medium", "high"]
    requires_user_confirmation: bool
    params: dict
```

## 4. Failure Classes

| Class | Examples | Default |
|---|---|---|
| `input` | `INPUT_MISSING`, `INPUT_CORRUPT` | stop and ask user |
| `runtime` | `RUNTIME_MISSING`, `DEPENDENCY` | repair runtime |
| `hardware` | `OOM`, device lost | switch device / reduce load |
| `timeout` | `TIMEOUT` | retry with larger timeout |
| `worker_internal` | `INTERNAL` | retry once, then report |
| `interrupted` | `INTERRUPTED` | startup recovery, validate partial artifacts |
| `cancelled` | `CANCELLED` | mark cancelled |
| `permission` | `PERMISSION` | ask user to fix path/permission |
| `disk` | `DISK_FULL` | free space / move work dir |
| `plugin` | missing plugin / incompatible plugin | disable or install compatible plugin |

## 5. Retry Rules

Retry is allowed only when:

- `failure_policy` permits retry.
- `retry_count < max_retries`.
- error class is retryable.
- Scheduler can produce a valid ResourceBinding and RuntimeBinding.
- retry does not repeat the same known-failing condition without a change.

Non-retryable by default:

- `CANCELLED`
- `INPUT_CORRUPT`
- `PERMISSION`
- `DISK_FULL`
- missing required plugin
- incompatible runtime

Debug discipline:

- Do not stack speculative retries.
- Record the root cause or best known failure point before retry.
- If retry changes params, device, runtime, or backend, record that change.

## 6. Partial Artifacts

Partial artifact rules:

- Worker can report `partial_artifacts` in failed event.
- Scheduler validates existence and hash when available.
- Partial artifacts are marked `partial`.
- UI shows them as usable, previewable, exportable, or unsafe.

Examples:

```text
ASR failed after segment 120
  -> partial subtitle can be previewed/exported

video enhance failed after frame 4000
  -> image sequence partial can be inspected

mux failed after temp output
  -> partial video may be suspect until ffprobe verifies it
```

## 7. Downstream Impact

When a task fails:

```text
failed task
  -> find downstream tasks through task_dependencies
  -> classify each downstream task:
       blocked
       skippable
       runnable_with_partial
       runnable_with_fallback
  -> update Queue Monitor
```

Rules:

- Downstream tasks are not silently deleted.
- Skip/fallback requires explicit policy or user confirmation.
- If downstream can run with partial artifact, UI must label the result as partial-derived.

## 8. Recovery Actions

### retry

Same task, same params, same runtime/device if still valid.

Use for:

- transient timeout
- temporary file lock
- short-lived process failure

### retry_with_changes

Same node, modified execution params.

Use for:

- lower batch size
- lower concurrency
- longer timeout

### switch_runtime

Same node, different RuntimeBinding.

Use for:

- CUDA backend broken
- missing model format
- switch from GPU backend to CPU backend

### switch_device

Same runtime class, different ResourceBinding.

Use for:

- OOM on one GPU
- user wants another GPU

### fallback_node

Use `fallback_node_type` after compatibility validation.

### skip

Mark task skipped and continue only if downstream can accept missing or partial input.

### export_partial

Export usable artifacts without pretending the full Job completed.

## 9. Crash Recovery

Startup recovery:

```text
App starts
  -> scan jobs/tasks with running/queued status
  -> inspect worker pids and resource locks
  -> mark dead workers failed or interrupted
  -> release stale locks
  -> validate artifacts
  -> rebuild queue from SQLite
  -> show recovery summary
```

Task states:

| Previous state | Startup recovery |
|---|---|
| `queued` | return to `pending` or `queued` based on queue policy |
| `running` with live Worker | reconnect monitor if possible |
| `running` with dead Worker | mark `failed` / `INTERRUPTED` |
| `retry_pending` | requeue |
| `completed` | validate artifacts lazily |

## 10. Failure UI

Failure view must show:

- Failed stage.
- Human-readable reason.
- Technical reason.
- Error code.
- Affected downstream tasks.
- Usable artifacts.
- Recommended recovery actions.
- Logs and Worker events.
- Runtime and device used.

User-facing report format for non-obvious bugs:

```text
Root cause - Scope - Severity and priority - Fix plan - Fix scope - Risk of new bugs
```

## 11. Storage Requirements

Must persist:

- task status.
- task_events.
- artifacts and task_artifacts.
- resource_locks.
- error_code and error_message.
- recovery action chosen.
- retry_count and retry history.

Future table candidate:

```text
failure_records
recovery_actions
recovery_attempts
```

首版可先把 recovery metadata 放入 task_events payload，等行为稳定后拆表。

## 12. 首版实现建议

第一阶段：

- Failure classification helper。
- RecoveryAction model。
- Queue Monitor failure row。
- simulated OOM / timeout / runtime missing tests。
- startup stale running-task recovery。

暂不实现：

- frame-level resume。
- automatic partial video repair。
- distributed worker recovery。

## 13. 参考资料

- AWS Step Functions error handling: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html
- Kubernetes Job failure handling: https://kubernetes.io/docs/concepts/workloads/controllers/job/
- Temporal failure detection and retries: https://docs.temporal.io/encyclopedia/retry-policies
- Celery task retrying: https://docs.celeryq.dev/en/stable/userguide/tasks.html#retrying
