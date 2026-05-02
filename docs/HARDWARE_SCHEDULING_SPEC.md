# Atelier Hardware Scheduling Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的硬件检测、资源请求、调度绑定、资源锁、OOM 降级和硬件状态展示策略。

## 1. 目标

Atelier 的硬件调度必须让本地 AI 视频任务可解释、可控、可恢复。

```text
检测真实硬件
声明资源需求
Scheduler 做最终绑定
Worker 只使用绑定结果
冲突可解释
OOM 可恢复
```

## 2. 参考软件与取舍

### NVIDIA NVML / nvidia-ml-py

可借鉴：

- NVML 是 NVIDIA 官方 GPU 管理与监控 API。
- 适合读取 GPU 名称、显存、利用率、进程占用、driver 信息和健康状态。

Atelier 的取舍：

- NVIDIA GPU 首选 `nvidia-ml-py` 读取 NVML。
- NVML 不可用时降级为 unknown GPU state，而不是让应用启动失败。

### psutil

可借鉴：

- psutil 是跨平台系统与进程监控库，可读取 CPU、内存、磁盘、网络和进程信息。

Atelier 的取舍：

- CPU/RAM/磁盘/Worker 进程健康优先用 psutil。
- 温度、风扇等平台差异较大的信息只做 optional signals。

### Kubernetes Device Plugins

可借鉴：

- 把 GPU 视为可调度资源。
- 先由设备插件暴露资源，再由调度器根据资源请求安排任务。
- 不同 GPU 类型用 labels / selectors 表达。

Atelier 的取舍：

- 不引入 Kubernetes。
- 借鉴“resource request + scheduler binding + capability labels”的模型。

### Slurm GRES

可借鉴：

- GPU 属于 generic resources，可以被声明、检测、分配和隔离。
- 自动检测结果和配置可能不一致，需要诊断输出。

Atelier 的取舍：

- 本地单机不实现 HPC 队列。
- 借鉴 GRES 的设备清单、resource lock 和诊断思想。

## 3. 核心模型

```text
HardwareSnapshot
  -> DeviceInfo[]
  -> captured_at

ResourceRequest
  -> device_type
  -> capabilities
  -> vram_mb
  -> cpu_cores
  -> ram_mb
  -> exclusive

ResourceBinding
  -> device_id
  -> allocated_vram_mb
  -> shared_with
  -> binding_reason

ResourceLock
  -> task_id
  -> device_id
  -> lock_type
  -> acquired_at
  -> heartbeat_at
  -> stale_after
```

## 4. Device Identity

Atelier 不应把 `cuda:0` 当作稳定事实。

设备标识分三层：

```text
stable_device_id   -> Atelier 内部稳定 ID，尽量基于 PCI bus id / UUID
runtime_device_id  -> backend 使用的 ID，如 cuda index / vulkan device index
display_name       -> GUI 展示名，如 NVIDIA RTX 4090
```

规则：

- Scheduler 和数据库存 `stable_device_id`。
- Worker 启动时 RuntimeManager 将其转换为 backend 可用的 `runtime_device_id`。
- 示例文档不得把 `cuda:0` 写成默认策略，只能作为 explicit test fixture。

## 5. Hardware Detection

检测层：

```text
HardwareDetector
  -> NvidiaAdapter(NVML)
  -> CpuRamAdapter(psutil)
  -> DiskAdapter(psutil / pathlib)
  -> RuntimeCapabilityAdapter(RuntimeManager)
```

检测内容：

- GPU name / UUID / driver version。
- VRAM total / free / used。
- GPU utilization。
- active process list when available。
- CPU logical/physical cores。
- RAM total / available。
- disk free space for work/cache/output directories。
- backend capability: `cuda`, `vulkan`, `cpu`, `avx2`, etc.

失败处理：

- 某个 adapter 失败不应阻止 App 启动。
- 失败 adapter 在 Hardware panel 中显示 `unknown` 或 `unavailable`。
- Scheduler 不应把 unknown GPU 当作可用 GPU。

## 6. Scheduling Flow

```text
Queue receives Job
  -> Scheduler loads ExecutionPlan
  -> HardwareDetector captures current snapshot
  -> RuntimeManager resolves RuntimeBinding candidates
  -> Scheduler filters tasks whose dependencies are complete
  -> Scheduler checks ResourceRequest + RuntimeRequest
  -> Scheduler writes ResourceBinding
  -> Scheduler writes resource_locks
  -> Scheduler starts Worker
  -> Scheduler monitors Worker events and heartbeat
  -> Scheduler releases resource_locks
```

规则：

- Scheduler 是唯一资源绑定事实源。
- GUI 只能表达 preference，如 preferred GPU 或 avoid GPU。
- Lane hint 只影响排序和建议，不是最终绑定。
- Runtime availability 必须参与调度；没有 backend 的硬件不可被选中。

## 7. Scheduling Policy

默认策略：

```text
1. dependency ready
2. runtime available
3. hardware available
4. exclusive tasks before shared tasks
5. larger VRAM tasks before smaller VRAM tasks within same priority
6. user priority
7. FIFO within same priority
```

资源模式：

| 模式 | 含义 |
|---|---|
| `exclusive` | 独占设备。适合大模型、插帧、超分、未知显存峰值任务。 |
| `shared` | 可共享设备。适合轻量翻译、小模型、短任务。 |
| `cpu` | 只使用 CPU。 |
| `any` | Scheduler 可选 CPU/GPU/backend。 |

共享规则：

- 共享任务的 VRAM 估算总和不能超过可用阈值。
- 估算不可信的任务默认倾向 exclusive。
- 任务运行中超过阈值时，后续共享任务不再进入该 GPU。

## 8. Hardware Policy

用户可配置：

```yaml
hardware_policy:
  preferred_devices: []
  excluded_devices: []
  max_parallel_gpu_tasks: 1
  reserve_vram_mb: 1024
  reserve_system_ram_mb: 2048
  allow_cpu_fallback: true
  allow_runtime_backend_switch: true
```

规则：

- policy 是约束和偏好，不是绕过 Scheduler 的命令。
- policy 变更后未运行任务重新调度，运行中任务不强制迁移。

## 9. OOM And Resource Failure

OOM 处理：

```text
Worker reports OOM
  -> Scheduler marks task failed with error_code=OOM
  -> release resource lock
  -> record peak usage if available
  -> propose recovery actions
```

恢复建议：

- 减少并行任务。
- 切换到更大显存 GPU。
- 降低 batch size。
- 切换更小模型。
- 切换 CPU/backend。
- 跳过该节点并保留可用 artifacts。

禁止：

- 静默重试到同一 GPU 且参数不变。
- 自动改用户参数但不记录。
- GUI 直接修改 Worker 命令。

## 10. Stale Lock Recovery

resource lock 可能因为 App 崩溃、Worker 被杀、系统重启而残留。

启动恢复流程：

```text
App starts
  -> scan resource_locks where released_at is NULL
  -> check owner_pid
  -> check task status
  -> check heartbeat_at / stale_after
  -> mark stale locks released with reason
  -> recover affected jobs
```

规则：

- 不能只因为 lock 存在就永久阻塞设备。
- stale lock 释放必须写入 event / audit note。
- 如果 Worker 仍存在且 task running，不释放锁。

## 11. UI Requirements

Hardware panel 必须显示：

- GPU / CPU / RAM / disk。
- 每个设备当前 active tasks。
- reserved / used / free VRAM。
- runtime/backend availability。
- conflicts and suggested fixes。

Queue Monitor 必须显示：

- waiting for dependency。
- waiting for hardware。
- waiting for runtime。
- running on which device。
- failed because of OOM / timeout / runtime missing。

## 12. 首版实现建议

第一阶段：

- `HardwareDetector` with psutil + optional NVML。
- `ResourceRequest` / `ResourceBinding` models。
- SQLite `resource_locks` usage。
- simulated GPU device for tests。
- Scheduler binding unit tests。

暂不实现：

- MIG / multi-instance GPU。
- distributed scheduling。
- thermal throttling policy。
- automatic model quantization。

## 13. 参考资料

- NVIDIA NVML API: https://docs.nvidia.com/deploy/nvml-api/index.html
- psutil documentation: https://psutil.readthedocs.io/en/latest/
- Kubernetes GPU scheduling: https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/
- Kubernetes device plugins: https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/
- Slurm GRES scheduling: https://slurm.schedmd.com/gres.html
