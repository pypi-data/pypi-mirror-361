## 基于功能分类的fastapi项目结构

```
app_name_function/                      # 项目名称
  ├─requirements.txt			# 安装依赖文件
  ├─.env				# 环境变量文件
  ├─README.md
  ├─migrations/				# 数据库迁移相关
  ├─src/					# 主应用目录
  │   ├─main.py				# FastAPI应用入口
  │   ├─__init__.py
  │   ├─api/				# API路由
  │   │   ├─__init__.py
  │   │   └─v1/				# API版本1
  │   │       ├─routers.py		# 路由聚合
  │   │       ├─__init__.py
  │   │       └─endpoints/		# 各个端点API对应的URL
  │   │           ├─items.py		# 例如物品API
  │   │           ├─users.py		# 例如用户API
  │   │           └─__init__.py
  │   ├─core/				# 核心配置和工具
  │   │   ├─config.py			# 应用配置
  │   │   ├─security.py			# 认证和安全相关
  │   │   └─__init__.py
  │   ├─db/				# 数据库相关
  │   │   ├─session.py			# 数据库会话
  │   │   ├─__init__.py
  │   │   └─repositories/		# 数据库操作
  │   │       ├─item_db.py
  │   │       └─user_db.py
  │   ├─models/				# 数据模型
  │   │   ├─db_models.py		# ORM模型 数据库模型
  │   │   ├─schemas.py			# Pydantic模型
  │   │   └─__init__.py
  │   ├─services/			# 业务逻辑
  │   │   ├─item_service.py		# 例如物品业务逻辑
  │   │   ├─user_service.py		# 例如用户业务逻辑
  │   │   └─__init__.py
  │   └─utils/				# 工具相关
  │       ├─helpers.py			# 辅助函数
  │       ├─logger.py			# 日志配置
  │       └─__init__.py
  ├─static/				# 静态文件
  └─tests/				# 测试用例
      ├─conftest.py
      ├─test_xx.py
      └─__init__.py
```

## 部署

构建镜像

```
docker build -t app_name .
```

运行容器

```
docker run -d --name fastapi -p 20201:20201 appname
```
