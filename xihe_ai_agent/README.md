# 羲和AI代理系统 - 全自动Android设备控制平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Android](https://img.shields.io/badge/Android-Termux-green.svg)](https://termux.com/)

羲和AI代理系统是一个基于AI的Android设备全自动控制平台，能够通过自然语言指令控制Android设备执行各种自动化任务，包括视频刷取、消息发送、网页抓取、应用控制等。

## 🌟 核心特性

### 🤖 AI驱动控制
- **自然语言理解**: 支持中文自然语言指令，无需编程知识
- **智能任务规划**: AI自动解析指令并制定执行计划
- **上下文感知**: 理解任务上下文，提供智能建议

### 📱 Android设备控制
- **屏幕操作**: 点击、滑动、输入文本、按键操作
- **应用管理**: 启动、关闭、切换应用
- **系统交互**: 返回、主页、最近任务等系统操作

### 🎬 视频自动化
- **多平台支持**: 抖音、快手、B站、微博等
- **智能刷取**: 自动观看、点赞、评论、分享
- **人性化操作**: 随机延迟、模拟真实用户行为

### 💬 消息自动化
- **多平台消息**: 微信、QQ、短信等
- **批量发送**: 支持批量消息发送
- **模板消息**: 预定义消息模板
- **自动回复**: 智能自动回复功能

### 🌐 网页抓取
- **基于Termux Web Scraper**: 继承强大的网页抓取能力
- **多种数据类型**: 文本、链接、图片、表单、表格等
- **反检测技术**: 有头模式浏览器，绕过反爬虫检测
- **批量处理**: 支持批量网页抓取

### ⏰ 任务调度
- **定时任务**: 支持Cron表达式定时执行
- **间隔任务**: 按固定间隔执行任务
- **事件驱动**: 基于事件触发的任务执行
- **任务管理**: 完整的任务生命周期管理

## 🏗️ 系统架构

```
羲和AI代理系统
├── AI代理核心 (ai_agent.py)
│   ├── 指令理解
│   ├── 任务规划
│   └── 执行协调
├── Android控制 (android_control.py)
│   ├── 屏幕操作
│   ├── 应用控制
│   └── 系统交互
├── UI自动化 (ui_automation.py)
│   ├── 视频刷取
│   ├── 应用内操作
│   └── 界面交互
├── 消息自动化 (messaging.py)
│   ├── 多平台消息
│   ├── 批量发送
│   └── 自动回复
├── 网页抓取 (web_automation.py)
│   ├── 数据抓取
│   ├── 表单填写
│   └── 网站监控
├── 任务调度 (task_scheduler.py)
│   ├── 定时任务
│   ├── 任务队列
│   └── 执行管理
└── 配置管理 (config_manager.py)
    ├── 配置存储
    ├── 参数验证
    └── 模板管理
```

## 🚀 快速开始

### 环境要求

- **Android设备**: Android 7.0+ (推荐Android 10+)
- **Termux**: 最新版本
- **Python**: 3.10+
- **ADB**: Android调试桥
- **网络连接**: 用于AI API调用

### 安装步骤

1. **安装Termux**
   ```bash
   # 从F-Droid或Google Play安装Termux
   ```

2. **克隆项目**
   ```bash
   git clone https://github.com/your-username/xihe-ai-agent.git
   cd xihe-ai-agent
   ```

3. **运行安装脚本**
   ```bash
   chmod +x scripts/start_xihe.sh
   ./scripts/start_xihe.sh --help
   ```

4. **配置系统**
   ```bash
   # 编辑配置文件
   nano config/xihe_config.json
   
   # 配置AI API密钥
   # 配置Android设备信息
   # 配置通知设置
   ```

5. **启动系统**
   ```bash
   # 交互模式
   ./scripts/start_xihe.sh --interactive
   
   # 守护进程模式
   ./scripts/start_xihe.sh --daemon
   ```

### 基本使用

#### 交互模式
```bash
python3 main.py --interactive
```

#### 命令行模式
```bash
# 执行单个命令
python3 main.py --command "刷抖音视频"

# 查看帮助
python3 main.py --help
```

## 📖 使用指南

### 基本命令

#### Android控制
```
点击(100,200)          # 点击屏幕坐标
滑动(100,200,300,400)  # 滑动屏幕
输入:文本内容          # 输入文本
返回                   # 按返回键
主页                   # 按主页键
启动应用:微信          # 启动应用
关闭应用:微信          # 关闭应用
```

#### 视频自动化
```
刷抖音视频             # 自动刷抖音
刷快手视频             # 自动刷快手
刷B站视频              # 自动刷B站
自动点赞:抖音:10       # 自动点赞10个视频
```

#### 消息发送
```
发微信消息:张三:你好    # 发送微信消息
发QQ消息:李四:消息内容  # 发送QQ消息
发短信:13800138000:内容 # 发送短信
批量发消息:联系人列表:内容 # 批量发送
```

#### 网页抓取
```
抓取网页:https://example.com  # 抓取网页
查询信息:关键词               # 搜索信息
填写表单:URL:表单数据         # 自动填表
监控网站:URL:选择器           # 监控网站变化
```

### 高级功能

#### 任务调度
```python
# 创建定时任务
from xihe_ai_agent.core.ai_agent import AIAgent
from xihe_ai_agent.modules.task_scheduler import Task, TaskType, ScheduleType

ai_agent = AIAgent()

# 添加每小时执行的刷视频任务
task = Task(
    id="video_task_1",
    type=TaskType.VIDEO_WATCHING,
    description="每小时刷抖音视频",
    parameters={"platform": "douyin", "duration": 300}
)

await ai_agent.task_scheduler.add_task(
    task=task,
    schedule_type=ScheduleType.INTERVAL,
    schedule_config={"interval_seconds": 3600}
)
```

#### 自定义消息模板
```python
from xihe_ai_agent.modules.messaging import MessageTemplate, MessagePlatform

# 创建自定义模板
template = MessageTemplate(
    name="节日祝福",
    content="祝{name}节日快乐！{greeting}",
    variables=["name", "greeting"],
    platform=MessagePlatform.WECHAT
)

# 添加模板
ai_agent.messaging.add_message_template(template)
```

#### 批量网页抓取
```python
# 批量抓取多个网站
urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]

result = await ai_agent.web_automation.batch_scraping(
    urls=urls,
    data_type="text",
    selectors={"title": "h1", "content": ".content"},
    concurrent_limit=3
)
```

## ⚙️ 配置说明

### 主要配置项

#### Android配置
```json
{
  "android": {
    "adb_path": "adb",
    "device_id": "",
    "screen_width": 1080,
    "screen_height": 2340,
    "tap_delay": 0.1,
    "swipe_duration": 300
  }
}
```

#### AI配置
```json
{
  "ai": {
    "api_key": "your-openai-api-key",
    "api_url": "https://api.openai.com/v1/chat/completions",
    "model": "gpt-3.5-turbo",
    "max_tokens": 1000,
    "temperature": 0.7
  }
}
```

#### 通知配置
```json
{
  "notification": {
    "enabled": true,
    "telegram_bot_token": "your-bot-token",
    "telegram_chat_id": "your-chat-id"
  }
}
```

## 🔧 开发指南

### 添加新的控制模块

1. **创建模块文件**
   ```python
   # modules/my_module.py
   class MyModule:
       def __init__(self, config_manager):
           self.config = config_manager
       
       async def my_function(self, params):
           # 实现功能
           pass
   ```

2. **集成到AI代理**
   ```python
   # core/ai_agent.py
   from .modules.my_module import MyModule
   
   class AIAgent:
       def __init__(self, config_path):
           # ...
           self.my_module = MyModule(self.config)
   ```

3. **添加指令处理**
   ```python
   async def _understand_intent(self, command, context):
       if "我的指令" in command:
           return {
               "type": TaskType.MY_TASK,
               "action": "my_action",
               "parameters": {}
           }
   ```

### 自定义任务类型

1. **定义任务类型**
   ```python
   class TaskType(Enum):
       MY_CUSTOM_TASK = "my_custom_task"
   ```

2. **实现执行逻辑**
   ```python
   async def _execute_my_custom_task(self, task):
       # 实现自定义任务逻辑
       pass
   ```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

本软件仅供学习和研究使用。使用者需要遵守相关法律法规和平台服务条款。作者不对使用本软件造成的任何后果承担责任。

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索 [Issues](https://github.com/your-username/xihe-ai-agent/issues)
3. 创建新的 Issue
4. 联系开发者

## 🙏 致谢

- [Termux Web Scraper](https://github.com/kpliuta/termux-web-scraper) - 网页抓取基础
- [Selenium](https://selenium.dev/) - 浏览器自动化
- [OpenAI](https://openai.com/) - AI API服务

---

**羲和AI代理系统** - 让AI接管你的Android设备，实现真正的智能化自动化！