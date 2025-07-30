"""
FastAPI脚手架工具的主入口点
"""

if __name__ == "__main__":
    try:
        from .cli import app
        app()
    except ImportError:
        # 如果没有安装依赖，提供简化版本
        import sys
        from .generator import ProjectGenerator
        
        if len(sys.argv) < 3:
            print("使用方法: python -m fastapi_generator <项目名> <模板类型>")
            print("模板类型: function 或 module")
            sys.exit(1)
        
        project_name = sys.argv[1]
        template_type = sys.argv[2] if len(sys.argv) > 2 else "module"
        
        try:
            generator = ProjectGenerator(project_name, template_type)
            project_path = generator.generate()
            print(f"✅ 项目 '{project_name}' 创建成功！")
            print(f"📁 位置: {project_path}")
            print(f"🏛️ 架构: {'功能分层架构' if template_type == 'function' else '模块化架构'}")
        except Exception as e:
            print(f"❌ 创建项目失败: {e}")
            sys.exit(1)
