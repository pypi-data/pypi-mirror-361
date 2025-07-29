#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask服务端示例
演示如何使用Ultra Pass Sidecar异构服务

功能描述:
- 演示Flask应用集成sidecar
- 包含多个API接口示例
- 自动权限拦截
- 配置中心使用示例
- 异构服务提供者示例

@author: lzg
@created: 2025-07-02 16:45:18
@version: 1.0.0
"""

from flask import Flask, request
from ultra_pass_sidecar import init_sidecar, config_local, config_remote

app = Flask(__name__)

@app.route('/api/hello/<name>', methods=['GET'])
def hello(name):
    return {'message': f'Hello, {name}!'}

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    include_orders = request.args.get('include_orders', 'false').lower() == 'true'
    user_data = {
        'user_id': user_id, 
        'name': f'User{user_id}', 
        'email': f'user{user_id}@example.com'
    }
    if include_orders:
        user_data['orders'] = [{'id': 1, 'status': '已支付'}, {'id': 2, 'status': '待发货'}]
    return user_data

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return {
        'id': 999,
        'name': data.get('name'),
        'email': data.get('email'),
        'age': data.get('age'),
        'status': 'created'
    }

@app.route('/api/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    return {
        'keyword': keyword,
        'page': page,
        'size': size,
        'total': 100,
        'results': [
            {'id': 1, 'title': f'搜索结果1 - {keyword}'},
            {'id': 2, 'title': f'搜索结果2 - {keyword}'}
        ]
    }

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return {'orders': [{'id': 1, 'status': '已支付'}, {'id': 2, 'status': '待发货'}]}

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置信息"""
    return {
        'server_port': server_port,
        'redis_host': redis_host,
        'redis_port': redis_port,
        'app_name': app_name,
        'environment': environment
    }

if __name__ == '__main__':
    print('🚀 启动Flask服务端...')
    init_sidecar(app)  # 传入app实例，自动设置权限拦截器
    
    # 获取配置
    server_port = config_local('server.port', 9201)
    redis_host = config_remote('spring.data.redis.host', 'localhost')
    redis_port = config_remote('spring.data.redis.port', 6379)
    app_name = config_remote('application.name', 'unknown')
    environment = config_remote('profiles.active', 'dev')
    
    print(f'📋 配置信息:')
    print(f'  - 服务器端口: {server_port}')
    print(f'  - Redis主机: {redis_host}')
    print(f'  - Redis端口: {redis_port}')
    print(f'  - 应用名称: {app_name}')
    print(f'  - 环境: {environment}')
    
    app.run(host='0.0.0.0', port=server_port, debug=True) 