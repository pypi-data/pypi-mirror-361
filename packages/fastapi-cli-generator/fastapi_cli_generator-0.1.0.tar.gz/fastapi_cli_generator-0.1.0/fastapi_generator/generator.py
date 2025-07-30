"""
FastAPI项目生成器核心模块
"""

import shutil
import re
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None


class ProjectGenerator:
    """主项目生成器类"""

    def __init__(self, project_name: str, template_type: str):
        self.project_name = project_name
        self.template_type = template_type
        self.output_dir = Path.cwd()
        self.project_path = self.output_dir / project_name

        # 验证项目名称
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', project_name):
            raise ValueError("项目名称必须以字母开头，只能包含字母、数字、连字符和下划线")

        # 验证模板类型
        if template_type not in ['function', 'module']:
            raise ValueError("模板类型必须是 'function' 或 'module'")
    
    def generate(self) -> Path:
        """生成完整的FastAPI项目"""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # 创建项目目录
            task1 = progress.add_task("正在创建项目目录...", total=None)
            self._create_project_directory()
            progress.update(task1, completed=True)

            # 复制模板结构
            task2 = progress.add_task("正在复制项目结构...", total=None)
            self._copy_template_structure()
            progress.update(task2, completed=True)

            # 替换项目名称
            task3 = progress.add_task("正在替换项目名称...", total=None)
            self._replace_project_names()
            progress.update(task3, completed=True)

        return self.project_path
    
    def _create_project_directory(self):
        """创建主项目目录"""
        if self.project_path.exists():
            raise FileExistsError(f"目录 {self.project_path} 已存在")

        self.project_path.mkdir(parents=True, exist_ok=True)

    def _copy_template_structure(self):
        """复制模板结构"""
        # 获取模板源目录
        template_source = Path(__file__).parent.parent / f"app_name_{self.template_type}"

        if not template_source.exists():
            raise FileNotFoundError(f"模板目录 {template_source} 不存在")

        # 复制整个模板结构
        for item in template_source.iterdir():
            if item.is_dir():
                shutil.copytree(item, self.project_path / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, self.project_path / item.name)
    
    def _replace_project_names(self):
        """替换模板中的项目名称占位符"""
        # 需要替换的文件类型
        text_extensions = {'.py', '.md', '.txt', '.yml', '.yaml', '.json', '.toml', '.cfg', '.ini'}

        # 遍历所有文件
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in text_extensions:
                try:
                    # 读取文件内容
                    content = file_path.read_text(encoding='utf-8')

                    # 替换占位符
                    # app_name -> 实际项目名
                    content = content.replace('app_name', self.project_name)
                    # APP_NAME -> 大写项目名
                    content = content.replace('APP_NAME', self.project_name.upper())

                    # 写回文件
                    file_path.write_text(content, encoding='utf-8')

                except (UnicodeDecodeError, PermissionError):
                    # 跳过无法读取的文件
                    continue
    

