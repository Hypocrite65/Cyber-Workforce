# 版本: v1.2
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-28
# 总结: 升级 AgentFactory，支持通过配置文件中的 role_mapping 自动分配模型。

import os
import autogen
from .utils import load_secrets_config, get_model_config

class AgentFactory:
    def __init__(self):
        self.secrets_config = load_secrets_config()
        if not self.secrets_config and not os.environ.get("DASHSCOPE_API_KEY"):
            print("⚠️ Warning: No configuration found in secrets/config.json or environment!")

    def _get_llm_config(self, model_alias=None):
        """构造 Autogen 的 llm_config"""
        model_cfg = get_model_config(self.secrets_config, model_alias)
        
        if not model_cfg:
            return {
                "config_list": [{"model": "unknown", "api_key": "sk-missing"}],
                "temperature": 0.3
            }
            
        config_list = [{
            "model": model_cfg.get("model"),
            "api_key": model_cfg.get("api_key"),
            "base_url": model_cfg.get("base_url"),
        }]
        
        return {
            "config_list": config_list,
            "temperature": model_cfg.get("temperature", 0.3),
            "timeout": 120,
        }

    def create_assistant(self, name, system_message, model_alias=None):
        """
        创建 AssistantAgent
        :param name: Agent 名称，用于查找 role_mapping
        :param model_alias: 显式指定模型别名 (优先级最高)
        """
        # 1. 优先级: 显式参数 > 角色映射 > 默认模型
        selected_alias = model_alias
        
        if not selected_alias:
            # 检查 role_mapping
            role_map = self.secrets_config.get("role_mapping", {})
            selected_alias = role_map.get(name)
            
        # 2. 如果仍未指定，get_model_config 会自动使用 default_model
        
        llm_config = self._get_llm_config(selected_alias)
        
        # 打印调试信息，确认模型选择
        actual_model = llm_config["config_list"][0].get("model")
        print(f"🤖 Agent '{name}' initialized with model: {actual_model}")

        return autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config=llm_config
        )

    def create_user_proxy(self, name="UserProxy", human_input_mode="NEVER", max_replies=30):
        return autogen.UserProxyAgent(
            name=name,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=max_replies,
            code_execution_config=False,
        )
