# 羲和AI代理系统 - 可视化界面版

## 🌟 项目概述

羲和AI代理系统是一个基于AI的Android设备全自动控制平台，现在提供了完整的Web可视化界面，支持AI交互、代码编辑、屏幕识别、实时监控等功能。

## 🎯 核心功能

### 1. **AI对话界面** (`/ai-chat`)
- 🤖 **自然语言交互**: 通过聊天界面与AI代理进行对话
- 💬 **智能指令理解**: 支持中文自然语言指令
- 📊 **实时状态显示**: 显示系统连接状态和执行统计
- ⚡ **快捷指令**: 预设常用命令快速执行

### 2. **代码编辑器** (`/code-editor`)
- 📝 **在线代码编辑**: 支持Python代码编辑和语法高亮
- 📁 **脚本管理**: 创建、保存、加载、删除脚本
- 🚀 **实时执行**: 在线执行Python脚本
- 📋 **代码模板**: 提供常用功能的代码模板
- 📊 **执行输出**: 实时显示脚本执行结果

### 3. **屏幕识别** (`/screen-recognition`)
- 👁️ **实时屏幕流**: 实时显示Android设备屏幕
- 🔍 **OCR文本识别**: 自动识别屏幕中的文字
- 🎯 **元素检测**: 自动检测按钮、输入框等UI元素
- 🖱️ **可视化操作**: 点击屏幕元素进行交互
- 📸 **截图功能**: 手动截图和元素标注

### 4. **系统仪表板** (`/dashboard`)
- 📊 **实时监控**: 系统状态、任务执行、性能指标
- 📈 **数据可视化**: 任务执行统计图表
- 📋 **任务管理**: 查看和管理自动化任务
- 🔧 **快速操作**: 系统控制和管理功能
- 📱 **设备状态**: Android设备连接状态监控

## 🚀 快速开始

### 环境要求

- **Python 3.10+**
- **Android设备** (通过ADB连接)
- **现代浏览器** (Chrome, Firefox, Safari, Edge)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/xihe-ai-agent.git
   cd xihe-ai-agent
   ```

2. **安装依赖**
   ```bash
   # 安装Web界面依赖
   pip install -r web_server/requirements.txt
   
   # 安装核心依赖
   pip install -r requirements.txt
   ```

3. **配置系统**
   ```bash
   # 编辑配置文件
   nano config/xihe_config.json
   
   # 配置Android设备连接
   # 配置AI API密钥
   # 配置通知设置
   ```

4. **启动系统**
   ```bash
   # 完整启动 (推荐)
   ./start_xihe_complete.sh
   
   # 或分别启动
   python3 main.py --daemon &
   cd web_server && python3 run_web.py
   ```

5. **访问界面**
   - 打开浏览器访问: `http://localhost:5000`
   - 或访问: `http://127.0.0.1:5000`

## 📖 使用指南

### AI对话界面

1. **基本对话**
   - 在输入框中输入自然语言指令
   - 例如: "刷抖音视频"、"发微信消息给张三"
   - AI会自动理解并执行相应操作

2. **快捷指令**
   - 点击预设的快捷按钮
   - 快速执行常用操作

3. **状态监控**
   - 查看系统连接状态
   - 监控执行统计信息

### 代码编辑器

1. **创建脚本**
   - 点击"新建脚本"按钮
   - 输入脚本名称和内容
   - 使用代码模板快速开始

2. **编辑代码**
   - 支持Python语法高亮
   - 自动缩进和代码补全
   - 代码格式化功能

3. **执行脚本**
   - 点击"运行脚本"按钮
   - 查看实时执行输出
   - 支持停止执行

4. **脚本管理**
   - 保存和加载脚本
   - 删除不需要的脚本
   - 脚本列表管理

### 屏幕识别

1. **开始识别**
   - 点击"开始识别"按钮
   - 系统会实时显示Android屏幕
   - 自动检测屏幕元素

2. **元素操作**
   - 点击屏幕上的元素进行交互
   - 查看元素详细信息
   - 执行点击、滑动等操作

3. **OCR识别**
   - 自动识别屏幕中的文字
   - 搜索特定文本内容
   - 高亮显示识别结果

4. **录制功能**
   - 录制屏幕操作过程
   - 保存操作序列
   - 回放操作步骤

### 系统仪表板

1. **系统概览**
   - 查看系统整体状态
   - 监控关键指标
   - 实时数据更新

2. **任务管理**
   - 查看所有任务状态
   - 启动、停止、暂停任务
   - 任务执行历史

3. **性能监控**
   - CPU、内存、磁盘使用率
   - 系统资源监控
   - 性能趋势分析

4. **快速操作**
   - 系统控制功能
   - 日志导出
   - 缓存清理

## 🔧 配置说明

### 主要配置项

```json
{
  "android": {
    "adb_path": "adb",
    "device_id": "",
    "screen_width": 1080,
    "screen_height": 2340
  },
  "ai": {
    "api_key": "your-openai-api-key",
    "api_url": "https://api.openai.com/v1/chat/completions",
    "model": "gpt-3.5-turbo"
  },
  "web_scraping": {
    "headless": false,
    "user_agent": "Mozilla/5.0...",
    "screenshot_on_error": true
  },
  "notification": {
    "enabled": true,
    "telegram_bot_token": "your-bot-token",
    "telegram_chat_id": "your-chat-id"
  }
}
```

### 环境变量

```bash
# AI API配置
export OPENAI_API_KEY="your-api-key"

# Android设备配置
export ANDROID_DEVICE_ID="device-id"

# 服务器配置
export WEB_HOST="0.0.0.0"
export WEB_PORT="5000"
```

## 🎮 使用示例

### 1. 自动刷抖音视频

**AI对话方式:**
```
用户: 刷抖音视频
AI: 好的，我来帮你自动刷抖音视频
```

**代码方式:**
```python
import asyncio

async def main():
    # 启动抖音
    await android_controller.launch_app("抖音")
    await asyncio.sleep(3)
    
    # 刷10个视频
    for i in range(10):
        await asyncio.sleep(30)  # 观看30秒
        await android_controller.swipe(400, 800, 400, 200)  # 滑动到下一个
    
    print("刷视频完成")

asyncio.run(main())
```

### 2. 批量发送消息

**AI对话方式:**
```
用户: 发微信消息给张三、李四、王五，内容是"大家好！"
AI: 好的，我来批量发送微信消息
```

**代码方式:**
```python
import asyncio

async def main():
    contacts = ["张三", "李四", "王五"]
    message = "大家好！"
    
    for contact in contacts:
        # 搜索联系人
        await android_controller.tap(200, 100)
        await android_controller.input_text(contact)
        await asyncio.sleep(2)
        
        # 发送消息
        await android_controller.tap(200, 200)
        await android_controller.input_text(message)
        await android_controller.tap(800, 600)
        
        await asyncio.sleep(1)

asyncio.run(main())
```

### 3. 网页数据抓取

**AI对话方式:**
```
用户: 抓取网页 https://www.example.com 的标题和内容
AI: 好的，我来抓取网页数据
```

**代码方式:**
```python
import asyncio

async def main():
    result = await ai_agent.web_automation.scrape_website(
        url="https://www.example.com",
        data_type="text",
        selectors={
            "title": "h1",
            "content": "p"
        }
    )
    
    if result["success"]:
        print("标题:", result["result"]["data"]["title"])
        print("内容:", result["result"]["data"]["content"])

asyncio.run(main())
```

## 🔍 高级功能

### 1. 自定义代码模板

在代码编辑器中，可以创建和使用自定义模板：

```python
# 自定义模板示例
def create_custom_template():
    template = {
        "name": "自定义自动化",
        "content": """
import asyncio

async def main():
    # 你的自动化代码
    pass

asyncio.run(main())
        """
    }
    return template
```

### 2. 屏幕录制和回放

```python
# 录制屏幕操作
async def record_operations():
    # 开始录制
    await screen_recognition.start_recording()
    
    # 执行操作
    await android_controller.tap(500, 800)
    await android_controller.input_text("Hello")
    
    # 停止录制
    await screen_recognition.stop_recording()
```

### 3. 实时监控和告警

```python
# 设置监控规则
monitoring_rules = {
    "cpu_threshold": 80,
    "memory_threshold": 90,
    "error_threshold": 5
}

# 监控系统状态
async def monitor_system():
    while True:
        status = await get_system_status()
        if status["cpu"] > monitoring_rules["cpu_threshold"]:
            send_alert("CPU使用率过高")
        await asyncio.sleep(60)
```

## 🛠️ 开发指南

### 添加新功能

1. **创建新模块**
   ```python
   # modules/new_module.py
   class NewModule:
       def __init__(self, config):
           self.config = config
       
       async def new_function(self):
           # 实现新功能
           pass
   ```

2. **集成到Web界面**
   ```python
   # web_server/app.py
   from modules.new_module import NewModule
   
   class XiheWebServer:
       def __init__(self):
           self.new_module = NewModule(self.config)
   ```

3. **添加API端点**
   ```python
   @app.route('/api/new_endpoint', methods=['POST'])
   def new_endpoint():
       data = request.get_json()
       result = self.new_module.process(data)
       return jsonify(result)
   ```

### 自定义界面

1. **修改模板**
   - 编辑 `web_server/templates/` 中的HTML文件
   - 添加新的CSS样式
   - 修改JavaScript逻辑

2. **添加新页面**
   - 创建新的HTML模板
   - 添加路由处理
   - 更新导航菜单

## 🐛 故障排除

### 常见问题

1. **Web界面无法访问**
   - 检查端口5000是否被占用
   - 确认防火墙设置
   - 查看服务器日志

2. **Android设备连接失败**
   - 检查ADB连接: `adb devices`
   - 确认USB调试已开启
   - 检查设备授权

3. **AI功能不工作**
   - 检查API密钥配置
   - 确认网络连接
   - 查看错误日志

4. **屏幕识别失败**
   - 检查OpenCV安装
   - 确认Tesseract OCR安装
   - 查看权限设置

### 日志查看

```bash
# 查看系统日志
tail -f logs/xihe.log

# 查看Web服务器日志
tail -f web_server.log

# 查看错误日志
grep "ERROR" logs/xihe.log
```

## 📞 技术支持

如果您遇到问题或有建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索 [Issues](https://github.com/your-username/xihe-ai-agent/issues)
3. 创建新的 Issue
4. 联系开发团队

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**羲和AI代理系统** - 让AI接管你的Android设备，通过可视化界面实现真正的智能化自动化！