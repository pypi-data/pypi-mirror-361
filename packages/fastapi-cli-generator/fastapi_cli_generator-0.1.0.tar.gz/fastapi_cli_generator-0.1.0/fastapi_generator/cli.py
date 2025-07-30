"""
FastAPI项目脚手架生成工具 - 主CLI接口
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import Optional
from pathlib import Path

from .generator import ProjectGenerator

console = Console()
app = typer.Typer(
    name="fastapi-create",
    help="FastAPI项目脚手架生成工具 - 快速创建FastAPI项目！",
    rich_markup_mode="rich",
)


def version_callback(value: bool):
    """显示版本信息"""
    if value:
        from . import __version__
        console.print(f"FastAPI脚手架工具版本: [bold green]{__version__}[/bold green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="显示版本信息并退出",
    ),
):
    """
    🚀 FastAPI项目脚手架生成工具

    快速创建不同架构模式的FastAPI项目
    """
    pass


@app.command()
def create(
    project_name: str = typer.Argument(..., help="要创建的项目名称"),
    template: Optional[str] = typer.Option(
        None,
        "--template",
        "-t",
        help="模板类型: 'function'(功能分层) 或 'module'(模块化)",
    ),
):
    """
    创建新的FastAPI项目

    示例:
        fastapi-create my-project
        fastapi-create my-project --template module
        fastapi-create my-project --template function
    """

    # 显示欢迎信息
    welcome_text = Text("FastAPI项目脚手架生成工具", style="bold blue")
    console.print(Panel(welcome_text, title="欢迎", border_style="blue"))

    try:
        # 交互式选择模板类型
        if template is None:
            console.print("\n[bold blue]请选择项目架构模式:[/bold blue]")
            console.print("1. [green]function[/green] - 功能分层架构 (按技术层次组织代码)")
            console.print("2. [green]module[/green] - 模块化架构 (按业务领域组织代码)")

            choice = typer.prompt("\n请输入选择 (1 或 2)", type=int)
            if choice == 1:
                template = "function"
            elif choice == 2:
                template = "module"
            else:
                console.print("[red]无效选择，使用默认模块化架构[/red]")
                template = "module"

        # 生成项目
        generator = ProjectGenerator(project_name, template)
        project_path = generator.generate()

        # 显示成功信息
        success_panel = Panel(
            f"项目 '[bold green]{project_name}[/bold green]' 创建成功！\n\n"
            f"位置: [cyan]{project_path}[/cyan]\n"
            f"架构: [cyan]{'功能分层架构' if template == 'function' else '模块化架构'}[/cyan]\n\n"
            f"下一步操作:\n"
            f"   cd {project_name}\n"
            f"   pip install -r requirements.txt\n"
            f"   uvicorn src.main:app --reload",
            title="创建成功",
            border_style="green"
        )
        console.print(success_panel)

    except Exception as e:
        error_panel = Panel(
            f"创建项目时出错: {str(e)}",
            title="错误",
            border_style="red"
        )
        console.print(error_panel)
        raise typer.Exit(1)


@app.command()
def list_templates():
    """列出可用的项目模板"""
    templates_info = [
        ("function", "功能分层架构", "按技术层次组织代码 (api/services/models/db分离)"),
        ("module", "模块化架构", "按业务领域组织代码 (每个模块包含完整的MVC结构)"),
    ]

    console.print("\n[bold blue]可用模板:[/bold blue]\n")

    for template_id, name, description in templates_info:
        console.print(f"* [bold green]{template_id}[/bold green] - {name}")
        console.print(f"  {description}\n")


if __name__ == "__main__":
    app()
