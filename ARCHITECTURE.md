# 技术架构文档 (Architecture)

## 1. 系统设计理念
本系统旨在构建一个**安全、可扩展、全容器化**的 AI 协同开发环境。核心设计原则包括：

- **Core/Plugin 分离**: 框架逻辑 (`ai_core`) 与业务逻辑（技能、Prompt）完全解耦。
- **Output Isolation**: 所有的副作用（文件写入、Git 操作）被限制在沙箱目录中。
- **Configuration Driven**: 所有的可变部分（模型、团队结构）均通过 JSON 配置驱动。

## 2. 核心模块详解

### 2.1 Agent 运行时 (`ai_core.runner`)
Runner 是系统的"心脏"，负责：
1. **初始化环境**: 创建 `output/` 下的独立 Workspace，初始化 Git 仓库。
2. **加载配置**: 读取 `companies/*.json` 或通过 `team_builder` 动态生成配置。
3. **Agent 编排**: 实例化 AutoGen GroupChat，并挂载 Hook。
   - **Hook 机制**: 拦截所有消息，进行日志记录 (`save_log`) 和代码解析 (`extract_and_save_code`).

### 2.2 技能体系 (`ai_core.skills`)
技能不是简单的函数，而是一个完整的微型应用包：
- **`__init__.py`**: 导出标准接口。
- **`runner.py`**: 包含技能的业务逻辑（如调用 LLM 进行 HR 分析）。
- **`prompts/`**: 技能专属的 Prompt，不污染全局 Prompt 库。

### 2.3 安全层 (`ai_core.tools`)
安全是重中之重。
- **`is_safe_path()`**: 这是一个路径防火墙。它计算目标路径的绝对路径，并检查其是否以 Workspace 路径为前缀。
- **Git整合**: 任何代码写入都会自动触发 `git add/commit`，保证有了版本回溯能力。

## 3. 工程目录指引

### 根目录
| 文件/文件夹 | 作用 |
| :--- | :--- |
| `main.py` | CLI 入口，处理参数解析。 |
| `Dockerfile` | 环境镜像定义。 |
| `run_docker.sh/bat` | 跨平台一键运行脚本。 |

### ai_core/ (框架核心)
| 模块 | 作用 |
| :--- | :--- |
| `base_agent.py` | 工厂模式实现，处理 Config Loading 和 Role Mapping。 |
| `runner.py` | 流程编排。 |
| `tools.py` | 底层 IO 与 安全检查。 |
| `skills/` | 插件化技能库。 |
| `prompts/` | 通用角色 Prompt 库。 |

## 4. 扩展指南

### 如何添加新角色？
1. 在 `ai_core/prompts/` 下新建 `my_expert.md`。
2. 在 `companies/` 的 JSON 中引用它。

### 如何添加新技能？
1. 复制 `ai_core/skills/team_builder` 文件夹。
2. 修改 `runner.py` 实现你的逻辑。
3. 在 `main.py` 中注册新的参数触发它。
