# Atelier Runtime Environment Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的 runtime ownership、runtime pack、model store、backend 选择和健康检查策略。

## 1. 目标

Atelier 不应把环境配置责任推给用户。软件应管理自己能管理的 runtime，并清楚报告不能代管的系统依赖。

```text
App Runtime       -> Python / PySide6 / Qt plugins / app dependencies
Tool Runtime      -> FFmpeg / ffprobe / llama.cpp / whisper.cpp / ncnn-vulkan
Backend Runtime   -> CUDA / Vulkan / CPU / MLX / ROCm 等 backend 变体
Model Store       -> ASR / LLM / enhance / interpolation model assets
Runtime Manifest  -> 版本、路径、hash、capabilities、状态
```

## 1.1 三层环境模型

Atelier 的环境不要混成一个目录。默认按三层理解和实现：

```text
App Install Dir
  -> 软件本体，只读为主
  -> Atelier.exe、应用代码、GUI 自身 Python runtime、PySide6、Qt plugins、必要 DLL

AtelierData Dir
  -> 用户可写 runtime / data
  -> FFmpeg、ffprobe、whisper.cpp、llama.cpp、worker env、模型、插件、cache、staging、日志、数据库

Dev Workspace
  -> 仅开发期存在
  -> 源码、.venv、测试缓存、本地 .atelier/AtelierData
```

规则：

- `atelier/runtime/` 是 RuntimeManager 的源码目录，只放管理 runtime 的 Python 代码，不放 runtime 本体。
- GUI 自身环境属于 App Runtime，随应用安装包分发，发布后位于 App Install Dir 内。
- Tool Runtime、Backend Runtime、Worker Python env 和模型资产属于 AtelierData，由 RuntimeManager / RuntimeStore 管理。
- 开发期 `.venv/` 只用于本仓库开发和测试，不是产品 runtime，不提交，不作为 RuntimeManager 的事实源。
- 开发期可用 `.atelier/AtelierData/` 模拟用户数据目录；该目录同样不提交。

开发期建议布局：

```text
E:/AI/Atelier/
  .venv/                    # 开发 Python env，gitignore
  .atelier/
    AtelierData/             # 开发期本地 runtime/data，gitignore
      runtimes/
      models/
      plugins/
      cache/
      staging/
  atelier/
    runtime/                 # runtime 管理源码，不放 runtime 本体
```

发布期建议布局：

```text
C:/Program Files/Atelier/
  Atelier.exe
  app-runtime/
    python/
    site-packages/
    qt-plugins/
    dlls/
  app/

%LOCALAPPDATA%/Atelier/AtelierData/
  runtimes/
  models/
  plugins/
  cache/
  staging/
```

## 2. 参考软件与取舍

### LM Studio

可借鉴：

- App 和 LLM runtime 分离。
- Runtime 可以独立下载、更新和切换。
- 不同 backend 变体可以并存。
- 模型资产有独立目录和抽象配置。

Atelier 的取舍：

- 采用 runtime pack 和 model store 思路。
- 不采用单一全局 active runtime。
- 每个 Task 由 Scheduler + RuntimeManager 生成自己的 `RuntimeBinding`。

### Blender Extensions

可借鉴：

- 扩展必须带 manifest。
- 扩展可离线安装，也可从 repository 安装。
- 扩展声明类型、版本和权限。

Atelier 的取舍：

- Runtime pack 与 plugin pack 都使用 manifest。
- Runtime pack 不允许隐式修改系统环境。

### Python Desktop Packaging

可借鉴：

- 应用本体应包含 Python、Qt runtime 和所需 Python 依赖。
- 用户不应先安装 Python 才能运行 Atelier。

Atelier 的取舍：

- Windows 首版优先 self-contained app runtime。
- 外部重型工具和模型不强行塞进 App Package，交给 RuntimeManager。

## 3. RuntimeManager 职责

RuntimeManager 负责：

- 读取 RuntimeManifest。
- 管理 runtime component 的安装状态。
- 管理 model asset 的导入、校验、删除和状态。
- 根据 Task 的 RuntimeRequest 解析 RuntimeBinding。
- 检查 hardware/backend 兼容性。
- 为 Worker 提供工具路径、模型路径和环境变量。
- 报告 runtime health。

RuntimeManager 不负责：

- 运行重型任务。
- 分配 GPU / CPU 资源。
- 绕过 Scheduler 启动 Worker。
- 在用户不知情时替换系统 GPU driver。

## 4. Runtime 目录布局

建议默认：

```text
AtelierData/
  runtimes/
    components/
      ffmpeg/7.1.0/
      llama.cpp/b4600-cuda/
      whisper.cpp/v1.7.0-cpu/
      realesrgan-ncnn-vulkan/20220424/
    python-envs/
      worker-default/
    manifests/
      installed.json
      available-cache.json

  models/
    asr/
    llm/
    enhance/
    interpolate/

  plugins/
    installed/
    disabled/

  staging/
  cache/
```

用户可在 Settings 中移动 `AtelierData`，但移动必须通过软件执行，不能要求用户手工改路径。

## 5. Runtime Manifest

```toml
schema_version = "1"
runtime_id = "whisper.cpp-cuda-v1.7.0"
name = "whisper.cpp CUDA"
component = "whisper.cpp"
version = "1.7.0"
platform = "windows-x86_64"
kind = "backend"
status = "ready"

[paths]
root = "runtimes/components/whisper.cpp/v1.7.0-cuda"
executable = "bin/whisper-cli.exe"
library_dir = "bin"

[capabilities]
tasks = ["asr"]
hardware = ["gpu"]
backends = ["cuda"]
formats = ["ggml", "gguf"]

[requirements]
min_driver = ""
requires_gpu = true
min_vram_mb = 2048

[integrity]
sha256 = "<sha256>"
signature = "<signature>"
```

## 6. Model Asset Manifest

```yaml
schema_version: "1"
model_id: "whisper-large-v3"
display_name: "Whisper Large V3"
task_types:
  - asr
backends:
  - faster-whisper
  - whisper.cpp
formats:
  - safetensors
  - gguf
version: "large-v3"
local_path: "models/asr/whisper-large-v3"
hash: "<sha256>"
size_bytes: 0
recommended_vram_mb: 8192
default_params:
  language: auto
  beam_size: 5
compatible_runtimes:
  - "faster-whisper-cuda"
  - "whisper.cpp-cuda"
  - "whisper.cpp-cpu"
```

规则：

- `MODEL_ID` 参数必须引用 model store 中的 `model_id`。
- 用户导入本地模型时，Atelier 生成或补全 manifest。
- 模型路径不直接暴露给 WorkflowNode，Worker 通过 `RuntimeBinding.model_paths` 使用。

## 7. RuntimeRequest / RuntimeBinding

Task 声明需求：

```python
RuntimeRequest(
    components=["ffmpeg", "whisper.cpp"],
    capabilities=["asr", "cuda"],
    model_ids=["whisper-large-v3"],
)
```

RuntimeManager 解析结果：

```python
RuntimeBinding(
    runtime_id="asr-whisper-cuda-binding",
    component_paths={
        "whisper.cpp": "AtelierData/runtimes/components/whisper.cpp/v1.7.0-cuda/bin/whisper-cli.exe"
    },
    model_paths={
        "whisper-large-v3": "AtelierData/models/asr/whisper-large-v3/model.gguf"
    },
    env={
        "PATH": "<scoped worker path only>"
    },
)
```

规则：

- Worker 不读全局 `PATH`。
- Worker 不自行安装 runtime。
- RuntimeBinding 是只读输入。
- Scheduler 启动 Worker 前必须持有 `ResourceBinding` 和 `RuntimeBinding`。

## 8. Health Check

Runtime health 状态：

```text
missing
installing
ready
broken
disabled
incompatible
update_available
```

健康检查内容：

- 文件是否存在。
- hash/signature 是否匹配。
- 可执行文件是否能启动。
- backend 是否与硬件兼容。
- model asset 是否完整。
- worker dry-run 是否通过。

## 9. Cache Fingerprint

Cache key 必须纳入：

```text
node_type
node_version
params_hash
input_artifact_hashes
runtime_id
runtime_version
backend
worker_version
model_id
model_hash/version
hardware-sensitive settings
```

目的：

- 防止不同 backend 误用旧产物。
- 防止模型版本变化后命中旧缓存。
- 保留可解释的缓存来源。

## 10. 首版实现建议

第一阶段只实现：

- 读取本地 runtime manifest。
- 读取本地 model manifest。
- 输出 `RuntimeBinding`。
- 对 simulated Worker 做 health check。
- GUI 显示 runtime 状态。

暂不实现：

- 在线下载。
- 自动更新。
- 第三方 runtime repository。
- 完整模型市场。

## 11. 参考资料

- LM Studio runtimes: https://lmstudio.ai/docs/cli/runtime/runtime
- LM Studio model.yaml: https://lmstudio.ai/docs/app/modelyaml
- LM Studio offline operation: https://lmstudio.ai/docs/app/offline
- Blender Extensions: https://docs.blender.org/manual/en/latest/advanced/extensions/
- PySide6 deployment: https://doc.qt.io/qtforpython-6/deployment/index.html
- PyInstaller: https://pyinstaller.org/en/stable/
