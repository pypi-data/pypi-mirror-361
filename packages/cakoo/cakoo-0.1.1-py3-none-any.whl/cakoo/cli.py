def main():
    from rich import print
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress
    import time

    console = Console()

    console.rule("[bold bright_blue]cakoo CLI[/]", style="cyan")
    console.print("[bold]Cross-Platform C++ Project Manager[/bold]", style="bright_white")
    console.print("[dim]By Vishal | Powered by CMake + Clang + Conan/vcpkg\n[/dim]")

    name = Prompt.ask("[green]📦 Project name[/green]", default="aura")
    dep = Prompt.ask("[magenta]🔧 Dependency manager[/magenta]", choices=["vcpkg", "conan"], default="vcpkg")
    target = Prompt.ask("[yellow]🎯 Target platform[/yellow]",
                        choices=["windows", "linux", "macos", "android"], default="windows")

    console.print("\n[bold underline]Summary:[/bold underline]")
    console.print(f"📦 [cyan]Project[/cyan]: [bold]{name}[/bold]")
    console.print(f"🔧 [cyan]Dependencies[/cyan]: [bold]{dep}[/bold]")
    console.print(f"🎯 [cyan]Target[/cyan]: [bold]{target}[/bold]")

    if Confirm.ask("\n🚀 [bold green]Proceed with setup?[/bold green]", default=True):
        with Progress() as progress:
            task = progress.add_task(f"[green]Initializing project files...", total=100)
            for _ in range(20):
                time.sleep(0.1)
                progress.update(task, advance=5)
        console.print("\n✅ [bold green]Project initialized successfully![/bold green]")
    else:
        console.print("\n❌ [bold red]Setup canceled.[/bold red]")
