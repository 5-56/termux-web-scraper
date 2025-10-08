"""
自适应执行引擎
根据屏幕识别反馈动态调整和优化自动化代码，实现完美的任务执行
"""

import asyncio
import logging
import time
import json
import ast
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re


class ExecutionStrategy(Enum):
    """执行策略枚举"""
    CONSERVATIVE = "conservative"    # 保守策略，优先稳定性
    AGGRESSIVE = "aggressive"       # 激进策略，优先速度
    ADAPTIVE = "adaptive"          # 自适应策略，根据反馈调整
    LEARNING = "learning"          # 学习策略，基于历史经验


class AdjustmentAction(Enum):
    """调整动作枚举"""
    MODIFY_COORDINATES = "modify_coordinates"
    ADJUST_TIMING = "adjust_timing"
    CHANGE_STRATEGY = "change_strategy"
    ADD_RETRY = "add_retry"
    SKIP_STEP = "skip_step"
    REPLACE_STEP = "replace_step"


@dataclass
class ExecutionContext:
    """执行上下文"""
    task_id: str
    step_id: str
    original_code: str
    current_code: str
    feedback_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    adjustment_count: int = 0
    max_adjustments: int = 5


@dataclass
class CodeAdjustment:
    """代码调整"""
    action: AdjustmentAction
    description: str
    old_code: str
    new_code: str
    confidence: float
    reason: str


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    message: str
    final_code: str
    adjustments_made: List[CodeAdjustment]
    performance_improvement: float
    execution_time: float


class AdaptiveExecutionEngine:
    """自适应执行引擎"""
    
    def __init__(self, config_manager, screen_feedback_system, code_generator):
        """
        初始化自适应执行引擎
        
        Args:
            config_manager: 配置管理器
            screen_feedback_system: 屏幕反馈系统
            code_generator: 代码生成器
        """
        self.config = config_manager
        self.screen_feedback = screen_feedback_system
        self.code_generator = code_generator
        self.logger = logging.getLogger("AdaptiveExecution")
        
        # 执行策略
        self.execution_strategy = ExecutionStrategy.ADAPTIVE
        self.max_retries = config_manager.get("adaptive_execution.max_retries", 3)
        self.learning_enabled = config_manager.get("adaptive_execution.learning_enabled", True)
        
        # 代码调整规则
        self.adjustment_rules = [
            self._adjust_coordinates,
            self._adjust_timing,
            self._adjust_retry_logic,
            self._adjust_error_handling,
            self._adjust_element_detection
        ]
        
        # 学习数据
        self.learning_data = {
            "successful_patterns": {},
            "failed_patterns": {},
            "coordinate_adjustments": {},
            "timing_adjustments": {},
            "strategy_preferences": {}
        }
        
        self.logger.info("自适应执行引擎初始化完成")
    
    async def execute_with_adaptation(self, task_plan, generated_code: str) -> ExecutionResult:
        """
        执行任务并自适应调整
        
        Args:
            task_plan: 任务计划
            generated_code: 生成的代码
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"开始自适应执行任务: {task_plan.task_id}")
            
            start_time = time.time()
            current_code = generated_code
            adjustments_made = []
            
            # 创建执行上下文
            context = ExecutionContext(
                task_id=task_plan.task_id,
                step_id="main",
                original_code=generated_code,
                current_code=current_code,
                feedback_history=[],
                performance_metrics={}
            )
            
            # 执行任务步骤
            for step in task_plan.steps:
                step_result = await self._execute_step_with_adaptation(step, context)
                
                if step_result["success"]:
                    self.logger.info(f"步骤 {step.id} 执行成功")
                else:
                    self.logger.warning(f"步骤 {step.id} 执行失败，尝试调整")
                    
                    # 尝试调整代码
                    adjustment_result = await self._adjust_code_for_step(step, context, step_result)
                    
                    if adjustment_result:
                        adjustments_made.extend(adjustment_result["adjustments"])
                        current_code = adjustment_result["new_code"]
                        context.current_code = current_code
                        
                        # 重试执行
                        retry_result = await self._execute_step_with_adaptation(step, context)
                        if retry_result["success"]:
                            self.logger.info(f"步骤 {step.id} 调整后执行成功")
                        else:
                            self.logger.error(f"步骤 {step.id} 调整后仍然失败")
            
            # 计算性能改进
            execution_time = time.time() - start_time
            performance_improvement = self._calculate_performance_improvement(context)
            
            # 更新学习数据
            if self.learning_enabled:
                await self._update_learning_data(context, adjustments_made)
            
            result = ExecutionResult(
                success=True,
                message="任务执行完成",
                final_code=current_code,
                adjustments_made=adjustments_made,
                performance_improvement=performance_improvement,
                execution_time=execution_time
            )
            
            self.logger.info(f"自适应执行完成: {task_plan.task_id}, 调整次数: {len(adjustments_made)}")
            return result
            
        except Exception as e:
            self.logger.error(f"自适应执行失败: {e}")
            return ExecutionResult(
                success=False,
                message=f"执行失败: {e}",
                final_code=generated_code,
                adjustments_made=[],
                performance_improvement=0.0,
                execution_time=time.time() - start_time
            )
    
    async def _execute_step_with_adaptation(self, step, context: ExecutionContext) -> Dict[str, Any]:
        """执行单个步骤并收集反馈"""
        try:
            # 执行步骤
            execution_result = await self._execute_step(step, context)
            
            # 收集屏幕反馈
            feedback = await self.screen_feedback.monitor_execution(
                step.id, step.type.value, step.parameters
            )
            
            # 更新上下文
            context.feedback_history.append({
                "step_id": step.id,
                "feedback": asdict(feedback),
                "timestamp": time.time()
            })
            
            return {
                "success": feedback.feedback_type.value == "success",
                "feedback": feedback,
                "execution_result": execution_result
            }
            
        except Exception as e:
            self.logger.error(f"步骤执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "feedback": None
            }
    
    async def _execute_step(self, step, context: ExecutionContext) -> Dict[str, Any]:
        """执行单个步骤"""
        try:
            if step.type.value == "launch_app":
                app_name = step.parameters.get("app_name", "")
                result = await self.android_controller.launch_app(app_name)
                await asyncio.sleep(3)
                
            elif step.type.value == "tap":
                x, y = step.parameters.get("x", 0), step.parameters.get("y", 0)
                result = await self.android_controller.tap(x, y)
                await asyncio.sleep(1)
                
            elif step.type.value == "swipe":
                start_x = step.parameters.get("start_x", 0)
                start_y = step.parameters.get("start_y", 0)
                end_x = step.parameters.get("end_x", 0)
                end_y = step.parameters.get("end_y", 0)
                duration = step.parameters.get("duration", 300)
                result = await self.android_controller.swipe(start_x, start_y, end_x, end_y, duration)
                await asyncio.sleep(1)
                
            elif step.type.value == "input":
                text = step.parameters.get("text", "")
                result = await self.android_controller.input_text(text)
                await asyncio.sleep(1)
                
            else:
                result = False
            
            return {"success": result, "step_type": step.type.value}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _adjust_code_for_step(self, step, context: ExecutionContext, 
                                  step_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """为步骤调整代码"""
        try:
            if context.adjustment_count >= context.max_adjustments:
                self.logger.warning(f"步骤 {step.id} 已达到最大调整次数")
                return None
            
            adjustments = []
            new_code = context.current_code
            
            # 应用调整规则
            for rule in self.adjustment_rules:
                rule_adjustments = await rule(step, context, step_result)
                if rule_adjustments:
                    adjustments.extend(rule_adjustments)
                    
                    # 应用调整到代码
                    for adjustment in rule_adjustments:
                        new_code = self._apply_code_adjustment(new_code, adjustment)
            
            if adjustments:
                context.adjustment_count += 1
                return {
                    "adjustments": adjustments,
                    "new_code": new_code
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"代码调整失败: {e}")
            return None
    
    async def _adjust_coordinates(self, step, context: ExecutionContext, 
                                step_result: Dict[str, Any]) -> List[CodeAdjustment]:
        """调整坐标"""
        adjustments = []
        
        try:
            if step.type.value == "tap":
                feedback = step_result.get("feedback")
                if feedback and feedback.adjustments:
                    for adjustment in feedback.adjustments:
                        if adjustment.get("type") == "coordinate":
                            old_coords = adjustment.get("old_coordinates", (0, 0))
                            new_coords = adjustment.get("new_coordinates", (0, 0))
                            
                            # 生成坐标调整
                            old_code = f"await android_controller.tap({old_coords[0]}, {old_coords[1]})"
                            new_code = f"await android_controller.tap({new_coords[0]}, {new_coords[1]})"
                            
                            adjustments.append(CodeAdjustment(
                                action=AdjustmentAction.MODIFY_COORDINATES,
                                description=f"调整点击坐标: {old_coords} -> {new_coords}",
                                old_code=old_code,
                                new_code=new_code,
                                confidence=adjustment.get("confidence", 0.8),
                                reason="屏幕识别反馈建议"
                            ))
        
        except Exception as e:
            self.logger.error(f"坐标调整失败: {e}")
        
        return adjustments
    
    async def _adjust_timing(self, step, context: ExecutionContext, 
                           step_result: Dict[str, Any]) -> List[CodeAdjustment]:
        """调整时间"""
        adjustments = []
        
        try:
            feedback = step_result.get("feedback")
            if feedback and feedback.adjustments:
                for adjustment in feedback.adjustments:
                    if adjustment.get("type") == "timing":
                        wait_time = adjustment.get("suggestions", {}).get("wait_time", 1)
                        
                        # 查找等待时间代码
                        old_code = "await asyncio.sleep(1)"
                        new_code = f"await asyncio.sleep({wait_time})"
                        
                        adjustments.append(CodeAdjustment(
                            action=AdjustmentAction.ADJUST_TIMING,
                            description=f"调整等待时间: 1秒 -> {wait_time}秒",
                            old_code=old_code,
                            new_code=new_code,
                            confidence=0.7,
                            reason="性能反馈建议"
                        ))
        
        except Exception as e:
            self.logger.error(f"时间调整失败: {e}")
        
        return adjustments
    
    async def _adjust_retry_logic(self, step, context: ExecutionContext, 
                                step_result: Dict[str, Any]) -> List[CodeAdjustment]:
        """调整重试逻辑"""
        adjustments = []
        
        try:
            if not step_result.get("success", False):
                # 添加重试逻辑
                retry_code = """
                # 添加重试逻辑
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # 原始操作
                        {original_code}
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"尝试 {attempt + 1} 失败，重试中...")
                            await asyncio.sleep(2)
                        else:
                            raise e
                """
                
                adjustments.append(CodeAdjustment(
                    action=AdjustmentAction.ADD_RETRY,
                    description="添加重试逻辑",
                    old_code="",
                    new_code=retry_code,
                    confidence=0.8,
                    reason="执行失败需要重试"
                ))
        
        except Exception as e:
            self.logger.error(f"重试逻辑调整失败: {e}")
        
        return adjustments
    
    async def _adjust_error_handling(self, step, context: ExecutionContext, 
                                   step_result: Dict[str, Any]) -> List[CodeAdjustment]:
        """调整错误处理"""
        adjustments = []
        
        try:
            if not step_result.get("success", False):
                error = step_result.get("error", "")
                
                # 根据错误类型添加特定的错误处理
                if "timeout" in error.lower():
                    error_handling = """
                    try:
                        # 原始操作
                        {original_code}
                    except TimeoutError as e:
                        logger.warning(f"操作超时: {e}")
                        # 增加超时时间后重试
                        await asyncio.sleep(5)
                        # 重试操作
                        {original_code}
                    """
                elif "not found" in error.lower():
                    error_handling = """
                    try:
                        # 原始操作
                        {original_code}
                    except Exception as e:
                        logger.warning(f"元素未找到: {e}")
                        # 尝试通过OCR查找元素
                        elements = await screen_recognition.find_text("{target_text}")
                        if elements:
                            element = elements[0]
                            x, y = element.bbox[0] + element.bbox[2] // 2, element.bbox[1] + element.bbox[3] // 2
                            await android_controller.tap(x, y)
                        else:
                            raise e
                    """
                else:
                    error_handling = """
                    try:
                        # 原始操作
                        {original_code}
                    except Exception as e:
                        logger.error(f"操作失败: {e}")
                        # 截图保存错误状态
                        await android_controller.take_screenshot(f"screenshots/error_{int(time.time())}.png")
                        raise e
                    """
                
                adjustments.append(CodeAdjustment(
                    action=AdjustmentAction.REPLACE_STEP,
                    description="增强错误处理",
                    old_code="",
                    new_code=error_handling,
                    confidence=0.9,
                    reason=f"错误类型: {error}"
                ))
        
        except Exception as e:
            self.logger.error(f"错误处理调整失败: {e}")
        
        return adjustments
    
    async def _adjust_element_detection(self, step, context: ExecutionContext, 
                                      step_result: Dict[str, Any]) -> List[CodeAdjustment]:
        """调整元素检测"""
        adjustments = []
        
        try:
            feedback = step_result.get("feedback")
            if feedback and feedback.suggestions:
                for suggestion in feedback.suggestions:
                    if "检查元素是否存在" in suggestion:
                        # 添加元素存在性检查
                        element_check_code = """
                        # 检查元素是否存在
                        elements = await screen_recognition.detect_all_elements()
                        if not elements:
                            logger.warning("未检测到任何元素，等待页面加载")
                            await asyncio.sleep(3)
                            elements = await screen_recognition.detect_all_elements()
                        
                        if not elements:
                            raise Exception("页面加载失败，未检测到元素")
                        """
                        
                        adjustments.append(CodeAdjustment(
                            action=AdjustmentAction.REPLACE_STEP,
                            description="添加元素存在性检查",
                            old_code="",
                            new_code=element_check_code,
                            confidence=0.8,
                            reason="屏幕识别建议"
                        ))
        
        except Exception as e:
            self.logger.error(f"元素检测调整失败: {e}")
        
        return adjustments
    
    def _apply_code_adjustment(self, code: str, adjustment: CodeAdjustment) -> str:
        """应用代码调整"""
        try:
            if adjustment.action == AdjustmentAction.MODIFY_COORDINATES:
                # 替换坐标
                return code.replace(adjustment.old_code, adjustment.new_code)
            
            elif adjustment.action == AdjustmentAction.ADJUST_TIMING:
                # 替换等待时间
                return code.replace(adjustment.old_code, adjustment.new_code)
            
            elif adjustment.action == AdjustmentAction.ADD_RETRY:
                # 添加重试逻辑
                return adjustment.new_code.format(original_code=code)
            
            elif adjustment.action == AdjustmentAction.REPLACE_STEP:
                # 替换步骤
                return adjustment.new_code
            
            else:
                return code
                
        except Exception as e:
            self.logger.error(f"应用代码调整失败: {e}")
            return code
    
    def _calculate_performance_improvement(self, context: ExecutionContext) -> float:
        """计算性能改进"""
        try:
            if not context.feedback_history:
                return 0.0
            
            # 计算成功率改进
            success_count = len([f for f in context.feedback_history 
                               if f["feedback"]["feedback_type"] == "success"])
            total_count = len(context.feedback_history)
            success_rate = success_count / total_count if total_count > 0 else 0.0
            
            # 计算调整效果
            adjustment_effectiveness = 1.0 - (context.adjustment_count / context.max_adjustments)
            
            # 综合性能改进
            performance_improvement = (success_rate * 0.7 + adjustment_effectiveness * 0.3) * 100
            
            return performance_improvement
            
        except Exception as e:
            self.logger.error(f"计算性能改进失败: {e}")
            return 0.0
    
    async def _update_learning_data(self, context: ExecutionContext, 
                                  adjustments: List[CodeAdjustment]):
        """更新学习数据"""
        try:
            # 记录成功的模式
            if context.feedback_history:
                last_feedback = context.feedback_history[-1]["feedback"]
                if last_feedback["feedback_type"] == "success":
                    pattern_key = f"{context.step_id}_{last_feedback['message']}"
                    self.learning_data["successful_patterns"][pattern_key] = {
                        "code": context.current_code,
                        "adjustments": [asdict(adj) for adj in adjustments],
                        "timestamp": time.time()
                    }
            
            # 记录坐标调整
            for adjustment in adjustments:
                if adjustment.action == AdjustmentAction.MODIFY_COORDINATES:
                    coord_key = f"{context.step_id}_coordinates"
                    if coord_key not in self.learning_data["coordinate_adjustments"]:
                        self.learning_data["coordinate_adjustments"][coord_key] = []
                    
                    self.learning_data["coordinate_adjustments"][coord_key].append({
                        "old_coordinates": adjustment.old_code,
                        "new_coordinates": adjustment.new_code,
                        "confidence": adjustment.confidence,
                        "timestamp": time.time()
                    })
            
            # 记录时间调整
            for adjustment in adjustments:
                if adjustment.action == AdjustmentAction.ADJUST_TIMING:
                    timing_key = f"{context.step_id}_timing"
                    if timing_key not in self.learning_data["timing_adjustments"]:
                        self.learning_data["timing_adjustments"][timing_key] = []
                    
                    self.learning_data["timing_adjustments"][timing_key].append({
                        "old_timing": adjustment.old_code,
                        "new_timing": adjustment.new_code,
                        "confidence": adjustment.confidence,
                        "timestamp": time.time()
                    })
            
            # 保存学习数据
            await self._save_learning_data()
            
        except Exception as e:
            self.logger.error(f"更新学习数据失败: {e}")
    
    async def _save_learning_data(self):
        """保存学习数据"""
        try:
            learning_file = "data/learning_data.json"
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info("学习数据已保存")
            
        except Exception as e:
            self.logger.error(f"保存学习数据失败: {e}")
    
    async def load_learning_data(self):
        """加载学习数据"""
        try:
            learning_file = "data/learning_data.json"
            with open(learning_file, 'r', encoding='utf-8') as f:
                self.learning_data = json.load(f)
            
            self.logger.info("学习数据已加载")
            
        except FileNotFoundError:
            self.logger.info("学习数据文件不存在，使用默认数据")
        except Exception as e:
            self.logger.error(f"加载学习数据失败: {e}")
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """获取学习摘要"""
        try:
            return {
                "successful_patterns_count": len(self.learning_data["successful_patterns"]),
                "coordinate_adjustments_count": len(self.learning_data["coordinate_adjustments"]),
                "timing_adjustments_count": len(self.learning_data["timing_adjustments"]),
                "total_learning_data": sum(len(v) for v in self.learning_data.values() if isinstance(v, dict))
            }
            
        except Exception as e:
            self.logger.error(f"获取学习摘要失败: {e}")
            return {}