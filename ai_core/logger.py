# -*- coding: utf-8 -*-
# 版本: v1.0
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-29
# 总结: 实现运行时日志系统，支持文件和控制台双输出，时间戳管理。

import logging
import os
from datetime import datetime
from pathlib import Path

class WorkflowLogger:
    """
    工作流日志管理器
    - 支持时间戳日志文件
    - 双输出：控制台 + 文件
    - 分级日志：DEBUG, INFO, WARNING, ERROR
    """
    
    def __init__(self, project_name, log_dir="logs"):
        """
        初始化日志器
        :param project_name: 项目名称
        :param log_dir: 日志根目录
        """
        self.project_name = project_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 生成时间戳日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"run_{timestamp}_{project_name}.log"
        
        # 配置日志器
        self.logger = logging.getLogger(f"CyberWorkforce.{project_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加 handler
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """配置文件和控制台处理器"""
        # 文件处理器 - 详细日志
        file_handler = logging.FileHandler(
            self.log_file, 
            mode='w', 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器 - 简洁日志
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """信息日志"""
        self.logger.info(message)
    
    def debug(self, message):
        """调试日志"""
        self.logger.debug(message)
    
    def warning(self, message):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """错误日志"""
        self.logger.error(message)
    
    def agent_message(self, agent_name, content):
        """记录 Agent 消息"""
        self.logger.info(f"[{agent_name}] {content[:200]}...")  # 控制台简短
        self.logger.debug(f"[{agent_name}] Full Message:\n{content}")  # 文件完整
    
    def get_log_path(self):
        """获取日志文件路径"""
        return str(self.log_file)
