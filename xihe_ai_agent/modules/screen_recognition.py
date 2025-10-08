"""
屏幕识别模块
提供实时屏幕识别、OCR、元素检测等功能
"""

import cv2
import numpy as np
import pytesseract
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image
import base64
import io
import asyncio
import time


@dataclass
class DetectedElement:
    """检测到的元素"""
    type: str  # text, button, image, etc.
    text: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    clickable: bool = True


@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    bbox: Tuple[int, int, int, int]
    confidence: float


class ScreenRecognition:
    """屏幕识别器"""
    
    def __init__(self, android_controller):
        """
        初始化屏幕识别器
        
        Args:
            android_controller: Android控制器实例
        """
        self.android_controller = android_controller
        self.logger = logging.getLogger("ScreenRecognition")
        
        # OCR配置
        self.ocr_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz一二三四五六七八九十'
        
        # 元素检测配置
        self.button_templates = []
        self.icon_templates = []
        
        # 缓存
        self.last_screenshot = None
        self.last_screenshot_time = 0
        self.cache_duration = 1.0  # 缓存1秒
        
        self.logger.info("屏幕识别器初始化完成")
    
    async def get_screenshot(self, force_refresh: bool = False) -> np.ndarray:
        """
        获取屏幕截图
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            屏幕截图数组
        """
        current_time = time.time()
        
        # 检查缓存
        if (not force_refresh and 
            self.last_screenshot is not None and 
            current_time - self.last_screenshot_time < self.cache_duration):
            return self.last_screenshot
        
        try:
            # 截取屏幕
            screenshot_path = await self.android_controller.take_screenshot()
            if not screenshot_path:
                raise Exception("截图失败")
            
            # 读取图片
            img = cv2.imread(screenshot_path)
            if img is None:
                raise Exception("无法读取截图")
            
            # 更新缓存
            self.last_screenshot = img
            self.last_screenshot_time = current_time
            
            return img
            
        except Exception as e:
            self.logger.error(f"获取截图失败: {e}")
            raise
    
    async def detect_text(self, region: Optional[Tuple[int, int, int, int]] = None) -> List[OCRResult]:
        """
        检测屏幕中的文本
        
        Args:
            region: 检测区域 (x, y, width, height)，None表示全屏
            
        Returns:
            OCR识别结果列表
        """
        try:
            # 获取截图
            img = await self.get_screenshot()
            
            # 裁剪区域
            if region:
                x, y, w, h = region
                img = img[y:y+h, x:x+w]
            
            # 预处理图片
            processed_img = self._preprocess_for_ocr(img)
            
            # OCR识别
            data = pytesseract.image_to_data(processed_img, config=self.ocr_config, output_type=pytesseract.Output.DICT)
            
            results = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                confidence = float(data['conf'][i])
                
                if text and confidence > 30:  # 过滤低置信度结果
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # 调整坐标（如果裁剪了区域）
                    if region:
                        x += region[0]
                        y += region[1]
                    
                    results.append(OCRResult(
                        text=text,
                        bbox=(x, y, w, h),
                        confidence=confidence
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"文本检测失败: {e}")
            return []
    
    async def find_text(self, target_text: str, exact_match: bool = False) -> List[DetectedElement]:
        """
        查找指定文本
        
        Args:
            target_text: 目标文本
            exact_match: 是否精确匹配
            
        Returns:
            找到的元素列表
        """
        try:
            ocr_results = await self.detect_text()
            elements = []
            
            for result in ocr_results:
                text = result.text
                match = False
                
                if exact_match:
                    match = text == target_text
                else:
                    match = target_text.lower() in text.lower()
                
                if match:
                    x, y, w, h = result.bbox
                    elements.append(DetectedElement(
                        type="text",
                        text=text,
                        bbox=(x, y, x + w, y + h),
                        confidence=result.confidence,
                        clickable=True
                    ))
            
            return elements
            
        except Exception as e:
            self.logger.error(f"查找文本失败: {e}")
            return []
    
    async def detect_buttons(self) -> List[DetectedElement]:
        """
        检测按钮元素
        
        Returns:
            检测到的按钮列表
        """
        try:
            img = await self.get_screenshot()
            
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                # 计算轮廓面积
                area = cv2.contourArea(contour)
                if area < 100:  # 过滤小轮廓
                    continue
                
                # 获取边界框
                x, y, w, h = cv2.boundingRect(contour)
                
                # 过滤太小的按钮
                if w < 30 or h < 30:
                    continue
                
                # 检查长宽比
                aspect_ratio = w / h
                if aspect_ratio < 0.5 or aspect_ratio > 3:
                    continue
                
                # 提取按钮区域进行OCR
                button_img = img[y:y+h, x:x+w]
                button_text = self._extract_text_from_region(button_img)
                
                buttons.append(DetectedElement(
                    type="button",
                    text=button_text,
                    bbox=(x, y, x + w, y + h),
                    confidence=0.8,
                    clickable=True
                ))
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"按钮检测失败: {e}")
            return []
    
    async def detect_images(self) -> List[DetectedElement]:
        """
        检测图片元素
        
        Returns:
            检测到的图片列表
        """
        try:
            img = await self.get_screenshot()
            
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 使用模板匹配检测常见图标
            images = []
            
            # 这里可以添加更多图标模板
            # 目前使用简单的轮廓检测
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 5000:  # 图片大小范围
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 检查长宽比
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 2:
                        images.append(DetectedElement(
                            type="image",
                            text="",
                            bbox=(x, y, x + w, y + h),
                            confidence=0.7,
                            clickable=True
                        ))
            
            return images
            
        except Exception as e:
            self.logger.error(f"图片检测失败: {e}")
            return []
    
    async def detect_all_elements(self) -> List[DetectedElement]:
        """
        检测所有元素
        
        Returns:
            所有检测到的元素列表
        """
        try:
            elements = []
            
            # 检测文本
            text_elements = await self.detect_text()
            for result in text_elements:
                x, y, w, h = result.bbox
                elements.append(DetectedElement(
                    type="text",
                    text=result.text,
                    bbox=(x, y, x + w, y + h),
                    confidence=result.confidence,
                    clickable=True
                ))
            
            # 检测按钮
            button_elements = await self.detect_buttons()
            elements.extend(button_elements)
            
            # 检测图片
            image_elements = await self.detect_images()
            elements.extend(image_elements)
            
            return elements
            
        except Exception as e:
            self.logger.error(f"元素检测失败: {e}")
            return []
    
    async def find_element_by_text(self, text: str, element_type: str = "any") -> Optional[DetectedElement]:
        """
        根据文本查找元素
        
        Args:
            text: 文本内容
            element_type: 元素类型 (text, button, image, any)
            
        Returns:
            找到的元素，未找到返回None
        """
        try:
            elements = await self.detect_all_elements()
            
            for element in elements:
                if element_type != "any" and element.type != element_type:
                    continue
                
                if text.lower() in element.text.lower():
                    return element
            
            return None
            
        except Exception as e:
            self.logger.error(f"查找元素失败: {e}")
            return None
    
    async def click_element(self, element: DetectedElement) -> bool:
        """
        点击元素
        
        Args:
            element: 要点击的元素
            
        Returns:
            是否点击成功
        """
        try:
            x, y, w, h = element.bbox
            center_x = x + w // 2
            center_y = y + h // 2
            
            return await self.android_controller.tap(center_x, center_y)
            
        except Exception as e:
            self.logger.error(f"点击元素失败: {e}")
            return False
    
    async def get_screen_info(self) -> Dict[str, Any]:
        """
        获取屏幕信息
        
        Returns:
            屏幕信息字典
        """
        try:
            img = await self.get_screenshot()
            height, width = img.shape[:2]
            
            # 检测所有元素
            elements = await self.detect_all_elements()
            
            # 统计信息
            text_count = len([e for e in elements if e.type == "text"])
            button_count = len([e for e in elements if e.type == "button"])
            image_count = len([e for e in elements if e.type == "image"])
            
            return {
                "width": width,
                "height": height,
                "elements": {
                    "total": len(elements),
                    "text": text_count,
                    "button": button_count,
                    "image": image_count
                },
                "elements_list": [
                    {
                        "type": e.type,
                        "text": e.text,
                        "bbox": e.bbox,
                        "confidence": e.confidence,
                        "clickable": e.clickable
                    }
                    for e in elements
                ]
            }
            
        except Exception as e:
            self.logger.error(f"获取屏幕信息失败: {e}")
            return {}
    
    def _preprocess_for_ocr(self, img: np.ndarray) -> np.ndarray:
        """
        为OCR预处理图片
        
        Args:
            img: 输入图片
            
        Returns:
            预处理后的图片
        """
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 自适应阈值
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 形态学操作
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def _extract_text_from_region(self, img: np.ndarray) -> str:
        """
        从图片区域提取文本
        
        Args:
            img: 图片区域
            
        Returns:
            提取的文本
        """
        try:
            processed = self._preprocess_for_ocr(img)
            text = pytesseract.image_to_string(processed, config=self.ocr_config).strip()
            return text
        except:
            return ""
    
    async def save_screenshot_with_annotations(self, elements: List[DetectedElement], 
                                            save_path: str) -> bool:
        """
        保存带标注的截图
        
        Args:
            elements: 要标注的元素列表
            save_path: 保存路径
            
        Returns:
            是否保存成功
        """
        try:
            img = await self.get_screenshot()
            
            # 绘制标注
            for element in elements:
                x, y, w, h = element.bbox
                
                # 绘制边界框
                color = (0, 255, 0) if element.clickable else (0, 0, 255)
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                
                # 绘制文本标签
                if element.text:
                    cv2.putText(img, element.text, (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # 保存图片
            cv2.imwrite(save_path, img)
            return True
            
        except Exception as e:
            self.logger.error(f"保存标注截图失败: {e}")
            return False