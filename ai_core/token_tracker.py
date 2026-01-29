# -*- coding: utf-8 -*-
# 版本: v1.0
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-29
# 总结: Token 使用追踪和成本监控模块，支持预算控制和自动终止。

import json
from pathlib import Path
from datetime import datetime

class TokenTracker:
    """
    Token 使用追踪器
    - 统计每个模型的 token 消耗
    - 成本估算（基于配置的价格）
    - 预算控制和超限警告
    """
    
    # 默认价格表（每百万 token 的价格，单位：元）
    DEFAULT_PRICING = {
        "qwen-max": {"input": 0.04, "output": 0.12},
        "qwen-turbo": {"input": 0.003, "output": 0.006},
        "qwen-plus": {"input": 0.008, "output": 0.024},
        # 预留本地模型接口
        "ollama": {"input": 0.0, "output": 0.0},
        "local": {"input": 0.0, "output": 0.0}
    }
    
    def __init__(self, project_name, budget_limit=None, log_dir="logs"):
        """
        初始化追踪器
        :param project_name: 项目名称
        :param budget_limit: 预算上限（元），None 表示无限制
        :param log_dir: 日志目录
        """
        self.project_name = project_name
        self.budget_limit = budget_limit
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 统计数据
        self.usage = {}  # {model_name: {"input": tokens, "output": tokens}}
        self.total_cost = 0.0
        self.round_count = 0
        self.start_time = datetime.now()
        
        # 时间戳文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.usage_file = self.log_dir / f"token_usage_{timestamp}_{project_name}.json"
    
    def track_usage(self, model_name, input_tokens, output_tokens):
        """
        记录 token 使用
        :param model_name: 模型名称
        :param input_tokens: 输入 token 数
        :param output_tokens: 输出 token 数
        """
        if model_name not in self.usage:
            self.usage[model_name] = {"input": 0, "output": 0, "calls": 0}
        
        self.usage[model_name]["input"] += input_tokens
        self.usage[model_name]["output"] += output_tokens
        self.usage[model_name]["calls"] += 1
        
        # 计算成本
        cost = self._calculate_cost(model_name, input_tokens, output_tokens)
        self.total_cost += cost
        
        return cost
    
    def _calculate_cost(self, model_name, input_tokens, output_tokens):
        """计算成本（元）"""
        pricing = self.DEFAULT_PRICING.get(model_name, {"input": 0.0, "output": 0.0})
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    def increment_round(self):
        """增加轮次计数"""
        self.round_count += 1
    
    def check_budget(self):
        """
        检查预算
        :return: (is_exceeded, remaining_budget)
        """
        if self.budget_limit is None:
            return False, None
        
        remaining = self.budget_limit - self.total_cost
        return self.total_cost >= self.budget_limit, remaining
    
    def get_summary(self):
        """获取统计摘要"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            "project": self.project_name,
            "duration_seconds": round(duration, 2),
            "total_rounds": self.round_count,
            "total_cost_cny": round(self.total_cost, 4),
            "budget_limit_cny": self.budget_limit,
            "models": {}
        }
        
        for model, stats in self.usage.items():
            total_tokens = stats["input"] + stats["output"]
            model_cost = self._calculate_cost(model, stats["input"], stats["output"])
            
            summary["models"][model] = {
                "calls": stats["calls"],
                "input_tokens": stats["input"],
                "output_tokens": stats["output"],
                "total_tokens": total_tokens,
                "cost_cny": round(model_cost, 4)
            }
        
        return summary
    
    def save_report(self):
        """保存使用报告"""
        summary = self.get_summary()
        
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(self.usage_file)
    
    def print_summary(self):
        """打印摘要到控制台"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print(f"📊 Token 使用报告 - {self.project_name}")
        print("="*60)
        print(f"⏱️  运行时长: {summary['duration_seconds']}s")
        print(f"🔄 总轮次: {summary['total_rounds']}")
        print(f"💰 总成本: ¥{summary['total_cost_cny']:.4f}")
        
        if self.budget_limit:
            print(f"📈 预算限制: ¥{self.budget_limit:.4f}")
            remaining = self.budget_limit - summary['total_cost_cny']
            print(f"💵 剩余预算: ¥{remaining:.4f}")
        
        print("\n模型详情:")
        for model, stats in summary['models'].items():
            print(f"  🤖 {model}:")
            print(f"     调用次数: {stats['calls']}")
            print(f"     输入 Tokens: {stats['input_tokens']:,}")
            print(f"     输出 Tokens: {stats['output_tokens']:,}")
            print(f"     成本: ¥{stats['cost_cny']:.4f}")
        
        print("="*60 + "\n")
