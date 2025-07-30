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
import questionary

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


def interactive_create():
    """交互式创建项目"""
    # 显示欢迎信息
    welcome_text = Text("FastAPI项目脚手架生成工具", style="bold blue")
    console.print(Panel(welcome_text, title="欢迎", border_style="blue"))

    console.print("\n[bold green]让我们一起创建你的FastAPI项目！[/bold green]\n")

    try:
        # 1. 获取项目名称
        project_name = questionary.text(
            "请输入项目名称:",
            validate=lambda x: len(x) > 0 and x.replace('-', '').replace('_', '').isalnum(),
            instruction="(只能包含字母、数字、连字符和下划线)"
        ).ask()

        if not project_name:
            console.print("[yellow]已取消创建[/yellow]")
            return

        # 2. 选择架构模式
        console.print(f"\n[bold blue]项目名称:[/bold blue] {project_name}")
        console.print("[bold blue]请选择项目架构模式:[/bold blue]")

        template_choice = questionary.select(
            "选择架构:",
            choices=[
                questionary.Choice(
                    title="🧩 模块化架构 - 按业务领域组织代码 (推荐)",
                    value="module"
                ),
                questionary.Choice(
                    title="🏗️ 功能分层架构 - 按技术层次组织代码",
                    value="function"
                ),
            ],
            instruction="使用方向键选择，回车确认"
        ).ask()

        if not template_choice:
            console.print("[yellow]已取消创建[/yellow]")
            return

        # 3. 确认创建
        console.print(f"\n[bold green]配置确认:[/bold green]")
        console.print(f"项目名称: [cyan]{project_name}[/cyan]")
        console.print(f"架构模式: [cyan]{'模块化架构' if template_choice == 'module' else '功能分层架构'}[/cyan]")

        confirm = questionary.confirm("确认创建项目?", default=True).ask()

        if not confirm:
            console.print("[yellow]已取消创建[/yellow]")
            return

        # 4. 创建项目
        generator = ProjectGenerator(project_name, template_choice)
        project_path = generator.generate()

        # 5. 显示成功信息
        success_panel = Panel(
            f"项目 '[bold green]{project_name}[/bold green]' 创建成功！\n\n"
            f"位置: [cyan]{project_path}[/cyan]\n"
            f"架构: [cyan]{'模块化架构' if template_choice == 'module' else '功能分层架构'}[/cyan]\n\n"
            f"下一步操作:\n"
            f"   cd {project_name}\n"
            f"   pip install -r requirements.txt\n"
            f"   uvicorn src.main:app --reload",
            title="创建成功",
            border_style="green"
        )
        console.print(success_panel)

    except KeyboardInterrupt:
        console.print("\n[yellow]已取消创建[/yellow]")
    except Exception as e:
        error_panel = Panel(
            f"创建项目时出错: {str(e)}",
            title="错误",
            border_style="red"
        )
        console.print(error_panel)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
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
    # 如果没有提供子命令，启动交互式创建
    if ctx.invoked_subcommand is None:
        interactive_create()


@app.command()
def create(
    project_name: Optional[str] = typer.Argument(None, help="要创建的项目名称"),
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
        fastapi-create create my-project
        fastapi-create create my-project --template module
        fastapi-create create  # 交互式创建
    """

    # 如果没有提供项目名称，启动交互式创建
    if project_name is None:
        interactive_create()
        return

    try:
        # 交互式选择模板类型
        if template is None:
            console.print(f"\n[bold blue]项目名称:[/bold blue] {project_name}")
            console.print("[bold blue]请选择项目架构模式:[/bold blue]")

            template_choice = questionary.select(
                "选择架构:",
                choices=[
                    questionary.Choice(
                        title="🧩 模块化架构 - 按业务领域组织代码 (推荐)",
                        value="module"
                    ),
                    questionary.Choice(
                        title="🏗️ 功能分层架构 - 按技术层次组织代码",
                        value="function"
                    ),
                ],
                instruction="使用方向键选择，回车确认"
            ).ask()

            if not template_choice:
                console.print("[yellow]已取消创建[/yellow]")
                return

            template = template_choice

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
