#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Pass Python Sidecar

一个简洁的Python微服务sidecar，支持自动注册到Nacos和Feign风格调用。

功能特性:
- 自动服务注册到Nacos
- Feign风格的HTTP客户端调用
- 异构服务支持（Java、Python、Go等）
- 配置中心支持
- 权限拦截器
- 心跳保活机制
- 优雅关闭

@author: lzg
@created: 2025-07-01 14:23:45
@version: 1.0.0
"""

import asyncio
import threading
import yaml
import aiohttp
import json
import re
import inspect
import sys
import os
from typing import Dict, Any, Optional, Callable
from functools import wraps

# 全局配置
_config = None
_nacos_client = None
_service_name = None
_service_port = None
_config_center = None
_web_framework = None
_auth_interceptor = None

def init_sidecar(app=None):
    """
    初始化sidecar，自动注册服务到Nacos
    服务端启动时调用此函数即可
    
    Args:
        app: Web应用实例（Flask、FastAPI等），可选
    """
    global _config, _nacos_client, _service_name, _service_port, _config_center, _web_framework, _auth_interceptor
    
    # 加载配置
    with open('bootstrap.yml', 'r', encoding='utf-8') as f:
        _config = yaml.safe_load(f)
    
    _service_name = _config['application']['name']
    _service_port = _config['server']['port']
    nacos_addr = _config['cloud']['nacos']['discovery']['server-addr']
    
    # 从配置文件读取IP地址
    service_ip = _config.get('cloud', {}).get('nacos', {}).get('discovery', {}).get('ip', '127.0.0.1')
    
    # 检测Web框架
    _web_framework = detect_web_framework()
    print(f"🔍 检测到Web框架: {_web_framework}")
    
    # 启动Nacos客户端
    _nacos_client = NacosClient(nacos_addr, _service_name, _service_port, service_ip)
    
    # 启动配置中心
    _config_center = ConfigCenter(nacos_addr, _service_name, _config)
    
    # 初始化权限拦截器
    _auth_interceptor = AuthInterceptor()
    
    # 如果传入了app实例，自动设置权限拦截器
    if app is not None:
        setup_auth_interceptor_internal(app)
    
    # 预加载权限微服务接口
    _load_auth_service()
    
    def _run():
        async def start_all():
            await _nacos_client.start()
            await _config_center.start()
            # 保持心跳任务运行
            while _nacos_client.running:
                await asyncio.sleep(1)
        
        asyncio.run(start_all())
    
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    
    # 注册信号处理器，优雅关闭
    import signal
    def signal_handler(signum, frame):
        print(f"\n🛑 收到信号 {signum}，正在优雅关闭...")
        asyncio.run(stop_sidecar())
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"🚀 Sidecar启动成功 - 服务名: {_service_name}, 端口: {_service_port}")

def setup_auth_interceptor_internal(app):
    """内部函数：设置权限拦截器"""
    global _auth_interceptor, _web_framework
    
    if _auth_interceptor is None:
        print("⚠️ Sidecar未初始化，请先调用init_sidecar()")
        return
    
    if _web_framework == 'flask':
        _auth_interceptor.setup_flask_interceptor(app)
    elif _web_framework == 'fastapi':
        _auth_interceptor.setup_fastapi_interceptor(app)
    elif _web_framework == 'django':
        _auth_interceptor.setup_django_interceptor(app)
    else:
        print(f"⚠️ 不支持的Web框架: {_web_framework}")

def setup_auth_interceptor(app):
    """设置权限拦截器（向后兼容）"""
    setup_auth_interceptor_internal(app)

def detect_web_framework():
    """检测当前使用的Web框架"""
    # 检查Flask
    try:
        import flask
        if 'flask' in sys.modules:
            return 'flask'
    except ImportError:
        pass
    
    # 检查FastAPI
    try:
        import fastapi
        if 'fastapi' in sys.modules:
            return 'fastapi'
    except ImportError:
        pass
    
    # 检查Django
    try:
        import django
        if 'django' in sys.modules:
            return 'django'
    except ImportError:
        pass
    
    # 检查Gunicorn
    try:
        import gunicorn
        if 'gunicorn' in sys.modules:
            return 'gunicorn'
    except ImportError:
        pass
    
    # 检查Uvicorn
    try:
        import uvicorn
        if 'uvicorn' in sys.modules:
            return 'uvicorn'
    except ImportError:
        pass
    
    return 'unknown'

def setup_auth_interceptor(app):
    """设置权限拦截器"""
    global _auth_interceptor, _web_framework
    
    if _auth_interceptor is None:
        print("⚠️ Sidecar未初始化，请先调用init_sidecar()")
        return
    
    if _web_framework == 'flask':
        _auth_interceptor.setup_flask_interceptor(app)
    elif _web_framework == 'fastapi':
        _auth_interceptor.setup_fastapi_interceptor(app)
    elif _web_framework == 'django':
        _auth_interceptor.setup_django_interceptor(app)
    else:
        print(f"⚠️ 不支持的Web框架: {_web_framework}")

async def stop_sidecar():
    """停止sidecar"""
    global _nacos_client, _config_center
    
    if _nacos_client:
        await _nacos_client.stop()
    
    if _config_center and _config_center.session:
        await _config_center.session.close()

class ConfigValue:
    """配置值类，类似Java @Value注解"""
    
    def __init__(self, config_key: str, default: Any = None):
        self.config_key = config_key
        self.default = default
    
    def __get__(self, obj, objtype=None):
        return get_config_value(self.config_key, self.default)

def config_remote(config_key: str, default: Any = None):
    """
    从Nacos配置中心获取配置
    用法: 
    server_port = config_remote('server.port', 9201)
    redis_host = config_remote('spring.data.redis.host', 'localhost')
    """
    return get_config_value(config_key, default)

def config_local(config_key: str, default: Any = None) -> Any:
    """
    从本地bootstrap.yml获取配置
    用法:
    port = config_local('server.port', 9202)
    service_name = config_local('application.name', 'unknown')
    """
    global _config
    if _config is None:
        return default
    
    keys = config_key.split('.')
    current = _config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def get_config_value(config_key: str, default: Any = None) -> Any:
    """
    获取远程配置值
    支持点分隔的配置路径，如: spring.data.redis.host
    """
    global _config_center
    if _config_center is None:
        return default
    
    return _config_center.get_value(config_key, default)

# 为了向后兼容，保留别名
def remote_config(config_key: str, default: Any = None):
    """别名: config_remote"""
    return config_remote(config_key, default)

def local_config(config_key: str, default: Any = None) -> Any:
    """别名: config_local"""
    return config_local(config_key, default)

class AuthInterceptor:
    """权限拦截器"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    def setup_flask_interceptor(self, app):
        """设置Flask权限拦截器"""
        from flask import request, jsonify
        
        @app.before_request
        def before_request():
            # 跳过OPTIONS请求
            if request.method == 'OPTIONS':
                return None
            
            # 检查权限是否启用
            if not config_local('auth.enabled', True):
                return None
            
            # 检查排除路径
            exclude_paths = config_local('auth.exclude_paths', [])
            for exclude_path in exclude_paths:
                if request.path.startswith(exclude_path):
                    return None
            
            # 跳过静态文件
            if request.path.startswith('/static/'):
                return None
            
            # 跳过健康检查
            if request.path in ['/health', '/healthz', '/ping']:
                return None
            
            # 权限检查
            try:
                result = asyncio.run(self.auth_service.check_permission(
                    url=request.path,
                    method=request.method,
                    headers=dict(request.headers)
                ))
                
                if not result.get('has_permission', False):
                    return jsonify({
                        'code': 401,
                        'message': result.get('message', '权限不足')
                    }), 401
                    
            except Exception as e:
                print(f"权限检查异常: {e}")
                # 权限检查失败时，根据配置决定是否放行
                if config_local('auth.fail_open', True):
                    return None
                else:
                    return jsonify({
                        'code': 500,
                        'message': '权限检查失败'
                    }), 500
    
    def setup_fastapi_interceptor(self, app):
        """设置FastAPI权限拦截器"""
        from fastapi import Request, HTTPException
        from fastapi.responses import JSONResponse
        
        @app.middleware("http")
        async def auth_middleware(request: Request, call_next):
            # 跳过OPTIONS请求
            if request.method == "OPTIONS":
                return await call_next(request)
            
            # 检查权限是否启用
            if not config_local('auth.enabled', True):
                return await call_next(request)
            
            # 检查排除路径
            exclude_paths = config_local('auth.exclude_paths', [])
            for exclude_path in exclude_paths:
                if request.url.path.startswith(exclude_path):
                    return await call_next(request)
            
            # 跳过静态文件
            if request.url.path.startswith('/static/'):
                return await call_next(request)
            
            # 跳过健康检查
            if request.url.path in ['/health', '/healthz', '/ping']:
                return await call_next(request)
            
            # 权限检查
            try:
                result = await self.auth_service.check_permission(
                    url=str(request.url.path),
                    method=request.method,
                    headers=dict(request.headers)
                )
                
                if not result.get('has_permission', False):
                    return JSONResponse(
                        status_code=401,
                        content={
                            'code': 401,
                            'message': result.get('message', '权限不足')
                        }
                    )
                    
            except Exception as e:
                print(f"权限检查异常: {e}")
                # 权限检查失败时，根据配置决定是否放行
                if config_local('auth.fail_open', True):
                    return await call_next(request)
                else:
                    return JSONResponse(
                        status_code=500,
                        content={
                            'code': 500,
                            'message': '权限检查失败'
                        }
                    )
            
            return await call_next(request)
    
    def setup_django_interceptor(self, app):
        """设置Django权限拦截器"""
        # Django中间件实现
        pass

class AuthService:
    """权限服务"""
    
    def __init__(self):
        self.auth_client = AuthClient()
    
    async def check_permission(self, url: str, method: str, headers: dict) -> dict:
        """检查权限"""
        try:
            # 获取token
            token = headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return {
                    'has_permission': False,
                    'message': 'token不能为空'
                }
            
            # 调用权限微服务
            result = await self.auth_client.check_permission(url, token)
            return result
            
        except Exception as e:
            print(f"权限检查失败: {e}")
            return {
                'has_permission': False,
                'message': f'权限检查失败: {str(e)}'
            }

class AuthClient:
    """权限微服务客户端"""
    
    def __init__(self):
        self.auth_service = AuthPermissionService()
    
    async def check_permission(self, url: str, token: str) -> dict:
        """检查权限"""
        try:
            # 调用权限微服务
            result = await self.auth_service.check_permission(url=url, token=token)
            
            # 解析返回结果
            if result and result.get('code') == 200:
                return {
                    'has_permission': True,
                    'message': '权限验证通过'
                }
            else:
                return {
                    'has_permission': False,
                    'message': result.get('msg', '权限不足') if result else '权限验证失败'
                }
                
        except Exception as e:
            print(f"调用权限服务失败: {e}")
            # 根据配置决定失败时的行为
            if config_local('auth.fail_open', True):
                return {
                    'has_permission': True,
                    'message': '权限服务不可用，默认放行'
                }
            else:
                return {
                    'has_permission': False,
                    'message': f'权限服务调用失败: {str(e)}'
                }

# 权限微服务接口定义 - 动态加载
_auth_service_module = None

def _load_auth_service():
    """动态加载权限微服务接口"""
    global _auth_service_module
    if _auth_service_module is None:
        try:
            from . import auth_service
            _auth_service_module = auth_service
            print("✅ 权限微服务接口加载成功")
        except Exception as e:
            print(f"⚠️ 权限微服务接口加载失败: {e}")
            return None
    return _auth_service_module

class AuthPermissionService:
    """权限微服务接口代理"""
    
    def __init__(self):
        self._service = None
    
    def _get_service(self):
        """获取权限服务实例"""
        if self._service is None:
            module = _load_auth_service()
            if module:
                self._service = module.AuthPermissionService()
            else:
                raise Exception("权限微服务接口未加载")
        return self._service
    
    async def check_permission(self, url: str, token: str = None, code: str = None):
        """权限校验接口"""
        service = self._get_service()
        return await service.check_permission(url=url, token=token, code=code)
    
    async def get_menu_resources(self, code: str, token: str = None):
        """获取菜单资源"""
        service = self._get_service()
        return await service.get_menu_resources(code=code, token=token)

class ConfigCenter:
    """Nacos配置中心客户端"""
    
    def __init__(self, server_addr: str, service_name: str, bootstrap_config: dict):
        self.server_addr = server_addr
        self.service_name = service_name
        self.bootstrap_config = bootstrap_config
        self.session = None
        self.configs = {}
        self.listeners = {}
        
    async def start(self):
        """启动配置中心"""
        self.session = aiohttp.ClientSession()
        await self.load_configs()
        print(f"📋 配置中心启动成功: {self.service_name}")
        
    async def load_configs(self):
        """加载所有配置"""
        # 加载主配置
        await self.load_config(self.service_name, "DEFAULT_GROUP")
        
        # 加载共享配置
        shared_configs = self.bootstrap_config.get('cloud', {}).get('nacos', {}).get('config', {}).get('shared-configs', [])
        for shared_config in shared_configs:
            # 解析配置名称，如: application-${spring.profiles.active}.${spring.cloud.nacos.config.file-extension}
            config_name = self._resolve_config_name(shared_config)
            await self.load_config(config_name, "DEFAULT_GROUP")
    
    def _resolve_config_name(self, config_template: str) -> str:
        """解析配置名称模板"""
        # 简化实现，实际应该支持更复杂的变量替换
        profiles = self.bootstrap_config.get('profiles', {}).get('active', 'dev')
        file_ext = self.bootstrap_config.get('cloud', {}).get('nacos', {}).get('config', {}).get('file-extension', 'yml')
        
        config_name = config_template.replace('${spring.profiles.active}', profiles)
        config_name = config_name.replace('${spring.cloud.nacos.config.file-extension}', file_ext)
        return config_name
    
    async def load_config(self, data_id: str, group: str):
        """加载指定配置"""
        url = f"http://{self.server_addr}/nacos/v1/cs/configs"
        params = {
            'dataId': data_id,
            'group': group,
            'tenant': ''  # 命名空间，暂时为空
        }
        
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    # 解析YAML配置
                    config_data = yaml.safe_load(content) if content else {}
                    self.configs[data_id] = config_data
                    print(f"✅ 配置加载成功: {data_id}")
                else:
                    print(f"⚠️ 配置加载失败: {data_id}, 状态码: {resp.status}")
        except Exception as e:
            print(f"❌ 配置加载异常: {data_id}, 错误: {e}")
    
    def get_value(self, config_key: str, default: Any = None) -> Any:
        """
        获取配置值
        支持点分隔的配置路径，如: spring.data.redis.host
        """
        keys = config_key.split('.')
        
        # 遍历所有配置源
        for config_data in self.configs.values():
            value = self._get_nested_value(config_data, keys)
            if value is not None:
                return value
        
        return default
    
    def _get_nested_value(self, data: dict, keys: list) -> Any:
        """递归获取嵌套配置值"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

def feign(service_name: str):
    """
    定义Feign客户端的装饰器
    """
    def decorator(cls):
        cls._service_name = service_name
        # 为每个方法创建代理
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, '_http_method'):
                # 创建代理方法
                setattr(cls, attr_name, create_proxy_method(service_name, attr))
        return cls
    return decorator

def create_proxy_method(service_name: str, original_method):
    """创建代理方法"""
    async def proxy_method(self, *args, **kwargs):
        # 获取HTTP方法和路径
        method = original_method._http_method
        path_template = original_method._path
        
        # 处理路径参数
        path = path_template
        path_param_count = path_template.count('{')
        path_args = args[:path_param_count]
        other_args = args[path_param_count:]
        for i, arg in enumerate(path_args):
            path = re.sub(r'\{[^}]+\}', str(arg), path, count=1)
        
        # 处理查询参数
        params = {}
        for key, value in kwargs.items():
            if key not in ['data', 'json', 'headers']:
                if isinstance(value, bool):
                    params[key] = str(value).lower()
                else:
                    params[key] = value
        
        # 处理POST请求体自动组装
        data = kwargs.get('data')
        json_data = kwargs.get('json')
        headers = kwargs.get('headers', {})
        
        # 添加 from-source: inner 请求头
        headers = {**headers, "from-source": "inner"}
        
        if method == 'POST' and json_data is None and data is None:
            # 自动组装json体（去除path参数和headers参数）
            sig = inspect.signature(original_method)
            param_names = list(sig.parameters.keys())[1:]  # 跳过self
            # 跳过path参数
            param_names = param_names[path_param_count:]
            json_data = {}
            # 先处理多余的位置参数
            for i, v in enumerate(other_args):
                if i < len(param_names):
                    json_data[param_names[i]] = v
            # 再处理kwargs
            for k, v in kwargs.items():
                if k not in ['data', 'json', 'headers'] and k in param_names:
                    json_data[k] = v
            headers = {**headers, "Content-Type": "application/json"}
        elif json_data is not None:
            headers = {**headers, "Content-Type": "application/json"}
        
        # 调用远程服务
        async with FeignProxy(service_name) as proxy:
            return await proxy.call(method, path, params=params, data=data, json=json_data, headers=headers)
    
    return proxy_method

def get(path: str):
    """GET请求装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 这个方法会被feign_client装饰器替换
            pass
        wrapper._http_method = 'GET'
        wrapper._path = path
        return wrapper
    return decorator

def post(path: str):
    """POST请求装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 这个方法会被feign_client装饰器替换
            pass
        wrapper._http_method = 'POST'
        wrapper._path = path
        return wrapper
    return decorator

class NacosClient:
    """Nacos客户端"""
    
    def __init__(self, server_addr: str, service_name: str, port: int, ip: str = None):
        self.server_addr = server_addr
        self.service_name = service_name
        self.port = port
        self.ip = ip or '127.0.0.1'  # 默认使用127.0.0.1
        self.session = None
        self.heartbeat_task = None
        self.running = False
        
    async def start(self):
        """启动Nacos客户端"""
        self.session = aiohttp.ClientSession()
        await self.register_service()
        print(f"✅ 服务注册成功: {self.service_name} -> {self.server_addr}")
        
        # 启动心跳任务
        self.running = True
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        
    async def register_service(self):
        """注册服务到Nacos"""
        url = f"http://{self.server_addr}/nacos/v1/ns/instance"
        data = {
            'serviceName': self.service_name+"-py",
            'ip': self.ip,
            'port': str(self.port),
            'healthy': 'true',
            'enabled': 'true',
            'weight': '1.0',
            'metadata': json.dumps({'version': '1.0.0'})
        }
        
        async with self.session.post(url, data=data) as resp:
            if resp.status == 200:
                print(f"🎯 服务注册成功: {self.service_name}")
            else:
                print(f"❌ 服务注册失败: {self.service_name}")
    
    async def heartbeat_loop(self):
        """心跳循环，每10秒发送一次心跳"""
        print(f"🔄 心跳循环启动: {self.service_name}")
        while self.running:
            try:
                await asyncio.sleep(10)  # 10秒心跳间隔
                if self.running:
                    print(f"⏰ 准备发送心跳: {self.service_name}")
                    await self.send_heartbeat()
            except Exception as e:
                print(f"⚠️ 心跳发送异常: {e}")
    
    async def send_heartbeat(self):
        """发送心跳"""
        url = f"http://{self.server_addr}/nacos/v1/ns/instance/beat"
        params = {
            'serviceName': self.service_name+"-py",
            'ip': self.ip,
            'port': str(self.port),
            'weight': '1.0',
            'metadata': json.dumps({'version': '1.0.0'})
        }
        
        try:
            async with self.session.put(url, params=params) as resp:
                if resp.status == 200:
                    print(f"💓 心跳发送成功: {self.service_name}")
                else:
                    print(f"⚠️ 心跳发送失败: {self.service_name}, 状态码: {resp.status}")
        except Exception as e:
            print(f"❌ 心跳发送异常: {self.service_name}, 错误: {e}")
    
    async def deregister_service(self):
        """注销服务"""
        url = f"http://{self.server_addr}/nacos/v1/ns/instance"
        params = {
            'serviceName': self.service_name+"-py",
            'ip': self.ip,
            'port': self.port
        }
        
        try:
            async with self.session.delete(url, params=params) as resp:
                if resp.status == 200:
                    print(f"🔚 服务注销成功: {self.service_name}")
                else:
                    print(f"⚠️ 服务注销失败: {self.service_name}, 状态码: {resp.status}")
        except Exception as e:
            print(f"❌ 服务注销异常: {self.service_name}, 错误: {e}")
    
    async def stop(self):
        """停止Nacos客户端"""
        self.running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        await self.deregister_service()
        if self.session:
            await self.session.close()
    
    async def list_services(self):
        """获取服务列表"""
        try:
            url = f"http://{self.server_addr}/nacos/v1/ns/service/list"
            params = {
                'pageNo': '1',
                'pageSize': '100'
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    services = []
                    if 'doms' in data:
                        for service in data['doms']:
                            services.append(service)
                    return services
                else:
                    print(f"⚠️ 获取服务列表失败，状态码: {resp.status}")
                    return []
        except Exception as e:
            print(f"❌ 获取服务列表异常: {e}")
            return []

class FeignProxy:
    """Feign代理，用于客户端调用"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def call(self, method: str, path: str, **kwargs):
        """调用远程服务"""
        # 这里应该从Nacos获取服务地址
        # 简化实现，直接使用配置的地址
        base_url = f"http://127.0.0.1:9201"
        url = f"{base_url}{path}"
        
        async with self.session.request(method, url, **kwargs) as resp:
            return await resp.json()

def config_var(config_key: str, default: Any = None):
    """
    配置变量装饰器，类似Java @Value
    用法: redis_host = config_var("spring.data.redis.host", "localhost")
    """
    return get_config_value(config_key, default)

def create_config_vars():
    """
    创建配置变量，在init_sidecar后调用
    用法: 
    redis_host, redis_port, db_url = create_config_vars(
        "spring.data.redis.host",
        "spring.data.redis.port", 
        "spring.datasource.url"
    )
    """
    def _create_vars(*config_keys):
        return [get_config_value(key) for key in config_keys]
    return _create_vars

# 导出主要接口
__all__ = [
    'init_sidecar',
    'feign', 
    'get',
    'post',
    'config',
    'get_config_value',
    'local_config'
] 