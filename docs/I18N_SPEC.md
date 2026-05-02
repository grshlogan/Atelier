# Atelier I18N Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的多语言、热切换、文案 key、格式化和插件翻译策略。

## 1. 目标

Atelier 必须天生支持语言热切换。UI 文案不应散落在代码字符串里。

目标：

```text
UI 文案可翻译
语言可运行时切换
日志和技术符号保留原文
插件可提供自己的翻译包
布局切换不破坏翻译
```

## 2. 参考软件与取舍

### Qt Internationalization

可借鉴：

- `QTranslator` 安装翻译包。
- `QEvent::LanguageChange` 通知 widget 刷新文案。
- `.ts` / `.qm` 是成熟 Qt 翻译链。

Atelier 的取舍：

- 首版使用 Qt 翻译机制或兼容层。
- 所有 widget 必须实现 `retranslateUi()` 或等价刷新方法。

### VS Code Language Packs

可借鉴：

- UI 语言与扩展语言包可以分离。
- 语言配置属于用户设置。

Atelier 的取舍：

- 核心应用语言包与插件语言包分离。
- 插件 manifest 声明可用 locales。

### Professional Creator Tools

可借鉴：

- 文件路径、codec、model name、plugin id、日志和命令输出通常保留原始语言。

Atelier 的取舍：

- 人类可读 UI 用当前 locale。
- 技术符号、路径、模型名、node_type、error_code 保留原文。

## 3. Locale Model

```text
system  -> 跟随系统
zh-CN   -> 简体中文
en-US   -> English
ja-JP   -> Japanese
ko-KR   -> Korean
```

首版目标：

- `zh-CN`
- `en-US`

规则：

- 默认 `system`。
- 用户可以在 Settings 中切换。
- 切换立即生效，不要求重启。
- 无翻译时回退到 `en-US` 或 key fallback。

## 4. Text Key 规则

key 命名：

```text
app.menu.file
app.action.save
panel.queue.title
panel.runtime.title
workflow.node.asr.whisper.name
workflow.node.asr.whisper.param.model_size
error.runtime.missing.title
error.runtime.missing.body
```

规则：

- UI 代码不得直接写面向用户的长文案。
- `node_type`、`plugin_id`、`model_id` 不是翻译 key。
- NodeRegistryEntry 应为 display fields 提供 key。
- 错误解释使用 key + structured payload。

## 5. Runtime Hot Switch

语言切换流程：

```text
User selects locale
  -> Settings writes locale
  -> I18nManager loads translator
  -> QApplication installs translator
  -> broadcast localeChanged
  -> widgets receive LanguageChange
  -> retranslateUi()
  -> save current locale
```

要求：

- 切换语言不重建 Job、Scheduler、Worker。
- 切换语言不影响 WorkflowGraph、ExecutionPlan、Task 状态。
- 正在运行的 Worker 日志不重新翻译历史内容。
- 新 UI 消息使用新 locale。

## 6. Formatting

需要本地化：

- 日期时间显示。
- 数字分隔符。
- 文件大小。
- 时长。
- 百分比。

不本地化：

- 文件路径。
- 命令。
- `node_type`
- `task_id`
- `artifact_id`
- `error_code`
- model name。

## 7. Plugin Locales

插件可提供：

```text
locales/
  en-US.json
  zh-CN.json
```

或 Qt `.qm` 文件。

插件 manifest：

```toml
[locales]
default = "en-US"
available = ["en-US", "zh-CN"]
path = "locales"
```

规则：

- 插件 key 必须带 plugin namespace。
- 插件卸载后，历史 Job 仍显示可读 fallback。
- 插件翻译不能覆盖核心应用 key。

## 8. Error Message Contract

错误对象：

```python
class UserFacingError(BaseModel):
    code: str
    title_key: str
    body_key: str
    details: dict[str, str] = {}
    technical_reason: str = ""
```

展示：

```text
title = i18n(title_key, details)
body = i18n(body_key, details)
technical_reason = original text
```

规则：

- 技术原因保留原文。
- 用户解释使用当前语言。
- 日志不因语言切换被改写。

## 9. 首版实现建议

第一阶段：

- `I18nManager`
- `tr(key, **kwargs)`
- `localeChanged` signal
- `retranslateUi()` pattern
- `locales/en-US.json`
- `locales/zh-CN.json`

暂不实现：

- 在线语言包下载。
- 社区翻译平台集成。
- 复杂复数规则。

## 10. 参考资料

- Qt Internationalization: https://doc.qt.io/qt-6/internationalization.html
- Qt QTranslator: https://doc.qt.io/qt-6/qtranslator.html
- Qt LanguageChange event: https://doc.qt.io/qt-6/qevent.html
- VS Code Display Language: https://code.visualstudio.com/docs/configure/locales
