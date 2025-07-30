#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask服务端示例
演示如何使用Ultra Pass Sidecar异构服务

功能描述:
- 演示Flask应用集成sidecar
- 调用微服务的AuthPermissionService
- 提供用户信息和菜单资源接口

@author: lzg
@created: 2025-07-02 16:45:18
@version: 1.0.0
"""

from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from ultra_pass_sidecar import init_sidecar, config_local, config_remote
from ultra_pass_sidecar import feign, get
import os

app = Flask(__name__)
CORS(app)  # 启用CORS支持

@feign("ruoyi-system")
class AuthPermissionService:
    """权限微服务接口"""
    
    @get("/external/menu/resources")
    async def get_menu_resources(self, code: str):
        """获取菜单资源"""
        pass 

    @get("/external/user/info")
    async def get_user_info(self):
        """获取用户信息"""
        pass 

# 创建微服务实例
auth_service = AuthPermissionService()

@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory('.', 'index.html')

@app.route('/api/user/info', methods=['GET'])
async def get_user_info():
    """获取用户信息接口"""
    try:
        # 调用微服务获取用户信息（feign会自动从cookie获取token）
        user_info = await auth_service.get_user_info()
        
        return jsonify(user_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menu/resources', methods=['GET'])
async def get_menu_resources():
    """获取菜单资源接口"""
    try:
        # 从请求参数获取code
        code = request.args.get('code', '')
        
        # 调用微服务获取菜单资源（feign会自动从cookie获取token）
        menu_resources = await auth_service.get_menu_resources(code=code)
        
        return jsonify(menu_resources)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('🚀 启动Flask服务端...')
    init_sidecar(app)  # 传入app实例，自动设置权限拦截器
    
    # 获取配置
    server_port = config_local('server.port', 9202)
    app_name = config_remote('application.name', 'ultra-pass-py-template')
    environment = config_remote('profiles.active', 'dev')
    
    print(f'📋 配置信息:')
    print(f'  - 服务器端口: {server_port}')
    print(f'  - 应用名称: {app_name}')
    print(f'  - 环境: {environment}')
    print(f'🌐 前端页面: http://localhost:{server_port}')
    print(f'👤 用户信息接口: http://localhost:{server_port}/api/user/info')
    print(f'📋 菜单资源接口: http://localhost:{server_port}/api/menu/resources')
    
    app.run(host='0.0.0.0', port=server_port, debug=True) 