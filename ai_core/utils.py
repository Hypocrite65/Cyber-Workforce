# 版本: v1.1
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-28
# 总结: 升级配置加载逻辑，支持多模型JSON配置。

import os
import json

def load_secrets_config():
    """
    加载 secrets/config.json 的完整内容
    """
    current_dir = os.path.dirname(os.path.abspath(__file__)) # ai_core/
    root_dir = os.path.dirname(current_dir) # AutoGenTest/
    secret_path = os.path.join(root_dir, "secrets", "config.json")

    if os.path.exists(secret_path):
        try:
            with open(secret_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to read secrets/config.json: {e}")
    
    return None

def get_model_config(config_data, alias=None):
    """
    根据别名获取特定的模型配置。
    如果 alias 为 None，使用 default_model。
    """
    if not config_data:
        # Fallback for old env var (backward compatibility if needed, or just fail)
        api_key = os.environ.get("DASHSCOPE_API_KEY")
        if api_key:
            return {
                "model": "qwen-max", 
                "api_key": api_key,
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            }
        return None

    if alias is None:
        alias = config_data.get("default_model")
        
    models = config_data.get("models", {})
    return models.get(alias)
