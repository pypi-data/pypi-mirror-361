import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from .core import PufRepo
import json
from datetime import datetime
import os
from pathlib import Path
import sys

console = Console()

@click.group()
def cli():
    """PUF - Python Universal Framework for Model Version Control"""
    pass

@cli.command()
@click.option('--name', prompt='Your name', help='Your full name')
@click.option('--email', prompt='Your email', help='Your email address')
def init(name, email):
    """Initialize a new PUF repository"""
    try:
        repo = PufRepo()
        repo.init({"name": name, "email": email})
        console.print("[green]✓[/green] Initialized empty PUF repository")
        console.print(f"[blue]User:[/blue] {name} ({email})")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    finally:
        repo.close()

@cli.command()
@click.argument('model_path')
@click.option('--name', help='Model name')
@click.option('--version', help='Model version')
@click.option('--description', help='Model description')
def add(model_path, name, version, description):
    """Add a model to version control"""
    try:
        repo = PufRepo()
        metadata = {
            "name": name or model_path,
            "version": version or "1.0.0",
            "description": description or "",
            "added_at": datetime.utcnow().isoformat()
        }
        
        file_hash = repo.add_model(model_path, metadata)
        console.print(f"[green]✓[/green] Added model {name or model_path}")
        console.print(f"[blue]Hash:[/blue] {file_hash[:8]}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    finally:
        repo.close()

@cli.command()
@click.argument('model_name', required=False)
def list(model_name):
    """List model versions"""
    try:
        repo = PufRepo()
        
        if model_name:
            versions = repo.get_model_versions(model_name)
            if not versions:
                console.print(f"[yellow]No versions found for model:[/yellow] {model_name}")
                return

            table = Table(title=f"Versions of {model_name}")
            table.add_column("Hash", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Description")
            table.add_column("Created At", style="magenta")

            for version in versions:
                table.add_row(
                    version["hash"][:8],
                    version["metadata"]["version"],
                    version["metadata"].get("description", ""),
                    version["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                )
        else:
            with open(".puf/config.json", 'r') as f:
                config = json.load(f)
            
            models = repo.get_user_models(config["user_id"])
            if not models:
                console.print("[yellow]No models found[/yellow]")
                return

            table = Table(title="Your Models")
            table.add_column("Name", style="cyan")
            table.add_column("Latest Version", style="green")
            table.add_column("Description")
            table.add_column("Last Updated", style="magenta")

            for model in models:
                table.add_row(
                    model["filename"],
                    model["metadata"]["version"],
                    model["metadata"].get("description", ""),
                    model["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    finally:
        repo.close()

@cli.command()
@click.argument('version1')
@click.argument('version2')
@click.option('--metrics', is_flag=True, help='Compare performance metrics')
@click.option('--output', '-o', help='Output format (table/json)')
def compare(version1, version2, metrics, output):
    """Compare two model versions"""
    try:
        repo = PufRepo()
        comparison = repo.compare_versions(version1, version2)
        
        if not comparison:
            console.print("[yellow]No differences found between versions[/yellow]")
            return

        if output == 'json':
            console.print_json(data=comparison)
            return

        # Print comparison table
        table = Table(title=f"Comparison: {version1} vs {version2}")
        table.add_column("Metric", style="cyan")
        table.add_column(version1, style="green")
        table.add_column(version2, style="blue")
        table.add_column("Difference", style="yellow")

        for metric in comparison['metrics']:
            table.add_row(
                metric['name'],
                str(metric['value1']),
                str(metric['value2']),
                f"{metric['difference']:+.2%}"
            )

        console.print(table)

        if metrics and comparison.get('performance'):
            perf_table = Table(title="Performance Metrics")
            perf_table.add_column("Metric", style="cyan")
            perf_table.add_column(version1, style="green")
            perf_table.add_column(version2, style="blue")
            
            for metric, values in comparison['performance'].items():
                perf_table.add_row(
                    metric,
                    f"{values['v1']:.4f}",
                    f"{values['v2']:.4f}"
                )
            
            console.print("\nPerformance Comparison:")
            console.print(perf_table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    finally:
        repo.close()

@cli.command()
@click.argument('version')
@click.option('--format', '-f', default='table', help='Output format (table/json)')
def info(version, format):
    """Show detailed information about a model version"""
    try:
        repo = PufRepo()
        info = repo.get_version_info(version)
        
        if not info:
            console.print(f"[yellow]Version {version} not found[/yellow]")
            return

        if format == 'json':
            console.print_json(data=info)
            return

        # Print info table
        table = Table(title=f"Model Version: {version}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in info.items():
            if isinstance(value, dict):
                value = json.dumps(value, indent=2)
            elif isinstance(value, (list, tuple)):
                value = '\n'.join(map(str, value))
            table.add_row(key, str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    finally:
        repo.close()

@cli.group()
def remote():
    """Manage remote repositories."""
    pass

@remote.command('add')
@click.argument('name')
@click.argument('url')
def add_remote(name, url):
    """Add a new remote repository."""
    try:
        repo = PufRepo()
        repo.add_remote(name, url)
        console.print(f"✓ Added remote '{name}' with URL {url}", style="bold green")
    except Exception as e:
        console.print(f"Error adding remote: {e}", style="bold red")
        sys.exit(1)

@remote.command('list')
def list_remotes():
    """List all configured remotes."""
    try:
        repo = PufRepo()
        remotes = repo.list_remotes()
        if not remotes:
            console.print("No remotes configured.", style="dim")
        else:
            console.print("Configured Remotes:", style="bold")
            for name, url in remotes.items():
                console.print(f"{name}: {url}", style="dim")
    except Exception as e:
        console.print(f"Error listing remotes: {e}", style="bold red")
        sys.exit(1)

@remote.command('remove')
@click.argument('name')
def remove_remote(name):
    """Remove a remote repository."""
    try:
        repo = PufRepo()
        repo.remove_remote(name)
        console.print(f"✓ Removed remote '{name}'", style="bold green")
    except Exception as e:
        console.print(f"Error removing remote: {e}", style="bold red")
        sys.exit(1)

if __name__ == '__main__':
    cli()
