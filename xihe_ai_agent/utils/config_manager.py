"""
配置管理系统
提供配置文件的读取、写入、验证和管理功能
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AndroidConfig:
    """Android配置"""
    adb_path: str = "adb"
    device_id: str = ""
    screen_width: int = 1080
    screen_height: int = 2340
    tap_delay: float = 0.1
    swipe_duration: int = 300
    screenshot_quality: int = 80


@dataclass
class AIConfig:
    """AI配置"""
    api_key: str = ""
    api_url: str = "https://api.openai.com/v1/chat/completions"
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class SchedulerConfig:
    """调度器配置"""
    max_concurrent_tasks: int = 5
    task_timeout: int = 300
    cleanup_interval: int = 3600
    auto_cleanup_completed: bool = False
    max_task_history: int = 1000


@dataclass
class WebScrapingConfig:
    """网页抓取配置"""
    headless: bool = False
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    page_load_timeout: int = 30
    implicit_wait: int = 10
    screenshot_on_error: bool = True
    retry_count: int = 3


@dataclass
class UIAutomationConfig:
    """UI自动化配置"""
    video_watch_duration: int = 30
    scroll_interval: int = 5
    like_probability: float = 0.1
    comment_probability: float = 0.05
    share_probability: float = 0.02
    random_delay_min: float = 1.0
    random_delay_max: float = 3.0


@dataclass
class MessagingConfig:
    """消息配置"""
    platforms: List[str] = None
    default_platform: str = "wechat"
    send_delay_min: int = 5
    send_delay_max: int = 15
    auto_reply_enabled: bool = False
    reply_rules: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = ["wechat", "qq", "sms"]
        if self.reply_rules is None:
            self.reply_rules = []


@dataclass
class NotificationConfig:
    """通知配置"""
    enabled: bool = True
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    email_smtp_server: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_to: str = ""


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    file_path: str = "logs/xihe.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/xihe_config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("ConfigManager")
        
        # 默认配置
        self.default_config = {
            "android": AndroidConfig(),
            "ai": AIConfig(),
            "scheduler": SchedulerConfig(),
            "web_scraping": WebScrapingConfig(),
            "ui_automation": UIAutomationConfig(),
            "messaging": MessagingConfig(),
            "notification": NotificationConfig(),
            "logging": LoggingConfig()
        }
        
        # 当前配置
        self.config = self.default_config.copy()
        
        # 加载配置
        self.load_config()
        
        self.logger.info("配置管理器初始化完成")
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 合并配置
                self._merge_config(config_data)
                self.logger.info(f"加载配置文件: {self.config_path}")
            else:
                # 创建默认配置文件
                self.save_config()
                self.logger.info(f"创建默认配置文件: {self.config_path}")
                
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self.logger.info("使用默认配置")
    
    def save_config(self):
        """保存配置文件"""
        try:
            # 确保配置目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为可序列化的格式
            config_data = {}
            for key, value in self.config.items():
                if hasattr(value, '__dict__'):
                    config_data[key] = asdict(value)
                else:
                    config_data[key] = value
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"保存配置文件: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
    
    def _merge_config(self, config_data: Dict[str, Any]):
        """合并配置数据"""
        for section, section_config in config_data.items():
            if section in self.config:
                if isinstance(section_config, dict) and hasattr(self.config[section], '__dict__'):
                    # 更新数据类配置
                    for key, value in section_config.items():
                        if hasattr(self.config[section], key):
                            setattr(self.config[section], key, value)
                else:
                    # 直接替换
                    self.config[section] = section_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔 (如: "android.adb_path")
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                elif hasattr(value, '__dict__'):
                    value = getattr(value, k, None)
                else:
                    return default
                
                if value is None:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"获取配置失败 {key}: {e}")
            return default
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔
            value: 配置值
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # 导航到目标位置
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            
            self.logger.info(f"设置配置: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"设置配置失败 {key}: {e}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置节
        
        Args:
            section: 配置节名称
            
        Returns:
            配置节数据
        """
        if section in self.config:
            config_section = self.config[section]
            if hasattr(config_section, '__dict__'):
                return asdict(config_section)
            else:
                return config_section
        return {}
    
    def update_section(self, section: str, data: Dict[str, Any]):
        """
        更新配置节
        
        Args:
            section: 配置节名称
            data: 配置数据
        """
        if section in self.config:
            config_section = self.config[section]
            if hasattr(config_section, '__dict__'):
                # 更新数据类
                for key, value in data.items():
                    if hasattr(config_section, key):
                        setattr(config_section, key, value)
            else:
                # 直接更新字典
                self.config[section].update(data)
        
        self.logger.info(f"更新配置节: {section}")
    
    def validate_config(self) -> List[str]:
        """
        验证配置
        
        Returns:
            验证错误列表
        """
        errors = []
        
        # 验证Android配置
        android_config = self.get_section("android")
        if not android_config.get("adb_path"):
            errors.append("Android ADB路径未配置")
        
        # 验证AI配置
        ai_config = self.get_section("ai")
        if not ai_config.get("api_key"):
            errors.append("AI API密钥未配置")
        
        # 验证通知配置
        notification_config = self.get_section("notification")
        if notification_config.get("enabled"):
            if not notification_config.get("telegram_bot_token") and not notification_config.get("email_username"):
                errors.append("通知已启用但未配置通知方式")
        
        return errors
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self.logger.info("配置已重置为默认值")
    
    def export_config(self, export_path: str):
        """
        导出配置
        
        Args:
            export_path: 导出路径
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为可序列化的格式
            config_data = {}
            for key, value in self.config.items():
                if hasattr(value, '__dict__'):
                    config_data[key] = asdict(value)
                else:
                    config_data[key] = value
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"配置已导出到: {export_path}")
            
        except Exception as e:
            self.logger.error(f"导出配置失败: {e}")
    
    def import_config(self, import_path: str):
        """
        导入配置
        
        Args:
            import_path: 导入路径
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                raise FileNotFoundError(f"配置文件不存在: {import_path}")
            
            with open(import_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 合并配置
            self._merge_config(config_data)
            
            # 保存配置
            self.save_config()
            
            self.logger.info(f"配置已从 {import_path} 导入")
            
        except Exception as e:
            self.logger.error(f"导入配置失败: {e}")
    
    def get_app_config(self, app_name: str) -> Dict[str, Any]:
        """
        获取应用特定配置
        
        Args:
            app_name: 应用名称
            
        Returns:
            应用配置
        """
        app_configs = self.get("app_configs", {})
        return app_configs.get(app_name, {})
    
    def set_app_config(self, app_name: str, config: Dict[str, Any]):
        """
        设置应用特定配置
        
        Args:
            app_name: 应用名称
            config: 应用配置
        """
        app_configs = self.get("app_configs", {})
        app_configs[app_name] = config
        self.set("app_configs", app_configs)
    
    def get_task_template(self, template_name: str) -> Dict[str, Any]:
        """
        获取任务模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            任务模板
        """
        templates = self.get("task_templates", {})
        return templates.get(template_name, {})
    
    def set_task_template(self, template_name: str, template: Dict[str, Any]):
        """
        设置任务模板
        
        Args:
            template_name: 模板名称
            template: 任务模板
        """
        templates = self.get("task_templates", {})
        templates[template_name] = template
        self.set("task_templates", templates)
    
    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务模板"""
        return self.get("task_templates", {})
    
    def create_default_templates(self):
        """创建默认任务模板"""
        default_templates = {
            "刷抖音视频": {
                "type": "video_watching",
                "platform": "douyin",
                "duration": 300,
                "like_probability": 0.1,
                "comment_probability": 0.05
            },
            "发送微信消息": {
                "type": "messaging",
                "platform": "wechat",
                "recipient": "",
                "content": ""
            },
            "网页抓取": {
                "type": "web_scraping",
                "url": "",
                "data_type": "text",
                "headless": False
            },
            "自动点赞": {
                "type": "ui_automation",
                "app_name": "抖音",
                "action": "auto_like",
                "count": 10
            }
        }
        
        self.set("task_templates", default_templates)
        self.logger.info("创建默认任务模板")