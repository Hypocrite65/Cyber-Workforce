# AI Agent 能力参考手册

本文件描述了 current AI 系统的核心能力，作为设计新 Agent 角色时的参考。

## 1. 可用工具 (Tools)

### `save_file(filepath, content)`
- **功能**: 将代码或文本保存到工作区文件，并自动触发 Git 提交。
- **Agent 用法**: 
  - 方式 A (Tool Call): 直接调用 function `save_file`.
  - 方式 B (Markdown Parsing): 在代码块前加上路径注释，如 `#### src/main.py`.

### `read_file(filepath)`
- **功能**: 安全读取工作区内的文件内容。
- **适用角色**: Integrator, Reviewer, QA.

## 2. 现有角色模板 (Reference Roles)

- **WebArchitect**
  - 职责: Web 全栈设计与编码。
  - Prompt: `ai_core/prompts/web_expert.md`
  
- **EmbeddedEngineer**
  - 职责: 嵌入式 C 语言开发 (STM32)。
  - Prompt: `ai_core/prompts/embedded_expert.md`

## 3. 编排模式

- **GroupChat**: 所有角色在一个群组中自由发言（或按顺序）。
- **Manager**: 自动选择下一个发言人。
