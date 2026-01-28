# 🤖 AI Agent 协同开发框架
> 可能是最简单、最安全的 AutoGen 多智能体开发脚手架。无需编写 Python 代码，只需简述需求，AI 团队自动为您工作。

## ⚡ 30秒极速上手 (Quick Start)

### 1. 准备环境
**您唯一需要安装的软件**：
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) 或 Docker Engine (Linux)

*(无需 Python、无需 Node.js、无需 Git)*

### 2. 获取代码
```bash
git clone https://github.com/Hypocrite65/Cyber-Workforce.git
cd Cyber-Workforce
```

### 3. 配置密钥 (`secrets/config.json`)
复制示例文件并填入您的 API Key (支持 DashScope/OpenAI 等)：
**Windows:**
```cmd
copy secrets\config.json.example secrets\config.json
```
**Linux/Mac:**
```bash
cp secrets/config.json.example secrets/config.json
```
*编辑 `secrets/config.json` 填入您的 Key。*

### 4. 一键运行 🚀
直接运行脚本，告诉 AI 你的需求（例如："帮我写个用户登录页面"）：

**Windows (双击或命令行):**
```cmd
run_docker.bat --auto-team --task my_tasks\web_sample.txt
```

**Linux / Mac:**
```bash
./run_docker.sh --auto-team --task my_tasks/web_sample.txt
```

---

## 📂 产出在哪里？
运行完成后，所有代码会自动保存在 **`output/`** 目录中。
例如：`output/web_sample/workspace/`

---

## 🌟 核心特性 (Why This?)

| 特性 | 说明 |
| :--- | :--- |
| **🧠 智能组队 (Auto-Team)** | 不需要您手动定义 AI。系统内置 "HR" 会分析您的需求，自动招聘 PM、架构师、工程师。 |
| **🛡️ 纯净安全 (Safe Mode)** | 严格的沙箱机制。AI 只能在 `output/` 里写代码，**绝无权限**修改框架核心文件。 |
| **🔌 插件化技能** | 内置团队构建、信息搜索技能，支持模块化扩展。 |
| **🐳 全容器化** | 使用 Docker 封装环境，解决所有 "在我的机器上跑不起来" 的问题。 |

---

## ⚙️ 配置详解 (Configuration)

### 1. 修改 AI 思考轮数
默认情况下，AI 团队会进行最多 20 轮对话。如果您觉得太少（还没做完就停了）或太多（一直在闲聊），请修改 **`companies/` 下的 JSON 配置文件**：

```json
{
  "company_name": "Startup",
  "process": {
    "max_round": 50  <-- 修改这里 (建议 15-50)
  },
  "roles": [...]
}
```

### 2. 切换模型 (OpenAI / Claude / DashScope)
在 `secrets/config.json` 中配置您的模型：
```json
{
  "default_model": "qwen_max",
  "models": [
    {
       "model": "gpt-4",
       "api_key": "sk-...",
       "base_url": "https://api.openai.com/v1"
    }
  ]
}
```

---

## 📖 进阶指南

- **自定义 AI 公司**: 想要自己定义团队？请修改 `companies/` 下的 JSON 配置。
- **自定义角色**: 在 `ai_core/prompts/` 添加新的专家 Prompt。
- **查看架构文档**: 详见 [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 🧩 致谢与开源组件 (Acknowledgments)
本项目核心逻辑完全开源，并集成了以下优秀的开源算法/库作为技能支撑：

| 组件/库 | 用途 | 协议 |
| :--- | :--- | :--- |
| **[AutoGen](https://github.com/microsoft/autogen)** | 多智能体核心框架 | MIT |
| **[Tailwind CSS](https://tailwindcss.com)** | `ui_designer` 技能使用了其配色算法逻辑 | MIT |
| **[DuckDuckGo](https://pypi.org/project/duckduckgo-search/)** | `web_search` 技能推荐使用的搜索源 (无需 Key) | MIT |
| **Docker** | 容器化部署支持 | Apache 2.0 |

*本项目部分设计灵感来源于开源社区的最佳实践。*

---
*Created by Cyber-Workforce Team*
