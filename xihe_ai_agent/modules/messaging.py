"""
消息自动化模块
支持各种通讯平台的消息发送、群聊管理等功能
"""

import asyncio
import random
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .android_control import AndroidController


class MessagePlatform(Enum):
    """消息平台枚举"""
    WECHAT = "wechat"
    QQ = "qq"
    SMS = "sms"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    WEIBO = "weibo"


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"


@dataclass
class MessageTemplate:
    """消息模板"""
    name: str
    content: str
    variables: List[str] = None
    platform: MessagePlatform = MessagePlatform.WECHAT


@dataclass
class Contact:
    """联系人信息"""
    name: str
    platform: MessagePlatform
    identifier: str  # 微信号、QQ号、手机号等
    group: str = None  # 分组


class MessagingAutomation:
    """消息自动化控制器"""
    
    def __init__(self, android_controller: AndroidController, config_manager):
        """
        初始化消息自动化控制器
        
        Args:
            android_controller: Android控制器实例
            config_manager: 配置管理器
        """
        self.android_controller = android_controller
        self.config_manager = config_manager
        self.logger = logging.getLogger("MessagingAutomation")
        
        # 平台配置
        self.platform_configs = {
            MessagePlatform.WECHAT: {
                "app_name": "微信",
                "package_name": "com.tencent.mm",
                "search_selector": "com.tencent.mm:id/f8y",  # 搜索框
                "input_selector": "com.tencent.mm:id/al_",   # 输入框
                "send_selector": "com.tencent.mm:id/anv"     # 发送按钮
            },
            MessagePlatform.QQ: {
                "app_name": "QQ",
                "package_name": "com.tencent.mobileqq",
                "search_selector": "com.tencent.mobileqq:id/et_search_keyword",
                "input_selector": "com.tencent.mobileqq:id/input",
                "send_selector": "com.tencent.mobileqq:id/fun_btn"
            },
            MessagePlatform.SMS: {
                "app_name": "短信",
                "package_name": "com.android.mms",
                "input_selector": "com.android.mms:id/embedded_text_editor",
                "send_selector": "com.android.mms:id/send_button_sms"
            }
        }
        
        # 消息模板
        self.message_templates = [
            MessageTemplate(
                name="问候",
                content="你好！{name}，最近怎么样？",
                variables=["name"],
                platform=MessagePlatform.WECHAT
            ),
            MessageTemplate(
                name="节日祝福",
                content="祝{name}节日快乐！{greeting}",
                variables=["name", "greeting"],
                platform=MessagePlatform.WECHAT
            ),
            MessageTemplate(
                name="工作提醒",
                content="提醒：{task} 需要在 {deadline} 前完成",
                variables=["task", "deadline"],
                platform=MessagePlatform.WECHAT
            ),
            MessageTemplate(
                name="随机问候",
                content="{greeting}",
                variables=["greeting"],
                platform=MessagePlatform.WECHAT
            )
        ]
        
        # 随机问候语
        self.greetings = [
            "你好！",
            "早上好！",
            "下午好！",
            "晚上好！",
            "嗨！",
            "Hello！",
            "最近怎么样？",
            "工作顺利吗？",
            "学习怎么样？",
            "生活愉快！"
        ]
        
        self.logger.info("消息自动化控制器初始化完成")
    
    async def send_message(self, platform: str, recipient: str, content: str, 
                         message_type: str = "text") -> Dict[str, Any]:
        """
        发送消息
        
        Args:
            platform: 消息平台
            recipient: 接收者标识
            content: 消息内容
            message_type: 消息类型
            
        Returns:
            发送结果
        """
        try:
            platform_enum = MessagePlatform(platform)
            config = self.platform_configs[platform_enum]
            
            self.logger.info(f"发送{platform}消息给 {recipient}: {content}")
            
            # 启动应用
            await self.android_controller.launch_app(config["app_name"])
            await asyncio.sleep(3)
            
            # 根据平台执行不同的发送逻辑
            if platform_enum == MessagePlatform.WECHAT:
                result = await self._send_wechat_message(recipient, content)
            elif platform_enum == MessagePlatform.QQ:
                result = await self._send_qq_message(recipient, content)
            elif platform_enum == MessagePlatform.SMS:
                result = await self._send_sms_message(recipient, content)
            else:
                result = await self._send_generic_message(platform, recipient, content)
            
            return {
                "success": True,
                "platform": platform,
                "recipient": recipient,
                "content": content,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_wechat_message(self, recipient: str, content: str) -> Dict[str, Any]:
        """发送微信消息"""
        try:
            # 点击搜索框
            search_x = self.android_controller.screen_width // 2
            search_y = 150
            await self.android_controller.tap(search_x, search_y)
            await asyncio.sleep(1)
            
            # 输入联系人名称
            await self.android_controller.input_text(recipient)
            await asyncio.sleep(2)
            
            # 点击搜索结果
            result_x = self.android_controller.screen_width // 2
            result_y = 300
            await self.android_controller.tap(result_x, result_y)
            await asyncio.sleep(2)
            
            # 点击输入框
            input_x = self.android_controller.screen_width // 2
            input_y = self.android_controller.screen_height - 150
            await self.android_controller.tap(input_x, input_y)
            await asyncio.sleep(1)
            
            # 输入消息内容
            await self.android_controller.input_text(content)
            await asyncio.sleep(1)
            
            # 点击发送按钮
            send_x = self.android_controller.screen_width - 50
            send_y = self.android_controller.screen_height - 100
            await self.android_controller.tap(send_x, send_y)
            
            return {"action": "wechat_send", "success": True}
            
        except Exception as e:
            return {"action": "wechat_send", "success": False, "error": str(e)}
    
    async def _send_qq_message(self, recipient: str, content: str) -> Dict[str, Any]:
        """发送QQ消息"""
        try:
            # 点击搜索框
            search_x = self.android_controller.screen_width // 2
            search_y = 150
            await self.android_controller.tap(search_x, search_y)
            await asyncio.sleep(1)
            
            # 输入联系人名称
            await self.android_controller.input_text(recipient)
            await asyncio.sleep(2)
            
            # 点击搜索结果
            result_x = self.android_controller.screen_width // 2
            result_y = 300
            await self.android_controller.tap(result_x, result_y)
            await asyncio.sleep(2)
            
            # 点击输入框
            input_x = self.android_controller.screen_width // 2
            input_y = self.android_controller.screen_height - 150
            await self.android_controller.tap(input_x, input_y)
            await asyncio.sleep(1)
            
            # 输入消息内容
            await self.android_controller.input_text(content)
            await asyncio.sleep(1)
            
            # 点击发送按钮
            send_x = self.android_controller.screen_width - 50
            send_y = self.android_controller.screen_height - 100
            await self.android_controller.tap(send_x, send_y)
            
            return {"action": "qq_send", "success": True}
            
        except Exception as e:
            return {"action": "qq_send", "success": False, "error": str(e)}
    
    async def _send_sms_message(self, phone_number: str, content: str) -> Dict[str, Any]:
        """发送短信"""
        try:
            # 点击新建短信按钮
            new_sms_x = self.android_controller.screen_width - 100
            new_sms_y = 100
            await self.android_controller.tap(new_sms_x, new_sms_y)
            await asyncio.sleep(2)
            
            # 输入手机号
            phone_x = self.android_controller.screen_width // 2
            phone_y = 200
            await self.android_controller.tap(phone_x, phone_y)
            await self.android_controller.input_text(phone_number)
            await asyncio.sleep(1)
            
            # 点击输入框
            input_x = self.android_controller.screen_width // 2
            input_y = self.android_controller.screen_height - 200
            await self.android_controller.tap(input_x, input_y)
            await asyncio.sleep(1)
            
            # 输入消息内容
            await self.android_controller.input_text(content)
            await asyncio.sleep(1)
            
            # 点击发送按钮
            send_x = self.android_controller.screen_width - 50
            send_y = self.android_controller.screen_height - 100
            await self.android_controller.tap(send_x, send_y)
            
            return {"action": "sms_send", "success": True}
            
        except Exception as e:
            return {"action": "sms_send", "success": False, "error": str(e)}
    
    async def _send_generic_message(self, platform: str, recipient: str, content: str) -> Dict[str, Any]:
        """发送通用消息"""
        try:
            # 启动应用
            await self.android_controller.launch_app(platform)
            await asyncio.sleep(3)
            
            # 尝试找到搜索框并搜索联系人
            search_x = self.android_controller.screen_width // 2
            search_y = 150
            await self.android_controller.tap(search_x, search_y)
            await asyncio.sleep(1)
            
            await self.android_controller.input_text(recipient)
            await asyncio.sleep(2)
            
            # 点击搜索结果
            result_x = self.android_controller.screen_width // 2
            result_y = 300
            await self.android_controller.tap(result_x, result_y)
            await asyncio.sleep(2)
            
            # 尝试找到输入框
            input_x = self.android_controller.screen_width // 2
            input_y = self.android_controller.screen_height - 150
            await self.android_controller.tap(input_x, input_y)
            await asyncio.sleep(1)
            
            # 输入消息
            await self.android_controller.input_text(content)
            await asyncio.sleep(1)
            
            # 尝试找到发送按钮
            send_x = self.android_controller.screen_width - 50
            send_y = self.android_controller.screen_height - 100
            await self.android_controller.tap(send_x, send_y)
            
            return {"action": "generic_send", "success": True}
            
        except Exception as e:
            return {"action": "generic_send", "success": False, "error": str(e)}
    
    async def send_bulk_messages(self, platform: str, contacts: List[Contact], 
                               content: str, delay_range: tuple = (5, 15)) -> Dict[str, Any]:
        """
        批量发送消息
        
        Args:
            platform: 消息平台
            contacts: 联系人列表
            content: 消息内容
            delay_range: 发送间隔范围(秒)
            
        Returns:
            发送结果
        """
        try:
            self.logger.info(f"开始批量发送{platform}消息，联系人数量: {len(contacts)}")
            
            results = []
            success_count = 0
            
            for i, contact in enumerate(contacts):
                try:
                    # 发送消息
                    result = await self.send_message(
                        platform=platform,
                        recipient=contact.identifier,
                        content=content
                    )
                    
                    results.append({
                        "contact": contact.name,
                        "success": result["success"],
                        "error": result.get("error")
                    })
                    
                    if result["success"]:
                        success_count += 1
                    
                    # 随机延迟
                    if i < len(contacts) - 1:  # 最后一个不需要延迟
                        delay = random.uniform(delay_range[0], delay_range[1])
                        await asyncio.sleep(delay)
                    
                except Exception as e:
                    self.logger.error(f"发送给 {contact.name} 失败: {e}")
                    results.append({
                        "contact": contact.name,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "platform": platform,
                "total_contacts": len(contacts),
                "success_count": success_count,
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"批量发送消息失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_template_message(self, template_name: str, platform: str, 
                                  contacts: List[Contact], variables: Dict[str, str] = None) -> Dict[str, Any]:
        """
        发送模板消息
        
        Args:
            template_name: 模板名称
            platform: 消息平台
            contacts: 联系人列表
            variables: 模板变量
            
        Returns:
            发送结果
        """
        try:
            # 查找模板
            template = None
            for t in self.message_templates:
                if t.name == template_name and t.platform.value == platform:
                    template = t
                    break
            
            if not template:
                raise Exception(f"未找到模板: {template_name}")
            
            # 生成消息内容
            content = template.content
            if variables:
                for key, value in variables.items():
                    content = content.replace(f"{{{key}}}", value)
            
            # 处理随机变量
            if "{greeting}" in content:
                content = content.replace("{greeting}", random.choice(self.greetings))
            
            # 批量发送
            return await self.send_bulk_messages(platform, contacts, content)
            
        except Exception as e:
            self.logger.error(f"发送模板消息失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def auto_reply_messages(self, platform: str, reply_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        自动回复消息
        
        Args:
            platform: 消息平台
            reply_rules: 回复规则列表
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"开始{platform}自动回复")
            
            # 启动应用
            platform_config = self.platform_configs[MessagePlatform(platform)]
            await self.android_controller.launch_app(platform_config["app_name"])
            await asyncio.sleep(3)
            
            reply_count = 0
            max_replies = 10  # 最大回复数量
            
            for i in range(max_replies):
                try:
                    # 检查是否有新消息
                    has_new_message = await self._check_new_message()
                    
                    if not has_new_message:
                        await asyncio.sleep(5)  # 等待5秒后重试
                        continue
                    
                    # 获取消息内容
                    message_content = await self._get_latest_message()
                    
                    if not message_content:
                        continue
                    
                    # 匹配回复规则
                    reply_content = await self._match_reply_rule(message_content, reply_rules)
                    
                    if reply_content:
                        # 发送回复
                        await self._send_reply(reply_content)
                        reply_count += 1
                        
                        self.logger.info(f"自动回复: {reply_content}")
                    
                    # 延迟后继续
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    self.logger.error(f"自动回复第{i+1}次失败: {e}")
                    continue
            
            return {
                "success": True,
                "platform": platform,
                "replies_sent": reply_count
            }
            
        except Exception as e:
            self.logger.error(f"自动回复失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_new_message(self) -> bool:
        """检查是否有新消息"""
        # 这里可以通过截图识别新消息提示
        # 简化实现，返回随机结果
        return random.random() < 0.3
    
    async def _get_latest_message(self) -> Optional[str]:
        """获取最新消息内容"""
        # 这里可以通过OCR识别消息内容
        # 简化实现，返回示例消息
        sample_messages = [
            "你好",
            "在吗？",
            "最近怎么样？",
            "工作忙吗？",
            "吃饭了吗？"
        ]
        return random.choice(sample_messages)
    
    async def _match_reply_rule(self, message: str, rules: List[Dict[str, Any]]) -> Optional[str]:
        """匹配回复规则"""
        for rule in rules:
            keywords = rule.get("keywords", [])
            reply = rule.get("reply", "")
            
            if any(keyword in message for keyword in keywords):
                return reply
        
        return None
    
    async def _send_reply(self, content: str):
        """发送回复"""
        # 点击输入框
        input_x = self.android_controller.screen_width // 2
        input_y = self.android_controller.screen_height - 150
        await self.android_controller.tap(input_x, input_y)
        await asyncio.sleep(1)
        
        # 输入回复内容
        await self.android_controller.input_text(content)
        await asyncio.sleep(1)
        
        # 点击发送按钮
        send_x = self.android_controller.screen_width - 50
        send_y = self.android_controller.screen_height - 100
        await self.android_controller.tap(send_x, send_y)
    
    def add_message_template(self, template: MessageTemplate):
        """添加消息模板"""
        self.message_templates.append(template)
        self.logger.info(f"添加消息模板: {template.name}")
    
    def get_message_templates(self, platform: str = None) -> List[MessageTemplate]:
        """获取消息模板"""
        if platform:
            return [t for t in self.message_templates if t.platform.value == platform]
        return self.message_templates