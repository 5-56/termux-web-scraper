"""
智能执行引擎
整合AI规划、代码生成、屏幕识别反馈、自适应执行和学习系统
实现完美的自动化任务执行
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import traceback


class ExecutionPhase(Enum):
    """执行阶段枚举"""
    PLANNING = "planning"           # 规划阶段
    CODE_GENERATION = "code_generation"  # 代码生成阶段
    EXECUTION = "execution"         # 执行阶段
    ADAPTATION = "adaptation"       # 适应阶段
    LEARNING = "learning"          # 学习阶段
    COMPLETION = "completion"       # 完成阶段


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "pending"             # 等待中
    RUNNING = "running"             # 运行中
    ADAPTING = "adapting"           # 适应中
    SUCCESS = "success"             # 成功
    FAILED = "failed"               # 失败
    CANCELLED = "cancelled"         # 已取消


@dataclass
class ExecutionContext:
    """执行上下文"""
    task_id: str
    original_command: str
    current_phase: ExecutionPhase
    status: ExecutionStatus
    start_time: float
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    iterations: int = 0
    max_iterations: int = 5


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    message: str
    execution_time: float
    iterations: int
    adaptations_made: int
    learning_insights: List[str]
    final_code: str
    performance_metrics: Dict[str, Any]


class SmartExecutionEngine:
    """智能执行引擎"""
    
    def __init__(self, config_manager, android_controller, screen_recognition):
        """
        初始化智能执行引擎
        
        Args:
            config_manager: 配置管理器
            android_controller: Android控制器
            screen_recognition: 屏幕识别器
        """
        self.config = config_manager
        self.android_controller = android_controller
        self.screen_recognition = screen_recognition
        self.logger = logging.getLogger("SmartExecutionEngine")
        
        # 初始化各个模块
        from .ai_planner import AIPlanner
        from .code_generator import CodeGenerator
        from .screen_feedback import ScreenFeedbackSystem
        from .adaptive_execution import AdaptiveExecutionEngine
        from .learning_system import LearningSystem
        
        self.ai_planner = AIPlanner(config_manager)
        self.code_generator = CodeGenerator(config_manager)
        self.screen_feedback = ScreenFeedbackSystem(android_controller, screen_recognition)
        self.adaptive_execution = AdaptiveExecutionEngine(config_manager, self.screen_feedback, self.code_generator)
        self.learning_system = LearningSystem(config_manager)
        
        # 执行配置
        self.max_iterations = config_manager.get("smart_execution.max_iterations", 5)
        self.adaptation_threshold = config_manager.get("smart_execution.adaptation_threshold", 0.7)
        self.learning_enabled = config_manager.get("smart_execution.learning_enabled", True)
        
        # 执行历史
        self.execution_history: List[ExecutionContext] = []
        self.active_executions: Dict[str, ExecutionContext] = {}
        
        self.logger.info("智能执行引擎初始化完成")
    
    async def execute_task(self, command: str, context: Dict[str, Any] = None) -> ExecutionResult:
        """
        执行任务
        
        Args:
            command: 用户指令
            context: 上下文信息
            
        Returns:
            执行结果
        """
        task_id = f"task_{int(time.time())}"
        execution_context = ExecutionContext(
            task_id=task_id,
            original_command=command,
            current_phase=ExecutionPhase.PLANNING,
            status=ExecutionStatus.PENDING,
            start_time=time.time()
        )
        
        self.active_executions[task_id] = execution_context
        self.execution_history.append(execution_context)
        
        try:
            self.logger.info(f"开始执行任务: {command}")
            
            # 阶段1: AI规划
            execution_context.current_phase = ExecutionPhase.PLANNING
            execution_context.status = ExecutionStatus.RUNNING
            execution_context.progress = 10.0
            
            task_plan = await self.ai_planner.plan_task(command, context)
            self.logger.info(f"任务规划完成: {task_plan.task_id}")
            
            # 阶段2: 代码生成
            execution_context.current_phase = ExecutionPhase.CODE_GENERATION
            execution_context.progress = 20.0
            
            generated_code = self.code_generator.generate_code(task_plan)
            self.logger.info(f"代码生成完成: {len(generated_code.main_function)} 字符")
            
            # 阶段3: 自适应执行
            execution_context.current_phase = ExecutionPhase.EXECUTION
            execution_context.progress = 30.0
            
            execution_result = await self._execute_with_adaptation(task_plan, generated_code, execution_context)
            
            # 阶段4: 学习更新
            if self.learning_enabled and execution_result.success:
                execution_context.current_phase = ExecutionPhase.LEARNING
                execution_context.progress = 90.0
                
                await self.learning_system.learn_from_execution({
                    "task_id": task_id,
                    "command": command,
                    "success": execution_result.success,
                    "execution_time": execution_result.execution_time,
                    "adaptations_made": execution_result.adaptations_made,
                    "task_type": task_plan.complexity.value,
                    "app_name": self._extract_app_name(command)
                })
                
                self.logger.info("学习更新完成")
            
            # 阶段5: 完成
            execution_context.current_phase = ExecutionPhase.COMPLETION
            execution_context.status = ExecutionStatus.SUCCESS
            execution_context.progress = 100.0
            execution_context.end_time = time.time()
            
            # 生成学习洞察
            learning_insights = await self._generate_learning_insights(task_id)
            
            result = ExecutionResult(
                success=execution_result.success,
                message=execution_result.message,
                execution_time=execution_context.end_time - execution_context.start_time,
                iterations=execution_context.iterations,
                adaptations_made=execution_result.adaptations_made,
                learning_insights=learning_insights,
                final_code=execution_result.final_code,
                performance_metrics=self._calculate_performance_metrics(execution_context)
            )
            
            self.logger.info(f"任务执行完成: {task_id}, 成功: {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"任务执行失败: {e}")
            execution_context.status = ExecutionStatus.FAILED
            execution_context.error_message = str(e)
            execution_context.end_time = time.time()
            
            return ExecutionResult(
                success=False,
                message=f"执行失败: {e}",
                execution_time=execution_context.end_time - execution_context.start_time,
                iterations=execution_context.iterations,
                adaptations_made=0,
                learning_insights=[],
                final_code="",
                performance_metrics={}
            )
        
        finally:
            # 清理活跃执行
            if task_id in self.active_executions:
                del self.active_executions[task_id]
    
    async def _execute_with_adaptation(self, task_plan, generated_code, execution_context: ExecutionContext) -> ExecutionResult:
        """执行任务并自适应调整"""
        try:
            # 使用自适应执行引擎
            adaptive_result = await self.adaptive_execution.execute_with_adaptation(task_plan, generated_code.main_function)
            
            # 更新执行上下文
            execution_context.iterations += 1
            execution_context.progress = min(execution_context.progress + 50, 80.0)
            
            # 如果执行失败且还有迭代次数，尝试重新规划
            if not adaptive_result.success and execution_context.iterations < self.max_iterations:
                self.logger.info(f"执行失败，尝试重新规划 (迭代 {execution_context.iterations + 1}/{self.max_iterations})")
                
                # 获取优化建议
                suggestions = await self.learning_system.get_optimization_suggestions(
                    task_type=task_plan.complexity.value,
                    app_name=self._extract_app_name(task_plan.original_command)
                )
                
                if suggestions:
                    # 应用优化建议重新生成代码
                    optimized_code = await self._apply_optimization_suggestions(generated_code, suggestions)
                    adaptive_result = await self.adaptive_execution.execute_with_adaptation(task_plan, optimized_code)
                
                execution_context.iterations += 1
            
            return adaptive_result
            
        except Exception as e:
            self.logger.error(f"自适应执行失败: {e}")
            return ExecutionResult(
                success=False,
                message=f"自适应执行失败: {e}",
                execution_time=0,
                iterations=execution_context.iterations,
                adaptations_made=0,
                learning_insights=[],
                final_code="",
                performance_metrics={}
            )
    
    async def _apply_optimization_suggestions(self, generated_code, suggestions: List) -> str:
        """应用优化建议"""
        try:
            optimized_code = generated_code.main_function
            
            for suggestion in suggestions[:3]:  # 只应用前3个建议
                if suggestion.learning_type.value == "coordinate_optimization":
                    # 应用坐标优化
                    optimized_code = self._apply_coordinate_optimization(optimized_code, suggestion)
                elif suggestion.learning_type.value == "timing_optimization":
                    # 应用时间优化
                    optimized_code = self._apply_timing_optimization(optimized_code, suggestion)
                elif suggestion.learning_type.value == "error_prevention":
                    # 应用错误预防
                    optimized_code = self._apply_error_prevention(optimized_code, suggestion)
            
            return optimized_code
            
        except Exception as e:
            self.logger.error(f"应用优化建议失败: {e}")
            return generated_code.main_function
    
    def _apply_coordinate_optimization(self, code: str, suggestion) -> str:
        """应用坐标优化"""
        try:
            # 从建议中提取坐标信息
            description = suggestion.description
            if "使用" in description and "(" in description:
                # 提取坐标
                import re
                coord_match = re.search(r'\((\d+), (\d+)\)', description)
                if coord_match:
                    x, y = int(coord_match.group(1)), int(coord_match.group(2))
                    # 替换代码中的坐标
                    code = re.sub(r'android_controller\.tap\(\d+, \d+\)', 
                                f'android_controller.tap({x}, {y})', code)
            
            return code
            
        except Exception as e:
            self.logger.error(f"坐标优化应用失败: {e}")
            return code
    
    def _apply_timing_optimization(self, code: str, suggestion) -> str:
        """应用时间优化"""
        try:
            # 从建议中提取时间信息
            description = suggestion.description
            if "使用" in description and "秒" in description:
                import re
                time_match = re.search(r'(\d+\.?\d*)秒', description)
                if time_match:
                    wait_time = float(time_match.group(1))
                    # 替换代码中的等待时间
                    code = re.sub(r'await asyncio\.sleep\(\d+\.?\d*\)', 
                                f'await asyncio.sleep({wait_time})', code)
            
            return code
            
        except Exception as e:
            self.logger.error(f"时间优化应用失败: {e}")
            return code
    
    def _apply_error_prevention(self, code: str, suggestion) -> str:
        """应用错误预防"""
        try:
            # 添加错误预防代码
            error_prevention_code = """
            try:
                # 原始操作
                {original_code}
            except Exception as e:
                logger.warning(f"操作失败，尝试错误预防: {e}")
                # 等待后重试
                await asyncio.sleep(2)
                # 重新执行
                {original_code}
            """
            
            # 将原始代码包装在错误预防中
            return error_prevention_code.format(original_code=code)
            
        except Exception as e:
            self.logger.error(f"错误预防应用失败: {e}")
            return code
    
    async def _generate_learning_insights(self, task_id: str) -> List[str]:
        """生成学习洞察"""
        insights = []
        
        try:
            # 获取学习指标
            metrics = self.learning_system.get_learning_metrics()
            
            if metrics.total_patterns > 0:
                insights.append(f"系统已学习 {metrics.total_patterns} 个执行模式")
                insights.append(f"成功率: {metrics.learning_accuracy:.1%}")
                insights.append(f"平均置信度: {metrics.average_confidence:.2f}")
            
            # 获取优化建议
            suggestions = await self.learning_system.get_optimization_suggestions()
            if suggestions:
                insights.append(f"发现 {len(suggestions)} 个优化建议")
                insights.append(f"最高置信度建议: {suggestions[0].description}")
            
            # 获取执行历史统计
            recent_executions = [ctx for ctx in self.execution_history if ctx.task_id == task_id]
            if recent_executions:
                success_count = len([ctx for ctx in recent_executions if ctx.status == ExecutionStatus.SUCCESS])
                total_count = len(recent_executions)
                insights.append(f"本次执行成功率: {success_count}/{total_count}")
            
        except Exception as e:
            self.logger.error(f"生成学习洞察失败: {e}")
            insights.append("学习洞察生成失败")
        
        return insights
    
    def _calculate_performance_metrics(self, execution_context: ExecutionContext) -> Dict[str, Any]:
        """计算性能指标"""
        try:
            execution_time = execution_context.end_time - execution_context.start_time if execution_context.end_time else 0
            
            metrics = {
                "execution_time": execution_time,
                "iterations": execution_context.iterations,
                "success_rate": 1.0 if execution_context.status == ExecutionStatus.SUCCESS else 0.0,
                "efficiency": execution_context.progress / max(execution_time, 1),  # 进度/时间
                "adaptation_ratio": execution_context.iterations / self.max_iterations,
                "phase_distribution": {
                    "planning_time": 0.1 * execution_time,
                    "code_generation_time": 0.1 * execution_time,
                    "execution_time": 0.7 * execution_time,
                    "learning_time": 0.1 * execution_time
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"性能指标计算失败: {e}")
            return {}
    
    def _extract_app_name(self, command: str) -> str:
        """从命令中提取应用名称"""
        apps = ["抖音", "快手", "微信", "QQ", "淘宝", "支付宝", "浏览器"]
        for app in apps:
            if app in command:
                return app
        return "unknown"
    
    async def get_execution_status(self, task_id: str) -> Optional[ExecutionContext]:
        """获取执行状态"""
        return self.active_executions.get(task_id)
    
    async def cancel_execution(self, task_id: str) -> bool:
        """取消执行"""
        try:
            if task_id in self.active_executions:
                execution_context = self.active_executions[task_id]
                execution_context.status = ExecutionStatus.CANCELLED
                execution_context.end_time = time.time()
                
                del self.active_executions[task_id]
                self.logger.info(f"任务已取消: {task_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"取消执行失败: {e}")
            return False
    
    def get_execution_history(self, limit: int = 10) -> List[ExecutionContext]:
        """获取执行历史"""
        return self.execution_history[-limit:]
    
    def get_system_insights(self) -> Dict[str, Any]:
        """获取系统洞察"""
        try:
            # 执行统计
            total_executions = len(self.execution_history)
            successful_executions = len([ctx for ctx in self.execution_history if ctx.status == ExecutionStatus.SUCCESS])
            failed_executions = len([ctx for ctx in self.execution_history if ctx.status == ExecutionStatus.FAILED])
            
            # 学习指标
            learning_metrics = self.learning_system.get_learning_metrics()
            
            # 性能指标
            if self.execution_history:
                avg_execution_time = sum(
                    (ctx.end_time - ctx.start_time) for ctx in self.execution_history 
                    if ctx.end_time
                ) / len(self.execution_history)
            else:
                avg_execution_time = 0
            
            return {
                "execution_statistics": {
                    "total_executions": total_executions,
                    "successful_executions": successful_executions,
                    "failed_executions": failed_executions,
                    "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
                    "average_execution_time": avg_execution_time
                },
                "learning_metrics": asdict(learning_metrics),
                "active_executions": len(self.active_executions),
                "system_health": "healthy" if successful_executions > failed_executions else "needs_attention"
            }
            
        except Exception as e:
            self.logger.error(f"获取系统洞察失败: {e}")
            return {}
    
    async def optimize_system(self) -> Dict[str, Any]:
        """优化系统"""
        try:
            self.logger.info("开始系统优化")
            
            optimization_results = {}
            
            # 1. 清理过期的执行历史
            current_time = time.time()
            self.execution_history = [
                ctx for ctx in self.execution_history 
                if current_time - ctx.start_time < 86400  # 保留24小时内的历史
            ]
            optimization_results["cleaned_history"] = len(self.execution_history)
            
            # 2. 优化学习数据
            if self.learning_enabled:
                # 获取学习摘要
                learning_summary = self.learning_system.get_learning_summary()
                optimization_results["learning_optimization"] = learning_summary
            
            # 3. 清理临时文件
            import os
            temp_files = ["screenshots", "logs"]
            for temp_dir in temp_files:
                if os.path.exists(temp_dir):
                    # 清理超过7天的文件
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path):
                            file_age = current_time - os.path.getmtime(file_path)
                            if file_age > 604800:  # 7天
                                os.remove(file_path)
            
            optimization_results["temp_files_cleaned"] = True
            
            self.logger.info("系统优化完成")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"系统优化失败: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """关闭系统"""
        try:
            self.logger.info("正在关闭智能执行引擎")
            
            # 取消所有活跃执行
            for task_id in list(self.active_executions.keys()):
                await self.cancel_execution(task_id)
            
            # 保存学习数据
            if self.learning_enabled:
                await self.learning_system._save_learning_data()
            
            self.logger.info("智能执行引擎已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭系统失败: {e}")