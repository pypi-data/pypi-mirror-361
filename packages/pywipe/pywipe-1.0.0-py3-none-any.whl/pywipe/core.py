# core.py

import subprocess
from rich.console import Console
from rich.table import Table
from .config import BASE_PACKAGES

console = Console()

def get_installed_packages():
    """
    Retrieves a list of all installed packages.
    """
    try:
        result = subprocess.run(
            ['pip', 'list', '--format=freeze'],
            capture_output=True,
            text=True,
            check=True
        )
        return [line.split('==')[0] for line in result.stdout.strip().split('\n')]
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]Error: Could not list installed packages. Is pip installed and in your PATH?[/red]")
        return []

def get_packages_to_uninstall(whitelist):
    """
    Determines which packages to uninstall based on the whitelist.
    """
    installed_packages = get_installed_packages()
    protected_packages = BASE_PACKAGES.union(set(whitelist))
    return [pkg for pkg in installed_packages if pkg not in protected_packages]

def uninstall_packages(packages, dry_run=False):
    """
    Uninstalls the given list of packages.
    """
    if not packages:
        console.print("[yellow]No user-installed packages to uninstall.[/yellow]")
        return

    table = Table(title="Packages to be Uninstalled")
    table.add_column("Package Name", style="cyan")

    for pkg in packages:
        table.add_row(pkg)

    console.print(table)

    if dry_run:
        console.print("\n[bold yellow]Dry run mode. No packages will be uninstalled.[/bold yellow]")
        return

    if not console.confirm("\n[bold red]Do you want to proceed with uninstallation?[/bold red]"):
        console.print("[yellow]Aborted.[/yellow]")
        return

    for pkg in packages:
        try:
            console.print(f"Uninstalling {pkg}...")
            subprocess.run(
                ['pip', 'uninstall', '-y', pkg],
                capture_output=True,
                text=True,
                check=True
            )
            console.print(f"[green]✔[/green] Uninstalled [bold]{pkg}[/bold] successfully.")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error uninstalling {pkg}: {e.stderr}[/red]")