# Ultra Pass Sidecar

> 功能描述: sidecar库文档，包含API说明、安装指南、使用示例、异构服务支持等  
> @author: lzg  
> @created: 2025-07-01 15:47:21  
> @version: 1.0.0  

Ultra Pass Python Sidecar 是一个简洁的Python微服务sidecar库，支持自动注册到Nacos和Feign风格调用。

## 功能特性

- ✅ **自动服务注册**：一键注册到Nacos服务发现中心
- ✅ **Feign风格调用**：类似Java Feign的简洁客户端调用
- ✅ **异构服务支持**：支持调用Java、Go、Node.js等不同语言的服务
- ✅ **配置中心支持**：自动从Nacos配置中心拉取配置
- ✅ **心跳保活**：自动心跳机制，保持服务在线
- ✅ **优雅关闭**：支持信号处理，优雅注销服务
- ✅ **多框架支持**：支持Flask、FastAPI等主流框架

## 快速开始

### 1. 安装依赖

#### 方式一：安装所有依赖（推荐）
```bash
pip install ultra-pass-sidecar==0.0.2
```

#### 方式二：从源码安装
```bash
git clone https://github.com/****/ultra-pass-py-sidecar.git
cd ultra-pass-py-sidecar/ultra_pass_sidecar
pip install -e .
```

### 2. 配置文件

创建 `bootstrap.yml`：

```yaml
server:
  port: 9202

application:
  name: python-test-server

profiles:
  active: dev

cloud:
  nacos:
    discovery:
      server-addr: 49.233.171.89:8848
      ip: 10.12.6.236
    config:
      server-addr: 49.233.171.89:8848
      file-extension: yml
      shared-configs:
        - application-${spring.profiles.active}.${spring.cloud.nacos.config.file-extension}
```

### 3. 服务端使用

```python
from flask import Flask
from ultra_pass_sidecar import init_sidecar, config_local, config_remote

app = Flask(__name__)

@app.route('/api/hello/<name>')
def hello(name):
    return {'message': f'Hello, {name}!'}

if __name__ == '__main__':
    # 一行代码启动sidecar
    init_sidecar()
    
    # 从配置文件读取端口
    port = config_local('server.port', 9202)
    # 从配置中心读取其他配置
    redis_host = config_remote('spring.data.redis.host', 'localhost')
    app.run(host='0.0.0.0', port=port, debug=True)
```

### 4. 客户端使用

```python
import asyncio
from ultra_pass_sidecar import feign, get

@feign("python-test-server")
class HelloService:
    @get("/api/hello/{name}")
    async def hello(self, name: str):
        pass

async def main():
    service = HelloService()
    result = await service.hello("World")
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
```

## 系统架构

### 线程架构图

```mermaid
graph TD
    A[程序启动] --> B[主线程启动]
    B --> C[Flask应用初始化]
    C --> D[加载bootstrap.yml]
    D --> E[注册路由]
    E --> F[调用init_sidecar]
    F --> G[创建子线程]
    G --> H[子线程启动事件循环]
    H --> I[启动Nacos客户端]
    I --> J[注册服务到Nacos]
    J --> K[创建心跳任务]
    K --> L[启动配置中心]
    L --> M[保持事件循环运行]
    M --> N[心跳任务每10秒执行]
    N --> O[服务保持在线]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style G fill:#fff3e0
    style K fill:#e8f5e8
    style N fill:#ffebee
```

### 并行执行时序图

```mermaid
sequenceDiagram
    participant MT as 主线程
    participant ST as 子线程
    participant N as Nacos
    participant H as 心跳任务
    
    MT->>ST: 创建子线程
    ST->>N: 注册服务
    ST->>H: 创建心跳任务
    loop 每10秒
        H->>N: 发送心跳
        N->>H: 心跳确认
    end
    MT->>MT: 处理HTTP请求
```

### 系统组件图

```mermaid
graph LR
    subgraph "主线程"
        A[Flask应用]
        B[HTTP请求处理]
    end
    
    subgraph "子线程"
        C[事件循环]
        D[Nacos客户端]
        E[配置中心]
        F[心跳任务]
    end
    
    subgraph "外部服务"
        G[Nacos注册中心]
        H[配置中心]
    end
    
    A --> B
    C --> D
    C --> E
    C --> F
    D --> G
    E --> H
    F --> G
```

## API 参考

### 核心函数

#### `init_sidecar()`
初始化sidecar，自动注册服务到Nacos。

#### `feign(service_name: str)`
定义Feign客户端的装饰器。

#### `get(path: str)` / `post(path: str)`
HTTP请求装饰器。

#### `config_remote(config_key: str, default: Any = None)`
从Nacos配置中心获取配置值。

#### `config_local(config_key: str, default: Any = None)`
从本地bootstrap.yml获取配置值。

### 配置说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `server.port` | 服务端口 | `9202` |
| `application.name` | 服务名称 | `python-test-server` |
| `cloud.nacos.discovery.server-addr` | Nacos地址 | `49.233.171.89:8848` |
| `cloud.nacos.discovery.ip` | 服务IP | `10.12.6.236` |

## 心跳机制

- **心跳间隔**：10秒
- **超时时间**：90秒（3次心跳失败后下线）
- **自动重连**：心跳失败时自动重试
- **优雅关闭**：程序退出时自动注销服务

## 技术栈

### 核心依赖
- **Python 3.8+**
- **Flask** - Web框架
- **aiohttp** - 异步HTTP客户端
- **PyYAML** - YAML配置文件解析
- **asyncio** - 异步编程支持

### Flask生态系统
- **Flask** - 轻量级Web框架
- **Jinja2** - 模板引擎
- **Werkzeug** - WSGI工具库
- **Gunicorn** - 生产级WSGI服务器
- **uWSGI** - 高性能WSGI服务器
- **Gevent** - 异步网络库
- **Eventlet** - 网络应用框架

### 支持的Web框架
- **Flask** - 轻量级Web框架
- **FastAPI** - 现代高性能Web框架
- **Starlette** - ASGI框架
- **Uvicorn** - ASGI服务器

### 可选依赖
- **SQLAlchemy** - ORM框架
- **Redis** - 缓存数据库
- **Prometheus** - 监控指标
- **Structlog** - 结构化日志
- **Pydantic** - 数据验证
- **Rich** - 终端美化
- **Click/Typer** - 命令行工具

### 开发工具
- **Pytest** - 测试框架
- **Black** - 代码格式化
- **Flake8** - 代码检查
- **MyPy** - 类型检查

## 安装选项

### 完整安装（推荐）
```bash
pip install ultra-pass-sidecar[all]
```
包含所有依赖，支持所有功能。

### 核心安装
```bash
pip install ultra-pass-sidecar
```
仅包含核心依赖，适合轻量级使用。

### 开发安装
```bash
pip install ultra-pass-sidecar[dev]
```
包含开发工具，适合贡献代码。

### 测试安装
```bash
pip install ultra-pass-sidecar[test]
```
包含测试工具，适合运行测试。

## 注意事项

1. **端口配置**：确保bootstrap.yml中的端口未被占用
2. **网络连接**：确保能访问Nacos服务器
3. **IP配置**：生产环境需要配置正确的服务IP
4. **心跳监控**：观察日志中的心跳信息确认服务在线

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！ 