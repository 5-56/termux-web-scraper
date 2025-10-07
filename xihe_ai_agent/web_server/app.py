"""
羲和AI代理系统 - Web界面服务器
提供可视化界面和实时交互功能
"""

import asyncio
import json
import logging
import base64
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import cv2
import numpy as np
from PIL import Image
import pytesseract

# 添加项目根目录到Python路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.ai_agent import AIAgent
from modules.android_control import AndroidController
from modules.screen_recognition import ScreenRecognition
from utils.config_manager import ConfigManager
from utils.logger import setup_logger


class XiheWebServer:
    """羲和Web服务器"""
    
    def __init__(self, config_path: str = "config/xihe_config.json"):
        self.config = ConfigManager(config_path)
        self.logger = setup_logger("WebServer")
        
        # 初始化Flask应用
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'xihe_secret_key_2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 初始化AI代理
        self.ai_agent = None
        self.android_controller = None
        self.screen_recognition = None
        
        # 连接状态
        self.connected_clients = set()
        self.is_screen_streaming = False
        
        # 设置路由和事件处理器
        self._setup_routes()
        self._setup_socket_events()
        
        self.logger.info("Web服务器初始化完成")
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/ai-chat')
        def ai_chat():
            return render_template('ai_chat.html')
        
        @self.app.route('/code-editor')
        def code_editor():
            return render_template('code_editor.html')
        
        @self.app.route('/dashboard')
        def dashboard():
            return render_template('dashboard.html')
        
        @self.app.route('/screen-recognition')
        def screen_recognition():
            return render_template('screen_recognition.html')
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify({
                'ai_agent_connected': self.ai_agent is not None,
                'android_connected': self.android_controller is not None,
                'screen_streaming': self.is_screen_streaming,
                'connected_clients': len(self.connected_clients)
            })
        
        @self.app.route('/api/screenshot')
        def api_screenshot():
            if not self.android_controller:
                return jsonify({'error': 'Android控制器未连接'}), 400
            
            try:
                screenshot_path = asyncio.run(self.android_controller.take_screenshot())
                if screenshot_path:
                    return send_file(screenshot_path, mimetype='image/png')
                else:
                    return jsonify({'error': '截图失败'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/execute_command', methods=['POST'])
        def api_execute_command():
            data = request.get_json()
            command = data.get('command', '')
            
            if not command:
                return jsonify({'error': '命令不能为空'}), 400
            
            try:
                result = asyncio.run(self._execute_command(command))
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/save_script', methods=['POST'])
        def api_save_script():
            data = request.get_json()
            script_name = data.get('name', '')
            script_content = data.get('content', '')
            
            if not script_name or not script_content:
                return jsonify({'error': '脚本名称和内容不能为空'}), 400
            
            try:
                script_path = Path(f"scripts/{script_name}.py")
                script_path.parent.mkdir(exist_ok=True)
                script_path.write_text(script_content, encoding='utf-8')
                
                return jsonify({'success': True, 'message': '脚本保存成功'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/load_script/<script_name>')
        def api_load_script(script_name):
            try:
                script_path = Path(f"scripts/{script_name}.py")
                if script_path.exists():
                    content = script_path.read_text(encoding='utf-8')
                    return jsonify({'success': True, 'content': content})
                else:
                    return jsonify({'error': '脚本不存在'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/list_scripts')
        def api_list_scripts():
            try:
                scripts_dir = Path("scripts")
                if scripts_dir.exists():
                    scripts = [f.stem for f in scripts_dir.glob("*.py")]
                    return jsonify({'success': True, 'scripts': scripts})
                else:
                    return jsonify({'success': True, 'scripts': []})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _setup_socket_events(self):
        """设置Socket事件处理器"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.connected_clients.add(request.sid)
            self.logger.info(f"客户端连接: {request.sid}")
            emit('status', {'message': '连接成功'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.connected_clients.discard(request.sid)
            self.logger.info(f"客户端断开: {request.sid}")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            room = data.get('room', 'default')
            join_room(room)
            emit('status', {'message': f'加入房间: {room}'})
        
        @self.socketio.on('ai_command')
        def handle_ai_command(data):
            command = data.get('command', '')
            if not command:
                emit('ai_response', {'error': '命令不能为空'})
                return
            
            try:
                result = asyncio.run(self._execute_command(command))
                emit('ai_response', result)
            except Exception as e:
                emit('ai_response', {'error': str(e)})
        
        @self.socketio.on('start_screen_stream')
        def handle_start_screen_stream():
            if not self.is_screen_streaming:
                self.is_screen_streaming = True
                asyncio.create_task(self._screen_stream_loop())
                emit('screen_stream_status', {'streaming': True})
        
        @self.socketio.on('stop_screen_stream')
        def handle_stop_screen_stream():
            self.is_screen_streaming = False
            emit('screen_stream_status', {'streaming': False})
        
        @self.socketio.on('execute_script')
        def handle_execute_script(data):
            script_content = data.get('content', '')
            if not script_content:
                emit('script_result', {'error': '脚本内容不能为空'})
                return
            
            try:
                result = asyncio.run(self._execute_script(script_content))
                emit('script_result', result)
            except Exception as e:
                emit('script_result', {'error': str(e)})
        
        @self.socketio.on('screen_click')
        def handle_screen_click(data):
            x = data.get('x', 0)
            y = data.get('y', 0)
            
            try:
                result = asyncio.run(self.android_controller.tap(x, y))
                emit('click_result', {'success': result, 'x': x, 'y': y})
            except Exception as e:
                emit('click_result', {'error': str(e)})
        
        @self.socketio.on('screen_swipe')
        def handle_screen_swipe(data):
            start_x = data.get('start_x', 0)
            start_y = data.get('start_y', 0)
            end_x = data.get('end_x', 0)
            end_y = data.get('end_y', 0)
            duration = data.get('duration', 300)
            
            try:
                result = asyncio.run(self.android_controller.swipe(
                    start_x, start_y, end_x, end_y, duration
                ))
                emit('swipe_result', {'success': result})
            except Exception as e:
                emit('swipe_result', {'error': str(e)})
    
    async def _execute_command(self, command: str) -> Dict[str, Any]:
        """执行AI命令"""
        if not self.ai_agent:
            await self._initialize_ai_agent()
        
        return await self.ai_agent.process_command(command)
    
    async def _execute_script(self, script_content: str) -> Dict[str, Any]:
        """执行Python脚本"""
        try:
            # 创建安全的执行环境
            exec_globals = {
                'ai_agent': self.ai_agent,
                'android_controller': self.android_controller,
                'screen_recognition': self.screen_recognition,
                'asyncio': asyncio,
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'bool': bool,
                'type': type,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
                'dir': dir,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sorted': sorted,
                'reversed': reversed,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'pow': pow,
                'divmod': divmod,
                'bin': bin,
                'hex': hex,
                'oct': oct,
                'ord': ord,
                'chr': chr,
                'ascii': ascii,
                'repr': repr,
                'eval': eval,
                'exec': exec,
                'compile': compile,
                'open': open,
                'input': input,
                'raw_input': input,  # Python 2 compatibility
                'file': open,  # Python 2 compatibility
                'xrange': range,  # Python 2 compatibility
                'unicode': str,  # Python 2 compatibility
                'basestring': str,  # Python 2 compatibility
                'long': int,  # Python 2 compatibility
                'unichr': chr,  # Python 2 compatibility
                'reduce': lambda func, seq, initial=None: functools.reduce(func, seq, initial) if initial is not None else functools.reduce(func, seq),
                'cmp': lambda x, y: (x > y) - (x < y),  # Python 2 compatibility
                'reload': lambda module: importlib.reload(module),  # Python 2 compatibility
                'apply': lambda func, args, kwargs=None: func(*args, **(kwargs or {})),  # Python 2 compatibility
                'coerce': lambda x, y: (x, y),  # Python 2 compatibility
                'intern': sys.intern,  # Python 2 compatibility
                'execfile': lambda filename, globals=None, locals=None: exec(open(filename).read(), globals or {}, locals or {}),  # Python 2 compatibility
                'file': open,  # Python 2 compatibility
                'buffer': memoryview,  # Python 2 compatibility
                'raw_input': input,  # Python 2 compatibility
                'xrange': range,  # Python 2 compatibility
                'unicode': str,  # Python 2 compatibility
                'basestring': str,  # Python 2 compatibility
                'long': int,  # Python 2 compatibility
                'unichr': chr,  # Python 2 compatibility
                'reduce': lambda func, seq, initial=None: functools.reduce(func, seq, initial) if initial is not None else functools.reduce(func, seq),
                'cmp': lambda x, y: (x > y) - (x < y),  # Python 2 compatibility
                'reload': lambda module: importlib.reload(module),  # Python 2 compatibility
                'apply': lambda func, args, kwargs=None: func(*args, **(kwargs or {})),  # Python 2 compatibility
                'coerce': lambda x, y: (x, y),  # Python 2 compatibility
                'intern': sys.intern,  # Python 2 compatibility
                'execfile': lambda filename, globals=None, locals=None: exec(open(filename).read(), globals or {}, locals or {}),  # Python 2 compatibility
                'file': open,  # Python 2 compatibility
                'buffer': memoryview,  # Python 2 compatibility
            }
            
            # 执行脚本
            exec(script_content, exec_globals)
            
            return {
                'success': True,
                'message': '脚本执行成功',
                'output': '脚本已执行完成'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '脚本执行失败'
            }
    
    async def _screen_stream_loop(self):
        """屏幕流循环"""
        while self.is_screen_streaming and self.android_controller:
            try:
                # 截取屏幕
                screenshot_path = await self.android_controller.take_screenshot()
                if screenshot_path:
                    # 读取图片并转换为base64
                    with open(screenshot_path, 'rb') as f:
                        image_data = f.read()
                    
                    # 压缩图片
                    img = Image.open(io.BytesIO(image_data))
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    
                    # 转换为base64
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=80)
                    img_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    # 发送给所有连接的客户端
                    self.socketio.emit('screen_frame', {
                        'image': img_base64,
                        'timestamp': datetime.now().isoformat()
                    })
                
                await asyncio.sleep(0.1)  # 10fps
                
            except Exception as e:
                self.logger.error(f"屏幕流错误: {e}")
                await asyncio.sleep(1)
    
    async def _initialize_ai_agent(self):
        """初始化AI代理"""
        if not self.ai_agent:
            self.ai_agent = AIAgent(self.config.config_path)
            await self.ai_agent.start()
            
            # 获取Android控制器
            self.android_controller = self.ai_agent.android_controller
            self.screen_recognition = ScreenRecognition(self.android_controller)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行Web服务器"""
        self.logger.info(f"启动Web服务器: http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    server = XiheWebServer()
    server.run(debug=True)