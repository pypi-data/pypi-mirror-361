## 基于模块分类的fastapi项目结构

```
app_name_module/				# 项目名称
  ├─README.md					# 项目文档
  ├─.env					# 环境变量文件
  ├─requirements.txt				# 依赖安装文件
  ├─migrations					# 迁移相关文件夹
  ├─src						# 源代码目录
  │   ├─main.py					# FastAPI 应用入口
  │   ├─__init__.py
  │   ├─core/					# 核心配置和共享代码
  │   │   ├─config.py				# 应用配置
  │   │   ├─dependencies.py			# 共享依赖项
  │   │   ├─security.py				# 认证和安全
  │   │   └─__init__.py
  │   ├─modules/				# 功能模块目录
  │   │   ├─auth/				# 认证模块
  │   │   │   ├─dependencies.py			# 模块特定依赖
  │   │   │   ├─models.py			# ORM模型
  │   │   │   ├─repositories.py			# 数据库操作
  │   │   │   ├─routers.py			# 路由定义
  │   │   │   ├─schemas.py			# Pydantic模型
  │   │   │   ├─services.py			# 业务逻辑
  │   │   │   └─__init__.py
  │   │   ├─items/				# 商品模块
  │   │   │   ├─dependencies.py
  │   │   │   ├─models.py
  │   │   │   ├─repositories.py
  │   │   │   ├─routers.py
  │   │   │   ├─schemas.py
  │   │   │   ├─services.py
  │   │   │   └─__init__.py
  │   │   └─users/				# 用户模块
  │   │       ├─dependencies.py
  │   │       ├─models.py
  │   │       ├─repositories.py
  │   │       ├─routers.py
  │   │       ├─schemas.py
  │   │       ├─services.py
  │   │       └─__init__.py
  │   └─shared/					# 共享代码
  │       ├─database.py				# 数据库连接
  │       ├─utils.py				# 共享工具函数
  │       └─__init__.py
  ├─static/
  └─tests/					# 测试目录
      ├─conftest.py
      ├─test_xx.py
      └─__init__.py
```
