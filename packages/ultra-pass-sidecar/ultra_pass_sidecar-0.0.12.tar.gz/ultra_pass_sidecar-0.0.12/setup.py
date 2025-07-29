#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Pass Sidecar 包配置文件

功能描述:
- Python包安装配置
- 依赖管理
- 版本信息
- 发布配置

@author: lzg
@created: 2025-07-01 11:52:17
@version: 1.0.0
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements

setup(
    name="ultra-pass-sidecar",
    version="0.0.12",
    author="Luozhiguo",
    author_email="luozhiguo@example.com",  # 请替换为您的邮箱
    description="一个简洁的Python微服务sidecar，支持自动注册到Nacos和Feign风格调用，支持配置中心，支持权限，资源管理",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ultra-pass-py-sidecar",  # 请替换为您的GitHub地址
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Distributed Computing",
        "Framework :: Flask",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 核心依赖
        "flask>=2.0.0,<3.0.0",
        "requests>=2.5.0,<3.0.0",
        "pyyaml>=5.1,<7.0.0",
        "python-dotenv>=0.19.0,<1.0.0",
        "aiohttp>=3.8.0,<4.0.0",
        # Web框架支持
        "fastapi>=0.68.0,<1.0.0",
        "uvicorn>=0.15.0,<1.0.0",
        "starlette>=0.14.0,<1.0.0",
        "pydantic>=1.8.0,<2.0.0",
        "django>=3.2.0,<4.0.0",
        # 异步和网络
        "asyncio-mqtt>=0.11.0,<1.0.0",
        "aiofiles>=0.8.0,<1.0.0",
        "websockets>=10.0,<11.0.0",
        "httpx>=0.24.0,<1.0.0",
        # 数据处理
        "marshmallow>=3.14.0,<4.0.0",
        "jsonschema>=4.0.0,<5.0.0",
        "urllib3>=1.26.0,<2.0.0",
        # 日志和监控
        "structlog>=21.5.0,<22.0.0",
        "prometheus-client>=0.14.0,<1.0.0",
        # 数据库
        "sqlalchemy>=1.4.0,<2.0.0",
        "alembic>=1.7.0,<2.0.0",
        "redis>=4.0.0,<5.0.0",
        # 安全和认证
        "cryptography>=3.4.0,<4.0.0",
        "PyJWT>=2.0.0,<3.0.0",
        "bcrypt>=3.2.0,<4.0.0",
        # 命令行工具
        "click>=8.0.0,<9.0.0",
        "rich>=12.0.0,<13.0.0",
        "typer>=0.4.0,<1.0.0",

    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "isort>=5.10.0",
            "pre-commit>=2.17.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
            "responses>=0.20.0",
            "httpx>=0.24.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.17.0",
        ],
        "all": [
            # 包含所有可选依赖
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
            "starlette>=0.14.0",
            "pydantic>=1.8.0",
            "asyncio-mqtt>=0.11.0",
            "aiofiles>=0.8.0",
            "python-dotenv>=0.19.0",
            "marshmallow>=3.14.0",
            "jsonschema>=4.0.0",
            "httpx>=0.24.0",
            "websockets>=10.0",
            "urllib3>=1.26.0",
            "structlog>=21.5.0",
            "prometheus-client>=0.14.0",
            "sqlalchemy>=1.4.0",
            "alembic>=1.7.0",
            "redis>=4.0.0",
            "cryptography>=3.4.0",
            "jwt>=1.3.1",
            "bcrypt>=3.2.0",
            "click>=8.0.0",
            "rich>=12.0.0",
            "typer>=0.4.0",
            "pydantic-settings>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ultra-pass-sidecar=ultra_pass_sidecar.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ultra_pass_sidecar": ["*.yml", "*.yaml", "*.json"],
    },
    keywords=[
        "microservice",
        "sidecar",
        "nacos",
        "service-discovery",
        "feign",
        "flask",
        "fastapi",
        "async",
        "http-client",
        "configuration",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ultra-pass-py-sidecar/issues",
        "Source": "https://github.com/yourusername/ultra-pass-py-sidecar",
        "Documentation": "https://github.com/yourusername/ultra-pass-py-sidecar#readme",
    },
    license="MIT",
    zip_safe=False,
) 