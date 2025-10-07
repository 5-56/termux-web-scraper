"""
Android设备控制模块
提供屏幕操作、应用控制、系统交互等功能
"""

import subprocess
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..utils.config_manager import ConfigManager


class ActionType(Enum):
    """操作类型枚举"""
    TAP = "tap"
    SWIPE = "swipe"
    INPUT = "input"
    KEY = "key"
    SCREENSHOT = "screenshot"
    LAUNCH_APP = "launch_app"
    CLOSE_APP = "close_app"
    BACK = "back"
    HOME = "home"
    RECENTS = "recents"


@dataclass
class Action:
    """操作数据结构"""
    type: ActionType
    parameters: Dict[str, Any]
    delay: float = 1.0


class AndroidController:
    """Android设备控制器"""
    
    def __init__(self, config: ConfigManager):
        """
        初始化Android控制器
        
        Args:
            config: 配置管理器
        """
        self.config = config
        self.logger = logging.getLogger("AndroidController")
        
        # ADB连接配置
        self.adb_path = config.get("android.adb_path", "adb")
        self.device_id = config.get("android.device_id", "")
        
        # 屏幕尺寸
        self.screen_width = 0
        self.screen_height = 0
        
        # 应用包名映射
        self.app_packages = {
            "微信": "com.tencent.mm",
            "抖音": "com.ss.android.ugc.aweme",
            "快手": "com.smile.gifmaker",
            "微博": "com.sina.weibo",
            "淘宝": "com.taobao.taobao",
            "支付宝": "com.eg.android.AlipayGphone",
            "浏览器": "com.android.chrome",
            "设置": "com.android.settings"
        }
        
        self.logger.info("Android控制器初始化完成")
    
    async def start(self):
        """启动Android控制器"""
        try:
            # 检查ADB连接
            await self._check_adb_connection()
            
            # 获取屏幕尺寸
            await self._get_screen_size()
            
            self.logger.info("Android控制器启动成功")
            
        except Exception as e:
            self.logger.error(f"Android控制器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止Android控制器"""
        self.logger.info("Android控制器已停止")
    
    async def _check_adb_connection(self):
        """检查ADB连接状态"""
        try:
            cmd = [self.adb_path, "devices"]
            if self.device_id:
                cmd.extend(["-s", self.device_id])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise Exception(f"ADB连接失败: {result.stderr}")
            
            devices = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            connected_devices = [line for line in devices if 'device' in line and 'offline' not in line]
            
            if not connected_devices:
                raise Exception("没有连接的Android设备")
            
            self.logger.info(f"ADB连接成功，发现 {len(connected_devices)} 个设备")
            
        except subprocess.TimeoutExpired:
            raise Exception("ADB连接超时")
        except Exception as e:
            raise Exception(f"ADB连接检查失败: {e}")
    
    async def _get_screen_size(self):
        """获取屏幕尺寸"""
        try:
            cmd = [self.adb_path, "shell", "wm", "size"]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "wm", "size"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise Exception(f"获取屏幕尺寸失败: {result.stderr}")
            
            # 解析屏幕尺寸 "Physical size: 1080x2340"
            size_line = result.stdout.strip()
            if "Physical size:" in size_line:
                size_str = size_line.split("Physical size:")[1].strip()
                width, height = map(int, size_str.split('x'))
                self.screen_width = width
                self.screen_height = height
                
                self.logger.info(f"屏幕尺寸: {width}x{height}")
            else:
                raise Exception("无法解析屏幕尺寸")
                
        except Exception as e:
            raise Exception(f"获取屏幕尺寸失败: {e}")
    
    async def tap(self, x: int, y: int, duration: float = 0.1) -> bool:
        """
        点击屏幕指定位置
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 点击持续时间
            
        Returns:
            操作是否成功
        """
        try:
            # 确保坐标在屏幕范围内
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))
            
            cmd = [self.adb_path, "shell", "input", "tap", str(x), str(y)]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "input", "tap", str(x), str(y)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info(f"点击坐标: ({x}, {y})")
                return True
            else:
                self.logger.error(f"点击失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"点击操作异常: {e}")
            return False
    
    async def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 300) -> bool:
        """
        滑动屏幕
        
        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 滑动持续时间(毫秒)
            
        Returns:
            操作是否成功
        """
        try:
            cmd = [
                self.adb_path, "shell", "input", "swipe",
                str(start_x), str(start_y), str(end_x), str(end_y), str(duration)
            ]
            if self.device_id:
                cmd = [
                    self.adb_path, "-s", self.device_id, "shell", "input", "swipe",
                    str(start_x), str(start_y), str(end_x), str(end_y), str(duration)
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info(f"滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
                return True
            else:
                self.logger.error(f"滑动失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"滑动操作异常: {e}")
            return False
    
    async def input_text(self, text: str) -> bool:
        """
        输入文本
        
        Args:
            text: 要输入的文本
            
        Returns:
            操作是否成功
        """
        try:
            # 转义特殊字符
            escaped_text = text.replace(' ', '%s').replace('&', '\\&')
            
            cmd = [self.adb_path, "shell", "input", "text", escaped_text]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "input", "text", escaped_text]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info(f"输入文本: {text}")
                return True
            else:
                self.logger.error(f"输入文本失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"输入文本异常: {e}")
            return False
    
    async def press_key(self, key_code: str) -> bool:
        """
        按下按键
        
        Args:
            key_code: 按键代码 (如: KEYCODE_HOME, KEYCODE_BACK, KEYCODE_ENTER)
            
        Returns:
            操作是否成功
        """
        try:
            cmd = [self.adb_path, "shell", "input", "keyevent", key_code]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "input", "keyevent", key_code]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info(f"按下按键: {key_code}")
                return True
            else:
                self.logger.error(f"按键失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"按键操作异常: {e}")
            return False
    
    async def take_screenshot(self, save_path: str = None) -> Optional[str]:
        """
        截取屏幕截图
        
        Args:
            save_path: 保存路径，如果为None则使用临时路径
            
        Returns:
            截图文件路径
        """
        try:
            if save_path is None:
                timestamp = int(time.time())
                save_path = f"/tmp/screenshot_{timestamp}.png"
            
            # 在设备上截取截图
            device_path = "/sdcard/screenshot.png"
            cmd = [self.adb_path, "shell", "screencap", "-p", device_path]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "screencap", "-p", device_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise Exception(f"截取截图失败: {result.stderr}")
            
            # 将截图从设备拉取到本地
            pull_cmd = [self.adb_path, "pull", device_path, save_path]
            if self.device_id:
                pull_cmd = [self.adb_path, "-s", self.device_id, "pull", device_path, save_path]
            
            pull_result = subprocess.run(pull_cmd, capture_output=True, text=True, timeout=10)
            
            if pull_result.returncode == 0:
                self.logger.info(f"截图保存到: {save_path}")
                return save_path
            else:
                raise Exception(f"拉取截图失败: {pull_result.stderr}")
                
        except Exception as e:
            self.logger.error(f"截图操作异常: {e}")
            return None
    
    async def launch_app(self, app_name: str) -> bool:
        """
        启动应用
        
        Args:
            app_name: 应用名称或包名
            
        Returns:
            操作是否成功
        """
        try:
            # 获取应用包名
            package_name = self.app_packages.get(app_name, app_name)
            
            cmd = [self.adb_path, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info(f"启动应用: {app_name} ({package_name})")
                return True
            else:
                self.logger.error(f"启动应用失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"启动应用异常: {e}")
            return False
    
    async def close_app(self, app_name: str) -> bool:
        """
        关闭应用
        
        Args:
            app_name: 应用名称或包名
            
        Returns:
            操作是否成功
        """
        try:
            package_name = self.app_packages.get(app_name, app_name)
            
            cmd = [self.adb_path, "shell", "am", "force-stop", package_name]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "am", "force-stop", package_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info(f"关闭应用: {app_name} ({package_name})")
                return True
            else:
                self.logger.error(f"关闭应用失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"关闭应用异常: {e}")
            return False
    
    async def get_current_app(self) -> Optional[str]:
        """
        获取当前前台应用
        
        Returns:
            当前应用包名
        """
        try:
            cmd = [self.adb_path, "shell", "dumpsys", "window", "windows", "|", "grep", "-E", "mCurrentFocus|mFocusedApp"]
            if self.device_id:
                cmd = [self.adb_path, "-s", self.device_id, "shell", "dumpsys", "window", "windows", "|", "grep", "-E", "mCurrentFocus|mFocusedApp"]
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                # 解析输出获取包名
                if "mCurrentFocus" in output:
                    # 提取包名
                    parts = output.split()
                    for part in parts:
                        if "/" in part and "." in part:
                            package_name = part.split("/")[0]
                            self.logger.info(f"当前应用: {package_name}")
                            return package_name
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取当前应用异常: {e}")
            return None
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        执行通用命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            执行结果
        """
        try:
            # 解析命令
            if command.startswith("点击"):
                # 解析点击命令 "点击(100,200)"
                import re
                match = re.search(r'点击\((\d+),(\d+)\)', command)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    success = await self.tap(x, y)
                    return {"action": "tap", "success": success, "coordinates": (x, y)}
            
            elif command.startswith("滑动"):
                # 解析滑动命令 "滑动(100,200,300,400)"
                import re
                match = re.search(r'滑动\((\d+),(\d+),(\d+),(\d+)\)', command)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    success = await self.swipe(x1, y1, x2, y2)
                    return {"action": "swipe", "success": success, "coordinates": (x1, y1, x2, y2)}
            
            elif command.startswith("输入"):
                # 解析输入命令 "输入:文本内容"
                text = command[3:]  # 去掉"输入"前缀
                success = await self.input_text(text)
                return {"action": "input", "success": success, "text": text}
            
            elif command == "返回":
                success = await self.press_key("KEYCODE_BACK")
                return {"action": "back", "success": success}
            
            elif command == "主页":
                success = await self.press_key("KEYCODE_HOME")
                return {"action": "home", "success": success}
            
            elif command == "最近任务":
                success = await self.press_key("KEYCODE_APP_SWITCH")
                return {"action": "recents", "success": success}
            
            else:
                return {"action": "unknown", "success": False, "error": f"未知命令: {command}"}
                
        except Exception as e:
            self.logger.error(f"执行命令异常: {e}")
            return {"action": "error", "success": False, "error": str(e)}
    
    async def execute_action_sequence(self, actions: List[Action]) -> List[Dict[str, Any]]:
        """
        执行操作序列
        
        Args:
            actions: 操作序列
            
        Returns:
            执行结果列表
        """
        results = []
        
        for action in actions:
            try:
                if action.type == ActionType.TAP:
                    x, y = action.parameters["x"], action.parameters["y"]
                    success = await self.tap(x, y)
                    results.append({"action": "tap", "success": success, "coordinates": (x, y)})
                
                elif action.type == ActionType.SWIPE:
                    start_x, start_y = action.parameters["start_x"], action.parameters["start_y"]
                    end_x, end_y = action.parameters["end_x"], action.parameters["end_y"]
                    duration = action.parameters.get("duration", 300)
                    success = await self.swipe(start_x, start_y, end_x, end_y, duration)
                    results.append({"action": "swipe", "success": success, "coordinates": (start_x, start_y, end_x, end_y)})
                
                elif action.type == ActionType.INPUT:
                    text = action.parameters["text"]
                    success = await self.input_text(text)
                    results.append({"action": "input", "success": success, "text": text})
                
                elif action.type == ActionType.KEY:
                    key_code = action.parameters["key_code"]
                    success = await self.press_key(key_code)
                    results.append({"action": "key", "success": success, "key_code": key_code})
                
                elif action.type == ActionType.LAUNCH_APP:
                    app_name = action.parameters["app_name"]
                    success = await self.launch_app(app_name)
                    results.append({"action": "launch_app", "success": success, "app_name": app_name})
                
                elif action.type == ActionType.CLOSE_APP:
                    app_name = action.parameters["app_name"]
                    success = await self.close_app(app_name)
                    results.append({"action": "close_app", "success": success, "app_name": app_name})
                
                # 添加延迟
                if action.delay > 0:
                    await asyncio.sleep(action.delay)
                
            except Exception as e:
                self.logger.error(f"执行操作失败: {e}")
                results.append({"action": action.type.value, "success": False, "error": str(e)})
        
        return results