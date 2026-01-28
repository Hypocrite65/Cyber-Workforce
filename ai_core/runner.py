# 版本: v1.1
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-28
# 总结: 升级 Runner，支持通过 JSON 配置文件动态组建 AI 公司/团队。

import os
import autogen
import json
from .base_agent import AgentFactory
from .tools import init_workspace, save_code_to_file, save_log, extract_and_save_code

def load_text_file(filepath):
    """通用文件读取"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def load_prompt(filename):
    """加载 prompts 目录下的 Markdown 文件 (Legacy Support)"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "prompts", filename)
    return load_text_file(path)

def run_company(company_config_path, task_content, work_dir):
    """
    运行基于 JSON 配置定义的 AI 公司
    """
    # 1. 环境初始化
    init_workspace(work_dir)
    print(f"🔧 Initialized workspace at: {work_dir}")
    print(f"🏢 Loading Company Config: {company_config_path}")
    
    # 2. 读取配置
    try:
        with open(company_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load company config: {e}")
        return

    factory = AgentFactory()
    user_proxy = factory.create_user_proxy()
    
    # Tool registration
    def save_file(filepath, content):
        success, msg = save_code_to_file(work_dir, filepath, content)
        return msg
    user_proxy.register_function(function_map={"save_file": save_file})
    
    agents = [user_proxy]
    
    # 3. 动态创建角色
    roles = config.get("roles", [])
    for role in roles:
        name = role.get("name")
        prompt_file = role.get("prompt_file")
        model_alias = role.get("model_alias")
        append_msg = role.get("system_message_append", "")
        
        # 允许 prompt_file 是相对路径
        if not os.path.isabs(prompt_file):
            # 假设相对于当前工作目录（根目录）
            # 或者尝试相对于配置文件所在目录
            if not os.path.exists(prompt_file):
                # 尝试相对于 config 文件
                alt_path = os.path.join(os.path.dirname(company_config_path), prompt_file)
                if os.path.exists(alt_path):
                    prompt_file = alt_path
        
        sys_msg = load_text_file(prompt_file)
        if append_msg:
            sys_msg += f"\n\n{append_msg}"
            
        if not sys_msg:
            sys_msg = f"You are {name}."
            
        print(f"  👤 Hire: {name} (Model: {model_alias or 'auto'})")
        agent = factory.create_assistant(
            name=name,
            system_message=sys_msg,
            model_alias=model_alias
        )
        agents.append(agent)
        
    # 4. 启动群聊
    process_cfg = config.get("process", {})
    max_round = process_cfg.get("max_round", 20)
    speaker_method = process_cfg.get("speaker_selection_method", "auto")
    
    groupchat = autogen.GroupChat(
        agents=agents,
        messages=[],
        max_round=max_round,
        speaker_selection_method=speaker_method
    )
    
    # Hook for logging and parsing
    original_append = groupchat.append
    def logged_append(message, speaker):
        original_append(message, speaker)
        sender = message.get("name", "Unknown")
        content = message.get("content", "")
        save_log(work_dir, sender, content)
        saved_files = extract_and_save_code(work_dir, content)
        if saved_files:
            print(f"✅ Extracted & Saved {len(saved_files)} files: {saved_files}")
            
    groupchat.append = logged_append
    
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=factory._get_llm_config())
    
    print("🚀 Company Started Working...")
    user_proxy.initiate_chat(manager, message=task_content)
    print("✅ Work Session Finished.")


def run_project(project_type, task_content, work_dir):
    """
    (Legacy) 运行基于硬编码类型的项目
    """
    # 简单的适配层：构造一个虚拟的 config 字典，然后复用逻辑?
    # 为了保持代码独立性，这里保留简单的硬编码逻辑，或者指向预定义的 JSON
    
    # 也可以直接生成一个临时的 JSON 并调用 run_company，但为了简单，这里保留原样
    # 不过既然升级了，我们还是保留原样，确保不破坏 main.py 的逻辑
    # 如果想更优雅，可以将 run_project 内部逻辑也指向 "companies/default_web.json"
    
    # 此处省略重复代码，仅做简单维护。为保证功能完整，这里必须包含完整逻辑。
    # 为节省篇幅，我们其实可以报错提示用户使用 --company，但为了兼容 main.py:
    
    init_workspace(work_dir)
    print(f"🔧 Initialized workspace at: {work_dir}")
    
    factory = AgentFactory()
    user_proxy = factory.create_user_proxy()
    
    def save_file(filepath, content):
        success, msg = save_code_to_file(work_dir, filepath, content)
        return msg
    user_proxy.register_function(function_map={"save_file": save_file})
    
    agents = [user_proxy]
    
    if project_type == "web":
        print("🌐 Loading Web Team (Legacy Mode)...")
        sys_msg = load_prompt("web_expert.md")
        web = factory.create_assistant("WebArchitect", sys_msg, model_alias="qwen_max")
        agents.append(web)
    elif project_type == "embedded":
        print("🔌 Loading Embedded Team (Legacy Mode)...")
        sys_msg = load_prompt("embedded_expert.md")
        emb = factory.create_assistant("EmbeddedEngineer", sys_msg)
        rev = factory.create_assistant("CodeReviewer", "Review C Code specifically for safety.")
        agents.append(emb)
        agents.append(rev)
        
    groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=15)
    
    original_append = groupchat.append
    def logged_append(message, speaker):
        original_append(message, speaker)
        sender = message.get("name", "Unknown")
        content = message.get("content", "")
        save_log(work_dir, sender, content)
        extract_and_save_code(work_dir, content)
            
    groupchat.append = logged_append
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=factory._get_llm_config())
    
    user_proxy.initiate_chat(manager, message=task_content)
