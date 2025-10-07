"""
AI代理核心模块
负责理解用户指令、制定执行计划、协调各个控制模块
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..modules.android_control import AndroidController
from ..modules.web_automation import WebAutomation
from ..modules.ui_automation import UIAutomation
from ..modules.messaging import MessagingAutomation
from ..modules.task_scheduler import TaskScheduler
from ..utils.config_manager import ConfigManager
from ..utils.logger import setup_logger


class TaskType(Enum):
    """任务类型枚举"""
    WEB_SCRAPING = "web_scraping"
    UI_AUTOMATION = "ui_automation"
    MESSAGING = "messaging"
    VIDEO_WATCHING = "video_watching"
    DATA_QUERY = "data_query"
    APP_CONTROL = "app_control"


@dataclass
class Task:
    """任务数据结构"""
    id: str
    type: TaskType
    description: str
    parameters: Dict[str, Any]
    priority: int = 1
    schedule: Optional[str] = None
    dependencies: List[str] = None


class AIAgent:
    """AI代理核心类"""
    
    def __init__(self, config_path: str = "config/xihe_config.json"):
        """
        初始化AI代理
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = setup_logger("AIAgent")
        self.config = ConfigManager(config_path)
        
        # 初始化各个控制模块
        self.android_controller = AndroidController(self.config)
        self.web_automation = WebAutomation(self.config)
        self.ui_automation = UIAutomation(self.config)
        self.messaging = MessagingAutomation(self.config)
        self.task_scheduler = TaskScheduler(self.config)
        
        # 任务队列和执行状态
        self.task_queue = asyncio.Queue()
        self.running_tasks = {}
        self.task_history = []
        
        self.logger.info("羲和AI代理系统初始化完成")
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户指令
        
        Args:
            command: 用户指令文本
            context: 上下文信息
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"处理指令: {command}")
            
            # 1. 理解指令意图
            intent = await self._understand_intent(command, context)
            
            # 2. 制定执行计划
            plan = await self._create_execution_plan(intent)
            
            # 3. 执行任务
            result = await self._execute_plan(plan)
            
            return {
                "success": True,
                "intent": intent,
                "plan": plan,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"处理指令失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _understand_intent(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        理解用户指令意图
        
        Args:
            command: 用户指令
            context: 上下文信息
            
        Returns:
            意图解析结果
        """
        # 这里可以集成大语言模型API进行意图理解
        # 目前使用规则匹配作为示例
        
        intent_patterns = {
            "刷视频": {
                "type": TaskType.VIDEO_WATCHING,
                "action": "watch_videos",
                "parameters": {"duration": 300, "platform": "douyin"}
            },
            "发消息": {
                "type": TaskType.MESSAGING,
                "action": "send_message",
                "parameters": {"platform": "wechat", "content": ""}
            },
            "查询信息": {
                "type": TaskType.DATA_QUERY,
                "action": "query_data",
                "parameters": {"query": "", "source": "web"}
            },
            "网页抓取": {
                "type": TaskType.WEB_SCRAPING,
                "action": "scrape_website",
                "parameters": {"url": "", "data_type": "text"}
            }
        }
        
        # 简单的关键词匹配
        for keyword, intent in intent_patterns.items():
            if keyword in command:
                return intent
        
        # 默认返回通用任务
        return {
            "type": TaskType.APP_CONTROL,
            "action": "general_control",
            "parameters": {"command": command}
        }
    
    async def _create_execution_plan(self, intent: Dict[str, Any]) -> List[Task]:
        """
        根据意图创建执行计划
        
        Args:
            intent: 意图解析结果
            
        Returns:
            任务执行计划
        """
        tasks = []
        task_id = f"task_{len(self.task_history) + 1}"
        
        task = Task(
            id=task_id,
            type=TaskType(intent["type"]),
            description=f"执行{intent['action']}任务",
            parameters=intent["parameters"]
        )
        
        tasks.append(task)
        return tasks
    
    async def _execute_plan(self, plan: List[Task]) -> Dict[str, Any]:
        """
        执行任务计划
        
        Args:
            plan: 任务计划
            
        Returns:
            执行结果
        """
        results = []
        
        for task in plan:
            try:
                self.logger.info(f"开始执行任务: {task.description}")
                
                # 根据任务类型选择执行模块
                if task.type == TaskType.WEB_SCRAPING:
                    result = await self._execute_web_scraping(task)
                elif task.type == TaskType.UI_AUTOMATION:
                    result = await self._execute_ui_automation(task)
                elif task.type == TaskType.MESSAGING:
                    result = await self._execute_messaging(task)
                elif task.type == TaskType.VIDEO_WATCHING:
                    result = await self._execute_video_watching(task)
                elif task.type == TaskType.DATA_QUERY:
                    result = await self._execute_data_query(task)
                else:
                    result = await self._execute_general_task(task)
                
                results.append({
                    "task_id": task.id,
                    "success": True,
                    "result": result
                })
                
                self.task_history.append(task)
                
            except Exception as e:
                self.logger.error(f"任务执行失败 {task.id}: {e}")
                results.append({
                    "task_id": task.id,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total_tasks": len(plan),
            "successful_tasks": len([r for r in results if r["success"]]),
            "results": results
        }
    
    async def _execute_web_scraping(self, task: Task) -> Dict[str, Any]:
        """执行网页抓取任务"""
        return await self.web_automation.scrape_website(
            url=task.parameters.get("url"),
            data_type=task.parameters.get("data_type", "text")
        )
    
    async def _execute_ui_automation(self, task: Task) -> Dict[str, Any]:
        """执行UI自动化任务"""
        return await self.ui_automation.execute_ui_task(
            app_name=task.parameters.get("app_name"),
            actions=task.parameters.get("actions", [])
        )
    
    async def _execute_messaging(self, task: Task) -> Dict[str, Any]:
        """执行消息发送任务"""
        return await self.messaging.send_message(
            platform=task.parameters.get("platform"),
            recipient=task.parameters.get("recipient"),
            content=task.parameters.get("content")
        )
    
    async def _execute_video_watching(self, task: Task) -> Dict[str, Any]:
        """执行视频观看任务"""
        return await self.ui_automation.watch_videos(
            platform=task.parameters.get("platform", "douyin"),
            duration=task.parameters.get("duration", 300)
        )
    
    async def _execute_data_query(self, task: Task) -> Dict[str, Any]:
        """执行数据查询任务"""
        return await self.web_automation.query_data(
            query=task.parameters.get("query"),
            source=task.parameters.get("source", "web")
        )
    
    async def _execute_general_task(self, task: Task) -> Dict[str, Any]:
        """执行通用任务"""
        return await self.android_controller.execute_command(
            command=task.parameters.get("command")
        )
    
    async def start(self):
        """启动AI代理系统"""
        self.logger.info("启动羲和AI代理系统")
        
        # 启动任务调度器
        await self.task_scheduler.start()
        
        # 启动Android控制器
        await self.android_controller.start()
        
        self.logger.info("羲和AI代理系统启动完成")
    
    async def stop(self):
        """停止AI代理系统"""
        self.logger.info("停止羲和AI代理系统")
        
        await self.task_scheduler.stop()
        await self.android_controller.stop()
        
        self.logger.info("羲和AI代理系统已停止")