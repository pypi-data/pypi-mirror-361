 #!/usr/bin/env python3
"""
Django Revolution CLI

Interactive command-line interface for Django Revolution API client generator.
"""

import sys
import json
import yaml
from typing import List

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from django_revolution import create_generator, quick_generate
from django_revolution.config import get_settings
from django_revolution.utils import Logger


console = Console()


def main():
    """Main CLI entry point."""
    try:
        show_welcome()
        
        # Main menu
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "🚀 Generate API Clients",
                "🔧 Show Configuration", 
                "📊 Show Version Info",
                "❌ Exit"
            ]
        ).ask()
        
        if action == "🚀 Generate API Clients":
            return handle_generate_interactive()
        elif action == "🔧 Show Configuration":
            return handle_config_interactive()
        elif action == "📊 Show Version Info":
            return handle_version()
        elif action == "❌ Exit":
            console.print("👋 Goodbye!")
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        console.print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        console.print(f"❌ Error: {e}")
        return 1


def show_welcome():
    """Show welcome message."""
    welcome_text = """
[bold blue]Django Revolution[/bold blue]
[italic]Zone-based API Client Generator[/italic]

Generate TypeScript and Python clients from your Django REST Framework APIs
organized by zones with automatic OpenAPI schema generation.
    """
    
    console.print(Panel(welcome_text, title="🎯 Welcome", border_style="blue"))


def handle_generate_interactive() -> int:
    """Interactive generation flow."""
    console.print("\n[bold]🚀 API Client Generation[/bold]")
    
    # Get configuration
    config = get_settings()
    
    # Zone selection
    available_zones = list(config.zones.keys())
    selected_zones = questionary.checkbox(
        "Select zones to generate:",
        choices=available_zones,
        default=available_zones
    ).ask()
    
    if not selected_zones:
        console.print("⚠️  No zones selected. Exiting.")
        return 1
    
    # Client type selection
    client_types = questionary.checkbox(
        "Select client types to generate:",
        choices=[
            "TypeScript",
            "Python"
        ],
        default=["TypeScript", "Python"]
    ).ask()
    
    if not client_types:
        console.print("⚠️  No client types selected. Exiting.")
        return 1
    
    # Archive option
    create_archive = questionary.confirm(
        "Create archive of generated clients?",
        default=True
    ).ask()
    
    # Verbose mode
    verbose = questionary.confirm(
        "Enable verbose logging?",
        default=False
    ).ask()
    
    # Confirm generation
    summary_text = f"""
[bold]Generation Summary:[/bold]
• Zones: {', '.join(selected_zones)}
• Clients: {', '.join(client_types)}
• Archive: {'Yes' if create_archive else 'No'}
• Verbose: {'Yes' if verbose else 'No'}
    """
    
    console.print(Panel(summary_text, title="📋 Summary", border_style="green"))
    
    proceed = questionary.confirm(
        "Proceed with generation?",
        default=True
    ).ask()
    
    if not proceed:
        console.print("❌ Generation cancelled.")
        return 0
    
    # Configure logging
    if verbose:
        Logger.set_level('DEBUG')
    
    # Generate with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating API clients...", total=None)
        
        try:
            summary = quick_generate(
                zones=selected_zones,
                typescript="TypeScript" in client_types,
                python="Python" in client_types,
                archive=create_archive
            )
            
            progress.update(task, description="✅ Generation completed!")
            
            # Show results
            show_generation_results(summary)
            
            return 0
            
        except Exception as e:
            progress.update(task, description="❌ Generation failed!")
            console.print(f"Error: {e}")
            return 1


def show_generation_results(summary):
    """Display generation results in a nice table."""
    table = Table(title="📊 Generation Results")
    
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    table.add_row("Zones Processed", str(len(summary.zones)))
    table.add_row("TypeScript Clients", str(summary.typescript_count))
    table.add_row("Python Clients", str(summary.python_count))
    table.add_row("Archives Created", str(summary.archive_count))
    
    if summary.errors:
        table.add_row("Warnings", str(len(summary.errors)))
    
    console.print(table)
    
    if summary.errors:
        console.print("\n[bold yellow]⚠️  Warnings:[/bold yellow]")
        for error in summary.errors:
            console.print(f"  • {error}")


def handle_config_interactive() -> int:
    """Interactive configuration display."""
    console.print("\n[bold]🔧 Configuration[/bold]")
    
    config = get_settings()
    
    # Format selection
    format_choice = questionary.select(
        "Select output format:",
        choices=[
            "Pretty (Rich)",
            "JSON",
            "YAML"
        ]
    ).ask()
    
    if format_choice == "Pretty (Rich)":
        show_config_pretty(config)
    elif format_choice == "JSON":
        console.print(json.dumps(config.model_dump(), indent=2))
    elif format_choice == "YAML":
        console.print(yaml.dump(config.model_dump(), default_flow_style=False))
    
    return 0


def show_config_pretty(config):
    """Display configuration in a pretty format."""
    table = Table(title="🔧 Django Revolution Configuration")
    
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    table.add_row("Base URL", config.base_url)
    table.add_row("Output Directory", str(config.output_dir))
    table.add_row("Monorepo Path", str(config.monorepo_path))
    table.add_row("Zones", ", ".join(config.zones.keys()))
    table.add_row("TypeScript", "✅" if config.generators.typescript.enabled else "❌")
    table.add_row("Python", "✅" if config.generators.python.enabled else "❌")
    table.add_row("Archive", "✅" if config.archive.enabled else "❌")
    
    console.print(table)


def handle_version() -> int:
    """Show version information."""
    from django_revolution import __version__, __author__, __description__
    
    version_text = f"""
[bold blue]Django Revolution[/bold blue]
Version: [green]{__version__}[/green]
Author: [yellow]{__author__}[/yellow]
Description: [italic]{__description__}[/italic]
    """
    
    console.print(Panel(version_text, title="📦 Version Info", border_style="blue"))
    return 0


if __name__ == '__main__':
    sys.exit(main())