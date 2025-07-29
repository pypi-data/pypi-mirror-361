#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feign客户端示例
演示如何使用Ultra Pass Sidecar进行微服务调用

功能描述:
- 演示Feign风格的服务调用
- 调用不同微服务接口
- 异构服务调用（Java、Python等）
- 异步调用示例
- 服务发现和负载均衡

@author: lzg
@created: 2025-07-04 11:28:56
@version: 1.0.0
"""

import asyncio
from ultra_pass_sidecar import feign, get

# 调用您的Python服务端接口
@feign("ruoyi-system")
class SysUserService:
    @get("/user/info/{username}")
    async def get_user_info(self, username: str):
        """获取用户信息 - 调用服务端接口"""
        pass

@feign("python-test-server")
class HelloService:
    @get("/user/hello/{name}")
    async def get_hello(self, name: str):
        """问候接口 - 调用服务端接口"""
        pass

async def main():
    print("📞 测试调用服务端接口...")
    
    # 调用服务端接口
    sys_user_service = SysUserService()
    
    # 调用 /user/info/{username} 接口
    result = await sys_user_service.get_user_info("admin")
    print(f"✅ 用户信息接口调用结果: {result}")

    # 调用 /user/hello/{name} 接口
    hello_service = HelloService()
    hello_result = await hello_service.get_hello("admin")
    print(f"✅ 问候接口调用结果: {hello_result}")

if __name__ == '__main__':
    asyncio.run(main()) 