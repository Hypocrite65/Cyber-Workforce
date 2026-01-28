---
name: Team Builder
description: 自动分析需求并组建 AI 开发团队
version: 1.0
author: wei-Aug2024
---

# Team Builder Skill

## 简介
该技能利用 LLM (HR Director) 分析自然语言需求，输出符合系统要求的 JSON 团队配置文件。

## 工作流程
1. 接收用户需求。
2. HR Agent 评估复杂度。
3. 从 `ai_core/prompts` 中选择合适的角色。
4. 生成 `companies/xxx.json` 配置文件。

## 依赖
- AutoGen
- ai_core.base_agent
