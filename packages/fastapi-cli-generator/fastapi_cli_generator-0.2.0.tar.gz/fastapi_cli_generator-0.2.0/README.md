# FastAPI CLI Generator

🚀 A command-line tool for quickly creating FastAPI projects with different architectural patterns.

[中文文档](README_CN.md) | [English Documentation](README.md)

## Features

- 🏗️ **Two Architecture Patterns**: Functional layered vs Modular architecture
- 🎯 **Interactive CLI**: User-friendly interface with Chinese support
- 📁 **Complete Project Structure**: Templates based on best practices
- ⚡ **Ready to Use**: Generated projects can run immediately

## Installation

```bash
pip install fastapi-cli-generator
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
│   ├── modules/              # 业务模块
│   │   ├── auth/             # 认证模块
│   │   ├── users/            # 用户管理
│   │   └── items/            # 项目管理
│   └── shared/               # 共享工具
├── tests/                    # 测试文件
└── requirements.txt
```

### 2. Functional Layered Architecture (function)

Organize code by technical layers:

```
my-project/
├── src/
│   ├── api/v1/endpoints/     # API端点
│   ├── core/                 # 核心配置
│   ├── db/repositories/      # 数据库操作
│   ├── models/               # 数据模型
│   ├── services/             # 业务逻辑
│   └── utils/                # 工具函数
├── tests/                    # 测试文件
└── requirements.txt
```

## Develop

```bash
# 克隆项目
git clone <repository-url>
cd fastapi_proj_template

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装为可编辑包
pip install -e .

# 运行测试
python test_generation.py
```

## License

MIT License
