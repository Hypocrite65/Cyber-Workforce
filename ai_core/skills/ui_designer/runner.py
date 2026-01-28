# 版本: v1.1
# 总结: 升级为 "AI决策 + 算法执行" 模式

import os
import json
import re
import sys

# 导入算法引擎
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from color_engine import generate_design_tokens

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from ai_core.base_agent import AgentFactory

def load_skill_prompt(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "prompts", filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f: return f.read()
    return "You are a UI Designer."

def generate_design_system(requirement, output_path):
    factory = AgentFactory()
    
    # 1. 第一步：决策 (Decision Making)
    # 让 LLM 只负责它擅长的：理解语义，提取品牌色
    decision_prompt = """
    你是一个设计总监。请根据用户的产品需求，决定一个最合适的【品牌主色】(Hex Code)。
    
    只输出颜色代码，例如：#3B82F6
    不要输出任何其他废话。
    """
    
    director = factory.create_assistant("DesignDirector", decision_prompt, model_alias="qwen_max")
    user = factory.create_user_proxy(human_input_mode="NEVER", max_replies=1)
    
    print("🎨 [Skill] UIDesigner: Deciding Brand Identity...")
    res = user.initiate_chat(director, message=f"Product Requirement:\n{requirement}")
    
    # 提取颜色
    color_hex = res.chat_history[-1]['content'].strip()
    # 简单的正则提取，防止 LLM 多嘴
    match = re.search(r'#[0-9a-fA-F]{6}', color_hex)
    if match:
        brand_color = match.group(0)
    else:
        brand_color = "#3B82F6" # Fallback Blue
        
    print(f"🎨 [Skill] Selected Brand Color: {brand_color}")
    
    # 2. 第二步：执行 (Algorithmic Execution)
    # 使用确定性算法生成完整的系统，而不是让 LLM 瞎编
    design_tokens = generate_design_tokens(brand_color)
    
    # 3. 第三步：生成文档 (Documentation)
    # 再让 LLM 基于生成的数据写文档，这次它有了确定的数据作为上下文
    doc_prompt = load_skill_prompt("design_expert.md")
    doc_prompt += f"\n\n【系统数据】\n{json.dumps(design_tokens, indent=2)}\n\n请基于上述 JSON 数据，写一份详细的 Markdown 设计规范文档。"
    
    writer = factory.create_assistant("DocWriter", doc_prompt, model_alias="qwen_max")
    res_doc = user.initiate_chat(writer, message="Please write the documentation based on the provided tokens.")
    
    final_doc = res_doc.chat_history[-1]['content']
    
    # 拼接 JSON 和 文档
    full_output = f"# Design System Specifications\n\n"
    full_output += f"## Design Tokens (Machine Readable)\n```json\n{json.dumps(design_tokens, indent=2)}\n```\n\n"
    full_output += final_doc
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_output)
        print(f"✅ [Skill] Design System Generated: {output_path}")
        return True
    except Exception as e:
        print(f"❌ [Skill] Failed: {e}")
        return False
