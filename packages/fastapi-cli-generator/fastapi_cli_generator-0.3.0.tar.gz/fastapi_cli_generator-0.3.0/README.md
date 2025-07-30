# FastAPI CLI Generator

🚀 A command-line tool for quickly creating FastAPI projects with different architectural patterns.

[中文文档](README_CN.md) | [English Documentation](README.md)

## Features

- 🏗️ **Two Architecture Patterns**: Functional layered vs Modular architecture
- 🎯 **Interactive CLI**: User-friendly interface with Chinese support
- 📁 **Complete Project Structure**: Templates based on best practices
- ⚡ **Ready to Use**: Generated projects can run immediately
- 🔧 **Modern Configuration**: Pydantic Settings with type safety and multi-environment support
- 🐳 **Docker Ready**: Includes Dockerfile and deployment configurations
- 📝 **Environment Management**: Support for .env and .env.prod with proper priority

## Installation

```bash
pip install fastapi-cli-generator -i https://pypi.org/simple
```

## Quick Start

### Interactive Mode (Recommended)

```bash
fastapi-create
```

### Command Line Mode

```bash
# Create with specific template
fastapi-create create my-project --template module
fastapi-create create my-project --template function

# List available templates
fastapi-create list-templates
```

## Usage

### Basic Usage

```bash
# Create project (interactive mode)
fastapi-create my-project

# Specify template type
fastapi-create my-project --template module
fastapi-create my-project --template function
```

### List Available Templates

```bash
fastapi-create list-templates
```

## Architecture Patterns

### 1. Modular Architecture (module) - Recommended

Organize code by business domains, each module contains complete MVC structure:

```
my-project/
├── src/
│   ├── core/                 # 核心配置
│   │   ├── config.py         # Pydantic Settings配置
│   │   ├── dependencies.py   # 共享依赖项
│   │   └── security.py       # 认证和安全
│   ├── modules/              # 业务模块
│   │   ├── auth/             # 认证模块
│   │   ├── users/            # 用户管理
│   │   └── items/            # 项目管理
│   └── shared/               # 共享工具
│       ├── database.py       # 数据库连接
│       └── utils.py          # 共享工具函数
├── tests/                    # 测试文件
├── .env                      # 开发环境配置
├── .env.prod                 # 生产环境配置
├── Dockerfile                # Docker部署配置
└── requirements.txt
```

### 2. Functional Layered Architecture (function)

Organize code by technical layers:

```
my-project/
├── src/
│   ├── api/v1/endpoints/     # API端点
│   ├── core/                 # 核心配置
│   │   └── config.py         # Pydantic Settings配置
│   ├── db/repositories/      # 数据库操作
│   ├── models/               # 数据模型
│   ├── services/             # 业务逻辑
│   └── utils/                # 工具函数
├── tests/                    # 测试文件
├── .env                      # 开发环境配置
├── .env.prod                 # 生产环境配置
├── Dockerfile                # Docker部署配置
└── requirements.txt
```

## Configuration Management

Generated projects use **Pydantic Settings** for type-safe configuration management:

### Environment Files Priority
- `.env` - Development environment (default)
- `.env.prod` - Production environment (higher priority)

### Configuration Features
- **Type Safety**: All settings are properly typed (bool, str, int, etc.)
- **Default Values**: Sensible defaults for quick start
- **Environment Override**: Production settings override development ones
- **Validation**: Automatic validation of configuration values

### Example Configuration
```python
# src/core/config.py
class Settings(BaseSettings):
    DEBUG_MODE: bool = True
    STATIC_DIR: str = "static"
    STATIC_URL: str = "/static"
    STATIC_NAME: str = "static"

    class Config:
        env_file = (".env", ".env.prod")  # Multiple env files, latter takes priority
```

## Running Generated Projects

```bash
# Navigate to your project
cd my-project

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.main:app --reload

# Or run with custom host/port
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### Docker Deployment

```bash
# Build image
docker build -t my-project .

# Run container
docker run -d --name my-project -p 8080:20201 my-project
```

## Development

```bash
# Clone repository
git clone https://github.com/xukache/fastapi-cli-generator.git
cd fastapi-cli-generator

# Install in development mode
pip install -e .

# Test the CLI
fastapi-create --help

# Run tests
python test_generation.py
```

## License

MIT License
