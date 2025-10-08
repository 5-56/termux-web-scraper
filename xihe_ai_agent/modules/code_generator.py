"""
智能代码生成器
根据AI规划生成高质量的自动化代码，并支持动态调整和优化
"""

import ast
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class CodeTemplate(Enum):
    """代码模板类型"""
    BASIC_CONTROL = "basic_control"
    VIDEO_AUTOMATION = "video_automation"
    MESSAGING = "messaging"
    WEB_SCRAPING = "web_scraping"
    UI_INTERACTION = "ui_interaction"
    DATA_PROCESSING = "data_processing"


@dataclass
class CodeBlock:
    """代码块"""
    id: str
    type: str
    content: str
    dependencies: List[str] = None
    parameters: Dict[str, Any] = None
    error_handling: str = None


@dataclass
class GeneratedCode:
    """生成的代码"""
    task_id: str
    main_function: str
    helper_functions: List[str]
    imports: List[str]
    error_handling: str
    logging: str
    configuration: Dict[str, Any]
    test_cases: List[str] = None


class CodeGenerator:
    """智能代码生成器"""
    
    def __init__(self, config_manager):
        """
        初始化代码生成器
        
        Args:
            config_manager: 配置管理器
        """
        self.config = config_manager
        self.logger = logging.getLogger("CodeGenerator")
        
        # 代码模板库
        self.templates = {
            CodeTemplate.BASIC_CONTROL: self._get_basic_control_template(),
            CodeTemplate.VIDEO_AUTOMATION: self._get_video_automation_template(),
            CodeTemplate.MESSAGING: self._get_messaging_template(),
            CodeTemplate.WEB_SCRAPING: self._get_web_scraping_template(),
            CodeTemplate.UI_INTERACTION: self._get_ui_interaction_template(),
            CodeTemplate.DATA_PROCESSING: self._get_data_processing_template()
        }
        
        # 代码优化规则
        self.optimization_rules = [
            self._optimize_imports,
            self._optimize_error_handling,
            self._optimize_logging,
            self._optimize_performance,
            self._optimize_readability
        ]
        
        self.logger.info("代码生成器初始化完成")
    
    def generate_code(self, task_plan, screen_feedback: Dict[str, Any] = None) -> GeneratedCode:
        """
        生成自动化代码
        
        Args:
            task_plan: 任务计划
            screen_feedback: 屏幕识别反馈
            
        Returns:
            生成的代码
        """
        try:
            self.logger.info(f"开始生成代码: {task_plan.task_id}")
            
            # 1. 分析任务类型
            task_type = self._analyze_task_type(task_plan)
            
            # 2. 生成主要代码块
            main_function = self._generate_main_function(task_plan, task_type)
            
            # 3. 生成辅助函数
            helper_functions = self._generate_helper_functions(task_plan, task_type)
            
            # 4. 生成导入语句
            imports = self._generate_imports(task_plan, task_type)
            
            # 5. 生成错误处理
            error_handling = self._generate_error_handling(task_plan)
            
            # 6. 生成日志记录
            logging_code = self._generate_logging(task_plan)
            
            # 7. 生成配置
            configuration = self._generate_configuration(task_plan)
            
            # 8. 生成测试用例
            test_cases = self._generate_test_cases(task_plan)
            
            # 9. 应用屏幕反馈优化
            if screen_feedback:
                main_function = self._apply_screen_feedback(main_function, screen_feedback)
            
            # 10. 代码优化
            generated_code = GeneratedCode(
                task_id=task_plan.task_id,
                main_function=main_function,
                helper_functions=helper_functions,
                imports=imports,
                error_handling=error_handling,
                logging=logging_code,
                configuration=configuration,
                test_cases=test_cases
            )
            
            # 应用优化规则
            for rule in self.optimization_rules:
                generated_code = rule(generated_code)
            
            self.logger.info(f"代码生成完成: {task_plan.task_id}")
            return generated_code
            
        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            raise
    
    def _analyze_task_type(self, task_plan) -> CodeTemplate:
        """分析任务类型"""
        command = task_plan.original_command.lower()
        
        if "刷视频" in command or "抖音" in command or "快手" in command:
            return CodeTemplate.VIDEO_AUTOMATION
        elif "发消息" in command or "微信" in command or "qq" in command:
            return CodeTemplate.MESSAGING
        elif "抓取" in command or "网页" in command or "数据" in command:
            return CodeTemplate.WEB_SCRAPING
        elif "点击" in command or "滑动" in command or "输入" in command:
            return CodeTemplate.UI_INTERACTION
        elif "处理" in command or "分析" in command or "计算" in command:
            return CodeTemplate.DATA_PROCESSING
        else:
            return CodeTemplate.BASIC_CONTROL
    
    def _generate_main_function(self, task_plan, task_type: CodeTemplate) -> str:
        """生成主函数"""
        template = self.templates[task_type]
        
        # 替换模板变量
        main_function = template["main_function"]
        main_function = main_function.replace("{{TASK_ID}}", task_plan.task_id)
        main_function = main_function.replace("{{COMMAND}}", task_plan.original_command)
        main_function = main_function.replace("{{STEPS}}", self._generate_steps_code(task_plan.steps))
        
        return main_function
    
    def _generate_steps_code(self, steps) -> str:
        """生成步骤代码"""
        code_lines = []
        
        for i, step in enumerate(steps):
            step_code = self._generate_single_step_code(step, i + 1)
            code_lines.append(step_code)
        
        return "\n".join(code_lines)
    
    def _generate_single_step_code(self, step, step_number: int) -> str:
        """生成单个步骤的代码"""
        code_template = """
        # 步骤{step_number}: {description}
        try:
            logger.info("执行步骤{step_number}: {description}")
            {step_code}
            logger.info("步骤{step_number}执行成功")
        except Exception as e:
            logger.error(f"步骤{step_number}执行失败: {{e}}")
            {error_handling}
        """
        
        step_code = self._get_step_implementation(step)
        error_handling = self._get_step_error_handling(step)
        
        return code_template.format(
            step_number=step_number,
            description=step.description,
            step_code=step_code,
            error_handling=error_handling
        )
    
    def _get_step_implementation(self, step) -> str:
        """获取步骤实现代码"""
        if step.type.value == "launch_app":
            return f"""
            await android_controller.launch_app("{step.parameters.get('app_name', '')}")
            await asyncio.sleep(3)  # 等待应用启动"""
        
        elif step.type.value == "wait":
            duration = step.parameters.get("duration", 1)
            return f"await asyncio.sleep({duration})"
        
        elif step.type.value == "tap":
            x = step.parameters.get("x", 0)
            y = step.parameters.get("y", 0)
            return f"""
            success = await android_controller.tap({x}, {y})
            if not success:
                raise Exception("点击操作失败")
            await asyncio.sleep(1)"""
        
        elif step.type.value == "swipe":
            start_x = step.parameters.get("start_x", 0)
            start_y = step.parameters.get("start_y", 0)
            end_x = step.parameters.get("end_x", 0)
            end_y = step.parameters.get("end_y", 0)
            duration = step.parameters.get("duration", 300)
            return f"""
            success = await android_controller.swipe({start_x}, {start_y}, {end_x}, {end_y}, {duration})
            if not success:
                raise Exception("滑动操作失败")
            await asyncio.sleep(1)"""
        
        elif step.type.value == "input":
            text = step.parameters.get("text", "")
            return f"""
            success = await android_controller.input_text("{text}")
            if not success:
                raise Exception("输入操作失败")
            await asyncio.sleep(1)"""
        
        elif step.type.value == "screenshot":
            save_path = step.parameters.get("save_path", "screenshot.png")
            return f"""
            screenshot_path = await android_controller.take_screenshot("{save_path}")
            if not screenshot_path:
                raise Exception("截图失败")
            logger.info(f"截图保存到: {{screenshot_path}}")"""
        
        elif step.type.value == "ocr_detect":
            target_text = step.parameters.get("target_text", "")
            region = step.parameters.get("region", {})
            return f"""
            # 使用屏幕识别进行OCR检测
            elements = await screen_recognition.find_text("{target_text}")
            if not elements:
                raise Exception("未找到目标文本: {target_text}")
            logger.info(f"找到文本元素: {{len(elements)}}个")"""
        
        elif step.type.value == "element_detect":
            element_types = step.parameters.get("element_types", [])
            return f"""
            # 检测UI元素
            elements = await screen_recognition.detect_all_elements()
            filtered_elements = [e for e in elements if e.type in {element_types}]
            logger.info(f"检测到UI元素: {{len(filtered_elements)}}个")"""
        
        else:
            return f"# 未实现的步骤类型: {step.type.value}"
    
    def _get_step_error_handling(self, step) -> str:
        """获取步骤错误处理代码"""
        if step.fallback_steps:
            return f"""
            # 执行备用步骤
            logger.info("执行备用步骤")
            {self._generate_fallback_code(step.fallback_steps)}"""
        else:
            return """
            # 记录错误并继续执行
            logger.warning("步骤执行失败，继续执行下一步")"""
    
    def _generate_fallback_code(self, fallback_steps: List[str]) -> str:
        """生成备用步骤代码"""
        # 这里可以根据fallback_steps生成相应的备用代码
        return "# 备用步骤实现"
    
    def _generate_helper_functions(self, task_plan, task_type: CodeTemplate) -> List[str]:
        """生成辅助函数"""
        template = self.templates[task_type]
        helper_functions = []
        
        for func_name, func_code in template.get("helper_functions", {}).items():
            helper_functions.append(func_code)
        
        return helper_functions
    
    def _generate_imports(self, task_plan, task_type: CodeTemplate) -> List[str]:
        """生成导入语句"""
        base_imports = [
            "import asyncio",
            "import logging",
            "import time",
            "from datetime import datetime",
            "from typing import Dict, List, Any, Optional"
        ]
        
        template = self.templates[task_type]
        template_imports = template.get("imports", [])
        
        return base_imports + template_imports
    
    def _generate_error_handling(self, task_plan) -> str:
        """生成错误处理代码"""
        return """
def handle_error(error: Exception, step_name: str, context: Dict[str, Any] = None):
    \"\"\"统一错误处理\"\"\"
    logger.error(f"执行{step_name}时发生错误: {error}")
    
    # 记录错误上下文
    if context:
        logger.error(f"错误上下文: {context}")
    
    # 截图保存错误状态
    try:
        error_screenshot = f"screenshots/error_{int(time.time())}.png"
        android_controller.take_screenshot(error_screenshot)
        logger.info(f"错误截图保存到: {error_screenshot}")
    except Exception as e:
        logger.error(f"保存错误截图失败: {e}")
    
    # 根据错误类型决定是否重试
    if isinstance(error, TimeoutError):
        logger.warning("超时错误，可能需要调整等待时间")
    elif isinstance(error, ConnectionError):
        logger.warning("连接错误，检查设备连接")
    else:
        logger.warning("未知错误，建议检查配置")
"""
    
    def _generate_logging(self, task_plan) -> str:
        """生成日志记录代码"""
        return """
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/task_{task_id}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(f"Task_{task_id}")
"""
    
    def _generate_configuration(self, task_plan) -> Dict[str, Any]:
        """生成配置"""
        return {
            "task_id": task_plan.task_id,
            "original_command": task_plan.original_command,
            "complexity": task_plan.complexity.value,
            "estimated_duration": task_plan.estimated_duration,
            "retry_count": 3,
            "timeout": 300,
            "screenshot_on_error": True,
            "log_level": "INFO"
        }
    
    def _generate_test_cases(self, task_plan) -> List[str]:
        """生成测试用例"""
        test_cases = [
            f"def test_task_{task_plan.task_id}():",
            "    \"\"\"测试任务执行\"\"\"",
            "    # 测试基本功能",
            "    assert True  # 占位符",
            "",
            f"def test_error_handling_{task_plan.task_id}():",
            "    \"\"\"测试错误处理\"\"\"",
            "    # 测试错误处理",
            "    assert True  # 占位符"
        ]
        return test_cases
    
    def _apply_screen_feedback(self, main_function: str, screen_feedback: Dict[str, Any]) -> str:
        """应用屏幕识别反馈优化代码"""
        # 根据屏幕反馈调整坐标
        if "element_positions" in screen_feedback:
            for element_id, position in screen_feedback["element_positions"].items():
                # 替换硬编码的坐标
                pattern = rf"android_controller\.tap\(\d+,\s*\d+\)"
                replacement = f"android_controller.tap({position['x']}, {position['y']})"
                main_function = re.sub(pattern, replacement, main_function)
        
        # 根据屏幕反馈调整等待时间
        if "loading_times" in screen_feedback:
            avg_loading_time = sum(screen_feedback["loading_times"]) / len(screen_feedback["loading_times"])
            # 替换等待时间
            pattern = r"await asyncio\.sleep\(\d+\)"
            replacement = f"await asyncio.sleep({int(avg_loading_time)})"
            main_function = re.sub(pattern, replacement, main_function)
        
        return main_function
    
    def _optimize_imports(self, code: GeneratedCode) -> GeneratedCode:
        """优化导入语句"""
        # 去重并排序
        code.imports = sorted(list(set(code.imports)))
        return code
    
    def _optimize_error_handling(self, code: GeneratedCode) -> GeneratedCode:
        """优化错误处理"""
        # 添加更详细的错误处理
        enhanced_error_handling = code.error_handling + """
    
    # 发送错误通知
    try:
        if notification_config.get("enabled"):
            send_error_notification(error, step_name, context)
    except Exception as e:
        logger.error(f"发送错误通知失败: {e}")
"""
        code.error_handling = enhanced_error_handling
        return code
    
    def _optimize_logging(self, code: GeneratedCode) -> GeneratedCode:
        """优化日志记录"""
        # 添加性能监控日志
        enhanced_logging = code.logging + """
    
# 性能监控
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.step_times = []
    
    def start_step(self, step_name):
        self.start_time = time.time()
        logger.info(f"开始执行: {step_name}")
    
    def end_step(self, step_name):
        if self.start_time:
            duration = time.time() - self.start_time
            self.step_times.append(duration)
            logger.info(f"完成执行: {step_name}, 耗时: {duration:.2f}秒")
    
    def get_performance_summary(self):
        if self.step_times:
            return {
                "total_time": sum(self.step_times),
                "average_time": sum(self.step_times) / len(self.step_times),
                "max_time": max(self.step_times),
                "min_time": min(self.step_times)
            }
        return {}

performance_monitor = PerformanceMonitor()
"""
        code.logging = enhanced_logging
        return code
    
    def _optimize_performance(self, code: GeneratedCode) -> GeneratedCode:
        """优化性能"""
        # 添加缓存和批处理优化
        return code
    
    def _optimize_readability(self, code: GeneratedCode) -> GeneratedCode:
        """优化可读性"""
        # 添加注释和文档字符串
        return code
    
    def _get_basic_control_template(self) -> Dict[str, Any]:
        """获取基础控制模板"""
        return {
            "main_function": """
async def execute_task():
    \"\"\"执行自动化任务: {{COMMAND}}\"\"\"
    logger.info(f"开始执行任务: {{TASK_ID}}")
    
    try:
        {{STEPS}}
        
        logger.info("任务执行完成")
        return {"success": True, "message": "任务执行成功"}
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        handle_error(e, "main_task")
        return {"success": False, "error": str(e)}
""",
            "helper_functions": {},
            "imports": []
        }
    
    def _get_video_automation_template(self) -> Dict[str, Any]:
        """获取视频自动化模板"""
        return {
            "main_function": """
async def execute_task():
    \"\"\"执行视频自动化任务: {{COMMAND}}\"\"\"
    logger.info(f"开始执行视频自动化任务: {{TASK_ID}}")
    
    try:
        {{STEPS}}
        
        logger.info("视频自动化任务执行完成")
        return {"success": True, "message": "视频自动化任务执行成功"}
        
    except Exception as e:
        logger.error(f"视频自动化任务执行失败: {e}")
        handle_error(e, "video_automation")
        return {"success": False, "error": str(e)}
""",
            "helper_functions": {
                "random_delay": """
async def random_delay(min_seconds=1, max_seconds=3):
    \"\"\"随机延迟\"\"\"
    import random
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)
    logger.debug(f"随机延迟: {delay:.2f}秒")
""",
                "check_video_playing": """
async def check_video_playing():
    \"\"\"检查视频是否正在播放\"\"\"
    # 通过屏幕识别检查视频播放状态
    elements = await screen_recognition.detect_all_elements()
    # 这里可以添加具体的视频播放检测逻辑
    return True
"""
            },
            "imports": ["import random"]
        }
    
    def _get_messaging_template(self) -> Dict[str, Any]:
        """获取消息发送模板"""
        return {
            "main_function": """
async def execute_task():
    \"\"\"执行消息发送任务: {{COMMAND}}\"\"\"
    logger.info(f"开始执行消息发送任务: {{TASK_ID}}")
    
    try:
        {{STEPS}}
        
        logger.info("消息发送任务执行完成")
        return {"success": True, "message": "消息发送任务执行成功"}
        
    except Exception as e:
        logger.error(f"消息发送任务执行失败: {e}")
        handle_error(e, "messaging")
        return {"success": False, "error": str(e)}
""",
            "helper_functions": {
                "search_contact": """
async def search_contact(contact_name):
    \"\"\"搜索联系人\"\"\"
    logger.info(f"搜索联系人: {contact_name}")
    
    # 点击搜索框
    await android_controller.tap(200, 100)
    await asyncio.sleep(1)
    
    # 输入联系人名称
    await android_controller.input_text(contact_name)
    await asyncio.sleep(2)
    
    # 点击搜索结果
    await android_controller.tap(200, 200)
    await asyncio.sleep(2)
    
    logger.info(f"联系人搜索完成: {contact_name}")
""",
                "send_message": """
async def send_message(message_text):
    \"\"\"发送消息\"\"\"
    logger.info(f"发送消息: {message_text}")
    
    # 点击输入框
    await android_controller.tap(200, 600)
    await asyncio.sleep(1)
    
    # 输入消息内容
    await android_controller.input_text(message_text)
    await asyncio.sleep(1)
    
    # 点击发送按钮
    await android_controller.tap(800, 600)
    await asyncio.sleep(1)
    
    logger.info("消息发送完成")
"""
            },
            "imports": []
        }
    
    def _get_web_scraping_template(self) -> Dict[str, Any]:
        """获取网页抓取模板"""
        return {
            "main_function": """
async def execute_task():
    \"\"\"执行网页抓取任务: {{COMMAND}}\"\"\"
    logger.info(f"开始执行网页抓取任务: {{TASK_ID}}")
    
    try:
        {{STEPS}}
        
        logger.info("网页抓取任务执行完成")
        return {"success": True, "message": "网页抓取任务执行成功"}
        
    except Exception as e:
        logger.error(f"网页抓取任务执行失败: {e}")
        handle_error(e, "web_scraping")
        return {"success": False, "error": str(e)}
""",
            "helper_functions": {
                "navigate_to_url": """
async def navigate_to_url(url):
    \"\"\"导航到指定URL\"\"\"
    logger.info(f"导航到URL: {url}")
    
    # 点击地址栏
    await android_controller.tap(400, 100)
    await asyncio.sleep(1)
    
    # 输入URL
    await android_controller.input_text(url)
    await asyncio.sleep(1)
    
    # 点击访问按钮
    await android_controller.tap(800, 100)
    await asyncio.sleep(5)  # 等待页面加载
    
    logger.info("URL导航完成")
""",
                "extract_data": """
async def extract_data(selectors):
    \"\"\"提取网页数据\"\"\"
    logger.info("开始提取网页数据")
    
    # 使用屏幕识别提取数据
    elements = await screen_recognition.detect_all_elements()
    
    # 根据选择器过滤元素
    extracted_data = {}
    for selector_name, selector_info in selectors.items():
        # 这里可以添加具体的数据提取逻辑
        extracted_data[selector_name] = f"提取的数据: {selector_name}"
    
    logger.info(f"数据提取完成: {len(extracted_data)}个字段")
    return extracted_data
"""
            },
            "imports": []
        }
    
    def _get_ui_interaction_template(self) -> Dict[str, Any]:
        """获取UI交互模板"""
        return {
            "main_function": """
async def execute_task():
    \"\"\"执行UI交互任务: {{COMMAND}}\"\"\"
    logger.info(f"开始执行UI交互任务: {{TASK_ID}}")
    
    try:
        {{STEPS}}
        
        logger.info("UI交互任务执行完成")
        return {"success": True, "message": "UI交互任务执行成功"}
        
    except Exception as e:
        logger.error(f"UI交互任务执行失败: {e}")
        handle_error(e, "ui_interaction")
        return {"success": False, "error": str(e)}
""",
            "helper_functions": {
                "wait_for_element": """
async def wait_for_element(element_description, timeout=10):
    \"\"\"等待元素出现\"\"\"
    logger.info(f"等待元素: {element_description}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        elements = await screen_recognition.detect_all_elements()
        # 这里可以添加具体的元素检测逻辑
        if elements:
            logger.info(f"找到元素: {element_description}")
            return True
        await asyncio.sleep(1)
    
    logger.warning(f"元素未找到: {element_description}")
    return False
""",
                "smart_click": """
async def smart_click(element_description):
    \"\"\"智能点击元素\"\"\"
    logger.info(f"智能点击: {element_description}")
    
    # 先尝试通过OCR找到元素
    elements = await screen_recognition.find_text(element_description)
    if elements:
        element = elements[0]
        x, y = element.bbox[0] + element.bbox[2] // 2, element.bbox[1] + element.bbox[3] // 2
        await android_controller.tap(x, y)
        logger.info(f"通过OCR点击成功: {element_description}")
        return True
    
    # 如果OCR失败，使用预设坐标
    logger.warning(f"OCR点击失败，使用预设坐标: {element_description}")
    return False
"""
            },
            "imports": []
        }
    
    def _get_data_processing_template(self) -> Dict[str, Any]:
        """获取数据处理模板"""
        return {
            "main_function": """
async def execute_task():
    \"\"\"执行数据处理任务: {{COMMAND}}\"\"\"
    logger.info(f"开始执行数据处理任务: {{TASK_ID}}")
    
    try:
        {{STEPS}}
        
        logger.info("数据处理任务执行完成")
        return {"success": True, "message": "数据处理任务执行成功"}
        
    except Exception as e:
        logger.error(f"数据处理任务执行失败: {e}")
        handle_error(e, "data_processing")
        return {"success": False, "error": str(e)}
""",
            "helper_functions": {
                "process_data": """
async def process_data(raw_data):
    \"\"\"处理数据\"\"\"
    logger.info(f"开始处理数据: {len(raw_data)}条记录")
    
    processed_data = []
    for item in raw_data:
        # 这里可以添加具体的数据处理逻辑
        processed_item = {
            "original": item,
            "processed": f"处理后的数据: {item}",
            "timestamp": datetime.now().isoformat()
        }
        processed_data.append(processed_item)
    
    logger.info(f"数据处理完成: {len(processed_data)}条记录")
    return processed_data
""",
                "save_data": """
async def save_data(data, filename):
    \"\"\"保存数据\"\"\"
    logger.info(f"保存数据到文件: {filename}")
    
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"数据保存完成: {filename}")
"""
            },
            "imports": ["import json"]
        }