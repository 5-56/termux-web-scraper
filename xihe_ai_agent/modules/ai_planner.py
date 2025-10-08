"""
AI任务规划模块
负责分析用户任务，制定详细的执行计划，并生成相应的自动化代码
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re


class TaskComplexity(Enum):
    """任务复杂度枚举"""
    SIMPLE = "simple"      # 简单任务，1-3步
    MEDIUM = "medium"      # 中等任务，4-8步
    COMPLEX = "complex"    # 复杂任务，9+步


class StepType(Enum):
    """步骤类型枚举"""
    LAUNCH_APP = "launch_app"
    WAIT = "wait"
    TAP = "tap"
    SWIPE = "swipe"
    INPUT = "input"
    SCREENSHOT = "screenshot"
    OCR_DETECT = "ocr_detect"
    ELEMENT_DETECT = "element_detect"
    CONDITION_CHECK = "condition_check"
    LOOP = "loop"
    CONDITIONAL = "conditional"


@dataclass
class ExecutionStep:
    """执行步骤"""
    id: str
    type: StepType
    description: str
    parameters: Dict[str, Any]
    expected_result: str
    fallback_steps: List[str] = None
    retry_count: int = 3
    timeout: int = 10
    confidence: float = 0.8


@dataclass
class TaskPlan:
    """任务计划"""
    task_id: str
    original_command: str
    complexity: TaskComplexity
    steps: List[ExecutionStep]
    estimated_duration: int  # 预估执行时间(秒)
    success_criteria: List[str]
    risk_factors: List[str]
    generated_code: str = ""


class AIPlanner:
    """AI任务规划器"""
    
    def __init__(self, config_manager):
        """
        初始化AI规划器
        
        Args:
            config_manager: 配置管理器
        """
        self.config = config_manager
        self.logger = logging.getLogger("AIPlanner")
        
        # 任务模式库
        self.task_patterns = {
            "刷视频": self._plan_video_watching,
            "发消息": self._plan_messaging,
            "抓取网页": self._plan_web_scraping,
            "启动应用": self._plan_app_launch,
            "截图": self._plan_screenshot,
            "搜索": self._plan_search,
            "登录": self._plan_login,
            "注册": self._plan_register,
            "购买": self._plan_purchase,
            "下载": self._plan_download
        }
        
        # 应用知识库
        self.app_knowledge = {
            "抖音": {
                "package": "com.ss.android.ugc.aweme",
                "main_activity": "com.ss.android.ugc.aweme.main.MainActivity",
                "ui_elements": {
                    "视频区域": {"selector": "com.ss.android.ugc.aweme:id/feed_list", "type": "list"},
                    "点赞按钮": {"selector": "com.ss.android.ugc.aweme:id/awh", "type": "button"},
                    "评论按钮": {"selector": "com.ss.android.ugc.aweme:id/awj", "type": "button"},
                    "分享按钮": {"selector": "com.ss.android.ugc.aweme:id/awk", "type": "button"},
                    "搜索框": {"selector": "com.ss.android.ugc.aweme:id/search", "type": "input"}
                },
                "common_actions": ["滑动", "点赞", "评论", "分享", "搜索"]
            },
            "微信": {
                "package": "com.tencent.mm",
                "main_activity": "com.tencent.mm.ui.LauncherUI",
                "ui_elements": {
                    "搜索框": {"selector": "com.tencent.mm:id/f8y", "type": "input"},
                    "聊天列表": {"selector": "com.tencent.mm:id/b4e", "type": "list"},
                    "输入框": {"selector": "com.tencent.mm:id/al_", "type": "input"},
                    "发送按钮": {"selector": "com.tencent.mm:id/anv", "type": "button"}
                },
                "common_actions": ["搜索", "发送消息", "查看聊天", "添加好友"]
            },
            "淘宝": {
                "package": "com.taobao.taobao",
                "main_activity": "com.taobao.tao.TBMainActivity",
                "ui_elements": {
                    "搜索框": {"selector": "com.taobao.taobao:id/searchEdit", "type": "input"},
                    "商品列表": {"selector": "com.taobao.taobao:id/recycler_view", "type": "list"},
                    "购买按钮": {"selector": "com.taobao.taobao:id/buyNow", "type": "button"}
                },
                "common_actions": ["搜索商品", "查看详情", "加入购物车", "购买"]
            }
        }
        
        self.logger.info("AI规划器初始化完成")
    
    async def plan_task(self, command: str, context: Dict[str, Any] = None) -> TaskPlan:
        """
        规划任务
        
        Args:
            command: 用户指令
            context: 上下文信息
            
        Returns:
            任务计划
        """
        try:
            self.logger.info(f"开始规划任务: {command}")
            
            # 1. 分析任务类型和复杂度
            task_type, complexity = self._analyze_task(command)
            
            # 2. 生成任务ID
            task_id = f"task_{int(asyncio.get_event_loop().time())}"
            
            # 3. 根据任务类型选择规划方法
            if task_type in self.task_patterns:
                steps = await self.task_patterns[task_type](command, context)
            else:
                steps = await self._plan_generic_task(command, context)
            
            # 4. 评估任务复杂度
            complexity = self._evaluate_complexity(steps)
            
            # 5. 生成代码
            generated_code = self._generate_code(steps, task_id)
            
            # 6. 创建任务计划
            plan = TaskPlan(
                task_id=task_id,
                original_command=command,
                complexity=complexity,
                steps=steps,
                estimated_duration=self._estimate_duration(steps),
                success_criteria=self._define_success_criteria(command, steps),
                risk_factors=self._identify_risk_factors(steps),
                generated_code=generated_code
            )
            
            self.logger.info(f"任务规划完成: {task_id}, 步骤数: {len(steps)}")
            return plan
            
        except Exception as e:
            self.logger.error(f"任务规划失败: {e}")
            raise
    
    def _analyze_task(self, command: str) -> Tuple[str, TaskComplexity]:
        """分析任务类型和复杂度"""
        command_lower = command.lower()
        
        # 识别任务类型
        task_type = "generic"
        for pattern, _ in self.task_patterns.items():
            if pattern in command_lower:
                task_type = pattern
                break
        
        # 评估复杂度
        complexity_indicators = {
            "简单": ["截图", "启动", "点击"],
            "中等": ["发消息", "搜索", "登录"],
            "复杂": ["刷视频", "抓取", "购买", "批量"]
        }
        
        complexity = TaskComplexity.SIMPLE
        for level, indicators in complexity_indicators.items():
            if any(indicator in command_lower for indicator in indicators):
                if level == "简单":
                    complexity = TaskComplexity.SIMPLE
                elif level == "中等":
                    complexity = TaskComplexity.MEDIUM
                else:
                    complexity = TaskComplexity.COMPLEX
        
        return task_type, complexity
    
    async def _plan_video_watching(self, command: str, context: Dict[str, Any] = None) -> List[ExecutionStep]:
        """规划视频观看任务"""
        steps = []
        
        # 解析参数
        platform = self._extract_platform(command)
        duration = self._extract_duration(command, default=300)
        count = self._extract_count(command, default=10)
        
        app_info = self.app_knowledge.get(platform, {})
        
        # 步骤1: 启动应用
        steps.append(ExecutionStep(
            id="step_1",
            type=StepType.LAUNCH_APP,
            description=f"启动{platform}应用",
            parameters={
                "app_name": platform,
                "package_name": app_info.get("package", ""),
                "main_activity": app_info.get("main_activity", "")
            },
            expected_result="应用成功启动并显示主界面",
            timeout=15
        ))
        
        # 步骤2: 等待应用加载
        steps.append(ExecutionStep(
            id="step_2",
            type=StepType.WAIT,
            description="等待应用完全加载",
            parameters={"duration": 3},
            expected_result="应用界面完全加载"
        ))
        
        # 步骤3-12: 循环观看视频
        for i in range(count):
            # 观看视频
            steps.append(ExecutionStep(
                id=f"step_watch_{i+1}",
                type=StepType.WAIT,
                description=f"观看第{i+1}个视频",
                parameters={"duration": duration // count},
                expected_result="视频正常播放"
            ))
            
            # 随机操作
            if i < count - 1:  # 不是最后一个视频
                # 随机点赞
                if i % 3 == 0:
                    steps.append(ExecutionStep(
                        id=f"step_like_{i+1}",
                        type=StepType.TAP,
                        description=f"点赞第{i+1}个视频",
                        parameters={
                            "x": 800,
                            "y": 600,
                            "description": "点赞按钮"
                        },
                        expected_result="点赞成功",
                        confidence=0.7
                    ))
                
                # 滑动到下一个视频
                steps.append(ExecutionStep(
                    id=f"step_swipe_{i+1}",
                    type=StepType.SWIPE,
                    description=f"滑动到第{i+2}个视频",
                    parameters={
                        "start_x": 400,
                        "start_y": 800,
                        "end_x": 400,
                        "end_y": 200,
                        "duration": 300
                    },
                    expected_result="成功切换到下一个视频"
                ))
        
        return steps
    
    async def _plan_messaging(self, command: str, context: Dict[str, Any] = None) -> List[ExecutionStep]:
        """规划消息发送任务"""
        steps = []
        
        # 解析参数
        platform = self._extract_platform(command, default="微信")
        recipients = self._extract_recipients(command)
        message = self._extract_message(command)
        
        app_info = self.app_knowledge.get(platform, {})
        
        # 步骤1: 启动应用
        steps.append(ExecutionStep(
            id="step_1",
            type=StepType.LAUNCH_APP,
            description=f"启动{platform}应用",
            parameters={
                "app_name": platform,
                "package_name": app_info.get("package", ""),
                "main_activity": app_info.get("main_activity", "")
            },
            expected_result="应用成功启动",
            timeout=15
        ))
        
        # 步骤2: 等待应用加载
        steps.append(ExecutionStep(
            id="step_2",
            type=StepType.WAIT,
            description="等待应用加载",
            parameters={"duration": 3},
            expected_result="应用界面加载完成"
        ))
        
        # 步骤3-N: 为每个联系人发送消息
        for i, recipient in enumerate(recipients):
            # 搜索联系人
            steps.append(ExecutionStep(
                id=f"step_search_{i+1}",
                type=StepType.TAP,
                description=f"点击搜索框搜索联系人: {recipient}",
                parameters={
                    "x": 200,
                    "y": 100,
                    "description": "搜索框"
                },
                expected_result="搜索框获得焦点"
            ))
            
            steps.append(ExecutionStep(
                id=f"step_input_search_{i+1}",
                type=StepType.INPUT,
                description=f"输入联系人名称: {recipient}",
                parameters={"text": recipient},
                expected_result="搜索框显示输入内容"
            ))
            
            steps.append(ExecutionStep(
                id=f"step_wait_search_{i+1}",
                type=StepType.WAIT,
                description="等待搜索结果",
                parameters={"duration": 2},
                expected_result="搜索结果出现"
            ))
            
            # 点击搜索结果
            steps.append(ExecutionStep(
                id=f"step_select_{i+1}",
                type=StepType.TAP,
                description=f"选择联系人: {recipient}",
                parameters={
                    "x": 200,
                    "y": 200,
                    "description": "搜索结果"
                },
                expected_result="进入聊天界面",
                fallback_steps=[f"step_ocr_detect_{i+1}"]
            ))
            
            # OCR检测备用方案
            steps.append(ExecutionStep(
                id=f"step_ocr_detect_{i+1}",
                type=StepType.OCR_DETECT,
                description=f"通过OCR检测联系人: {recipient}",
                parameters={
                    "target_text": recipient,
                    "region": {"x": 0, "y": 150, "width": 400, "height": 300}
                },
                expected_result="找到联系人名称"
            ))
            
            # 输入消息
            steps.append(ExecutionStep(
                id=f"step_input_msg_{i+1}",
                type=StepType.TAP,
                description="点击输入框",
                parameters={
                    "x": 200,
                    "y": 600,
                    "description": "消息输入框"
                },
                expected_result="输入框获得焦点"
            ))
            
            steps.append(ExecutionStep(
                id=f"step_type_msg_{i+1}",
                type=StepType.INPUT,
                description=f"输入消息内容: {message}",
                parameters={"text": message},
                expected_result="消息内容输入完成"
            ))
            
            # 发送消息
            steps.append(ExecutionStep(
                id=f"step_send_{i+1}",
                type=StepType.TAP,
                description="点击发送按钮",
                parameters={
                    "x": 800,
                    "y": 600,
                    "description": "发送按钮"
                },
                expected_result="消息发送成功"
            ))
            
            # 返回聊天列表
            if i < len(recipients) - 1:
                steps.append(ExecutionStep(
                    id=f"step_back_{i+1}",
                    type=StepType.TAP,
                    description="返回聊天列表",
                    parameters={
                        "x": 50,
                        "y": 100,
                        "description": "返回按钮"
                    },
                    expected_result="返回聊天列表界面"
                ))
        
        return steps
    
    async def _plan_web_scraping(self, command: str, context: Dict[str, Any] = None) -> List[ExecutionStep]:
        """规划网页抓取任务"""
        steps = []
        
        # 解析参数
        url = self._extract_url(command)
        data_type = self._extract_data_type(command, default="text")
        selectors = self._extract_selectors(command)
        
        # 步骤1: 启动浏览器
        steps.append(ExecutionStep(
            id="step_1",
            type=StepType.LAUNCH_APP,
            description="启动浏览器",
            parameters={
                "app_name": "浏览器",
                "package_name": "com.android.chrome"
            },
            expected_result="浏览器启动成功",
            timeout=15
        ))
        
        # 步骤2: 等待浏览器加载
        steps.append(ExecutionStep(
            id="step_2",
            type=StepType.WAIT,
            description="等待浏览器加载",
            parameters={"duration": 3},
            expected_result="浏览器界面加载完成"
        ))
        
        # 步骤3: 输入URL
        steps.append(ExecutionStep(
            id="step_3",
            type=StepType.TAP,
            description="点击地址栏",
            parameters={
                "x": 400,
                "y": 100,
                "description": "地址栏"
            },
            expected_result="地址栏获得焦点"
        ))
        
        steps.append(ExecutionStep(
            id="step_4",
            type=StepType.INPUT,
            description=f"输入URL: {url}",
            parameters={"text": url},
            expected_result="URL输入完成"
        ))
        
        # 步骤4: 访问网页
        steps.append(ExecutionStep(
            id="step_5",
            type=StepType.TAP,
            description="访问网页",
            parameters={
                "x": 800,
                "y": 100,
                "description": "访问按钮"
            },
            expected_result="网页开始加载"
        ))
        
        # 步骤5: 等待网页加载
        steps.append(ExecutionStep(
            id="step_6",
            type=StepType.WAIT,
            description="等待网页完全加载",
            parameters={"duration": 10},
            expected_result="网页加载完成"
        ))
        
        # 步骤6: 截图保存
        steps.append(ExecutionStep(
            id="step_7",
            type=StepType.SCREENSHOT,
            description="截取网页截图",
            parameters={"save_path": f"screenshots/web_{int(asyncio.get_event_loop().time())}.png"},
            expected_result="截图保存成功"
        ))
        
        # 步骤7: OCR识别文本
        if data_type == "text":
            steps.append(ExecutionStep(
                id="step_8",
                type=StepType.OCR_DETECT,
                description="识别网页文本内容",
                parameters={
                    "region": {"x": 0, "y": 200, "width": 1080, "height": 1800},
                    "save_result": True
                },
                expected_result="文本识别完成"
            ))
        
        return steps
    
    async def _plan_generic_task(self, command: str, context: Dict[str, Any] = None) -> List[ExecutionStep]:
        """规划通用任务"""
        steps = []
        
        # 步骤1: 截图分析当前状态
        steps.append(ExecutionStep(
            id="step_1",
            type=StepType.SCREENSHOT,
            description="截取当前屏幕状态",
            parameters={"save_path": f"screenshots/current_{int(asyncio.get_event_loop().time())}.png"},
            expected_result="当前状态截图完成"
        ))
        
        # 步骤2: OCR识别屏幕内容
        steps.append(ExecutionStep(
            id="step_2",
            type=StepType.OCR_DETECT,
            description="识别屏幕文字内容",
            parameters={
                "region": {"x": 0, "y": 0, "width": 1080, "height": 2340},
                "save_result": True
            },
            expected_result="屏幕内容识别完成"
        ))
        
        # 步骤3: 检测UI元素
        steps.append(ExecutionStep(
            id="step_3",
            type=StepType.ELEMENT_DETECT,
            description="检测可交互的UI元素",
            parameters={
                "element_types": ["button", "input", "link", "image"],
                "save_result": True
            },
            expected_result="UI元素检测完成"
        ))
        
        # 步骤4: 根据识别结果执行操作
        steps.append(ExecutionStep(
            id="step_4",
            type=StepType.CONDITIONAL,
            description="根据屏幕内容执行相应操作",
            parameters={
                "condition": "screen_analysis",
                "action": "execute_based_on_content"
            },
            expected_result="根据分析结果执行操作"
        ))
        
        return steps
    
    def _extract_platform(self, command: str, default: str = "抖音") -> str:
        """从命令中提取平台名称"""
        platforms = ["抖音", "快手", "B站", "微信", "QQ", "淘宝", "支付宝"]
        for platform in platforms:
            if platform in command:
                return platform
        return default
    
    def _extract_duration(self, command: str, default: int = 300) -> int:
        """从命令中提取持续时间"""
        import re
        match = re.search(r'(\d+)\s*分钟?', command)
        if match:
            return int(match.group(1)) * 60
        match = re.search(r'(\d+)\s*秒?', command)
        if match:
            return int(match.group(1))
        return default
    
    def _extract_count(self, command: str, default: int = 10) -> int:
        """从命令中提取数量"""
        import re
        match = re.search(r'(\d+)\s*个?', command)
        if match:
            return int(match.group(1))
        return default
    
    def _extract_recipients(self, command: str) -> List[str]:
        """从命令中提取收件人列表"""
        import re
        # 匹配 "给张三、李四、王五" 或 "张三,李四,王五"
        match = re.search(r'给?([^:：]+)[:：]', command)
        if match:
            recipients_str = match.group(1)
            # 分割收件人
            recipients = re.split(r'[,，、]', recipients_str)
            return [r.strip() for r in recipients if r.strip()]
        return ["默认联系人"]
    
    def _extract_message(self, command: str) -> str:
        """从命令中提取消息内容"""
        import re
        match = re.search(r'[:：](.+)', command)
        if match:
            return match.group(1).strip()
        return "默认消息"
    
    def _extract_url(self, command: str) -> str:
        """从命令中提取URL"""
        import re
        match = re.search(r'(https?://[^\s]+)', command)
        if match:
            return match.group(1)
        return "https://www.example.com"
    
    def _extract_data_type(self, command: str, default: str = "text") -> str:
        """从命令中提取数据类型"""
        if "图片" in command or "image" in command.lower():
            return "image"
        elif "链接" in command or "link" in command.lower():
            return "link"
        elif "表格" in command or "table" in command.lower():
            return "table"
        return default
    
    def _extract_selectors(self, command: str) -> Dict[str, str]:
        """从命令中提取选择器"""
        # 这里可以根据命令解析出具体的选择器
        return {
            "title": "h1",
            "content": "p"
        }
    
    def _evaluate_complexity(self, steps: List[ExecutionStep]) -> TaskComplexity:
        """评估任务复杂度"""
        step_count = len(steps)
        if step_count <= 3:
            return TaskComplexity.SIMPLE
        elif step_count <= 8:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.COMPLEX
    
    def _estimate_duration(self, steps: List[ExecutionStep]) -> int:
        """估算任务执行时间"""
        total_duration = 0
        for step in steps:
            if step.type == StepType.WAIT:
                total_duration += step.parameters.get("duration", 0)
            elif step.type == StepType.LAUNCH_APP:
                total_duration += 15
            else:
                total_duration += 2
        return total_duration
    
    def _define_success_criteria(self, command: str, steps: List[ExecutionStep]) -> List[str]:
        """定义成功标准"""
        criteria = []
        
        if "刷视频" in command:
            criteria.append("成功观看指定数量的视频")
            criteria.append("完成滑动操作")
        elif "发消息" in command:
            criteria.append("成功发送消息给所有指定联系人")
            criteria.append("消息内容正确")
        elif "抓取" in command:
            criteria.append("成功访问目标网页")
            criteria.append("成功提取指定数据")
        
        return criteria
    
    def _identify_risk_factors(self, steps: List[ExecutionStep]) -> List[str]:
        """识别风险因素"""
        risks = []
        
        for step in steps:
            if step.type == StepType.LAUNCH_APP:
                risks.append("应用启动失败")
            elif step.type == StepType.OCR_DETECT:
                risks.append("文字识别不准确")
            elif step.type == StepType.TAP:
                risks.append("点击位置不准确")
            elif step.type == StepType.INPUT:
                risks.append("输入内容错误")
        
        return risks
    
    def _generate_code(self, steps: List[ExecutionStep], task_id: str) -> str:
        """生成自动化代码"""
        code_lines = [
            "import asyncio",
            "import time",
            "from datetime import datetime",
            "",
            f"# 任务ID: {task_id}",
            f"# 生成时间: {datetime.now().isoformat()}",
            "",
            "async def execute_task():",
            "    \"\"\"执行自动化任务\"\"\"",
            "    try:",
            "        print(f'开始执行任务: {task_id}')",
            ""
        ]
        
        for step in steps:
            code_lines.extend(self._generate_step_code(step))
        
        code_lines.extend([
            "",
            "        print('任务执行完成')",
            "        return {'success': True, 'message': '任务执行成功'}",
            "",
            "    except Exception as e:",
            "        print(f'任务执行失败: {e}')",
            "        return {'success': False, 'error': str(e)}",
            "",
            "# 运行任务",
            "if __name__ == '__main__':",
            "    asyncio.run(execute_task())"
        ])
        
        return "\n".join(code_lines)
    
    def _generate_step_code(self, step: ExecutionStep) -> List[str]:
        """生成单个步骤的代码"""
        code_lines = []
        
        if step.type == StepType.LAUNCH_APP:
            code_lines.extend([
                f"        # {step.description}",
                f"        print('{step.description}')",
                f"        await android_controller.launch_app('{step.parameters['app_name']}')",
                f"        await asyncio.sleep(3)",
                ""
            ])
        
        elif step.type == StepType.WAIT:
            duration = step.parameters.get("duration", 1)
            code_lines.extend([
                f"        # {step.description}",
                f"        print('{step.description}')",
                f"        await asyncio.sleep({duration})",
                ""
            ])
        
        elif step.type == StepType.TAP:
            x = step.parameters.get("x", 0)
            y = step.parameters.get("y", 0)
            code_lines.extend([
                f"        # {step.description}",
                f"        print('{step.description}')",
                f"        await android_controller.tap({x}, {y})",
                f"        await asyncio.sleep(1)",
                ""
            ])
        
        elif step.type == StepType.SWIPE:
            start_x = step.parameters.get("start_x", 0)
            start_y = step.parameters.get("start_y", 0)
            end_x = step.parameters.get("end_x", 0)
            end_y = step.parameters.get("end_y", 0)
            duration = step.parameters.get("duration", 300)
            code_lines.extend([
                f"        # {step.description}",
                f"        print('{step.description}')",
                f"        await android_controller.swipe({start_x}, {start_y}, {end_x}, {end_y}, {duration})",
                f"        await asyncio.sleep(1)",
                ""
            ])
        
        elif step.type == StepType.INPUT:
            text = step.parameters.get("text", "")
            code_lines.extend([
                f"        # {step.description}",
                f"        print('{step.description}')",
                f"        await android_controller.input_text('{text}')",
                f"        await asyncio.sleep(1)",
                ""
            ])
        
        elif step.type == StepType.SCREENSHOT:
            save_path = step.parameters.get("save_path", "screenshot.png")
            code_lines.extend([
                f"        # {step.description}",
                f"        print('{step.description}')",
                f"        screenshot_path = await android_controller.take_screenshot('{save_path}')",
                f"        print(f'截图保存到: {{screenshot_path}}')",
                ""
            ])
        
        elif step.type == StepType.OCR_DETECT:
            code_lines.extend([
                f"        # {step.description}",
                f"        print('{step.description}')",
                f"        # OCR识别功能需要屏幕识别模块支持",
                f"        # await screen_recognition.detect_text()",
                ""
            ])
        
        return code_lines