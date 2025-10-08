"""
UI自动化模块
专门处理应用内操作、视频刷取、界面交互等任务
"""

import asyncio
import random
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .android_control import AndroidController, Action, ActionType


class VideoPlatform(Enum):
    """视频平台枚举"""
    DOUYIN = "douyin"
    KUAISHOU = "kuaishou"
    BILIBILI = "bilibili"
    WEIBO = "weibo"
    TIKTOK = "tiktok"


class AppType(Enum):
    """应用类型枚举"""
    SOCIAL_MEDIA = "social_media"
    E_COMMERCE = "e_commerce"
    NEWS = "news"
    VIDEO = "video"
    MESSAGING = "messaging"


@dataclass
class VideoConfig:
    """视频配置"""
    platform: VideoPlatform
    watch_duration: int = 30  # 观看时长(秒)
    scroll_interval: int = 5  # 滚动间隔(秒)
    like_probability: float = 0.1  # 点赞概率
    comment_probability: float = 0.05  # 评论概率
    share_probability: float = 0.02  # 分享概率


@dataclass
class AppConfig:
    """应用配置"""
    app_name: str
    app_type: AppType
    package_name: str
    main_activity: str
    ui_elements: Dict[str, str]  # UI元素定位信息


class UIAutomation:
    """UI自动化控制器"""
    
    def __init__(self, android_controller: AndroidController, config_manager):
        """
        初始化UI自动化控制器
        
        Args:
            android_controller: Android控制器实例
            config_manager: 配置管理器
        """
        self.android_controller = android_controller
        self.config_manager = config_manager
        self.logger = logging.getLogger("UIAutomation")
        
        # 视频平台配置
        self.video_configs = {
            VideoPlatform.DOUYIN: VideoConfig(
                platform=VideoPlatform.DOUYIN,
                watch_duration=30,
                scroll_interval=5,
                like_probability=0.1,
                comment_probability=0.05,
                share_probability=0.02
            ),
            VideoPlatform.KUAISHOU: VideoConfig(
                platform=VideoPlatform.KUAISHOU,
                watch_duration=25,
                scroll_interval=4,
                like_probability=0.08,
                comment_probability=0.03,
                share_probability=0.01
            ),
            VideoPlatform.BILIBILI: VideoConfig(
                platform=VideoPlatform.BILIBILI,
                watch_duration=45,
                scroll_interval=8,
                like_probability=0.15,
                comment_probability=0.08,
                share_probability=0.03
            )
        }
        
        # 应用配置
        self.app_configs = {
            "微信": AppConfig(
                app_name="微信",
                app_type=AppType.MESSAGING,
                package_name="com.tencent.mm",
                main_activity="com.tencent.mm.ui.LauncherUI",
                ui_elements={
                    "搜索框": "com.tencent.mm:id/f8y",
                    "聊天列表": "com.tencent.mm:id/b4e",
                    "输入框": "com.tencent.mm:id/al_",
                    "发送按钮": "com.tencent.mm:id/anv"
                }
            ),
            "抖音": AppConfig(
                app_name="抖音",
                app_type=AppType.VIDEO,
                package_name="com.ss.android.ugc.aweme",
                main_activity="com.ss.android.ugc.aweme.main.MainActivity",
                ui_elements={
                    "视频区域": "com.ss.android.ugc.aweme:id/feed_list",
                    "点赞按钮": "com.ss.android.ugc.aweme:id/awh",
                    "评论按钮": "com.ss.android.ugc.aweme:id/awj",
                    "分享按钮": "com.ss.android.ugc.aweme:id/awk"
                }
            ),
            "快手": AppConfig(
                app_name="快手",
                app_type=AppType.VIDEO,
                package_name="com.smile.gifmaker",
                main_activity="com.smile.gifmaker.MainActivity",
                ui_elements={
                    "视频区域": "com.smile.gifmaker:id/feed_list",
                    "点赞按钮": "com.smile.gifmaker:id/like",
                    "评论按钮": "com.smile.gifmaker:id/comment",
                    "分享按钮": "com.smile.gifmaker:id/share"
                }
            )
        }
        
        self.logger.info("UI自动化控制器初始化完成")
    
    async def watch_videos(self, platform: str = "douyin", duration: int = 300) -> Dict[str, Any]:
        """
        自动刷视频
        
        Args:
            platform: 视频平台 (douyin, kuaishou, bilibili)
            duration: 总观看时长(秒)
            
        Returns:
            执行结果
        """
        try:
            platform_enum = VideoPlatform(platform)
            config = self.video_configs[platform_enum]
            
            self.logger.info(f"开始刷{platform}视频，总时长: {duration}秒")
            
            # 启动应用
            app_name = self._get_app_name_by_platform(platform_enum)
            await self.android_controller.launch_app(app_name)
            await asyncio.sleep(3)  # 等待应用启动
            
            # 开始刷视频
            start_time = time.time()
            video_count = 0
            actions_performed = []
            
            while time.time() - start_time < duration:
                try:
                    # 观看当前视频
                    watch_result = await self._watch_current_video(config)
                    actions_performed.append(watch_result)
                    
                    # 随机滑动到下一个视频
                    await self._scroll_to_next_video()
                    
                    video_count += 1
                    
                    # 随机延迟
                    delay = random.uniform(1, 3)
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    self.logger.error(f"刷视频过程中出错: {e}")
                    continue
            
            return {
                "success": True,
                "platform": platform,
                "duration": duration,
                "videos_watched": video_count,
                "actions_performed": actions_performed
            }
            
        except Exception as e:
            self.logger.error(f"刷视频失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _watch_current_video(self, config: VideoConfig) -> Dict[str, Any]:
        """
        观看当前视频
        
        Args:
            config: 视频配置
            
        Returns:
            观看结果
        """
        actions = []
        
        # 观看视频
        await asyncio.sleep(config.watch_duration)
        actions.append("观看视频")
        
        # 随机点赞
        if random.random() < config.like_probability:
            await self._like_video()
            actions.append("点赞")
        
        # 随机评论
        if random.random() < config.comment_probability:
            comment_text = await self._generate_random_comment()
            await self._comment_video(comment_text)
            actions.append(f"评论: {comment_text}")
        
        # 随机分享
        if random.random() < config.share_probability:
            await self._share_video()
            actions.append("分享")
        
        return {
            "watch_duration": config.watch_duration,
            "actions": actions
        }
    
    async def _scroll_to_next_video(self):
        """滑动到下一个视频"""
        # 从屏幕中央向上滑动
        start_x = self.android_controller.screen_width // 2
        start_y = self.android_controller.screen_height // 2
        end_x = start_x
        end_y = start_y - 300  # 向上滑动300像素
        
        await self.android_controller.swipe(start_x, start_y, end_x, end_y, 300)
    
    async def _like_video(self):
        """点赞视频"""
        # 点击点赞按钮区域 (通常在右下角)
        like_x = self.android_controller.screen_width - 100
        like_y = self.android_controller.screen_height - 200
        
        await self.android_controller.tap(like_x, like_y)
    
    async def _comment_video(self, comment_text: str):
        """评论视频"""
        # 点击评论按钮
        comment_x = self.android_controller.screen_width - 200
        comment_y = self.android_controller.screen_height - 200
        
        await self.android_controller.tap(comment_x, comment_y)
        await asyncio.sleep(1)
        
        # 输入评论
        await self.android_controller.input_text(comment_text)
        await asyncio.sleep(1)
        
        # 点击发送按钮
        send_x = self.android_controller.screen_width - 50
        send_y = self.android_controller.screen_height - 100
        
        await self.android_controller.tap(send_x, send_y)
        await asyncio.sleep(1)
        
        # 返回主界面
        await self.android_controller.press_key("KEYCODE_BACK")
    
    async def _share_video(self):
        """分享视频"""
        # 点击分享按钮
        share_x = self.android_controller.screen_width - 300
        share_y = self.android_controller.screen_height - 200
        
        await self.android_controller.tap(share_x, share_y)
        await asyncio.sleep(1)
        
        # 选择分享到微信
        wechat_x = self.android_controller.screen_width // 2
        wechat_y = self.android_controller.screen_height // 2 + 100
        
        await self.android_controller.tap(wechat_x, wechat_y)
        await asyncio.sleep(2)
        
        # 返回主界面
        await self.android_controller.press_key("KEYCODE_BACK")
        await self.android_controller.press_key("KEYCODE_BACK")
    
    async def _generate_random_comment(self) -> str:
        """生成随机评论"""
        comments = [
            "太棒了！",
            "666",
            "学到了",
            "哈哈哈",
            "赞一个",
            "不错不错",
            "支持",
            "好看",
            "有趣",
            "👍"
        ]
        return random.choice(comments)
    
    def _get_app_name_by_platform(self, platform: VideoPlatform) -> str:
        """根据平台获取应用名称"""
        platform_map = {
            VideoPlatform.DOUYIN: "抖音",
            VideoPlatform.KUAISHOU: "快手",
            VideoPlatform.BILIBILI: "哔哩哔哩",
            VideoPlatform.WEIBO: "微博"
        }
        return platform_map.get(platform, "抖音")
    
    async def execute_ui_task(self, app_name: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行UI任务
        
        Args:
            app_name: 应用名称
            actions: 操作列表
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"开始执行UI任务: {app_name}")
            
            # 启动应用
            await self.android_controller.launch_app(app_name)
            await asyncio.sleep(3)
            
            # 执行操作序列
            results = []
            for action in actions:
                result = await self._execute_ui_action(action)
                results.append(result)
                
                # 操作间延迟
                await asyncio.sleep(1)
            
            return {
                "success": True,
                "app_name": app_name,
                "actions_count": len(actions),
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"执行UI任务失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_ui_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个UI操作
        
        Args:
            action: 操作定义
            
        Returns:
            执行结果
        """
        action_type = action.get("type")
        
        if action_type == "tap":
            x, y = action.get("x", 0), action.get("y", 0)
            success = await self.android_controller.tap(x, y)
            return {"type": "tap", "success": success, "coordinates": (x, y)}
        
        elif action_type == "swipe":
            start_x, start_y = action.get("start_x", 0), action.get("start_y", 0)
            end_x, end_y = action.get("end_x", 0), action.get("end_y", 0)
            duration = action.get("duration", 300)
            success = await self.android_controller.swipe(start_x, start_y, end_x, end_y, duration)
            return {"type": "swipe", "success": success, "coordinates": (start_x, start_y, end_x, end_y)}
        
        elif action_type == "input":
            text = action.get("text", "")
            success = await self.android_controller.input_text(text)
            return {"type": "input", "success": success, "text": text}
        
        elif action_type == "key":
            key_code = action.get("key_code", "KEYCODE_BACK")
            success = await self.android_controller.press_key(key_code)
            return {"type": "key", "success": success, "key_code": key_code}
        
        else:
            return {"type": "unknown", "success": False, "error": f"未知操作类型: {action_type}"}
    
    async def auto_like_posts(self, app_name: str, count: int = 10) -> Dict[str, Any]:
        """
        自动点赞帖子
        
        Args:
            app_name: 应用名称
            count: 点赞数量
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"开始自动点赞 {app_name} 的 {count} 个帖子")
            
            # 启动应用
            await self.android_controller.launch_app(app_name)
            await asyncio.sleep(3)
            
            liked_count = 0
            for i in range(count):
                try:
                    # 点赞当前帖子
                    await self._like_current_post()
                    liked_count += 1
                    
                    # 滑动到下一个帖子
                    await self._scroll_to_next_post()
                    
                    # 随机延迟
                    delay = random.uniform(2, 5)
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    self.logger.error(f"点赞第{i+1}个帖子失败: {e}")
                    continue
            
            return {
                "success": True,
                "app_name": app_name,
                "target_count": count,
                "liked_count": liked_count
            }
            
        except Exception as e:
            self.logger.error(f"自动点赞失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _like_current_post(self):
        """点赞当前帖子"""
        # 双击屏幕中央区域点赞
        center_x = self.android_controller.screen_width // 2
        center_y = self.android_controller.screen_height // 2
        
        await self.android_controller.tap(center_x, center_y)
        await asyncio.sleep(0.1)
        await self.android_controller.tap(center_x, center_y)
    
    async def _scroll_to_next_post(self):
        """滑动到下一个帖子"""
        # 从屏幕中央向上滑动
        start_x = self.android_controller.screen_width // 2
        start_y = self.android_controller.screen_height // 2
        end_x = start_x
        end_y = start_y - 400  # 向上滑动400像素
        
        await self.android_controller.swipe(start_x, start_y, end_x, end_y, 300)
    
    async def auto_follow_users(self, app_name: str, count: int = 5) -> Dict[str, Any]:
        """
        自动关注用户
        
        Args:
            app_name: 应用名称
            count: 关注数量
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"开始自动关注 {app_name} 的 {count} 个用户")
            
            # 启动应用
            await self.android_controller.launch_app(app_name)
            await asyncio.sleep(3)
            
            followed_count = 0
            for i in range(count):
                try:
                    # 关注当前用户
                    await self._follow_current_user()
                    followed_count += 1
                    
                    # 滑动到下一个用户
                    await self._scroll_to_next_user()
                    
                    # 随机延迟
                    delay = random.uniform(3, 8)
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    self.logger.error(f"关注第{i+1}个用户失败: {e}")
                    continue
            
            return {
                "success": True,
                "app_name": app_name,
                "target_count": count,
                "followed_count": followed_count
            }
            
        except Exception as e:
            self.logger.error(f"自动关注失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _follow_current_user(self):
        """关注当前用户"""
        # 点击关注按钮 (通常在右上角)
        follow_x = self.android_controller.screen_width - 80
        follow_y = 200
        
        await self.android_controller.tap(follow_x, follow_y)
    
    async def _scroll_to_next_user(self):
        """滑动到下一个用户"""
        # 从屏幕中央向上滑动
        start_x = self.android_controller.screen_width // 2
        start_y = self.android_controller.screen_height // 2
        end_x = start_x
        end_y = start_y - 500  # 向上滑动500像素
        
        await self.android_controller.swipe(start_x, start_y, end_x, end_y, 300)