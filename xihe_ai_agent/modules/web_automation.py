"""
网页自动化模块
扩展现有的Termux Web Scraper功能，支持更多自动化场景
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import requests
from urllib.parse import urljoin, urlparse

# 导入现有的Termux Web Scraper组件
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from termux_web_scraper.scraper_builder import ScraperBuilder, get_default_driver_options
from termux_web_scraper.scraper_runner import ScraperRunner
from termux_web_scraper.helpers import (
    get_element, click_element, send_keys, select_option_by_text,
    random_sleep, save_screenshot
)
from termux_web_scraper.error_hook import ScreenshotErrorHook, NotificationErrorHook
from termux_web_scraper.notifier import TelegramNotifier

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ScrapingType(Enum):
    """抓取类型枚举"""
    TEXT = "text"
    LINKS = "links"
    IMAGES = "images"
    FORMS = "forms"
    TABLES = "tables"
    JSON = "json"
    SCREENSHOT = "screenshot"


@dataclass
class ScrapingTarget:
    """抓取目标"""
    url: str
    selectors: Dict[str, str] = None
    data_type: ScrapingType = ScrapingType.TEXT
    wait_time: int = 10
    scroll_to_bottom: bool = False
    take_screenshot: bool = False


@dataclass
class ScrapingResult:
    """抓取结果"""
    url: str
    success: bool
    data: Any = None
    error: str = None
    timestamp: float = None
    screenshot_path: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class WebAutomation:
    """网页自动化控制器"""
    
    def __init__(self, config_manager):
        """
        初始化网页自动化控制器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger("WebAutomation")
        
        # 配置
        self.headless = config_manager.get("web_scraping.headless", False)
        self.user_agent = config_manager.get("web_scraping.user_agent", 
                                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.page_load_timeout = config_manager.get("web_scraping.page_load_timeout", 30)
        self.implicit_wait = config_manager.get("web_scraping.implicit_wait", 10)
        self.screenshot_on_error = config_manager.get("web_scraping.screenshot_on_error", True)
        self.retry_count = config_manager.get("web_scraping.retry_count", 3)
        
        # 通知配置
        self.notification_config = config_manager.get_section("notification")
        
        self.logger.info("网页自动化控制器初始化完成")
    
    async def scrape_website(self, url: str, data_type: str = "text", 
                           selectors: Dict[str, str] = None,
                           wait_time: int = 10,
                           scroll_to_bottom: bool = False,
                           take_screenshot: bool = False) -> Dict[str, Any]:
        """
        抓取网站数据
        
        Args:
            url: 目标URL
            data_type: 数据类型
            selectors: CSS选择器
            wait_time: 等待时间
            scroll_to_bottom: 是否滚动到底部
            take_screenshot: 是否截图
            
        Returns:
            抓取结果
        """
        try:
            self.logger.info(f"开始抓取网站: {url}")
            
            # 创建抓取目标
            target = ScrapingTarget(
                url=url,
                selectors=selectors or {},
                data_type=ScrapingType(data_type),
                wait_time=wait_time,
                scroll_to_bottom=scroll_to_bottom,
                take_screenshot=take_screenshot
            )
            
            # 执行抓取
            result = await self._execute_scraping(target)
            
            return {
                "success": True,
                "url": url,
                "data_type": data_type,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"抓取网站失败: {e}")
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def _execute_scraping(self, target: ScrapingTarget) -> ScrapingResult:
        """执行抓取任务"""
        driver = None
        screenshot_path = None
        
        try:
            # 创建ScraperBuilder
            builder = ScraperBuilder()
            
            # 配置WebDriver选项
            options = get_default_driver_options()
            if self.headless:
                options.add_argument("--headless")
            
            options.set_preference("general.useragent.override", self.user_agent)
            builder.with_driver_options(options)
            
            # 添加错误处理
            if self.screenshot_on_error:
                builder.with_error_hook(ScreenshotErrorHook("./screenshots"))
            
            # 添加通知
            if self.notification_config.get("enabled") and self.notification_config.get("telegram_bot_token"):
                notifier = TelegramNotifier(
                    self.notification_config["telegram_bot_token"],
                    self.notification_config["telegram_chat_id"]
                )
                builder.with_notifier(notifier)
                builder.with_error_hook(NotificationErrorHook())
            
            # 定义抓取步骤
            def scraping_step(driver, state, notify):
                # 访问页面
                driver.get(target.url)
                notify(f"访问页面: {target.url}")
                
                # 等待页面加载
                WebDriverWait(driver, target.wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 滚动到底部
                if target.scroll_to_bottom:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    random_sleep(1000, 2000)
                
                # 截图
                if target.take_screenshot:
                    screenshot_path = save_screenshot(driver, "./screenshots")
                    state["screenshot_path"] = screenshot_path
                
                # 根据数据类型抓取数据
                if target.data_type == ScrapingType.TEXT:
                    data = self._extract_text_data(driver, target.selectors)
                elif target.data_type == ScrapingType.LINKS:
                    data = self._extract_links(driver, target.selectors)
                elif target.data_type == ScrapingType.IMAGES:
                    data = self._extract_images(driver, target.selectors)
                elif target.data_type == ScrapingType.FORMS:
                    data = self._extract_forms(driver, target.selectors)
                elif target.data_type == ScrapingType.TABLES:
                    data = self._extract_tables(driver, target.selectors)
                elif target.data_type == ScrapingType.JSON:
                    data = self._extract_json_data(driver, target.selectors)
                else:
                    data = {"content": driver.page_source}
                
                state["scraped_data"] = data
                notify(f"抓取完成，数据类型: {target.data_type.value}")
            
            # 构建并运行抓取器
            builder.with_step("Scraping", scraping_step)
            scraper = builder.build()
            
            # 运行抓取器
            scraper.run()
            
            # 获取结果
            scraped_data = scraper.state.get("scraped_data", {})
            screenshot_path = scraper.state.get("screenshot_path")
            
            return ScrapingResult(
                url=target.url,
                success=True,
                data=scraped_data,
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            self.logger.error(f"抓取执行失败: {e}")
            return ScrapingResult(
                url=target.url,
                success=False,
                error=str(e)
            )
    
    def _extract_text_data(self, driver: webdriver.Firefox, selectors: Dict[str, str]) -> Dict[str, Any]:
        """提取文本数据"""
        data = {}
        
        for key, selector in selectors.items():
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    if len(elements) == 1:
                        data[key] = elements[0].text
                    else:
                        data[key] = [elem.text for elem in elements]
                else:
                    data[key] = None
            except Exception as e:
                self.logger.warning(f"提取文本失败 {key}: {e}")
                data[key] = None
        
        return data
    
    def _extract_links(self, driver: webdriver.Firefox, selectors: Dict[str, str]) -> Dict[str, Any]:
        """提取链接数据"""
        data = {}
        
        for key, selector in selectors.items():
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                links = []
                for elem in elements:
                    href = elem.get_attribute("href")
                    text = elem.text
                    if href:
                        links.append({
                            "url": urljoin(driver.current_url, href),
                            "text": text
                        })
                data[key] = links
            except Exception as e:
                self.logger.warning(f"提取链接失败 {key}: {e}")
                data[key] = []
        
        return data
    
    def _extract_images(self, driver: webdriver.Firefox, selectors: Dict[str, str]) -> Dict[str, Any]:
        """提取图片数据"""
        data = {}
        
        for key, selector in selectors.items():
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                images = []
                for elem in elements:
                    src = elem.get_attribute("src")
                    alt = elem.get_attribute("alt")
                    if src:
                        images.append({
                            "url": urljoin(driver.current_url, src),
                            "alt": alt or ""
                        })
                data[key] = images
            except Exception as e:
                self.logger.warning(f"提取图片失败 {key}: {e}")
                data[key] = []
        
        return data
    
    def _extract_forms(self, driver: webdriver.Firefox, selectors: Dict[str, str]) -> Dict[str, Any]:
        """提取表单数据"""
        data = {}
        
        for key, selector in selectors.items():
            try:
                forms = driver.find_elements(By.CSS_SELECTOR, selector)
                form_data = []
                for form in forms:
                    form_info = {
                        "action": form.get_attribute("action") or "",
                        "method": form.get_attribute("method") or "get",
                        "inputs": []
                    }
                    
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        input_info = {
                            "type": inp.get_attribute("type") or "text",
                            "name": inp.get_attribute("name") or "",
                            "value": inp.get_attribute("value") or "",
                            "placeholder": inp.get_attribute("placeholder") or ""
                        }
                        form_info["inputs"].append(input_info)
                    
                    form_data.append(form_info)
                data[key] = form_data
            except Exception as e:
                self.logger.warning(f"提取表单失败 {key}: {e}")
                data[key] = []
        
        return data
    
    def _extract_tables(self, driver: webdriver.Firefox, selectors: Dict[str, str]) -> Dict[str, Any]:
        """提取表格数据"""
        data = {}
        
        for key, selector in selectors.items():
            try:
                tables = driver.find_elements(By.CSS_SELECTOR, selector)
                table_data = []
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    table_rows = []
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if not cells:
                            cells = row.find_elements(By.TAG_NAME, "th")
                        row_data = [cell.text for cell in cells]
                        table_rows.append(row_data)
                    table_data.append(table_rows)
                data[key] = table_data
            except Exception as e:
                self.logger.warning(f"提取表格失败 {key}: {e}")
                data[key] = []
        
        return data
    
    def _extract_json_data(self, driver: webdriver.Firefox, selectors: Dict[str, str]) -> Dict[str, Any]:
        """提取JSON数据"""
        data = {}
        
        for key, selector in selectors.items():
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                json_data = []
                for elem in elements:
                    try:
                        json_text = elem.text
                        json_obj = json.loads(json_text)
                        json_data.append(json_obj)
                    except json.JSONDecodeError:
                        continue
                data[key] = json_data
            except Exception as e:
                self.logger.warning(f"提取JSON失败 {key}: {e}")
                data[key] = []
        
        return data
    
    async def query_data(self, query: str, source: str = "web") -> Dict[str, Any]:
        """
        查询数据
        
        Args:
            query: 查询内容
            source: 数据源 (web, api, database)
            
        Returns:
            查询结果
        """
        try:
            self.logger.info(f"查询数据: {query}, 数据源: {source}")
            
            if source == "web":
                # 使用搜索引擎查询
                search_url = f"https://www.google.com/search?q={query}"
                result = await self.scrape_website(
                    url=search_url,
                    data_type="text",
                    selectors={
                        "search_results": ".g .yuRUbf a",
                        "descriptions": ".g .VwiC3b"
                    }
                )
                return result
            
            elif source == "api":
                # 使用API查询
                api_url = f"https://api.example.com/search?q={query}"
                response = requests.get(api_url, timeout=30)
                response.raise_for_status()
                return {
                    "success": True,
                    "data": response.json(),
                    "source": "api"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"不支持的数据源: {source}"
                }
                
        except Exception as e:
            self.logger.error(f"查询数据失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def auto_fill_form(self, url: str, form_data: Dict[str, str], 
                           submit: bool = True) -> Dict[str, Any]:
        """
        自动填写表单
        
        Args:
            url: 表单页面URL
            form_data: 表单数据
            submit: 是否提交表单
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"自动填写表单: {url}")
            
            builder = ScraperBuilder()
            
            def form_filling_step(driver, state, notify):
                # 访问表单页面
                driver.get(url)
                notify(f"访问表单页面: {url}")
                
                # 等待表单加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                
                # 填写表单字段
                for field_name, field_value in form_data.items():
                    try:
                        # 尝试多种选择器
                        selectors = [
                            f"input[name='{field_name}']",
                            f"input[id='{field_name}']",
                            f"textarea[name='{field_name}']",
                            f"select[name='{field_name}']"
                        ]
                        
                        element = None
                        for selector in selectors:
                            try:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                                break
                            except NoSuchElementException:
                                continue
                        
                        if element:
                            element.clear()
                            element.send_keys(field_value)
                            notify(f"填写字段 {field_name}: {field_value}")
                        else:
                            notify(f"未找到字段: {field_name}")
                            
                    except Exception as e:
                        notify(f"填写字段失败 {field_name}: {e}")
                
                # 提交表单
                if submit:
                    try:
                        submit_button = driver.find_element(By.CSS_SELECTOR, 
                                                          "input[type='submit'], button[type='submit'], button")
                        submit_button.click()
                        notify("表单已提交")
                    except Exception as e:
                        notify(f"提交表单失败: {e}")
                
                state["form_filled"] = True
            
            builder.with_step("FormFilling", form_filling_step)
            scraper = builder.build()
            scraper.run()
            
            return {
                "success": True,
                "url": url,
                "form_data": form_data,
                "submitted": submit
            }
            
        except Exception as e:
            self.logger.error(f"自动填写表单失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def monitor_website_changes(self, url: str, selectors: Dict[str, str],
                                    check_interval: int = 300) -> Dict[str, Any]:
        """
        监控网站变化
        
        Args:
            url: 监控的URL
            selectors: 监控的选择器
            check_interval: 检查间隔(秒)
            
        Returns:
            监控结果
        """
        try:
            self.logger.info(f"开始监控网站变化: {url}")
            
            # 获取初始内容
            initial_result = await self.scrape_website(
                url=url,
                data_type="text",
                selectors=selectors
            )
            
            if not initial_result["success"]:
                return initial_result
            
            initial_data = initial_result["result"]["data"]
            
            # 开始监控循环
            changes_detected = []
            check_count = 0
            
            while True:
                await asyncio.sleep(check_interval)
                check_count += 1
                
                # 获取当前内容
                current_result = await self.scrape_website(
                    url=url,
                    data_type="text",
                    selectors=selectors
                )
                
                if not current_result["success"]:
                    self.logger.warning(f"第{check_count}次检查失败")
                    continue
                
                current_data = current_result["result"]["data"]
                
                # 比较内容变化
                for key in selectors.keys():
                    if key in initial_data and key in current_data:
                        if initial_data[key] != current_data[key]:
                            change = {
                                "timestamp": time.time(),
                                "selector": key,
                                "old_value": initial_data[key],
                                "new_value": current_data[key]
                            }
                            changes_detected.append(change)
                            self.logger.info(f"检测到变化: {key}")
                
                # 更新初始数据
                initial_data = current_data
                
                # 如果检测到变化，可以发送通知
                if changes_detected and self.notification_config.get("enabled"):
                    # 这里可以发送通知
                    pass
            
        except Exception as e:
            self.logger.error(f"监控网站变化失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def batch_scraping(self, urls: List[str], data_type: str = "text",
                           selectors: Dict[str, str] = None,
                           concurrent_limit: int = 3) -> List[Dict[str, Any]]:
        """
        批量抓取
        
        Args:
            urls: URL列表
            data_type: 数据类型
            selectors: 选择器
            concurrent_limit: 并发限制
            
        Returns:
            抓取结果列表
        """
        try:
            self.logger.info(f"开始批量抓取，URL数量: {len(urls)}")
            
            # 创建信号量限制并发
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def scrape_single_url(url):
                async with semaphore:
                    return await self.scrape_website(
                        url=url,
                        data_type=data_type,
                        selectors=selectors
                    )
            
            # 并发执行抓取任务
            tasks = [scrape_single_url(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "url": urls[i],
                        "success": False,
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)
            
            success_count = sum(1 for r in processed_results if r["success"])
            
            return {
                "success": True,
                "total_urls": len(urls),
                "successful": success_count,
                "failed": len(urls) - success_count,
                "results": processed_results
            }
            
        except Exception as e:
            self.logger.error(f"批量抓取失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }