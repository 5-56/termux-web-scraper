"""
屏幕识别反馈系统
监控自动化任务执行过程，通过屏幕识别提供实时反馈和调整建议
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import cv2
import numpy as np
from PIL import Image
import pytesseract


class FeedbackType(Enum):
    """反馈类型枚举"""
    SUCCESS = "success"          # 执行成功
    FAILURE = "failure"          # 执行失败
    ADJUSTMENT = "adjustment"     # 需要调整
    WARNING = "warning"          # 警告
    INFO = "info"                # 信息


class AdjustmentType(Enum):
    """调整类型枚举"""
    COORDINATE = "coordinate"     # 坐标调整
    TIMING = "timing"            # 时间调整
    ELEMENT = "element"          # 元素调整
    STRATEGY = "strategy"        # 策略调整


@dataclass
class ScreenAnalysis:
    """屏幕分析结果"""
    timestamp: float
    screenshot_path: str
    elements: List[Dict[str, Any]]
    text_content: str
    ui_state: str
    loading_state: bool
    error_indicators: List[str]
    success_indicators: List[str]


@dataclass
class ExecutionFeedback:
    """执行反馈"""
    step_id: str
    feedback_type: FeedbackType
    message: str
    confidence: float
    adjustments: List[Dict[str, Any]] = None
    suggestions: List[str] = None
    screenshot_path: str = None


@dataclass
class PerformanceMetrics:
    """性能指标"""
    step_duration: float
    success_rate: float
    error_count: int
    retry_count: int
    accuracy_score: float


class ScreenFeedbackSystem:
    """屏幕识别反馈系统"""
    
    def __init__(self, android_controller, screen_recognition):
        """
        初始化屏幕反馈系统
        
        Args:
            android_controller: Android控制器
            screen_recognition: 屏幕识别器
        """
        self.android_controller = android_controller
        self.screen_recognition = screen_recognition
        self.logger = logging.getLogger("ScreenFeedback")
        
        # 反馈历史
        self.feedback_history: List[ExecutionFeedback] = []
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        
        # 屏幕状态缓存
        self.last_screen_analysis: Optional[ScreenAnalysis] = None
        self.screen_change_threshold = 0.1  # 屏幕变化阈值
        
        # 错误模式识别
        self.error_patterns = {
            "loading": ["加载中", "loading", "请稍候", "waiting"],
            "error": ["错误", "error", "失败", "failed", "无法", "不能"],
            "success": ["成功", "success", "完成", "完成", "ok", "确定"],
            "warning": ["警告", "warning", "注意", "caution", "提醒"]
        }
        
        # 成功模式识别
        self.success_patterns = {
            "app_launched": ["主界面", "首页", "home", "main"],
            "message_sent": ["已发送", "sent", "发送成功"],
            "video_playing": ["播放", "playing", "视频"],
            "page_loaded": ["内容", "content", "数据"]
        }
        
        self.logger.info("屏幕反馈系统初始化完成")
    
    async def monitor_execution(self, step_id: str, step_type: str, 
                              parameters: Dict[str, Any]) -> ExecutionFeedback:
        """
        监控执行过程
        
        Args:
            step_id: 步骤ID
            step_type: 步骤类型
            parameters: 步骤参数
            
        Returns:
            执行反馈
        """
        try:
            self.logger.info(f"开始监控步骤执行: {step_id}")
            
            # 1. 执行前屏幕分析
            pre_analysis = await self._analyze_screen_before_execution(step_id)
            
            # 2. 执行步骤
            execution_result = await self._execute_step_with_monitoring(step_id, step_type, parameters)
            
            # 3. 执行后屏幕分析
            post_analysis = await self._analyze_screen_after_execution(step_id)
            
            # 4. 生成反馈
            feedback = await self._generate_feedback(step_id, step_type, parameters, 
                                                   pre_analysis, post_analysis, execution_result)
            
            # 5. 记录反馈
            self.feedback_history.append(feedback)
            
            # 6. 更新性能指标
            self._update_performance_metrics(step_id, feedback)
            
            self.logger.info(f"步骤监控完成: {step_id}, 反馈类型: {feedback.feedback_type.value}")
            return feedback
            
        except Exception as e:
            self.logger.error(f"步骤监控失败: {e}")
            return ExecutionFeedback(
                step_id=step_id,
                feedback_type=FeedbackType.FAILURE,
                message=f"监控失败: {e}",
                confidence=0.0
            )
    
    async def _analyze_screen_before_execution(self, step_id: str) -> ScreenAnalysis:
        """执行前屏幕分析"""
        try:
            # 截取屏幕
            screenshot_path = await self.android_controller.take_screenshot()
            
            # 检测UI元素
            elements = await self.screen_recognition.detect_all_elements()
            
            # OCR识别文本
            text_content = await self._extract_text_content()
            
            # 分析UI状态
            ui_state = await self._analyze_ui_state(elements, text_content)
            
            # 检测加载状态
            loading_state = await self._detect_loading_state(text_content)
            
            # 检测错误指示器
            error_indicators = await self._detect_error_indicators(text_content)
            
            # 检测成功指示器
            success_indicators = await self._detect_success_indicators(text_content)
            
            analysis = ScreenAnalysis(
                timestamp=time.time(),
                screenshot_path=screenshot_path,
                elements=elements,
                text_content=text_content,
                ui_state=ui_state,
                loading_state=loading_state,
                error_indicators=error_indicators,
                success_indicators=success_indicators
            )
            
            self.last_screen_analysis = analysis
            return analysis
            
        except Exception as e:
            self.logger.error(f"执行前屏幕分析失败: {e}")
            return ScreenAnalysis(
                timestamp=time.time(),
                screenshot_path="",
                elements=[],
                text_content="",
                ui_state="unknown",
                loading_state=False,
                error_indicators=[],
                success_indicators=[]
            )
    
    async def _analyze_screen_after_execution(self, step_id: str) -> ScreenAnalysis:
        """执行后屏幕分析"""
        try:
            # 等待屏幕稳定
            await asyncio.sleep(1)
            
            # 截取屏幕
            screenshot_path = await self.android_controller.take_screenshot()
            
            # 检测UI元素
            elements = await self.screen_recognition.detect_all_elements()
            
            # OCR识别文本
            text_content = await self._extract_text_content()
            
            # 分析UI状态
            ui_state = await self._analyze_ui_state(elements, text_content)
            
            # 检测加载状态
            loading_state = await self._detect_loading_state(text_content)
            
            # 检测错误指示器
            error_indicators = await self._detect_error_indicators(text_content)
            
            # 检测成功指示器
            success_indicators = await self._detect_success_indicators(text_content)
            
            analysis = ScreenAnalysis(
                timestamp=time.time(),
                screenshot_path=screenshot_path,
                elements=elements,
                text_content=text_content,
                ui_state=ui_state,
                loading_state=loading_state,
                error_indicators=error_indicators,
                success_indicators=success_indicators
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"执行后屏幕分析失败: {e}")
            return ScreenAnalysis(
                timestamp=time.time(),
                screenshot_path="",
                elements=[],
                text_content="",
                ui_state="unknown",
                loading_state=False,
                error_indicators=[],
                success_indicators=[]
            )
    
    async def _execute_step_with_monitoring(self, step_id: str, step_type: str, 
                                          parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行步骤并监控"""
        start_time = time.time()
        
        try:
            if step_type == "tap":
                x, y = parameters.get("x", 0), parameters.get("y", 0)
                result = await self.android_controller.tap(x, y)
            elif step_type == "swipe":
                start_x, start_y = parameters.get("start_x", 0), parameters.get("start_y", 0)
                end_x, end_y = parameters.get("end_x", 0), parameters.get("end_y", 0)
                duration = parameters.get("duration", 300)
                result = await self.android_controller.swipe(start_x, start_y, end_x, end_y, duration)
            elif step_type == "input":
                text = parameters.get("text", "")
                result = await self.android_controller.input_text(text)
            elif step_type == "launch_app":
                app_name = parameters.get("app_name", "")
                result = await self.android_controller.launch_app(app_name)
            else:
                result = False
            
            duration = time.time() - start_time
            
            return {
                "success": result,
                "duration": duration,
                "step_type": step_type,
                "parameters": parameters
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "duration": duration,
                "step_type": step_type,
                "parameters": parameters
            }
    
    async def _generate_feedback(self, step_id: str, step_type: str, parameters: Dict[str, Any],
                               pre_analysis: ScreenAnalysis, post_analysis: ScreenAnalysis,
                               execution_result: Dict[str, Any]) -> ExecutionFeedback:
        """生成执行反馈"""
        try:
            # 基础反馈信息
            feedback_type = FeedbackType.SUCCESS
            message = "步骤执行成功"
            confidence = 1.0
            adjustments = []
            suggestions = []
            
            # 检查执行结果
            if not execution_result.get("success", False):
                feedback_type = FeedbackType.FAILURE
                message = f"步骤执行失败: {execution_result.get('error', '未知错误')}"
                confidence = 0.0
                
                # 生成调整建议
                adjustments = await self._generate_adjustments(step_type, parameters, 
                                                            pre_analysis, post_analysis, execution_result)
                suggestions = await self._generate_suggestions(step_type, parameters, 
                                                            pre_analysis, post_analysis, execution_result)
            
            # 检查屏幕变化
            elif await self._detect_screen_changes(pre_analysis, post_analysis):
                feedback_type = FeedbackType.ADJUSTMENT
                message = "检测到屏幕变化，可能需要调整"
                confidence = 0.7
                
                # 生成坐标调整建议
                coordinate_adjustments = await self._suggest_coordinate_adjustments(
                    step_type, parameters, pre_analysis, post_analysis
                )
                adjustments.extend(coordinate_adjustments)
            
            # 检查错误指示器
            elif post_analysis.error_indicators:
                feedback_type = FeedbackType.WARNING
                message = f"检测到错误指示器: {', '.join(post_analysis.error_indicators)}"
                confidence = 0.8
                
                # 生成错误处理建议
                error_suggestions = await self._generate_error_handling_suggestions(
                    post_analysis.error_indicators
                )
                suggestions.extend(error_suggestions)
            
            # 检查成功指示器
            elif post_analysis.success_indicators:
                feedback_type = FeedbackType.SUCCESS
                message = f"检测到成功指示器: {', '.join(post_analysis.success_indicators)}"
                confidence = 0.9
            
            # 检查加载状态
            elif post_analysis.loading_state:
                feedback_type = FeedbackType.INFO
                message = "检测到加载状态，建议等待"
                confidence = 0.6
                
                # 生成等待时间建议
                timing_adjustments = await self._suggest_timing_adjustments(
                    step_type, parameters, execution_result
                )
                adjustments.extend(timing_adjustments)
            
            return ExecutionFeedback(
                step_id=step_id,
                feedback_type=feedback_type,
                message=message,
                confidence=confidence,
                adjustments=adjustments,
                suggestions=suggestions,
                screenshot_path=post_analysis.screenshot_path
            )
            
        except Exception as e:
            self.logger.error(f"生成反馈失败: {e}")
            return ExecutionFeedback(
                step_id=step_id,
                feedback_type=FeedbackType.FAILURE,
                message=f"反馈生成失败: {e}",
                confidence=0.0
            )
    
    async def _extract_text_content(self) -> str:
        """提取屏幕文本内容"""
        try:
            ocr_results = await self.screen_recognition.detect_text()
            text_content = " ".join([result.text for result in ocr_results])
            return text_content
        except Exception as e:
            self.logger.error(f"文本提取失败: {e}")
            return ""
    
    async def _analyze_ui_state(self, elements: List[Dict[str, Any]], text_content: str) -> str:
        """分析UI状态"""
        try:
            # 统计元素类型
            element_types = {}
            for element in elements:
                element_type = element.get("type", "unknown")
                element_types[element_type] = element_types.get(element_type, 0) + 1
            
            # 根据元素类型判断UI状态
            if element_types.get("button", 0) > 5:
                return "main_interface"
            elif element_types.get("input", 0) > 0:
                return "input_interface"
            elif element_types.get("list", 0) > 0:
                return "list_interface"
            elif "登录" in text_content or "login" in text_content.lower():
                return "login_interface"
            elif "错误" in text_content or "error" in text_content.lower():
                return "error_interface"
            else:
                return "unknown_interface"
                
        except Exception as e:
            self.logger.error(f"UI状态分析失败: {e}")
            return "unknown"
    
    async def _detect_loading_state(self, text_content: str) -> bool:
        """检测加载状态"""
        loading_indicators = ["加载中", "loading", "请稍候", "waiting", "处理中", "processing"]
        return any(indicator in text_content.lower() for indicator in loading_indicators)
    
    async def _detect_error_indicators(self, text_content: str) -> List[str]:
        """检测错误指示器"""
        error_indicators = []
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern in text_content.lower():
                    error_indicators.append(f"{category}: {pattern}")
        return error_indicators
    
    async def _detect_success_indicators(self, text_content: str) -> List[str]:
        """检测成功指示器"""
        success_indicators = []
        for category, patterns in self.success_patterns.items():
            for pattern in patterns:
                if pattern in text_content.lower():
                    success_indicators.append(f"{category}: {pattern}")
        return success_indicators
    
    async def _detect_screen_changes(self, pre_analysis: ScreenAnalysis, 
                                   post_analysis: ScreenAnalysis) -> bool:
        """检测屏幕变化"""
        try:
            # 比较元素数量
            pre_element_count = len(pre_analysis.elements)
            post_element_count = len(post_analysis.elements)
            
            # 比较文本内容
            pre_text = pre_analysis.text_content
            post_text = post_analysis.text_content
            
            # 计算变化率
            element_change_rate = abs(post_element_count - pre_element_count) / max(pre_element_count, 1)
            text_change_rate = self._calculate_text_similarity(pre_text, post_text)
            
            # 判断是否有显著变化
            return element_change_rate > self.screen_change_threshold or text_change_rate < 0.8
            
        except Exception as e:
            self.logger.error(f"屏幕变化检测失败: {e}")
            return False
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 简单的Jaccard相似度
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _generate_adjustments(self, step_type: str, parameters: Dict[str, Any],
                                  pre_analysis: ScreenAnalysis, post_analysis: ScreenAnalysis,
                                  execution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成调整建议"""
        adjustments = []
        
        try:
            if step_type == "tap":
                # 坐标调整建议
                coordinate_adjustments = await self._suggest_coordinate_adjustments(
                    step_type, parameters, pre_analysis, post_analysis
                )
                adjustments.extend(coordinate_adjustments)
            
            elif step_type == "swipe":
                # 滑动参数调整建议
                swipe_adjustments = await self._suggest_swipe_adjustments(
                    step_type, parameters, pre_analysis, post_analysis
                )
                adjustments.extend(swipe_adjustments)
            
            elif step_type == "input":
                # 输入调整建议
                input_adjustments = await self._suggest_input_adjustments(
                    step_type, parameters, pre_analysis, post_analysis
                )
                adjustments.extend(input_adjustments)
            
            # 时间调整建议
            timing_adjustments = await self._suggest_timing_adjustments(
                step_type, parameters, execution_result
            )
            adjustments.extend(timing_adjustments)
            
        except Exception as e:
            self.logger.error(f"生成调整建议失败: {e}")
        
        return adjustments
    
    async def _suggest_coordinate_adjustments(self, step_type: str, parameters: Dict[str, Any],
                                            pre_analysis: ScreenAnalysis, 
                                            post_analysis: ScreenAnalysis) -> List[Dict[str, Any]]:
        """建议坐标调整"""
        adjustments = []
        
        try:
            if step_type == "tap":
                original_x = parameters.get("x", 0)
                original_y = parameters.get("y", 0)
                
                # 查找附近的按钮或可点击元素
                nearby_elements = []
                for element in post_analysis.elements:
                    if element.get("clickable", False):
                        bbox = element.get("bbox", [0, 0, 0, 0])
                        element_x = bbox[0] + bbox[2] // 2
                        element_y = bbox[1] + bbox[3] // 2
                        
                        distance = ((element_x - original_x) ** 2 + (element_y - original_y) ** 2) ** 0.5
                        if distance < 100:  # 100像素范围内
                            nearby_elements.append({
                                "element": element,
                                "x": element_x,
                                "y": element_y,
                                "distance": distance
                            })
                
                # 按距离排序，选择最近的元素
                nearby_elements.sort(key=lambda x: x["distance"])
                
                if nearby_elements:
                    best_element = nearby_elements[0]
                    adjustments.append({
                        "type": "coordinate",
                        "description": f"建议点击坐标调整为 ({best_element['x']}, {best_element['y']})",
                        "old_coordinates": (original_x, original_y),
                        "new_coordinates": (best_element["x"], best_element["y"]),
                        "confidence": 0.8
                    })
        
        except Exception as e:
            self.logger.error(f"坐标调整建议失败: {e}")
        
        return adjustments
    
    async def _suggest_swipe_adjustments(self, step_type: str, parameters: Dict[str, Any],
                                       pre_analysis: ScreenAnalysis, 
                                       post_analysis: ScreenAnalysis) -> List[Dict[str, Any]]:
        """建议滑动调整"""
        adjustments = []
        
        try:
            # 根据屏幕内容调整滑动参数
            if "视频" in post_analysis.text_content or "video" in post_analysis.text_content.lower():
                adjustments.append({
                    "type": "swipe",
                    "description": "检测到视频内容，建议调整滑动参数",
                    "suggestions": {
                        "duration": 300,
                        "start_y": 800,
                        "end_y": 200
                    }
                })
        
        except Exception as e:
            self.logger.error(f"滑动调整建议失败: {e}")
        
        return adjustments
    
    async def _suggest_input_adjustments(self, step_type: str, parameters: Dict[str, Any],
                                       pre_analysis: ScreenAnalysis, 
                                       post_analysis: ScreenAnalysis) -> List[Dict[str, Any]]:
        """建议输入调整"""
        adjustments = []
        
        try:
            # 检查输入框是否获得焦点
            input_elements = [e for e in post_analysis.elements if e.get("type") == "input"]
            if not input_elements:
                adjustments.append({
                    "type": "input",
                    "description": "未检测到输入框，建议先点击输入区域",
                    "suggestions": ["先点击输入框", "检查输入框位置"]
                })
        
        except Exception as e:
            self.logger.error(f"输入调整建议失败: {e}")
        
        return adjustments
    
    async def _suggest_timing_adjustments(self, step_type: str, parameters: Dict[str, Any],
                                        execution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """建议时间调整"""
        adjustments = []
        
        try:
            duration = execution_result.get("duration", 0)
            
            # 根据执行时间建议调整等待时间
            if duration > 5:
                adjustments.append({
                    "type": "timing",
                    "description": f"执行时间较长 ({duration:.2f}秒)，建议增加等待时间",
                    "suggestions": {
                        "wait_time": min(duration + 2, 10)
                    }
                })
            elif duration < 0.5:
                adjustments.append({
                    "type": "timing",
                    "description": f"执行时间较短 ({duration:.2f}秒)，建议减少等待时间",
                    "suggestions": {
                        "wait_time": max(duration + 1, 1)
                    }
                })
        
        except Exception as e:
            self.logger.error(f"时间调整建议失败: {e}")
        
        return adjustments
    
    async def _generate_suggestions(self, step_type: str, parameters: Dict[str, Any],
                                  pre_analysis: ScreenAnalysis, post_analysis: ScreenAnalysis,
                                  execution_result: Dict[str, Any]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        try:
            # 根据错误类型生成建议
            if not execution_result.get("success", False):
                error = execution_result.get("error", "")
                
                if "timeout" in error.lower():
                    suggestions.append("增加超时时间")
                elif "not found" in error.lower():
                    suggestions.append("检查元素是否存在")
                elif "permission" in error.lower():
                    suggestions.append("检查权限设置")
                else:
                    suggestions.append("检查网络连接和设备状态")
            
            # 根据屏幕状态生成建议
            if post_analysis.loading_state:
                suggestions.append("等待加载完成")
            
            if post_analysis.error_indicators:
                suggestions.append("处理错误提示")
            
            if post_analysis.ui_state == "login_interface":
                suggestions.append("检查登录状态")
            
        except Exception as e:
            self.logger.error(f"生成建议失败: {e}")
        
        return suggestions
    
    async def _generate_error_handling_suggestions(self, error_indicators: List[str]) -> List[str]:
        """生成错误处理建议"""
        suggestions = []
        
        for indicator in error_indicators:
            if "loading" in indicator.lower():
                suggestions.append("等待加载完成")
            elif "error" in indicator.lower():
                suggestions.append("检查错误信息并重试")
            elif "warning" in indicator.lower():
                suggestions.append("注意警告信息")
        
        return suggestions
    
    def _update_performance_metrics(self, step_id: str, feedback: ExecutionFeedback):
        """更新性能指标"""
        try:
            if step_id not in self.performance_metrics:
                self.performance_metrics[step_id] = PerformanceMetrics(
                    step_duration=0.0,
                    success_rate=0.0,
                    error_count=0,
                    retry_count=0,
                    accuracy_score=0.0
                )
            
            metrics = self.performance_metrics[step_id]
            
            # 更新成功率
            if feedback.feedback_type == FeedbackType.SUCCESS:
                metrics.success_rate = min(metrics.success_rate + 0.1, 1.0)
            else:
                metrics.success_rate = max(metrics.success_rate - 0.1, 0.0)
                metrics.error_count += 1
            
            # 更新准确度分数
            metrics.accuracy_score = feedback.confidence
            
            # 更新重试次数
            if feedback.feedback_type == FeedbackType.FAILURE:
                metrics.retry_count += 1
            
        except Exception as e:
            self.logger.error(f"更新性能指标失败: {e}")
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """获取反馈摘要"""
        try:
            total_feedback = len(self.feedback_history)
            success_count = len([f for f in self.feedback_history if f.feedback_type == FeedbackType.SUCCESS])
            failure_count = len([f for f in self.feedback_history if f.feedback_type == FeedbackType.FAILURE])
            adjustment_count = len([f for f in self.feedback_history if f.feedback_type == FeedbackType.ADJUSTMENT])
            
            return {
                "total_feedback": total_feedback,
                "success_count": success_count,
                "failure_count": failure_count,
                "adjustment_count": adjustment_count,
                "success_rate": success_count / total_feedback if total_feedback > 0 else 0,
                "performance_metrics": {k: asdict(v) for k, v in self.performance_metrics.items()}
            }
            
        except Exception as e:
            self.logger.error(f"获取反馈摘要失败: {e}")
            return {}
    
    def clear_feedback_history(self):
        """清空反馈历史"""
        self.feedback_history.clear()
        self.performance_metrics.clear()
        self.logger.info("反馈历史已清空")