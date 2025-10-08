"""
任务调度系统
支持定时任务、事件驱动任务、任务队列管理等功能
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from ..core.ai_agent import Task, TaskType


class ScheduleType(Enum):
    """调度类型枚举"""
    ONCE = "once"           # 执行一次
    INTERVAL = "interval"    # 间隔执行
    CRON = "cron"           # Cron表达式
    EVENT = "event"         # 事件驱动


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"     # 等待中
    RUNNING = "running"     # 运行中
    COMPLETED = "completed" # 已完成
    FAILED = "failed"       # 失败
    CANCELLED = "cancelled" # 已取消


@dataclass
class ScheduledTask:
    """调度任务"""
    id: str
    name: str
    task: Task
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        """执行时长(秒)"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, config_manager):
        """
        初始化任务调度器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger("TaskScheduler")
        
        # 任务存储
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.task_queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: List[TaskResult] = []
        
        # 调度器状态
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # 配置
        self.max_concurrent_tasks = config_manager.get("scheduler.max_concurrent_tasks", 5)
        self.task_timeout = config_manager.get("scheduler.task_timeout", 300)  # 5分钟
        self.cleanup_interval = config_manager.get("scheduler.cleanup_interval", 3600)  # 1小时
        
        self.logger.info("任务调度器初始化完成")
    
    async def start(self):
        """启动任务调度器"""
        if self.is_running:
            self.logger.warning("任务调度器已在运行")
            return
        
        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # 启动任务执行器
        for i in range(self.max_concurrent_tasks):
            asyncio.create_task(self._task_executor(f"executor-{i}"))
        
        # 启动清理任务
        asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("任务调度器启动成功")
    
    async def stop(self):
        """停止任务调度器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消调度器任务
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # 取消所有运行中的任务
        for task_id, task in self.running_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("任务调度器已停止")
    
    async def add_task(self, task: Task, schedule_type: ScheduleType, 
                      schedule_config: Dict[str, Any], name: str = None) -> str:
        """
        添加调度任务
        
        Args:
            task: 任务对象
            schedule_type: 调度类型
            schedule_config: 调度配置
            name: 任务名称
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        task_name = name or f"{task.type.value}_{task_id[:8]}"
        
        scheduled_task = ScheduledTask(
            id=task_id,
            name=task_name,
            task=task,
            schedule_type=schedule_type,
            schedule_config=schedule_config
        )
        
        # 计算下次执行时间
        scheduled_task.next_run = self._calculate_next_run(scheduled_task)
        
        self.scheduled_tasks[task_id] = scheduled_task
        
        self.logger.info(f"添加调度任务: {task_name} (ID: {task_id})")
        return task_id
    
    async def remove_task(self, task_id: str) -> bool:
        """
        移除调度任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功移除
        """
        if task_id not in self.scheduled_tasks:
            return False
        
        # 取消运行中的任务
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        # 移除调度任务
        del self.scheduled_tasks[task_id]
        
        self.logger.info(f"移除调度任务: {task_id}")
        return True
    
    async def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id not in self.scheduled_tasks:
            return False
        
        self.scheduled_tasks[task_id].enabled = True
        self.scheduled_tasks[task_id].next_run = self._calculate_next_run(self.scheduled_tasks[task_id])
        
        self.logger.info(f"启用任务: {task_id}")
        return True
    
    async def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id not in self.scheduled_tasks:
            return False
        
        self.scheduled_tasks[task_id].enabled = False
        self.scheduled_tasks[task_id].next_run = None
        
        # 取消运行中的任务
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        self.logger.info(f"禁用任务: {task_id}")
        return True
    
    async def trigger_task(self, task_id: str) -> bool:
        """
        立即触发任务执行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功触发
        """
        if task_id not in self.scheduled_tasks:
            return False
        
        scheduled_task = self.scheduled_tasks[task_id]
        if not scheduled_task.enabled:
            return False
        
        # 将任务加入队列
        await self.task_queue.put(scheduled_task)
        
        self.logger.info(f"触发任务执行: {task_id}")
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.scheduled_tasks:
            return None
        
        scheduled_task = self.scheduled_tasks[task_id]
        
        return {
            "id": scheduled_task.id,
            "name": scheduled_task.name,
            "status": scheduled_task.status.value,
            "enabled": scheduled_task.enabled,
            "created_at": scheduled_task.created_at.isoformat(),
            "last_run": scheduled_task.last_run.isoformat() if scheduled_task.last_run else None,
            "next_run": scheduled_task.next_run.isoformat() if scheduled_task.next_run else None,
            "run_count": scheduled_task.run_count,
            "max_runs": scheduled_task.max_runs
        }
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务状态"""
        return [self.get_task_status(task_id) for task_id in self.scheduled_tasks.keys()]
    
    def get_task_results(self, task_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取任务执行结果"""
        results = self.task_results
        
        if task_id:
            results = [r for r in results if r.task_id == task_id]
        
        # 按开始时间倒序排列
        results.sort(key=lambda x: x.start_time, reverse=True)
        
        # 限制返回数量
        results = results[:limit]
        
        return [{
            "task_id": r.task_id,
            "status": r.status.value,
            "start_time": r.start_time.isoformat(),
            "end_time": r.end_time.isoformat() if r.end_time else None,
            "duration": r.duration,
            "result": r.result,
            "error": r.error
        } for r in results]
    
    async def _scheduler_loop(self):
        """调度器主循环"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # 检查需要执行的任务
                for scheduled_task in self.scheduled_tasks.values():
                    if not scheduled_task.enabled:
                        continue
                    
                    if scheduled_task.next_run and current_time >= scheduled_task.next_run:
                        # 检查是否超过最大执行次数
                        if scheduled_task.max_runs and scheduled_task.run_count >= scheduled_task.max_runs:
                            scheduled_task.enabled = False
                            continue
                        
                        # 将任务加入队列
                        await self.task_queue.put(scheduled_task)
                        
                        # 更新下次执行时间
                        scheduled_task.next_run = self._calculate_next_run(scheduled_task)
                
                # 等待1秒后继续检查
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"调度器循环异常: {e}")
                await asyncio.sleep(5)
    
    async def _task_executor(self, executor_name: str):
        """任务执行器"""
        while self.is_running:
            try:
                # 从队列获取任务
                scheduled_task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # 检查任务是否已在运行
                if scheduled_task.id in self.running_tasks:
                    continue
                
                # 创建执行任务
                task_coroutine = self._execute_scheduled_task(scheduled_task)
                running_task = asyncio.create_task(task_coroutine)
                self.running_tasks[scheduled_task.id] = running_task
                
                # 等待任务完成
                try:
                    await asyncio.wait_for(running_task, timeout=self.task_timeout)
                except asyncio.TimeoutError:
                    self.logger.error(f"任务执行超时: {scheduled_task.id}")
                    running_task.cancel()
                except Exception as e:
                    self.logger.error(f"任务执行异常: {scheduled_task.id}, {e}")
                finally:
                    if scheduled_task.id in self.running_tasks:
                        del self.running_tasks[scheduled_task.id]
                
            except asyncio.TimeoutError:
                # 队列为空，继续等待
                continue
            except Exception as e:
                self.logger.error(f"任务执行器异常: {e}")
                await asyncio.sleep(1)
    
    async def _execute_scheduled_task(self, scheduled_task: ScheduledTask):
        """执行调度任务"""
        task_id = scheduled_task.id
        start_time = datetime.now()
        
        # 更新任务状态
        scheduled_task.status = TaskStatus.RUNNING
        scheduled_task.last_run = start_time
        scheduled_task.run_count += 1
        
        self.logger.info(f"开始执行任务: {scheduled_task.name} (ID: {task_id})")
        
        try:
            # 这里应该调用AI代理来执行任务
            # 简化实现，模拟任务执行
            await asyncio.sleep(1)  # 模拟执行时间
            
            result = {
                "success": True,
                "message": f"任务 {scheduled_task.name} 执行成功",
                "execution_time": 1.0
            }
            
            # 更新任务状态
            scheduled_task.status = TaskStatus.COMPLETED
            
            # 记录执行结果
            task_result = TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                start_time=start_time,
                end_time=datetime.now(),
                result=result
            )
            self.task_results.append(task_result)
            
            self.logger.info(f"任务执行完成: {scheduled_task.name} (ID: {task_id})")
            
        except Exception as e:
            # 更新任务状态
            scheduled_task.status = TaskStatus.FAILED
            
            # 记录执行结果
            task_result = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e)
            )
            self.task_results.append(task_result)
            
            self.logger.error(f"任务执行失败: {scheduled_task.name} (ID: {task_id}), 错误: {e}")
    
    def _calculate_next_run(self, scheduled_task: ScheduledTask) -> Optional[datetime]:
        """计算下次执行时间"""
        if not scheduled_task.enabled:
            return None
        
        current_time = datetime.now()
        schedule_type = scheduled_task.schedule_type
        config = scheduled_task.schedule_config
        
        if schedule_type == ScheduleType.ONCE:
            # 执行一次，如果已经执行过则不再执行
            if scheduled_task.run_count > 0:
                return None
            return current_time
        
        elif schedule_type == ScheduleType.INTERVAL:
            # 间隔执行
            interval_seconds = config.get("interval_seconds", 60)
            if scheduled_task.last_run:
                return scheduled_task.last_run + timedelta(seconds=interval_seconds)
            else:
                return current_time
        
        elif schedule_type == ScheduleType.CRON:
            # Cron表达式 (简化实现)
            cron_config = config.get("cron", "0 * * * *")  # 默认每小时执行
            # 这里应该解析Cron表达式，简化实现
            return current_time + timedelta(hours=1)
        
        elif schedule_type == ScheduleType.EVENT:
            # 事件驱动，不自动调度
            return None
        
        return None
    
    async def _cleanup_loop(self):
        """清理任务循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # 清理过期的执行结果
                cutoff_time = datetime.now() - timedelta(days=7)  # 保留7天
                self.task_results = [
                    r for r in self.task_results 
                    if r.start_time > cutoff_time
                ]
                
                # 清理已完成的任务 (如果配置了自动清理)
                auto_cleanup = self.config_manager.get("scheduler.auto_cleanup_completed", False)
                if auto_cleanup:
                    completed_tasks = [
                        task_id for task_id, task in self.scheduled_tasks.items()
                        if task.status == TaskStatus.COMPLETED and task.run_count > 0
                    ]
                    for task_id in completed_tasks:
                        await self.remove_task(task_id)
                
                self.logger.info("执行清理任务完成")
                
            except Exception as e:
                self.logger.error(f"清理任务异常: {e}")
    
    def create_interval_task(self, task: Task, interval_seconds: int, 
                           name: str = None, max_runs: int = None) -> str:
        """创建间隔执行任务"""
        config = {"interval_seconds": interval_seconds}
        if max_runs:
            config["max_runs"] = max_runs
        
        return asyncio.create_task(
            self.add_task(task, ScheduleType.INTERVAL, config, name)
        )
    
    def create_cron_task(self, task: Task, cron_expression: str, 
                        name: str = None) -> str:
        """创建Cron任务"""
        config = {"cron": cron_expression}
        return asyncio.create_task(
            self.add_task(task, ScheduleType.CRON, config, name)
        )
    
    def create_event_task(self, task: Task, name: str = None) -> str:
        """创建事件驱动任务"""
        config = {}
        return asyncio.create_task(
            self.add_task(task, ScheduleType.EVENT, config, name)
        )