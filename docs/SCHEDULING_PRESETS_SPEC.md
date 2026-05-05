# Atelier Scheduling Presets Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的调度预设系统。预设是面向用户的策略包，用于把复杂的 backlog、并发、设备偏好、fallback 和失败恢复倾向收敛成可理解的选择。预设不能绕过 Scheduler，不能直接写 Worker command。

## 1. 目标

Scheduling Presets 的目标是让入门用户能安全选择调度风格，同时让专业用户可以深入调整。

核心目标：

```text
入门用户选 preset 即可运行
进阶用户调整并发 / backlog / 优先级
专业用户调整设备偏好 / fallback / reserve VRAM
所有预设最终都由 Scheduler 编译成合法 ResourceBinding / RuntimeBinding
```

非目标：

```text
不提供任意 shell 命令模板
不让 preset 直接启动 Worker
不绕过 RuntimeManager
不把插件权限混入调度预设
不把一次运行中已经绑定的 running task 强制迁移
```

## 2. 参考资料与取舍

### Kubernetes Requests / Limits / Scheduler

可借鉴：

- 调度前声明资源需求和约束。
- Scheduler 根据可用资源做最终放置。
- Resource limits 用来防止单个 workload 过度占用。

Atelier 的取舍：

- 不做容器。
- 借鉴 request / limit 思想，把预设转换为 `ResourceRequest`、stage concurrency 和 policy bounds。

### Slurm GRES

可借鉴：

- GPU 是可声明、可分配、可绑定的资源。
- GPU utilization / memory accounting 可用于诊断。
- 资源分配后应该避免多个 job 随意争抢。

Atelier 的取舍：

- 不做集群。
- 借鉴“GPU 不是字符串 cuda:0，而是可调度资源”的原则。
- 预设只能表达 preference，不能绕过 Scheduler 写死设备。

### Celery Rate Limit

可借鉴：

- 对某类 task 设置启动速率或并发上限。
- API 类任务需要 queue/rate limit 保护 provider 限制。

Atelier 的取舍：

- 不引入 Celery。
- 对 `translate.llm`、`subtitle.review` 这类 API/LLM stage 设置 concurrency / rate hints。

## 3. 预设分级

```text
Simple:
  只选择 preset，不显示复杂参数

Standard:
  允许调整 stage concurrency、backlog limit、finish priority

Professional:
  允许调整 device preference、fallback、reserve_vram、stage weights

Debug:
  只用于观察和诊断，不推荐保存为普通 preset
```

## 4. SchedulePolicy 模型

```python
class SchedulingPreset(BaseModel):
    preset_id: str
    name_key: str
    description_key: str
    mode_level: Literal["simple", "standard", "professional", "debug"]
    policy: SchedulePolicy
    built_in: bool = True
    version: str = "1"

class SchedulePolicy(BaseModel):
    stage_weights: dict[str, float] = {}
    concurrency: ConcurrencyPolicy
    backpressure: BackpressurePolicy
    device_preferences: dict[str, DevicePreference] = {}
    fallback: FallbackPolicy
    failure_recovery: FailureRecoveryPreference
    safety: SafetyBounds
    ui_hints: SchedulingUiHints = SchedulingUiHints()
```

## 5. 子模型建议

```python
class DevicePreference(BaseModel):
    preferred_devices: list[str] = []
    excluded_devices: list[str] = []
    allow_cpu_fallback: bool = True
    exclusive_preferred: bool = False
    min_vram_mb: int | None = None
```

```python
class FallbackPolicy(BaseModel):
    allow_backend_switch: bool = True
    allow_model_downshift: bool = False
    allow_batch_or_tile_downshift: bool = True
    allow_cpu_fallback: bool = True
    require_user_confirmation_for_quality_loss: bool = True
```

```python
class FailureRecoveryPreference(BaseModel):
    retry_timeout_once: bool = True
    retry_oom_same_device: bool = False
    suggest_switch_device_on_oom: bool = True
    suggest_lower_batch_on_oom: bool = True
    keep_partial_artifacts: bool = True
```

```python
class SafetyBounds(BaseModel):
    reserve_vram_mb: int = 1024
    reserve_system_ram_mb: int = 2048
    max_pending_intermediate_bytes: int | None = None
    max_consecutive_failures_per_stage: int = 3
    require_confirmation_for_destructive_actions: bool = True
```

## 6. 内置预设清单

### 6.1 Auto Balanced

默认预设。

目标：

```text
在吞吐量、完成速度、显存安全和用户体验之间平衡。
```

建议策略：

```yaml
preset_id: auto_balanced
concurrency:
  max_cpu_tasks: 4
  max_disk_heavy_tasks: 2
  max_gpu_tasks_per_device: 1
  max_shared_gpu_tasks_per_device: 2
  max_remote_translate_tasks: 2
  max_local_llm_tasks: 1
  max_mux_tasks: 2
  max_export_tasks: 1
backpressure:
  max_ocr_backlog: 6
  max_translate_backlog: 8
  max_review_backlog: 6
  max_asr_ahead: 6
safety:
  reserve_vram_mb: 1024
  reserve_system_ram_mb: 2048
fallback:
  allow_cpu_fallback: true
  allow_batch_or_tile_downshift: true
```

适用：

```text
大多数用户
双 GPU 或单 GPU 均可
字幕 + 翻译 + 基础视频处理
```

### 6.2 Finish Videos First

目标：

```text
优先让已经接近完成的视频尽快导出，减少大量半成品悬挂。
```

策略：

```yaml
stage_weights:
  soft_mux: 1.5
  burn_subtitle: 1.4
  export: 1.7
  translate: 1.1
backpressure:
  max_ocr_backlog: 4
  max_translate_backlog: 5
  max_asr_ahead: 3
concurrency:
  max_mux_tasks: 3
  max_export_tasks: 2
```

适用：

```text
用户希望尽快看到成品
批量任务很多但不想所有视频都卡在中间阶段
```

代价：

```text
整体吞吐可能略低
前置 ASR / Enhance 可能被压制
```

### 6.3 Max Throughput

目标：

```text
尽量让硬件不闲置，追求总吞吐。
```

策略：

```yaml
stage_weights:
  asr: 1.2
  video_enhance: 1.2
  frame_interpolation: 1.2
  translate: 1.2
backpressure:
  max_ocr_backlog: 12
  max_translate_backlog: 16
  max_review_backlog: 12
  max_asr_ahead: 14
concurrency:
  max_cpu_tasks: 6
  max_disk_heavy_tasks: 3
  max_shared_gpu_tasks_per_device: 2
  max_remote_translate_tasks: 4
safety:
  reserve_vram_mb: 768
```

适用：

```text
高性能机器
用户接受较高资源占用
远程 API 有足够额度
```

风险：

```text
中间产物更多
硬盘 IO 压力更高
OOM 风险略高
```

### 6.4 Low VRAM Safe

目标：

```text
减少 OOM，适合 8GB / 12GB / 16GB 显存或显存紧张环境。
```

策略：

```yaml
concurrency:
  max_gpu_tasks_per_device: 1
  max_shared_gpu_tasks_per_device: 1
  max_local_llm_tasks: 1
backpressure:
  max_ocr_backlog: 3
  max_translate_backlog: 4
  max_asr_ahead: 3
safety:
  reserve_vram_mb: 2048
  reserve_system_ram_mb: 4096
fallback:
  allow_cpu_fallback: true
  allow_model_downshift: true
  allow_batch_or_tile_downshift: true
failure_recovery:
  retry_oom_same_device: false
  suggest_lower_batch_on_oom: true
  suggest_switch_device_on_oom: true
```

适用：

```text
单卡小显存
视频增强 / 插帧容易 OOM
本地 LLM 与视频任务冲突
```

### 6.5 Single GPU Safe

目标：

```text
单 GPU 机器上避免 ASR、LLM、Enhance、RIFE 互相抢显存。
```

策略：

```yaml
concurrency:
  max_gpu_tasks_per_device: 1
  max_shared_gpu_tasks_per_device: 1
  max_local_llm_tasks: 1
backpressure:
  max_ocr_backlog: 4
  max_translate_backlog: 5
  max_asr_ahead: 4
device_preferences:
  asr:
    allow_cpu_fallback: true
  translate:
    exclusive_preferred: true
  video_enhance:
    exclusive_preferred: true
  frame_interpolation:
    exclusive_preferred: true
```

适用：

```text
只有一张 GPU
想要稳定完成
```

### 6.6 Dual GPU Split

目标：

```text
双 GPU 机器上把慢 LLM / 翻译和视频增强类任务分开。
```

推荐默认：

```text
GPU 0: translate.llm / subtitle.review / local LLM
GPU 1: asr.whisper / enhance.realesrgan / enhance.rife
CPU: probe / audio_extract / normalize / mux / export
```

策略：

```yaml
device_preferences:
  translate:
    preferred_devices: ["gpu:0"]
    exclusive_preferred: true
  subtitle_review:
    preferred_devices: ["gpu:0"]
    exclusive_preferred: true
  asr:
    preferred_devices: ["gpu:1"]
    allow_cpu_fallback: true
  ocr:
    preferred_devices: ["gpu:1"]
    allow_cpu_fallback: true
  video_enhance:
    preferred_devices: ["gpu:1"]
    exclusive_preferred: true
  frame_interpolation:
    preferred_devices: ["gpu:1"]
    exclusive_preferred: true
concurrency:
  max_gpu_tasks_per_device: 1
  max_remote_translate_tasks: 2
  max_local_llm_tasks: 1
```

降级：

```text
如果只检测到 1 张 GPU，自动降级为 Single GPU Safe，并提示用户。
```

### 6.7 Subtitle First

目标：

```text
优先把字幕链路做完，适合字幕翻译/审校是核心需求的用户。
```

策略：

```yaml
stage_weights:
  audio_extract: 1.1
  asr: 1.4
  subtitle_normalize: 1.3
  translate: 1.5
  subtitle_review: 1.4
  soft_mux: 1.2
  video_enhance: 0.75
  frame_interpolation: 0.7
backpressure:
  max_ocr_backlog: 8
  max_translate_backlog: 10
  max_asr_ahead: 8
```

适用：

```text
主要目标是快速得到字幕
视频增强不是第一优先
```

### 6.8 Enhance First

目标：

```text
优先处理视频增强 / 插帧，适合视频画质提升是主需求的用户。
```

策略：

```yaml
stage_weights:
  video_enhance: 1.5
  frame_interpolation: 1.4
  asr: 0.9
  translate: 0.9
backpressure:
  max_ocr_backlog: 3
  max_translate_backlog: 4
  max_asr_ahead: 3
concurrency:
  max_gpu_tasks_per_device: 1
  max_disk_heavy_tasks: 2
safety:
  reserve_vram_mb: 1536
```

适用：

```text
批量视频增强
字幕可以稍后
```

### 6.9 Remote API Translation

目标：

```text
翻译走远程 API，本地 GPU 尽量留给 ASR / Enhance / RIFE。
```

策略：

```yaml
device_preferences:
  translate:
    preferred_devices: []
    allow_cpu_fallback: true
  subtitle_review:
    preferred_devices: []
    allow_cpu_fallback: true
concurrency:
  max_remote_translate_tasks: 2
  max_local_llm_tasks: 0
backpressure:
  max_ocr_backlog: 8
  max_translate_backlog: 12
  max_asr_ahead: 10
```

额外约束：

```text
必须检查 credential_ref
必须检查 provider rate / cost policy
API 并发不等于无限；默认保守
```

### 6.10 Local LLM Translation

目标：

```text
翻译和审校走本地 LLM，明确把本地 LLM 当成高占用 stage。
```

策略：

```yaml
device_preferences:
  translate:
    preferred_devices: ["gpu:0"]
    exclusive_preferred: true
    allow_cpu_fallback: false
  subtitle_review:
    preferred_devices: ["gpu:0"]
    exclusive_preferred: true
    allow_cpu_fallback: false
concurrency:
  max_local_llm_tasks: 1
  max_gpu_tasks_per_device: 1
backpressure:
  max_ocr_backlog: 4
  max_translate_backlog: 6
  max_asr_ahead: 4
safety:
  reserve_vram_mb: 2048
```

适用：

```text
本地模型翻译
用户有大显存 GPU
希望隐私优先或离线工作
```

### 6.11 Quiet / Low Power

目标：

```text
降低资源占用，减少风扇噪音和温度。
```

策略：

```yaml
concurrency:
  max_cpu_tasks: 2
  max_disk_heavy_tasks: 1
  max_gpu_tasks_per_device: 1
  max_remote_translate_tasks: 1
backpressure:
  max_ocr_backlog: 2
  max_translate_backlog: 3
  max_asr_ahead: 2
safety:
  reserve_vram_mb: 2048
  reserve_system_ram_mb: 4096
stage_weights:
  export: 0.9
  video_enhance: 0.7
  frame_interpolation: 0.7
```

适用：

```text
笔记本
夜间运行
用户希望系统仍可用于其他工作
```

## 7. 预设应用流程

```text
User selects preset
  -> UI sends intent: ApplySchedulingPreset(preset_id)
  -> Application Service loads preset
  -> Validate against current hardware/runtime
  -> Build SchedulePolicy
  -> Scheduler uses policy on next scheduling tick
  -> Running tasks keep current ResourceBinding
  -> Pending/queued/retry_pending tasks may be re-evaluated
  -> Hardware Scheduling Page refreshes
```

规则：

- 切换 preset 不强制迁移 running task。
- 对 running task 的取消/重启需要用户明确动作。
- 如果 preset 与当前硬件不兼容，应自动降级或显示 warning。
- Preset 应写入 Job / Plan metadata，便于复现。

## 8. 硬件兼容与降级

| Preset | 不兼容情况 | 降级 |
|---|---|---|
| Dual GPU Split | 只有 1 张 GPU | Single GPU Safe |
| Local LLM Translation | 没有本地 LLM runtime | Remote API Translation 或 Runtime Missing |
| Remote API Translation | credential missing | Local LLM Translation 或 Waiting Credential |
| Low VRAM Safe | 无 GPU | CPU Safe / degrade unsupported GPU tasks |
| Enhance First | video enhance runtime missing | Auto Balanced + runtime warning |

降级必须显示：

```text
Preset adjusted
Reason: Dual GPU Split requires at least 2 GPUs, only 1 available.
Applied fallback: Single GPU Safe.
```

## 9. 用户自定义 Preset

允许用户从内置 preset 派生 custom preset。

```python
class CustomSchedulingPreset(BaseModel):
    preset_id: str
    base_preset_id: str
    name: str
    policy_overrides: dict
    created_at: str
    updated_at: str
```

规则：

- Custom preset 只能覆盖白名单字段。
- 危险字段需要 Professional mode。
- preset schema version 不匹配时，迁移失败则禁用 custom preset，不阻塞 app 启动。
- 不在 preset 中保存 secrets。
- 不在 preset 中保存绝对本地 runtime 路径；路径归 RuntimeManager。

## 10. UI 呈现

### Simple Mode

只显示 preset 选择：

```text
Scheduling Preset: Auto Balanced
Current bottleneck: Translate Agent
Suggested: Remote API concurrency can be increased to 3
```

### Standard Mode

显示可调项：

```text
Translate concurrency
Translate backlog limit
ASR ahead limit
Finish videos first toggle
CPU fallback toggle
```

### Professional Mode

显示：

```text
Stage weights
Device preferences
Reserve VRAM
Local/remote LLM policy
OOM recovery behavior
Timeout retry behavior
```

### Debug Mode

显示：

```text
Raw SchedulePolicy JSON
ResourceBinding decision
Rejected candidate list
WaitingReason distribution
```

## 11. Preset 与 failure recovery

Preset 可影响建议动作，但不能修改错误事实。

例如 OOM：

```text
Low VRAM Safe:
  优先建议 lower batch / tile
  禁止 same GPU same params retry

Max Throughput:
  可建议 switch device
  不应自动降低质量，除非用户允许

Local LLM Translation:
  翻译 OOM 时建议 smaller model / CPU fallback disabled warning
```

TIMEOUT：

```text
Quiet / Low Power:
  可建议增加 timeout
  不建议提高并发

Max Throughput:
  可建议拆分任务或增加 worker timeout
```

CANCELLED：

```text
所有 preset:
  不进入普通 retry 路径
```

## 12. Preset 与 batch pipeline

Preset 主要影响：

```text
stage_weights
backpressure limits
concurrency limits
device preferences
fallback preferences
finish priority
```

不影响：

```text
同一视频内部 artifact dependency
Worker protocol event contract
SQLite event append rules
Security / secrets policy
Plugin permission model
```

## 13. 首版实现建议

### Phase A：内置 preset 数据文件

新增：

```text
atelier/scheduler/presets.py
atelier/scheduler/preset_models.py
```

或先用：

```text
atelier/scheduler/presets/*.json
```

### Phase B：Apply preset intent

- UI 选择 preset。
- Application service 更新 plan/job scheduling policy。
- Running task 不受影响。

### Phase C：Preset -> Scheduler tick

- Scheduler 使用 policy 过滤 candidate。
- 实现 Translate backlog / ASR ahead / remote translate concurrency。

### Phase D：Hardware Scheduling Page 展示

- Header 显示当前 preset。
- Inspector 显示 preset effects。
- Waiting reason 能说明 preset 导致的 pause。

### Phase E：Custom preset

- 用户从内置 preset 派生。
- 保存到 user settings 或 project metadata。

## 14. 与其他文档的关系

```text
BATCH_PIPELINE_SCHEDULING_SPEC
  -> 预设控制 backpressure / concurrency / finish priority

HARDWARE_SCHEDULING_PAGE_SPEC
  -> 预设选择和策略解释的 UI 入口

HARDWARE_SCHEDULING_SPEC
  -> 预设不能绕过 ResourceBinding / resource_locks

FAILURE_RECOVERY_SPEC
  -> 预设影响建议动作，不改错误事实

RUNTIME_ENVIRONMENT_SPEC
  -> 预设不能保存 runtime 绝对路径，只表达 runtime class / backend preference
```

## 15. Blockers

- 需要先冻结内置 stage key。
- 需要 Scheduler 支持 WaitingReason。
- 需要 HardwareDetector / RuntimeManager 提供可用性摘要。
- 需要决定 user settings 与 project metadata 的保存边界。

## 16. 参考资料

- Kubernetes Scheduler: https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/
- Kubernetes Limit Ranges: https://kubernetes.io/docs/concepts/policy/limit-range/
- Slurm GRES Scheduling: https://slurm.schedmd.com/gres.html
- Celery Task Rate Limit: https://docs.celeryq.dev/en/stable/userguide/tasks.html
- NVIDIA NVML API: https://docs.nvidia.com/deploy/nvml-api/
