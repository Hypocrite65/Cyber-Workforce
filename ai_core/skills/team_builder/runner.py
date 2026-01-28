# 版本: v1.1
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-28
# 总结: Team Builder 技能实现逻辑 (Refactored)

import os
import json
import sys

# 确保能找到 ai_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from ai_core.base_agent import AgentFactory

def load_skill_prompt(filename):
    """加载技能专用的 Prompt"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "prompts", filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are an HR Director."

def assess_and_build_team(task_content, output_path):
    """
    分析任务并生成公司配置 JSON
    """
    factory = AgentFactory()
    
    # 加载 HR Prompt
    hr_prompt = load_skill_prompt("hr_director.md")
    # 补充 JSON 格式要求
    hr_prompt += """
    
请输出如下 JSON 格式 (不要 Markdown):
{
    "company_name": "AutoTeam",
    "description": "...",
    "roles": [
        { "name": "...", "prompt_file": "ai_core/prompts/xxx.md", "model_alias": "qwen_max" }
    ],
    "process": { "max_round": 15 }
}
    """

    hr_agent = factory.create_assistant(
        "HR_Director",
        hr_prompt,
        model_alias="qwen_max"
    )
    
    user_proxy = factory.create_user_proxy(human_input_mode="NEVER", max_replies=1)
    
    print("🧠 [Skill] TeamBuilder: Analyzing requirement...")
    
    chat_res = user_proxy.initiate_chat(
        hr_agent, 
        message=f"Project Requirement:\n{task_content}"
    )
    
    # 提取 JSON
    content = chat_res.chat_history[-1]['content']
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        
    try:
        config = json.loads(content)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        print(f"✅ [Skill] Team Config Saved: {output_path}")
        return True
    except Exception as e:
        print(f"❌ [Skill] Failed to parse JSON: {e}")
        return False
