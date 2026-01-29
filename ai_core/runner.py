# 版本: v1.2
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-29
# 总结: 集成日志系统和 Token 追踪，支持预算控制和成本监控。

import os
import autogen
import json
from .base_agent import AgentFactory
from .tools import init_workspace, save_code_to_file, save_log, extract_and_save_code
from .logger import WorkflowLogger
from .token_tracker import TokenTracker

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
    集成日志系统和 Token 追踪
    """
    # 1. 环境初始化
    init_workspace(work_dir)
    
    # 提取项目名称
    project_name = os.path.basename(os.path.dirname(work_dir))
    
    # 初始化日志器
    logger = WorkflowLogger(project_name)
    logger.info(f"初始化工作空间: {work_dir}")
    logger.info(f"加载公司配置: {company_config_path}")
    
    print(f"🔧 Initialized workspace at: {work_dir}")
    print(f"🏢 Loading Company Config: {company_config_path}")
    print(f"📝 Log file: {logger.get_log_path()}")
    
    # 2. 读取配置
    try:
        with open(company_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        print(f"❌ Failed to load company config: {e}")
        return

    # 3. 初始化 Token 追踪器
    factory = AgentFactory()
    secrets_config = factory.secrets_config
    
    # 读取预算配置
    budget_cfg = secrets_config.get("budget_control", {})
    budget_enabled = budget_cfg.get("enabled", False)
    max_cost = budget_cfg.get("max_cost_cny") if budget_enabled else None
    max_rounds = budget_cfg.get("max_rounds", 30)
    warning_threshold = budget_cfg.get("warning_threshold", 0.8)
    
    tracker = TokenTracker(project_name, budget_limit=max_cost)
    logger.info(f"预算控制: {'启用' if budget_enabled else '禁用'}")
    if budget_enabled:
        logger.info(f"最大成本: ¥{max_cost}, 最大轮次: {max_rounds}")
    
    user_proxy = factory.create_user_proxy()
    
    # Tool registration
    def save_file(filepath, content):
        success, msg = save_code_to_file(work_dir, filepath, content)
        logger.info(f"保存文件: {filepath} - {'成功' if success else '失败'}")
        return msg
    user_proxy.register_function(function_map={"save_file": save_file})
    
    agents = [user_proxy]
    
    # 4. 动态创建角色
    roles = config.get("roles", [])
    for role in roles:
        name = role.get("name")
        prompt_file = role.get("prompt_file")
        model_alias = role.get("model_alias")
        append_msg = role.get("system_message_append", "")
        
        # 允许 prompt_file 是相对路径
        if not os.path.isabs(prompt_file):
            if not os.path.exists(prompt_file):
                alt_path = os.path.join(os.path.dirname(company_config_path), prompt_file)
                if os.path.exists(alt_path):
                    prompt_file = alt_path
        
        sys_msg = load_text_file(prompt_file)
        if append_msg:
            sys_msg += f"\n\n{append_msg}"
            
        if not sys_msg:
            sys_msg = f"You are {name}."
            
        logger.info(f"雇佣角色: {name} (模型: {model_alias or 'auto'})")
        print(f"  👤 Hire: {name} (Model: {model_alias or 'auto'})")
        agent = factory.create_assistant(
            name=name,
            system_message=sys_msg,
            model_alias=model_alias
        )
        agents.append(agent)
        
    # 5. 启动群聊
    process_cfg = config.get("process", {})
    configured_max_round = process_cfg.get("max_round", 20)
    # 使用配置中的较小值
    effective_max_round = min(configured_max_round, max_rounds)
    speaker_method = process_cfg.get("speaker_selection_method", "auto")
    
    logger.info(f"群聊配置: 最大轮次={effective_max_round}, 发言选择={speaker_method}")
    
    groupchat = autogen.GroupChat(
        agents=agents,
        messages=[],
        max_round=effective_max_round,
        speaker_selection_method=speaker_method
    )
    
    # 6. Hook for logging, parsing and token tracking
    original_append = groupchat.append
    budget_exceeded = False
    
    def logged_append(message, speaker):
        nonlocal budget_exceeded
        
        original_append(message, speaker)
        sender = message.get("name", "Unknown")
        content = message.get("content", "")
        
        # 日志记录
        logger.agent_message(sender, content)
        save_log(work_dir, sender, content)
        
        # 代码提取
        saved_files = extract_and_save_code(work_dir, content)
        if saved_files:
            logger.info(f"提取并保存 {len(saved_files)} 个文件: {saved_files}")
            print(f"✅ Extracted & Saved {len(saved_files)} files: {saved_files}")
        
        # Token 追踪（尝试从 message 中提取 usage 信息）
        usage = message.get("usage")
        if usage:
            model_name = message.get("model", "unknown")
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            cost = tracker.track_usage(model_name, input_tokens, output_tokens)
            logger.debug(f"Token 使用: {model_name} - 输入:{input_tokens}, 输出:{output_tokens}, 成本:¥{cost:.4f}")
        
        # 增加轮次
        tracker.increment_round()
        
        # 预算检查
        if budget_enabled:
            exceeded, remaining = tracker.check_budget()
            if exceeded and not budget_exceeded:
                budget_exceeded = True
                logger.warning(f"⚠️ 预算已超限! 当前成本: ¥{tracker.total_cost:.4f}")
                print(f"⚠️ Budget exceeded! Current cost: ¥{tracker.total_cost:.4f}")
                # 可以选择强制终止
                # raise Exception("Budget limit exceeded")
            elif remaining is not None and remaining < max_cost * (1 - warning_threshold):
                logger.warning(f"预算警告: 剩余 ¥{remaining:.4f}")
            
    groupchat.append = logged_append
    
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=factory._get_llm_config())
    
    logger.info("🚀 公司开始工作...")
    print("🚀 Company Started Working...")
    
    try:
        user_proxy.initiate_chat(manager, message=task_content)
    except Exception as e:
        logger.error(f"执行异常: {e}")
        print(f"❌ Execution Error: {e}")
    finally:
        # 保存报告
        logger.info("✅ 工作会话结束")
        print("✅ Work Session Finished.")
        
        # 打印和保存 Token 使用报告
        tracker.print_summary()
        report_path = tracker.save_report()
        logger.info(f"Token 使用报告已保存: {report_path}")
        print(f"📊 Token usage report saved: {report_path}")


def run_project(project_type, task_content, work_dir):
    """
    (Legacy) 运行基于硬编码类型的项目
    集成日志系统和 Token 追踪
    """
    init_workspace(work_dir)
    
    project_name = os.path.basename(os.path.dirname(work_dir))
    logger = WorkflowLogger(project_name)
    logger.info(f"Legacy 模式启动: {project_type}")
    
    print(f"🔧 Initialized workspace at: {work_dir}")
    print(f"📝 Log file: {logger.get_log_path()}")
    
    factory = AgentFactory()
    secrets_config = factory.secrets_config
    
    # 读取预算配置
    budget_cfg = secrets_config.get("budget_control", {})
    budget_enabled = budget_cfg.get("enabled", False)
    max_cost = budget_cfg.get("max_cost_cny") if budget_enabled else None
    
    tracker = TokenTracker(project_name, budget_limit=max_cost)
    
    user_proxy = factory.create_user_proxy()
    
    def save_file(filepath, content):
        success, msg = save_code_to_file(work_dir, filepath, content)
        logger.info(f"保存文件: {filepath} - {'成功' if success else '失败'}")
        return msg
    user_proxy.register_function(function_map={"save_file": save_file})
    
    agents = [user_proxy]
    
    if project_type == "web":
        print("🌐 Loading Web Team (Legacy Mode)...")
        logger.info("加载 Web 团队")
        sys_msg = load_prompt("web_expert.md")
        web = factory.create_assistant("WebArchitect", sys_msg, model_alias="qwen_max")
        agents.append(web)
    elif project_type == "embedded":
        print("🔌 Loading Embedded Team (Legacy Mode)...")
        logger.info("加载嵌入式团队")
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
        
        logger.agent_message(sender, content)
        save_log(work_dir, sender, content)
        extract_and_save_code(work_dir, content)
        
        # Token 追踪
        usage = message.get("usage")
        if usage:
            model_name = message.get("model", "unknown")
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            tracker.track_usage(model_name, input_tokens, output_tokens)
        
        tracker.increment_round()
            
    groupchat.append = logged_append
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=factory._get_llm_config())
    
    try:
        user_proxy.initiate_chat(manager, message=task_content)
    except Exception as e:
        logger.error(f"执行异常: {e}")
        print(f"❌ Execution Error: {e}")
    finally:
        tracker.print_summary()
        report_path = tracker.save_report()
        logger.info(f"Token 使用报告已保存: {report_path}")
        print(f"📊 Token usage report saved: {report_path}")
