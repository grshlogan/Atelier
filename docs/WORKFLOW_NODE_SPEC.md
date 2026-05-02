# Atelier Workflow Node Spec

> 状态：规划中，尚未实现。本文档是 Workflow Canvas 中节点、端口、连线和图的协议规范，作为未来 Pydantic model 和 GUI 渲染的直接依据。

## 1. 概述

WorkflowGraph 是 Atelier 的核心数据结构之一。用户在 Workflow Canvas 上通过拖放节点和连线来描述"对视频做什么"，最终产出一个 WorkflowGraph。

```text
用户操作 Workflow Canvas
  → 构建 WorkflowGraph（节点 + 连线）
    → 交给 ExecutionPlanner 生成 ExecutionPlan
      → 交给 Scheduler 调度执行
```

关键区分：

- **WorkflowNode** 描述"做什么"（ASR、翻译、增强……）。
- **ExecutionTask** 描述"怎么做"（哪台设备、分配多少显存、何时运行）。

节点不直接执行任务，也不持有运行时状态。运行时状态属于 ExecutionPlan 和 Worker。

## 2. 核心概念

| 概念 | 含义 |
|---|---|
| Node（节点） | 一个处理步骤的声明：类型、参数、输入输出端口、资源提示 |
| Port（端口） | 节点上的数据接口，分 input port 和 output port |
| Edge（边） | 连接一个 output port 到一个 input port，表示数据流向 |
| Slot（插槽） | Port 的同义词，GUI 中对端口的可视化锚点 |
| WorkflowGraph | 由节点和边组成的 DAG，描述完整处理流程 |

## 3. 节点分类 (NodeCategory)

```python
class NodeCategory(str, Enum):
    INPUT   = "input"
    PROCESS = "process"
    COMPOSE = "compose"
    OUTPUT  = "output"
    CONTROL = "control"
```

| 分类 | 用途 | 示例 node_type |
|---|---|---|
| `input` | 媒体输入源 | `input.video`, `input.audio`, `input.subtitle` |
| `process` | AI / 媒体处理 | `asr.whisper`, `translate.llm`, `subtitle.review`, `enhance.realesrgan`, `enhance.rife`, `audio.enhance` |
| `compose` | 合成 / 封装 | `compose.mux_subtitle`, `compose.burn_subtitle`, `compose.mux_audio` |
| `output` | 导出 / 输出 | `output.export`, `output.multi_format` |
| `control` | 流程控制（预留） | `control.branch`, `control.merge` |

## 4. 节点 Schema (WorkflowNode)

```python
class WorkflowNode(BaseModel):
    node_id:          str                         # ULID
    node_type:        str                         # 注册名，如 "asr.whisper"
    category:         NodeCategory
    display_name:     str                         # 人类可读名称
    version:          str                         # semver，如 "1.0.0"

    inputs:           list[PortDefinition]
    outputs:          list[PortDefinition]

    params:           list[NodeParam]             # 用户可配置参数
    param_values:     dict[str, Any]              # 用户设定的参数值（覆盖默认值）

    resource_hint:    ResourceHint | None = None  # 资源提示，非强制
    failure_policy:   FailurePolicy               # 失败策略

    cacheable:        bool = True                 # 是否支持缓存
    cache_key_fields: list[str] = []              # 参与 cache key 计算的参数名

    position:         tuple[float, float] = (0, 0)  # canvas 上的坐标，仅用于 GUI
```

### 字段说明

- `node_id`：全局唯一，ULID 格式。每个 WorkflowGraph 内不重复。
- `node_type`：从 NodeRegistry 注册的类型名。格式为 `{category_or_domain}.{name}`。
- `param_values`：用户在 Inspector 中设定的实际参数值。键名与 `params[].name` 对应。未设定的参数使用 `NodeParam.default`。
- `cache_key_fields`：决定哪些参数变化后需要重新执行。不列入的参数变化不影响缓存命中（例如 `display_name` 不影响缓存）。

## 5. 端口 Schema (PortDefinition)

```python
class PortDataType(str, Enum):
    VIDEO     = "video"
    AUDIO     = "audio"
    SUBTITLE  = "subtitle"
    IMAGE_SEQ = "image_seq"
    METADATA  = "metadata"
    ANY       = "any"

class PortDefinition(BaseModel):
    port_id:    str                       # 端口标识，node 内唯一
    direction:  Literal["input", "output"]
    data_type:  PortDataType
    required:   bool = True               # input port: 是否必须连线
    multi:      bool = False              # 是否接受多条连线
    label:      str = ""                  # GUI 显示名
```

### 连线兼容规则

| Source data_type | 可连接的 Target data_type |
|---|---|
| `video` | `video`, `any` |
| `audio` | `audio`, `any` |
| `subtitle` | `subtitle`, `any` |
| `image_seq` | `image_seq`, `any` |
| `metadata` | `metadata`, `any` |
| `any` | `any`，或在运行前已经绑定成具体类型的目标端口 |

`any` 类型用于通用节点（如 control 节点），运行时由实际数据决定类型。

约束：

- `target.data_type == any` 表示该输入端口可以接收任意已知具体类型。
- `source.data_type == any` 不应绕过类型检查；它必须在 ExecutionPlanner 生成计划前被推导或绑定为具体类型。
- 如果无法推导出具体类型，WorkflowGraph 验证应返回 `DataTypeUnresolved`，不应进入 ExecutionPlan。

## 6. 边 Schema (WorkflowEdge)

```python
class WorkflowEdge(BaseModel):
    edge_id:        str   # ULID
    source_node_id: str
    source_port_id: str
    target_node_id: str
    target_port_id: str
```

### 约束

- `source_port_id` 对应的 port 必须 `direction == "output"`。
- `target_port_id` 对应的 port 必须 `direction == "input"`。
- `source_node_id != target_node_id`（不可自连）。
- 同一 `(source_node_id, source_port_id, target_node_id, target_port_id)` 不可重复。
- 如果 target port 的 `multi == False`，则该 port 只能有一条入边。
- source 和 target 的 `data_type` 必须兼容（见 §5 连线兼容规则）。

## 7. 参数 Schema (NodeParam)

```python
class ParamType(str, Enum):
    STRING   = "string"
    INT      = "int"
    FLOAT    = "float"
    BOOL     = "bool"
    ENUM     = "enum"
    PATH     = "path"
    MODEL_ID = "model_id"

class ParamTier(str, Enum):
    BASIC    = "basic"
    ADVANCED = "advanced"
    EXPERT   = "expert"

class ParamConstraints(BaseModel):
    min:       float | int | None = None
    max:       float | int | None = None
    choices:   list[str] | None = None      # 仅 ENUM 类型
    regex:     str | None = None            # 仅 STRING 类型
    file_ext:  list[str] | None = None      # 仅 PATH 类型

class NodeParam(BaseModel):
    name:         str                       # 参数标识名
    display_name: str                       # 人类可读名
    type:         ParamType
    default:      Any | None = None
    constraints:  ParamConstraints | None = None
    tier:         ParamTier = ParamTier.BASIC
    dangerous:    bool = False              # True 时 GUI 需明确标记
    description:  str = ""                  # 简短说明
```

### tier 用途

- `basic`：Inspector 默认展开区域显示。
- `advanced`：需展开"高级"才可见。
- `expert`：需展开"专家"才可见，通常伴随 `dangerous = True` 标记。

## 8. ResourceHint Schema

```python
class DeviceType(str, Enum):
    GPU = "gpu"
    CPU = "cpu"
    ANY = "any"

class ResourceHint(BaseModel):
    device_type:          DeviceType = DeviceType.ANY
    vram_mb:              int | None = None       # 预估 VRAM 需求
    exclusive_gpu:        bool = False             # 是否需要独占 GPU
    estimated_duration_sec: float | None = None    # 预估时长（辅助 ETA）
```

ResourceHint 是节点对资源需求的"提示"，不是强制指令。ExecutionPlanner 和 Scheduler 根据 hint 与实际硬件做出最终决策。

## 9. FailurePolicy Schema

```python
class FailureAction(str, Enum):
    STOP  = "stop"
    SKIP  = "skip"
    RETRY = "retry"

class FailurePolicy(BaseModel):
    on_failure:         FailureAction = FailureAction.STOP
    max_retries:        int = 0
    fallback_node_type: str | None = None   # 失败后尝试替代节点类型
```

- `stop`：当前节点失败时中止整个 Job 中该节点的下游。
- `skip`：跳过当前节点，下游使用空输入或降级运行。
- `retry`：重试当前节点，最多 `max_retries` 次。
- `fallback_node_type`：如果重试全部失败，尝试用另一个 node_type 替代执行（例如 `enhance.realesrgan` 失败后尝试 `enhance.waifu2x`）。

`fallback_node_type` 必须通过 NodeRegistry 兼容性验证：

- fallback 节点的 required input ports 必须能由原节点的输入满足。
- fallback 节点的 output ports 必须覆盖原节点下游依赖的 artifact 类型。
- fallback 节点需要声明参数映射；不能隐式复用不兼容的 `param_values`。
- fallback 节点的 runtime requirements 和 resource hint 必须重新参与 ExecutionPlanner 与 Scheduler 检查。

## 10. WorkflowGraph Schema

```python
class WorkflowGraph(BaseModel):
    graph_id:    str                  # ULID
    name:        str
    description: str = ""
    nodes:       list[WorkflowNode]
    edges:       list[WorkflowEdge]
    created_at:  str                  # ISO 8601 UTC
    updated_at:  str                  # ISO 8601 UTC
```

### DAG 约束

WorkflowGraph 必须是有向无环图 (DAG)。任何使图产生环的连线操作应被 GUI 阻止，或在验证阶段标记为错误。

## 11. 验证规则

WorkflowGraph 在提交给 ExecutionPlanner 前必须通过以下验证：

| 编号 | 规则 | 错误类型 |
|---|---|---|
| V-01 | 图无环 | `CycleDetected` |
| V-02 | 所有 edge 引用的 node_id / port_id 真实存在 | `DanglingReference` |
| V-03 | edge 的 source port 为 output，target port 为 input | `PortDirectionMismatch` |
| V-04 | edge 两端的 data_type 兼容 | `DataTypeMismatch` |
| V-05 | 所有 `required == True` 的 input port 至少有一条入边 | `RequiredPortUnconnected` |
| V-06 | `multi == False` 的 input port 最多一条入边 | `MultiConnectionViolation` |
| V-07 | 不存在自连边 | `SelfLoop` |
| V-08 | 所有 param_values 中的值满足对应 NodeParam 的 constraints | `ParamConstraintViolation` |
| V-09 | 图至少有一个 input 类节点和一个 output 类节点 | `MissingInputOrOutput` |
| V-10 | 不存在孤立节点（无任何连线的非 input/output 节点） | `IsolatedNode`（warning） |

验证函数返回 `list[ValidationError]`，每条包含 `code`, `severity` (`error` | `warning`), `node_id`, `port_id`, `message`。

## 12. Runtime Requirement Schema

节点不直接假设系统已经安装 FFmpeg、CUDA、llama.cpp、whisper.cpp、ncnn-vulkan、模型文件或 Python 包。节点只声明运行需求，由 RuntimeManager 解析成可执行环境。

```python
class RuntimeRequirement(BaseModel):
    component:    str                    # "ffmpeg", "faster-whisper", "llama.cpp", "realesrgan-ncnn-vulkan"
    version:      str | None = None      # 精确版本或版本范围
    capabilities: list[str] = []         # "cuda", "vulkan", "cpu", "avx2" 等
    model_ids:    list[str] = []         # 需要的模型资产 ID，来自 Atelier model store
    optional:     bool = False
```

规则：

- GUI 只展示 runtime 状态和修复入口，不直接拼装安装命令。
- ExecutionPlanner 将 `runtime_requirements` 复制到 ExecutionTask 的 runtime request。
- Scheduler 启动 Worker 前必须确认 RuntimeManager 已解析出可用 runtime binding。
- `MODEL_ID` 参数必须引用 Atelier 管理的 model store，不应直接指向任意本地模型路径，除非该路径先被导入并登记。

## 13. 节点注册协议 (NodeRegistry)

```python
class NodeRegistryEntry(BaseModel):
    node_type:    str                   # 唯一注册名
    category:     NodeCategory
    display_name: str
    version:      str                   # semver
    description:  str
    inputs:       list[PortDefinition]
    outputs:      list[PortDefinition]
    params:       list[NodeParam]
    resource_hint: ResourceHint | None = None
    runtime_requirements: list[RuntimeRequirement] = []
    failure_policy: FailurePolicy       # 默认失败策略
    cacheable:    bool = True
    cache_key_fields: list[str] = []
    icon:         str = ""              # GUI 图标标识
    tags:         list[str] = []        # 分类标签
```

### 注册规则

- 所有 node_type 通过 NodeRegistry 注册，GUI 和 ExecutionPlanner 从 registry 读取可用节点列表。
- node_type 格式：`{domain}.{name}`，domain 建议与 NodeCategory 或功能域对齐。
- 同一 node_type 可注册多个版本。ExecutionPlanner 默认使用最新版本，除非用户在节点参数中指定版本。
- GUI 不硬编码任何节点的参数面板；Inspector 根据 `params` 定义动态生成参数表单。
- 新增 adapter 时同步注册 NodeRegistryEntry，否则该节点不可用。
- 新增需要外部工具、模型、CUDA/Vulkan/CPU backend 的节点时，必须同步声明 `runtime_requirements`。

## 14. 序列化格式

WorkflowGraph 使用 JSON 序列化。以下是一个最小示例（ASR + 翻译 + 字幕封装）：

```json
{
  "graph_id": "01JWF9XYZ0000000000000001",
  "name": "字幕翻译流程",
  "description": "提取字幕 → 翻译 → 封装",
  "nodes": [
    {
      "node_id": "01JWF9XYZ0000000000000010",
      "node_type": "input.video",
      "category": "input",
      "display_name": "视频输入",
      "version": "1.0.0",
      "inputs": [],
      "outputs": [
        {"port_id": "video_out", "direction": "output", "data_type": "video", "required": false, "multi": false, "label": "视频"},
        {"port_id": "audio_out", "direction": "output", "data_type": "audio", "required": false, "multi": false, "label": "音频"}
      ],
      "params": [
        {"name": "file_path", "display_name": "文件路径", "type": "path", "default": null, "constraints": {"file_ext": [".mp4", ".mkv", ".avi", ".mov"]}, "tier": "basic", "dangerous": false, "description": ""}
      ],
      "param_values": {"file_path": "D:/videos/source.mp4"},
      "resource_hint": null,
      "failure_policy": {"on_failure": "stop", "max_retries": 0, "fallback_node_type": null},
      "cacheable": false,
      "cache_key_fields": [],
      "position": [100, 200]
    },
    {
      "node_id": "01JWF9XYZ0000000000000020",
      "node_type": "asr.whisper",
      "category": "process",
      "display_name": "Whisper ASR",
      "version": "1.0.0",
      "inputs": [
        {"port_id": "audio_in", "direction": "input", "data_type": "audio", "required": true, "multi": false, "label": "音频"}
      ],
      "outputs": [
        {"port_id": "subtitle_out", "direction": "output", "data_type": "subtitle", "required": false, "multi": false, "label": "字幕"}
      ],
      "params": [
        {"name": "model_size", "display_name": "模型大小", "type": "enum", "default": "medium", "constraints": {"choices": ["tiny", "base", "small", "medium", "large", "large-v3"]}, "tier": "basic", "dangerous": false, "description": ""},
        {"name": "language", "display_name": "语言", "type": "string", "default": "auto", "constraints": null, "tier": "basic", "dangerous": false, "description": ""},
        {"name": "beam_size", "display_name": "Beam Size", "type": "int", "default": 5, "constraints": {"min": 1, "max": 20}, "tier": "advanced", "dangerous": false, "description": ""}
      ],
      "param_values": {"model_size": "large-v3", "language": "ja"},
      "resource_hint": {"device_type": "gpu", "vram_mb": 4096, "exclusive_gpu": true, "estimated_duration_sec": 120},
      "failure_policy": {"on_failure": "retry", "max_retries": 2, "fallback_node_type": null},
      "cacheable": true,
      "cache_key_fields": ["model_size", "language", "beam_size"],
      "position": [350, 200]
    },
    {
      "node_id": "01JWF9XYZ0000000000000030",
      "node_type": "translate.llm",
      "category": "process",
      "display_name": "LLM 翻译",
      "version": "1.0.0",
      "inputs": [
        {"port_id": "subtitle_in", "direction": "input", "data_type": "subtitle", "required": true, "multi": false, "label": "原始字幕"}
      ],
      "outputs": [
        {"port_id": "subtitle_out", "direction": "output", "data_type": "subtitle", "required": false, "multi": false, "label": "翻译字幕"}
      ],
      "params": [
        {"name": "target_lang", "display_name": "目标语言", "type": "string", "default": "zh-CN", "constraints": null, "tier": "basic", "dangerous": false, "description": ""},
        {"name": "model_id", "display_name": "模型", "type": "model_id", "default": "gpt-4o", "constraints": null, "tier": "basic", "dangerous": false, "description": ""},
        {"name": "glossary_path", "display_name": "术语表路径", "type": "path", "default": null, "constraints": {"file_ext": [".json", ".csv"]}, "tier": "advanced", "dangerous": false, "description": ""}
      ],
      "param_values": {"target_lang": "zh-CN", "model_id": "gpt-4o"},
      "resource_hint": {"device_type": "cpu", "vram_mb": null, "exclusive_gpu": false, "estimated_duration_sec": 60},
      "failure_policy": {"on_failure": "retry", "max_retries": 3, "fallback_node_type": null},
      "cacheable": true,
      "cache_key_fields": ["target_lang", "model_id", "glossary_path"],
      "position": [600, 200]
    },
    {
      "node_id": "01JWF9XYZ0000000000000040",
      "node_type": "compose.mux_subtitle",
      "category": "compose",
      "display_name": "字幕封装",
      "version": "1.0.0",
      "inputs": [
        {"port_id": "video_in", "direction": "input", "data_type": "video", "required": true, "multi": false, "label": "视频"},
        {"port_id": "subtitle_in", "direction": "input", "data_type": "subtitle", "required": true, "multi": true, "label": "字幕"}
      ],
      "outputs": [
        {"port_id": "video_out", "direction": "output", "data_type": "video", "required": false, "multi": false, "label": "输出视频"}
      ],
      "params": [
        {"name": "subtitle_codec", "display_name": "字幕编码", "type": "enum", "default": "srt", "constraints": {"choices": ["srt", "ass", "mov_text"]}, "tier": "basic", "dangerous": false, "description": ""},
        {"name": "default_track", "display_name": "设为默认轨道", "type": "bool", "default": true, "constraints": null, "tier": "basic", "dangerous": false, "description": ""}
      ],
      "param_values": {},
      "resource_hint": {"device_type": "cpu", "vram_mb": null, "exclusive_gpu": false, "estimated_duration_sec": 10},
      "failure_policy": {"on_failure": "stop", "max_retries": 0, "fallback_node_type": null},
      "cacheable": false,
      "cache_key_fields": [],
      "position": [850, 200]
    },
    {
      "node_id": "01JWF9XYZ0000000000000050",
      "node_type": "output.export",
      "category": "output",
      "display_name": "导出",
      "version": "1.0.0",
      "inputs": [
        {"port_id": "video_in", "direction": "input", "data_type": "video", "required": true, "multi": false, "label": "视频"}
      ],
      "outputs": [],
      "params": [
        {"name": "output_dir", "display_name": "输出目录", "type": "path", "default": null, "constraints": null, "tier": "basic", "dangerous": false, "description": ""},
        {"name": "filename_template", "display_name": "文件名模板", "type": "string", "default": "{input_name}_output.{ext}", "constraints": null, "tier": "advanced", "dangerous": false, "description": ""}
      ],
      "param_values": {"output_dir": "D:/videos/output"},
      "resource_hint": null,
      "failure_policy": {"on_failure": "stop", "max_retries": 0, "fallback_node_type": null},
      "cacheable": false,
      "cache_key_fields": [],
      "position": [1100, 200]
    }
  ],
  "edges": [
    {"edge_id": "01JWF9XYZ0000000000000101", "source_node_id": "01JWF9XYZ0000000000000010", "source_port_id": "audio_out", "target_node_id": "01JWF9XYZ0000000000000020", "target_port_id": "audio_in"},
    {"edge_id": "01JWF9XYZ0000000000000102", "source_node_id": "01JWF9XYZ0000000000000020", "source_port_id": "subtitle_out", "target_node_id": "01JWF9XYZ0000000000000030", "target_port_id": "subtitle_in"},
    {"edge_id": "01JWF9XYZ0000000000000103", "source_node_id": "01JWF9XYZ0000000000000010", "source_port_id": "video_out", "target_node_id": "01JWF9XYZ0000000000000040", "target_port_id": "video_in"},
    {"edge_id": "01JWF9XYZ0000000000000104", "source_node_id": "01JWF9XYZ0000000000000030", "source_port_id": "subtitle_out", "target_node_id": "01JWF9XYZ0000000000000040", "target_port_id": "subtitle_in"},
    {"edge_id": "01JWF9XYZ0000000000000105", "source_node_id": "01JWF9XYZ0000000000000040", "source_port_id": "video_out", "target_node_id": "01JWF9XYZ0000000000000050", "target_port_id": "video_in"}
  ],
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T10:30:00Z"
}
```

## 15. 与其他文档的关系

```text
WORKFLOW_NODE_SPEC (本文档)
  → EXECUTION_PLAN_SPEC：WorkflowGraph 是 ExecutionPlanner 的输入。
                         每个 WorkflowNode 在 plan 中产生一个或多个 ExecutionTask。
  → WORKER_PROTOCOL：   node_type 决定 Worker 使用哪个 adapter。
                         NodeParam / param_values 传递给 Worker 作为执行参数。
  → DATABASE_SCHEMA：   WorkflowGraph 整体序列化存入 workflow_graphs 表。
                         Preset 复用 graph_json 格式。
```
