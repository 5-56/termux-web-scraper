"""
学习系统
从执行经验中学习和改进，提供智能化的任务优化建议
"""

import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, Counter
import pickle
import os


class LearningType(Enum):
    """学习类型枚举"""
    PATTERN_RECOGNITION = "pattern_recognition"    # 模式识别
    COORDINATE_OPTIMIZATION = "coordinate_optimization"  # 坐标优化
    TIMING_OPTIMIZATION = "timing_optimization"    # 时间优化
    ERROR_PREVENTION = "error_prevention"         # 错误预防
    STRATEGY_SELECTION = "strategy_selection"     # 策略选择


class LearningAlgorithm(Enum):
    """学习算法枚举"""
    FREQUENCY_ANALYSIS = "frequency_analysis"     # 频率分析
    CLUSTERING = "clustering"                    # 聚类分析
    REGRESSION = "regression"                    # 回归分析
    CLASSIFICATION = "classification"            # 分类分析
    REINFORCEMENT = "reinforcement"              # 强化学习


@dataclass
class LearningPattern:
    """学习模式"""
    pattern_id: str
    pattern_type: str
    frequency: int
    success_rate: float
    confidence: float
    features: Dict[str, Any]
    examples: List[Dict[str, Any]]
    created_at: float
    last_updated: float


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_id: str
    learning_type: LearningType
    algorithm: LearningAlgorithm
    description: str
    confidence: float
    expected_improvement: float
    implementation: str
    prerequisites: List[str] = None


@dataclass
class LearningMetrics:
    """学习指标"""
    total_patterns: int
    successful_patterns: int
    failed_patterns: int
    average_confidence: float
    learning_accuracy: float
    improvement_rate: float
    last_learning_time: float


class LearningSystem:
    """学习系统"""
    
    def __init__(self, config_manager):
        """
        初始化学习系统
        
        Args:
            config_manager: 配置管理器
        """
        self.config = config_manager
        self.logger = logging.getLogger("LearningSystem")
        
        # 学习配置
        self.learning_enabled = config_manager.get("learning.enabled", True)
        self.min_pattern_frequency = config_manager.get("learning.min_pattern_frequency", 3)
        self.confidence_threshold = config_manager.get("learning.confidence_threshold", 0.7)
        self.learning_rate = config_manager.get("learning.learning_rate", 0.1)
        
        # 学习数据存储
        self.patterns: Dict[str, LearningPattern] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.optimization_suggestions: List[OptimizationSuggestion] = []
        
        # 学习算法
        self.algorithms = {
            LearningAlgorithm.FREQUENCY_ANALYSIS: self._frequency_analysis,
            LearningAlgorithm.CLUSTERING: self._clustering_analysis,
            LearningAlgorithm.REGRESSION: self._regression_analysis,
            LearningAlgorithm.CLASSIFICATION: self._classification_analysis,
            LearningAlgorithm.REINFORCEMENT: self._reinforcement_learning
        }
        
        # 学习文件路径
        self.learning_data_path = "data/learning_data.json"
        self.patterns_path = "data/patterns.pkl"
        self.suggestions_path = "data/suggestions.json"
        
        # 创建数据目录
        os.makedirs("data", exist_ok=True)
        
        # 加载学习数据
        self._load_learning_data()
        
        self.logger.info("学习系统初始化完成")
    
    async def learn_from_execution(self, execution_result: Dict[str, Any]):
        """
        从执行结果中学习
        
        Args:
            execution_result: 执行结果
        """
        try:
            if not self.learning_enabled:
                return
            
            self.logger.info("开始从执行结果中学习")
            
            # 记录执行历史
            self.execution_history.append({
                "timestamp": time.time(),
                "result": execution_result,
                "features": self._extract_features(execution_result)
            })
            
            # 分析执行模式
            patterns = await self._analyze_execution_patterns(execution_result)
            
            # 更新模式库
            for pattern in patterns:
                await self._update_pattern(pattern)
            
            # 生成优化建议
            suggestions = await self._generate_optimization_suggestions()
            self.optimization_suggestions.extend(suggestions)
            
            # 保存学习数据
            await self._save_learning_data()
            
            self.logger.info(f"学习完成，发现 {len(patterns)} 个模式，生成 {len(suggestions)} 个建议")
            
        except Exception as e:
            self.logger.error(f"学习过程失败: {e}")
    
    def _extract_features(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取执行特征"""
        features = {
            "task_type": execution_result.get("task_type", "unknown"),
            "success": execution_result.get("success", False),
            "execution_time": execution_result.get("execution_time", 0),
            "adjustment_count": execution_result.get("adjustment_count", 0),
            "error_type": execution_result.get("error_type", None),
            "screen_state": execution_result.get("screen_state", "unknown"),
            "app_name": execution_result.get("app_name", "unknown"),
            "coordinates": execution_result.get("coordinates", []),
            "timing": execution_result.get("timing", []),
            "feedback_quality": execution_result.get("feedback_quality", 0.5)
        }
        
        return features
    
    async def _analyze_execution_patterns(self, execution_result: Dict[str, Any]) -> List[LearningPattern]:
        """分析执行模式"""
        patterns = []
        
        try:
            features = self._extract_features(execution_result)
            
            # 1. 成功模式识别
            if features["success"]:
                success_pattern = await self._identify_success_pattern(features)
                if success_pattern:
                    patterns.append(success_pattern)
            
            # 2. 失败模式识别
            else:
                failure_pattern = await self._identify_failure_pattern(features)
                if failure_pattern:
                    patterns.append(failure_pattern)
            
            # 3. 坐标优化模式
            if features["coordinates"]:
                coord_pattern = await self._identify_coordinate_pattern(features)
                if coord_pattern:
                    patterns.append(coord_pattern)
            
            # 4. 时间优化模式
            if features["timing"]:
                timing_pattern = await self._identify_timing_pattern(features)
                if timing_pattern:
                    patterns.append(timing_pattern)
            
            # 5. 错误预防模式
            if features["error_type"]:
                error_pattern = await self._identify_error_prevention_pattern(features)
                if error_pattern:
                    patterns.append(error_pattern)
            
        except Exception as e:
            self.logger.error(f"模式分析失败: {e}")
        
        return patterns
    
    async def _identify_success_pattern(self, features: Dict[str, Any]) -> Optional[LearningPattern]:
        """识别成功模式"""
        try:
            pattern_key = f"success_{features['task_type']}_{features['app_name']}"
            
            if pattern_key in self.patterns:
                pattern = self.patterns[pattern_key]
                pattern.frequency += 1
                pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + 1.0) / pattern.frequency
                pattern.last_updated = time.time()
                pattern.examples.append(features)
            else:
                pattern = LearningPattern(
                    pattern_id=pattern_key,
                    pattern_type="success",
                    frequency=1,
                    success_rate=1.0,
                    confidence=0.8,
                    features=features,
                    examples=[features],
                    created_at=time.time(),
                    last_updated=time.time()
                )
                self.patterns[pattern_key] = pattern
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"成功模式识别失败: {e}")
            return None
    
    async def _identify_failure_pattern(self, features: Dict[str, Any]) -> Optional[LearningPattern]:
        """识别失败模式"""
        try:
            error_type = features.get("error_type", "unknown")
            pattern_key = f"failure_{features['task_type']}_{error_type}"
            
            if pattern_key in self.patterns:
                pattern = self.patterns[pattern_key]
                pattern.frequency += 1
                pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + 0.0) / pattern.frequency
                pattern.last_updated = time.time()
                pattern.examples.append(features)
            else:
                pattern = LearningPattern(
                    pattern_id=pattern_key,
                    pattern_type="failure",
                    frequency=1,
                    success_rate=0.0,
                    confidence=0.6,
                    features=features,
                    examples=[features],
                    created_at=time.time(),
                    last_updated=time.time()
                )
                self.patterns[pattern_key] = pattern
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"失败模式识别失败: {e}")
            return None
    
    async def _identify_coordinate_pattern(self, features: Dict[str, Any]) -> Optional[LearningPattern]:
        """识别坐标模式"""
        try:
            coordinates = features.get("coordinates", [])
            if not coordinates:
                return None
            
            # 分析坐标分布
            x_coords = [coord[0] for coord in coordinates]
            y_coords = [coord[1] for coord in coordinates]
            
            pattern_key = f"coordinate_{features['task_type']}_{features['app_name']}"
            
            if pattern_key in self.patterns:
                pattern = self.patterns[pattern_key]
                pattern.frequency += 1
                pattern.last_updated = time.time()
                
                # 更新坐标特征
                pattern.features["x_mean"] = np.mean(x_coords)
                pattern.features["y_mean"] = np.mean(y_coords)
                pattern.features["x_std"] = np.std(x_coords)
                pattern.features["y_std"] = np.std(y_coords)
                pattern.examples.append(features)
            else:
                pattern = LearningPattern(
                    pattern_id=pattern_key,
                    pattern_type="coordinate",
                    frequency=1,
                    success_rate=features.get("success", False),
                    confidence=0.7,
                    features={
                        "x_mean": np.mean(x_coords),
                        "y_mean": np.mean(y_coords),
                        "x_std": np.std(x_coords),
                        "y_std": np.std(y_coords),
                        "app_name": features["app_name"],
                        "task_type": features["task_type"]
                    },
                    examples=[features],
                    created_at=time.time(),
                    last_updated=time.time()
                )
                self.patterns[pattern_key] = pattern
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"坐标模式识别失败: {e}")
            return None
    
    async def _identify_timing_pattern(self, features: Dict[str, Any]) -> Optional[LearningPattern]:
        """识别时间模式"""
        try:
            timing = features.get("timing", [])
            if not timing:
                return None
            
            pattern_key = f"timing_{features['task_type']}_{features['app_name']}"
            
            if pattern_key in self.patterns:
                pattern = self.patterns[pattern_key]
                pattern.frequency += 1
                pattern.last_updated = time.time()
                
                # 更新时间特征
                pattern.features["avg_timing"] = np.mean(timing)
                pattern.features["min_timing"] = np.min(timing)
                pattern.features["max_timing"] = np.max(timing)
                pattern.examples.append(features)
            else:
                pattern = LearningPattern(
                    pattern_id=pattern_key,
                    pattern_type="timing",
                    frequency=1,
                    success_rate=features.get("success", False),
                    confidence=0.7,
                    features={
                        "avg_timing": np.mean(timing),
                        "min_timing": np.min(timing),
                        "max_timing": np.max(timing),
                        "app_name": features["app_name"],
                        "task_type": features["task_type"]
                    },
                    examples=[features],
                    created_at=time.time(),
                    last_updated=time.time()
                )
                self.patterns[pattern_key] = pattern
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"时间模式识别失败: {e}")
            return None
    
    async def _identify_error_prevention_pattern(self, features: Dict[str, Any]) -> Optional[LearningPattern]:
        """识别错误预防模式"""
        try:
            error_type = features.get("error_type", "unknown")
            pattern_key = f"error_prevention_{error_type}_{features['app_name']}"
            
            if pattern_key in self.patterns:
                pattern = self.patterns[pattern_key]
                pattern.frequency += 1
                pattern.last_updated = time.time()
                pattern.examples.append(features)
            else:
                pattern = LearningPattern(
                    pattern_id=pattern_key,
                    pattern_type="error_prevention",
                    frequency=1,
                    success_rate=0.0,  # 错误预防模式的成功率基于预防效果
                    confidence=0.6,
                    features={
                        "error_type": error_type,
                        "app_name": features["app_name"],
                        "task_type": features["task_type"],
                        "prevention_strategies": []
                    },
                    examples=[features],
                    created_at=time.time(),
                    last_updated=time.time()
                )
                self.patterns[pattern_key] = pattern
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"错误预防模式识别失败: {e}")
            return None
    
    async def _update_pattern(self, pattern: LearningPattern):
        """更新模式"""
        try:
            # 检查模式是否满足最小频率要求
            if pattern.frequency >= self.min_pattern_frequency:
                # 计算模式置信度
                pattern.confidence = self._calculate_pattern_confidence(pattern)
                
                # 如果置信度足够高，保存模式
                if pattern.confidence >= self.confidence_threshold:
                    self.patterns[pattern.pattern_id] = pattern
                    self.logger.info(f"模式已更新: {pattern.pattern_id}, 置信度: {pattern.confidence:.2f}")
            
        except Exception as e:
            self.logger.error(f"模式更新失败: {e}")
    
    def _calculate_pattern_confidence(self, pattern: LearningPattern) -> float:
        """计算模式置信度"""
        try:
            # 基于频率和成功率的置信度计算
            frequency_score = min(pattern.frequency / 10, 1.0)  # 频率分数
            success_score = pattern.success_rate  # 成功率分数
            consistency_score = self._calculate_consistency_score(pattern)  # 一致性分数
            
            # 加权平均
            confidence = (frequency_score * 0.3 + success_score * 0.4 + consistency_score * 0.3)
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"置信度计算失败: {e}")
            return 0.0
    
    def _calculate_consistency_score(self, pattern: LearningPattern) -> float:
        """计算一致性分数"""
        try:
            if len(pattern.examples) < 2:
                return 0.5
            
            # 计算特征的一致性
            features_list = [example for example in pattern.examples]
            
            # 计算数值特征的标准差
            numeric_features = ["execution_time", "adjustment_count", "feedback_quality"]
            consistency_scores = []
            
            for feature in numeric_features:
                values = [ex.get(feature, 0) for ex in features_list if ex.get(feature) is not None]
                if len(values) > 1:
                    std = np.std(values)
                    mean = np.mean(values)
                    if mean > 0:
                        cv = std / mean  # 变异系数
                        consistency_score = max(0, 1 - cv)  # 变异系数越小，一致性越高
                        consistency_scores.append(consistency_score)
            
            return np.mean(consistency_scores) if consistency_scores else 0.5
            
        except Exception as e:
            self.logger.error(f"一致性计算失败: {e}")
            return 0.5
    
    async def _generate_optimization_suggestions(self) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []
        
        try:
            # 1. 基于成功模式的建议
            success_suggestions = await self._generate_success_based_suggestions()
            suggestions.extend(success_suggestions)
            
            # 2. 基于失败模式的建议
            failure_suggestions = await self._generate_failure_based_suggestions()
            suggestions.extend(failure_suggestions)
            
            # 3. 基于坐标模式的建议
            coordinate_suggestions = await self._generate_coordinate_based_suggestions()
            suggestions.extend(coordinate_suggestions)
            
            # 4. 基于时间模式的建议
            timing_suggestions = await self._generate_timing_based_suggestions()
            suggestions.extend(timing_suggestions)
            
            # 5. 基于错误预防模式的建议
            error_prevention_suggestions = await self._generate_error_prevention_suggestions()
            suggestions.extend(error_prevention_suggestions)
            
        except Exception as e:
            self.logger.error(f"优化建议生成失败: {e}")
        
        return suggestions
    
    async def _generate_success_based_suggestions(self) -> List[OptimizationSuggestion]:
        """基于成功模式生成建议"""
        suggestions = []
        
        try:
            success_patterns = [p for p in self.patterns.values() if p.pattern_type == "success" and p.confidence > 0.8]
            
            for pattern in success_patterns:
                if pattern.frequency >= 5:  # 足够频繁的成功模式
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"success_{pattern.pattern_id}",
                        learning_type=LearningType.PATTERN_RECOGNITION,
                        algorithm=LearningAlgorithm.FREQUENCY_ANALYSIS,
                        description=f"应用成功模式: {pattern.pattern_id}",
                        confidence=pattern.confidence,
                        expected_improvement=pattern.success_rate * 20,  # 预期改进百分比
                        implementation=f"使用模式 {pattern.pattern_id} 的执行策略",
                        prerequisites=[f"任务类型: {pattern.features.get('task_type', 'unknown')}"]
                    )
                    suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"成功模式建议生成失败: {e}")
        
        return suggestions
    
    async def _generate_failure_based_suggestions(self) -> List[OptimizationSuggestion]:
        """基于失败模式生成建议"""
        suggestions = []
        
        try:
            failure_patterns = [p for p in self.patterns.values() if p.pattern_type == "failure" and p.frequency >= 3]
            
            for pattern in failure_patterns:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"failure_prevention_{pattern.pattern_id}",
                    learning_type=LearningType.ERROR_PREVENTION,
                    algorithm=LearningAlgorithm.CLASSIFICATION,
                    description=f"避免失败模式: {pattern.pattern_id}",
                    confidence=0.8,
                    expected_improvement=30,  # 避免失败可以显著提高成功率
                    implementation=f"在遇到 {pattern.features.get('error_type', 'unknown')} 错误时采用预防策略",
                    prerequisites=[f"应用: {pattern.features.get('app_name', 'unknown')}"]
                )
                suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"失败模式建议生成失败: {e}")
        
        return suggestions
    
    async def _generate_coordinate_based_suggestions(self) -> List[OptimizationSuggestion]:
        """基于坐标模式生成建议"""
        suggestions = []
        
        try:
            coord_patterns = [p for p in self.patterns.values() if p.pattern_type == "coordinate" and p.confidence > 0.7]
            
            for pattern in coord_patterns:
                if pattern.frequency >= 3:
                    x_mean = pattern.features.get("x_mean", 0)
                    y_mean = pattern.features.get("y_mean", 0)
                    x_std = pattern.features.get("x_std", 0)
                    y_std = pattern.features.get("y_std", 0)
                    
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"coordinate_optimization_{pattern.pattern_id}",
                        learning_type=LearningType.COORDINATE_OPTIMIZATION,
                        algorithm=LearningAlgorithm.CLUSTERING,
                        description=f"优化坐标: 使用 ({x_mean:.0f}, {y_mean:.0f}) ± ({x_std:.0f}, {y_std:.0f})",
                        confidence=pattern.confidence,
                        expected_improvement=15,
                        implementation=f"将点击坐标调整为 ({x_mean:.0f}, {y_mean:.0f})",
                        prerequisites=[f"应用: {pattern.features.get('app_name', 'unknown')}"]
                    )
                    suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"坐标模式建议生成失败: {e}")
        
        return suggestions
    
    async def _generate_timing_based_suggestions(self) -> List[OptimizationSuggestion]:
        """基于时间模式生成建议"""
        suggestions = []
        
        try:
            timing_patterns = [p for p in self.patterns.values() if p.pattern_type == "timing" and p.confidence > 0.7]
            
            for pattern in timing_patterns:
                if pattern.frequency >= 3:
                    avg_timing = pattern.features.get("avg_timing", 1)
                    min_timing = pattern.features.get("min_timing", 1)
                    max_timing = pattern.features.get("max_timing", 1)
                    
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"timing_optimization_{pattern.pattern_id}",
                        learning_type=LearningType.TIMING_OPTIMIZATION,
                        algorithm=LearningAlgorithm.REGRESSION,
                        description=f"优化等待时间: 使用 {avg_timing:.1f}秒 (范围: {min_timing:.1f}-{max_timing:.1f})",
                        confidence=pattern.confidence,
                        expected_improvement=10,
                        implementation=f"将等待时间设置为 {avg_timing:.1f}秒",
                        prerequisites=[f"应用: {pattern.features.get('app_name', 'unknown')}"]
                    )
                    suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"时间模式建议生成失败: {e}")
        
        return suggestions
    
    async def _generate_error_prevention_suggestions(self) -> List[OptimizationSuggestion]:
        """基于错误预防模式生成建议"""
        suggestions = []
        
        try:
            error_patterns = [p for p in self.patterns.values() if p.pattern_type == "error_prevention" and p.frequency >= 2]
            
            for pattern in error_patterns:
                error_type = pattern.features.get("error_type", "unknown")
                
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"error_prevention_{pattern.pattern_id}",
                    learning_type=LearningType.ERROR_PREVENTION,
                    algorithm=LearningAlgorithm.CLASSIFICATION,
                    description=f"预防 {error_type} 错误",
                    confidence=0.7,
                    expected_improvement=25,
                    implementation=f"在检测到 {error_type} 错误风险时采取预防措施",
                    prerequisites=[f"应用: {pattern.features.get('app_name', 'unknown')}"]
                )
                suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"错误预防建议生成失败: {e}")
        
        return suggestions
    
    async def get_optimization_suggestions(self, task_type: str = None, 
                                         app_name: str = None) -> List[OptimizationSuggestion]:
        """获取优化建议"""
        try:
            filtered_suggestions = []
            
            for suggestion in self.optimization_suggestions:
                # 根据任务类型和应用名称过滤
                if task_type and task_type not in suggestion.description:
                    continue
                if app_name and app_name not in suggestion.description:
                    continue
                
                # 按置信度排序
                filtered_suggestions.append(suggestion)
            
            # 按置信度降序排序
            filtered_suggestions.sort(key=lambda x: x.confidence, reverse=True)
            
            return filtered_suggestions[:10]  # 返回前10个建议
            
        except Exception as e:
            self.logger.error(f"获取优化建议失败: {e}")
            return []
    
    def get_learning_metrics(self) -> LearningMetrics:
        """获取学习指标"""
        try:
            total_patterns = len(self.patterns)
            successful_patterns = len([p for p in self.patterns.values() if p.pattern_type == "success"])
            failed_patterns = len([p for p in self.patterns.values() if p.pattern_type == "failure"])
            
            if total_patterns > 0:
                average_confidence = np.mean([p.confidence for p in self.patterns.values()])
                learning_accuracy = successful_patterns / total_patterns
            else:
                average_confidence = 0.0
                learning_accuracy = 0.0
            
            # 计算改进率
            if len(self.execution_history) > 10:
                recent_results = self.execution_history[-10:]
                success_rate = len([r for r in recent_results if r["result"].get("success", False)]) / len(recent_results)
                improvement_rate = success_rate * 100
            else:
                improvement_rate = 0.0
            
            return LearningMetrics(
                total_patterns=total_patterns,
                successful_patterns=successful_patterns,
                failed_patterns=failed_patterns,
                average_confidence=average_confidence,
                learning_accuracy=learning_accuracy,
                improvement_rate=improvement_rate,
                last_learning_time=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"获取学习指标失败: {e}")
            return LearningMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0)
    
    async def _save_learning_data(self):
        """保存学习数据"""
        try:
            # 保存模式数据
            with open(self.patterns_path, 'wb') as f:
                pickle.dump(self.patterns, f)
            
            # 保存建议数据
            suggestions_data = [asdict(s) for s in self.optimization_suggestions]
            with open(self.suggestions_path, 'w', encoding='utf-8') as f:
                json.dump(suggestions_data, f, ensure_ascii=False, indent=2)
            
            # 保存执行历史
            with open(self.learning_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.execution_history, f, ensure_ascii=False, indent=2)
            
            self.logger.info("学习数据已保存")
            
        except Exception as e:
            self.logger.error(f"保存学习数据失败: {e}")
    
    def _load_learning_data(self):
        """加载学习数据"""
        try:
            # 加载模式数据
            if os.path.exists(self.patterns_path):
                with open(self.patterns_path, 'rb') as f:
                    self.patterns = pickle.load(f)
            
            # 加载建议数据
            if os.path.exists(self.suggestions_path):
                with open(self.suggestions_path, 'r', encoding='utf-8') as f:
                    suggestions_data = json.load(f)
                    self.optimization_suggestions = [OptimizationSuggestion(**s) for s in suggestions_data]
            
            # 加载执行历史
            if os.path.exists(self.learning_data_path):
                with open(self.learning_data_path, 'r', encoding='utf-8') as f:
                    self.execution_history = json.load(f)
            
            self.logger.info("学习数据已加载")
            
        except Exception as e:
            self.logger.error(f"加载学习数据失败: {e}")
    
    def clear_learning_data(self):
        """清空学习数据"""
        try:
            self.patterns.clear()
            self.execution_history.clear()
            self.optimization_suggestions.clear()
            
            # 删除文件
            for path in [self.patterns_path, self.suggestions_path, self.learning_data_path]:
                if os.path.exists(path):
                    os.remove(path)
            
            self.logger.info("学习数据已清空")
            
        except Exception as e:
            self.logger.error(f"清空学习数据失败: {e}")
    
    # 学习算法实现
    async def _frequency_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """频率分析算法"""
        try:
            # 统计特征频率
            feature_counts = defaultdict(int)
            for item in data:
                for key, value in item.items():
                    feature_counts[f"{key}_{value}"] += 1
            
            # 找出高频特征
            high_frequency_features = {k: v for k, v in feature_counts.items() if v > len(data) * 0.5}
            
            return {
                "algorithm": "frequency_analysis",
                "high_frequency_features": high_frequency_features,
                "total_items": len(data)
            }
            
        except Exception as e:
            self.logger.error(f"频率分析失败: {e}")
            return {}
    
    async def _clustering_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚类分析算法"""
        try:
            # 简单的K-means聚类实现
            if len(data) < 3:
                return {"algorithm": "clustering", "clusters": []}
            
            # 提取数值特征
            numeric_features = []
            for item in data:
                features = [item.get("execution_time", 0), item.get("adjustment_count", 0)]
                numeric_features.append(features)
            
            # 简单的聚类（这里使用简化的实现）
            clusters = []
            if numeric_features:
                # 基于执行时间聚类
                execution_times = [f[0] for f in numeric_features]
                avg_time = np.mean(execution_times)
                
                fast_cluster = [i for i, t in enumerate(execution_times) if t < avg_time]
                slow_cluster = [i for i, t in enumerate(execution_times) if t >= avg_time]
                
                clusters = [fast_cluster, slow_cluster]
            
            return {
                "algorithm": "clustering",
                "clusters": clusters,
                "cluster_count": len(clusters)
            }
            
        except Exception as e:
            self.logger.error(f"聚类分析失败: {e}")
            return {}
    
    async def _regression_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """回归分析算法"""
        try:
            if len(data) < 2:
                return {"algorithm": "regression", "coefficients": []}
            
            # 简单的线性回归
            x_values = [item.get("adjustment_count", 0) for item in data]
            y_values = [item.get("execution_time", 0) for item in data]
            
            if len(x_values) > 1 and len(y_values) > 1:
                # 计算相关系数
                correlation = np.corrcoef(x_values, y_values)[0, 1]
                
                return {
                    "algorithm": "regression",
                    "correlation": correlation,
                    "relationship": "positive" if correlation > 0 else "negative"
                }
            
            return {"algorithm": "regression", "correlation": 0}
            
        except Exception as e:
            self.logger.error(f"回归分析失败: {e}")
            return {}
    
    async def _classification_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分类分析算法"""
        try:
            # 基于成功/失败分类
            success_items = [item for item in data if item.get("success", False)]
            failure_items = [item for item in data if not item.get("success", False)]
            
            # 分析成功和失败的特征差异
            success_features = {}
            failure_features = {}
            
            if success_items:
                success_features = {
                    "avg_execution_time": np.mean([item.get("execution_time", 0) for item in success_items]),
                    "avg_adjustment_count": np.mean([item.get("adjustment_count", 0) for item in success_items])
                }
            
            if failure_items:
                failure_features = {
                    "avg_execution_time": np.mean([item.get("execution_time", 0) for item in failure_items]),
                    "avg_adjustment_count": np.mean([item.get("adjustment_count", 0) for item in failure_items])
                }
            
            return {
                "algorithm": "classification",
                "success_features": success_features,
                "failure_features": failure_features,
                "success_count": len(success_items),
                "failure_count": len(failure_items)
            }
            
        except Exception as e:
            self.logger.error(f"分类分析失败: {e}")
            return {}
    
    async def _reinforcement_learning(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """强化学习算法"""
        try:
            # 简单的Q-learning实现
            # 这里使用简化的奖励机制
            rewards = []
            for item in data:
                if item.get("success", False):
                    reward = 1.0
                else:
                    reward = -0.5
                
                # 根据执行时间调整奖励
                execution_time = item.get("execution_time", 0)
                if execution_time > 10:  # 执行时间过长
                    reward *= 0.8
                
                rewards.append(reward)
            
            avg_reward = np.mean(rewards) if rewards else 0
            
            return {
                "algorithm": "reinforcement_learning",
                "average_reward": avg_reward,
                "total_episodes": len(data),
                "learning_rate": self.learning_rate
            }
            
        except Exception as e:
            self.logger.error(f"强化学习失败: {e}")
            return {}