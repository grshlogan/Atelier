# Runtime Management Foundation 计划

> 执行顺序：第 7 个后续计划。建议在 `plan_scheduler_lifecycle_dispatch_integration.md` 完成后执行。目标是在测试最简真实工作流前，先让 Atelier 具备可登记、可校验、可解析、可展示的 managed runtime 基础。

## Objective（目标）

建立首版 Runtime 管理骨架，让真实 adapter 和模型/工具执行前拥有可信的运行环境来源。

目标链路：

```text
AtelierData runtime layout
  -> RuntimeStore manifests
  -> local tool / worker env / model asset registration
  -> RuntimeHealthChecker validation
  -> RuntimeManager.resolve(RuntimeRequest)
  -> RuntimeBinding for Worker
  -> GUI-readable RuntimeSetupSnapshot
```

这一步不追求下载器、安装器或真实模型执行，先把“Atelier 知道自己能用什么 runtime，为什么能用，哪里坏了”立稳。

## Scope（范围）

- 扩展 runtime manifest / model asset manifest 的字段表达，让它能覆盖本地工具、Worker Python env、模型目录和 backend capability。
- 支持登记本地 tool runtime profile，例如 `ffmpeg`、`ffprobe`、`python.worker-dev`，并写入 `RuntimeStore`。
- 支持登记本地 model asset profile，至少覆盖模型 id、路径、backend、capabilities、hash 或 size metadata。
- 扩展 `RuntimeHealthChecker`，能检查 runtime path、model path、checksum，并为 Worker Python env / executable runtime 提供最小 dry-run health。
- 扩展 `RuntimeManager.resolve()`，输出 Worker 可用的 `RuntimeBinding`，包含 component paths、model paths、scoped env 和 binding reason。
- 提供 GUI 可读的 runtime setup snapshot / service，但不在本计划做完整 UI 交互。
- 更新 `RUNTIME_ENVIRONMENT_SPEC.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划。

暂不实现：

- 在线下载 runtime、模型或插件。
- 解压安装 runtime pack。
- package signature 验证、rollback、update channel。
- CUDA / Vulkan / driver 深度兼容性探测。
- 真实 FFmpeg / ASR / OCR / LLM / video enhance adapter。
- 插件 backend 执行。
- GUI 中运行重型任务。
- 让用户输入任意 shell command。

## Current Facts（当前事实）

- `atelier/runtime/store.py` 已有 `RuntimeStore`，会创建 `AtelierData/runtimes/components`、`python-envs`、`manifests`、`models/manifests`、`plugins`、`staging` 和 `cache`。
- `atelier/runtime/manifest.py` 已有 `RuntimeManifest`、`ModelAssetManifest` 和 `RuntimeStatus`。
- `atelier/runtime/manager.py` 已有 `RuntimeManager.resolve(RuntimeRequest)`，可从 managed manifests 解析 `RuntimeBinding`，但错误仍是普通 `RuntimeError`，字段也偏最小。
- `atelier/runtime/health.py` 已有 `RuntimeHealthChecker`，可检查 runtime component paths、model paths 和 SHA-256。
- `atelier/app/services.py` 已能基于 `AppPaths` 创建 `RuntimeStore`。
- 当前 `.venv/` 是开发环境，不是产品 runtime；开发期可以把当前 Python executable 登记为 `python.worker-dev`，但必须在 manifest 中标记为 dev/local profile，不把它写成发布 runtime。
- `docs/RUNTIME_ENVIRONMENT_SPEC.md`、`docs/EXTERNAL_TOOL_INTEGRATION_SPEC.md` 和 `docs/SECURITY_PRIVACY_SPEC.md` 已明确 RuntimeManager 不运行重任务、不分配硬件、不绕过 Scheduler、不接管系统 GPU driver。

## Constraints（约束）

- RuntimeManager 是 runtime/tool/model path 解析的唯一入口。
- GUI 不直接执行 FFmpeg、模型或外部工具；GUI 只能触发轻量 manifest registration / health check service。
- Worker 不从全局 `PATH` 自行寻找工具。
- Runtime profile 不得保存 secrets；远程 provider credential 只保存 `credential_ref`。
- 本计划不引入 conda、Celery、Redis、Electron、Tauri 或系统级安装器。
- 本计划不提交实际 runtime binaries、模型文件或用户本地路径。
- 开发期测试可以用临时 fake executable / stub Python script 验证路径和 dry-run，不依赖真实 FFmpeg。

## Execution Plan（执行计划）

### Phase A：manifest 与 store 字段加固

目标：

- 让 `RuntimeManifest` 表达 runtime kind、platform、display name、executable paths、library dirs、env、capabilities、backend tags、integrity metadata 和 local/dev profile 标记。
- 让 `ModelAssetManifest` 表达 model family、task types、backend compatibility、size/hash、metadata 和 status。
- 保持现有 tests 兼容或提供迁移兼容读取。

完成信号：

- 旧的最小 manifest 仍可读取。
- 新字段能覆盖 `ffmpeg` / `ffprobe` / `python.worker-dev` / demo model asset。
- `RuntimeStore` 仍原子写入 manifests。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_runtime_store tests.test_runtime_manager
```

状态：

- 已完成。

### Phase B：本地 runtime / model profile registration

目标：

- 新增受控的 registration service，用于登记用户选择或开发期提供的本地 runtime executable 和 model path。
- registration service 只写 managed manifest，不复制大文件，不修改系统环境。

完成信号：

- 可以登记 `ffprobe` / `ffmpeg` fake executable。
- 可以登记 `python.worker-dev` executable。
- 可以登记 demo model directory。
- path traversal、空路径、缺失路径和重复 id 有明确错误。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_runtime_registration
```

状态：

- 已完成。

### Phase C：health check 与 repair hint

目标：

- 扩展 RuntimeHealthChecker，生成 GUI 可读的健康状态和修复提示。
- 对 executable runtime 支持最小 dry-run，例如 `--version` 或 caller-provided safe probe args。

完成信号：

- missing / broken / disabled / incompatible / ready 状态可区分。
- hash mismatch、路径缺失、dry-run 失败有具体 issue。
- health report 不泄露 secrets，不记录任意命令。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_runtime_health
```

状态：

- 已完成。

### Phase D：RuntimeManager resolution 强化

目标：

- 让 `RuntimeManager.resolve()` 使用健康状态和 manifest capability，生成可交给 Worker 的 `RuntimeBinding`。
- 将缺失 runtime / model 的错误从普通 `RuntimeError` 收束为可诊断的 runtime resolution error。

完成信号：

- `RuntimeRequest(components=["ffprobe"], capabilities=["metadata"])` 能解析到 component path。
- 请求 model id 时能解析 `model_paths`。
- status 非 ready、capability 不匹配、backend 不匹配时给出明确错误。
- `RuntimeBinding.env` 只包含 scoped Worker env，不污染全局 PATH。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_runtime_manager
```

状态：

- 已完成。

### Phase E：RuntimeSetupSnapshot / service

目标：

- 为初始可操作 GUI 准备只读 runtime setup snapshot。
- 让 GUI 能展示 runtime components、models、health state、issues 和 repair hints。

完成信号：

- `RuntimeSetupSnapshot` 可由 `AppPaths` / `RuntimeStore` / `RuntimeHealthChecker` 构造。
- snapshot 不启动 Worker，不运行重任务。
- 后续 GUI plan 可直接使用该 service。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_runtime_setup_snapshot
```

状态：

- 已完成。

### Phase F：文档状态对齐

目标：

- 更新 runtime 文档和接手文档，明确首版 Runtime 管理已能做什么、仍不能做什么。

完成信号：

- `RUNTIME_ENVIRONMENT_SPEC.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划更新。
- 不把下载器、真实模型执行、插件 backend 或 GUI 重任务写成已完成。

验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

状态：

- 已完成。

## Child Plans（子计划）

- [plan_initial_actionable_gui_runtime_setup.md](./plan_initial_actionable_gui_runtime_setup.md)：在 Runtime 管理骨架完成后，让 GUI 具备最小 runtime setup 操作面。
- [plan_minimal_adapter_probe_workflow.md](./plan_minimal_adapter_probe_workflow.md)：在 Runtime 管理骨架完成后，实现最简 adapter / ffprobe metadata workflow。

## Verification（验证）

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_runtime_store tests.test_runtime_manager tests.test_runtime_health
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

当前验证结果：

- `.venv/Scripts/python -m unittest tests.test_runtime_store tests.test_runtime_manager`：5 tests passed。
- `.venv/Scripts/python -m unittest tests.test_runtime_setup_snapshot tests.test_runtime_manager tests.test_runtime_health tests.test_runtime_registration tests.test_runtime_store`：17 tests passed。
- `.venv/Scripts/python -m unittest discover -s tests`：80 tests passed。
- `.venv/Scripts/python -m compileall -q atelier tests`：passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

## Progress / Decisions（进展 / 决策）

- 2026-05-05：创建本计划。决策：在最简真实 workflow 前，先补 Runtime 管理骨架；本计划只做 manifest / registration / health / resolution / GUI snapshot，不下载 runtime、不执行真实模型、不接真实 adapter。
- 2026-05-05：开始执行 Phase A。决策：第一版 runtime 管理源码位于 `atelier/runtime/`；第一版 runtime 数据根目录由 `AppPaths.data_root` 决定，开发期为 `.atelier/AtelierData/runtimes/`，发布期为用户数据目录下的 `AtelierData/runtimes/`。Phase A 只扩展 manifest 字段并保持旧 manifest 兼容，不实现 registration service 或真实 adapter。
- 2026-05-05：完成 Phase A。`RuntimeManifest` 新增 runtime kind、display name、platform、executable paths、library dirs、scoped env、backend tags、integrity metadata 和 profile kind；`ModelAssetManifest` 新增 display name、model family、task types、compatible backends、size bytes、metadata 和 profile kind。旧的最小 manifest 仍兼容读取。
- 2026-05-05：完成 Phase B。新增 `RuntimeRegistrationService`，可登记本地 `ffprobe` / `ffmpeg` executable profile、`python.worker-dev` development Worker Python profile 和 demo model directory profile；空路径、缺失路径、相对 traversal、重复 runtime id 和重复 model id 会被拒绝。registration 只写 manifest，不复制、不下载、不执行工具。
- 2026-05-05：Phase B 验证通过：runtime registration/store/manager/health 相关测试 12 tests passed，完整 `unittest discover` 75 tests passed，`compileall` passed，文档尾随空格扫描无匹配，`git diff --check` 仅有 Windows CRLF conversion warnings。
- 2026-05-05：完成 Phase C。`RuntimeHealthReport` 新增 `repair_hints`；`RuntimeHealthChecker.check_runtime()` 支持 caller-provided safe dry-run probe args，使用 list-based subprocess 调用且不使用 shell。missing / checksum mismatch / dry-run failure 均有 GUI 可读修复提示。
- 2026-05-05：Phase C 验证通过：runtime health/registration/store/manager 相关测试 13 tests passed，完整 `unittest discover` 76 tests passed，`compileall` passed，文档尾随空格扫描无匹配，`git diff --check` 仅有 Windows CRLF conversion warnings。
- 2026-05-05：完成 Phase D。`RuntimeManager.resolve()` 会合并 manifest scoped env 到 `RuntimeBinding.env`，并用 `RuntimeResolutionError(subject_id, reason)` 表达 missing component、disabled runtime、capability mismatch 和 missing model asset 等诊断事实。
- 2026-05-05：Phase D 验证通过：runtime manager/health/registration/store 相关测试 16 tests passed，完整 `unittest discover` 79 tests passed，`compileall` passed，文档尾随空格扫描无匹配，`git diff --check` 仅有 Windows CRLF conversion warnings。
- 2026-05-05：完成 Phase E。新增 `RuntimeSetupSnapshot`、`RuntimeComponentSnapshot`、`ModelAssetSnapshot` 和 `build_runtime_setup_snapshot()`，可为后续 GUI Runtime Setup surface 提供只读 components/models/status/issues/repair hints。
- 2026-05-05：完成 Phase F。`RUNTIME_ENVIRONMENT_SPEC.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划已对齐当前 Runtime 管理骨架；仍明确未实现 runtime download/install、GUI runtime setup actions、AdapterRegistry 和真实 adapter execution。
- 2026-05-05：Phase E/F 完整验证通过：runtime setup/manager/health/registration/store 相关测试 17 tests passed，完整 `unittest discover` 80 tests passed，`compileall` passed，文档尾随空格扫描无匹配，`git diff --check` 仅有 Windows CRLF conversion warnings。

## Blockers（阻塞）

- 暂无。
