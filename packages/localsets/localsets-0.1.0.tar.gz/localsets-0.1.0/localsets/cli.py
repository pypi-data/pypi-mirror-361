"""
Command line interface for localsets.
"""

import click
import json
import logging
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from .core import PokemonData
from .formats import (
    RANDBATS_FORMATS, SMOGON_FORMATS, RANDBATS_FORMAT_MAPPINGS, 
    SMOGON_FORMAT_MAPPINGS, resolve_randbats_formats, resolve_smogon_formats,
    get_randbats_format_info, get_smogon_format_info
)

console = Console()


def setup_logging(verbose: bool):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def main(ctx, verbose):
    """Pokemon Data CLI - RandBats and Smogon sets."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


# RandBats commands
@main.group()
@click.pass_context
def randbats(ctx):
    """RandBats random battle data commands."""
    pass


@randbats.command()
@click.option('--format', '-f', 'format_name', help='Specific format to update')
@click.option('--all', 'update_all', is_flag=True, help='Update all formats')
@click.option('--force', is_flag=True, help='Force update even if no changes detected')
@click.pass_context
def update(ctx, format_name, update_all, force):
    """Update RandBats Pokemon random battle data."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing...", total=None)
        
        try:
            data = PokemonData(auto_update=False)
            
            if update_all:
                formats_to_update = RANDBATS_FORMATS
                progress.update(task, description="Updating all RandBats formats...")
            elif format_name:
                formats_to_update = resolve_randbats_formats([format_name])
                progress.update(task, description=f"Updating {format_name}...")
            else:
                formats_to_update = data.get_randbats_formats()
                progress.update(task, description="Updating loaded RandBats formats...")
            
            if not formats_to_update:
                console.print("[yellow]No RandBats formats to update[/yellow]")
                return
            
            if force:
                updated = data.updater.force_update(formats_to_update)
            else:
                updated = data.updater.update_formats(formats_to_update)
            
            if updated:
                console.print(f"[green]✓ Updated {len(updated)} RandBats formats: {', '.join(updated)}[/green]")
            else:
                console.print("[yellow]No RandBats updates needed[/yellow]")
                
        except Exception as e:
            console.print(f"[red]RandBats update failed: {e}[/red]")
            raise click.Abort()


@randbats.command()
@click.argument('pokemon_name')
@click.option('--format', '-f', 'format_name', help='Specific format to search in')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def get_randbats(ctx, pokemon_name, format_name, output_json):
    """Get RandBats Pokemon data."""
    try:
        data = PokemonData()
        pokemon_data = data.get_randbats(pokemon_name, format_name)
        
        if pokemon_data is None:
            console.print(f"[red]Pokemon '{pokemon_name}' not found in RandBats data[/red]")
            raise click.Abort()
        
        if output_json:
            console.print(json.dumps(pokemon_data, indent=2))
        else:
            display_randbats_data(pokemon_data, pokemon_name, format_name)
            
    except Exception as e:
        console.print(f"[red]Failed to get RandBats Pokemon data: {e}[/red]")
        raise click.Abort()


@randbats.command()
@click.option('--format', '-f', 'format_name', help='Specific format to list')
@click.option('--count', is_flag=True, help='Show only count')
@click.pass_context
def list_randbats(ctx, format_name, count):
    """List Pokemon in RandBats format(s)."""
    try:
        data = PokemonData()
        
        if format_name:
            formats_to_list = resolve_randbats_formats([format_name])
        else:
            formats_to_list = data.get_randbats_formats()
        
        if not formats_to_list:
            console.print("[yellow]No RandBats formats available[/yellow]")
            return
        
        if count:
            for fmt in formats_to_list:
                pokemon_list = data.list_randbats_pokemon(fmt)
                console.print(f"{fmt}: {len(pokemon_list)} Pokemon")
        else:
            for fmt in formats_to_list:
                pokemon_list = data.list_randbats_pokemon(fmt)
                display_pokemon_list(pokemon_list, fmt, "RandBats")
                
    except Exception as e:
        console.print(f"[red]Failed to list RandBats Pokemon: {e}[/red]")
        raise click.Abort()


# Smogon commands
@main.group()
@click.pass_context
def smogon(ctx):
    """Smogon competitive sets commands."""
    pass


@smogon.command()
@click.argument('pokemon_name')
@click.argument('format_name')
@click.option('--set', 'set_name', help='Specific set name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def get_smogon(ctx, pokemon_name, format_name, set_name, output_json):
    """Get Smogon sets for a Pokemon."""
    try:
        data = PokemonData()
        
        if set_name:
            # Get specific set
            set_data = data.get_smogon_set(pokemon_name, format_name, set_name)
            if set_data is None:
                console.print(f"[red]Set '{set_name}' not found for '{pokemon_name}' in {format_name}[/red]")
                raise click.Abort()
            
            if output_json:
                console.print(json.dumps(set_data, indent=2))
            else:
                display_smogon_set(set_data, pokemon_name, format_name, set_name)
        else:
            # Get all sets
            sets_data = data.get_smogon_sets(pokemon_name, format_name)
            if sets_data is None:
                console.print(f"[red]Pokemon '{pokemon_name}' not found in {format_name}[/red]")
                raise click.Abort()
            
            if output_json:
                console.print(json.dumps(sets_data, indent=2))
            else:
                display_smogon_sets(sets_data, pokemon_name, format_name)
            
    except Exception as e:
        console.print(f"[red]Failed to get Smogon sets: {e}[/red]")
        raise click.Abort()


@smogon.command()
@click.argument('pokemon_name')
@click.argument('format_name')
@click.pass_context
def sets(ctx, pokemon_name, format_name):
    """List all set names for a Pokemon in a Smogon format."""
    try:
        data = PokemonData()
        set_names = data.list_smogon_sets(pokemon_name, format_name)
        
        if not set_names:
            console.print(f"[yellow]No sets found for '{pokemon_name}' in {format_name}[/yellow]")
            return
        
        console.print(f"[cyan]Sets for {pokemon_name} in {format_name}:[/cyan]")
        for set_name in set_names:
            console.print(f"  • {set_name}")
            
    except Exception as e:
        console.print(f"[red]Failed to list Smogon sets: {e}[/red]")
        raise click.Abort()


@smogon.command()
@click.option('--format', '-f', 'format_name', help='Specific format to list')
@click.option('--count', is_flag=True, help='Show only count')
@click.pass_context
def list(ctx, format_name, count):
    """List Pokemon in Smogon format(s)."""
    try:
        data = PokemonData()
        
        if format_name:
            formats_to_list = resolve_smogon_formats([format_name])
        else:
            formats_to_list = data.get_smogon_formats()
        
        if not formats_to_list:
            console.print("[yellow]No Smogon formats available[/yellow]")
            return
        
        if count:
            for fmt in formats_to_list:
                pokemon_list = data.list_smogon_pokemon(fmt)
                console.print(f"{fmt}: {len(pokemon_list)} Pokemon")
        else:
            for fmt in formats_to_list:
                pokemon_list = data.list_smogon_pokemon(fmt)
                display_pokemon_list(pokemon_list, fmt, "Smogon")
                
    except Exception as e:
        console.print(f"[red]Failed to list Smogon Pokemon: {e}[/red]")
        raise click.Abort()


@smogon.command()
@click.argument('pokemon_name')
@click.pass_context
def search(ctx, pokemon_name):
    """Search for a Pokemon across all Smogon formats."""
    try:
        data = PokemonData()
        results = data.search_smogon(pokemon_name)
        
        if not results:
            console.print(f"[yellow]Pokemon '{pokemon_name}' not found in any Smogon format[/yellow]")
            return
        
        console.print(f"[cyan]Smogon sets for {pokemon_name}:[/cyan]")
        for format_name, sets_data in results.items():
            console.print(f"\n[green]{format_name}:[/green]")
            for set_name in sets_data.keys():
                console.print(f"  • {set_name}")
            
    except Exception as e:
        console.print(f"[red]Failed to search Smogon data: {e}[/red]")
        raise click.Abort()


@smogon.command()
@click.pass_context
def formats_smogon(ctx):
    """Show available Smogon formats."""
    try:
        table = Table(title="Available Smogon Formats")
        table.add_column("Format", style="cyan")
        table.add_column("Generation", style="yellow")
        table.add_column("Type", style="green")
        table.add_column("Description", style="white")
        
        for fmt in SMOGON_FORMATS:
            info = get_smogon_format_info(fmt)
            gen = info.get('generation', 'unknown')
            battle_type = info.get('type', 'unknown')
            
            # Generate description
            if 'doubles' in fmt:
                desc = "Double battle format"
            elif 'vgc' in fmt:
                desc = "Video Game Championships"
            elif 'ou' in fmt and 'doubles' not in fmt:
                desc = "OverUsed tier"
            elif 'uu' in fmt:
                desc = "UnderUsed tier"
            elif 'ru' in fmt:
                desc = "RarelyUsed tier"
            elif 'nu' in fmt:
                desc = "NeverUsed tier"
            elif 'pu' in fmt:
                desc = "PU tier"
            elif 'ubers' in fmt:
                desc = "Ubers tier"
            else:
                desc = "Competitive format"
            
            table.add_row(fmt, gen, battle_type, desc)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Failed to show Smogon formats: {e}[/red]")
        raise click.Abort()


# Unified commands
@main.command()
@click.argument('pokemon_name')
@click.option('--randbats', 'randbats_format', help='RandBats format to search in')
@click.option('--smogon', 'smogon_format', help='Smogon format to search in')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def get(ctx, pokemon_name, randbats_format, smogon_format, output_json):
    """Get Pokemon data from both RandBats and Smogon sources."""
    try:
        data = PokemonData()
        results = {}
        
        # Get RandBats data
        if randbats_format:
            randbats_data = data.get_randbats(pokemon_name, randbats_format)
            if randbats_data:
                results['randbats'] = {randbats_format: randbats_data}
        else:
            # Search all RandBats formats
            randbats_results = {}
            for fmt in data.get_randbats_formats():
                pokemon_data = data.get_randbats(pokemon_name, fmt)
                if pokemon_data:
                    randbats_results[fmt] = pokemon_data
            if randbats_results:
                results['randbats'] = randbats_results
        
        # Get Smogon data
        if smogon_format:
            smogon_data = data.get_smogon_sets(pokemon_name, smogon_format)
            if smogon_data:
                results['smogon'] = {smogon_format: smogon_data}
        else:
            # Search all Smogon formats
            smogon_results = data.search_smogon(pokemon_name)
            if smogon_results:
                results['smogon'] = smogon_results
        
        if not results:
            console.print(f"[red]Pokemon '{pokemon_name}' not found in any format[/red]")
            raise click.Abort()
        
        if output_json:
            console.print(json.dumps(results, indent=2))
        else:
            display_unified_results(results, pokemon_name)
            
    except Exception as e:
        console.print(f"[red]Failed to get Pokemon data: {e}[/red]")
        raise click.Abort()


@main.command()
@click.option('--all', is_flag=True, help='Show all formats from both sources')
@click.pass_context
def formats(ctx, all):
    """Show available formats."""
    try:
        if all:
            # Show both RandBats and Smogon formats
            console.print("[bold cyan]RandBats Formats:[/bold cyan]")
            randbats_table = Table()
            randbats_table.add_column("Format", style="cyan")
            randbats_table.add_column("Generation", style="yellow")
            randbats_table.add_column("Type", style="green")
            
            for fmt in RANDBATS_FORMATS:
                info = get_randbats_format_info(fmt)
                gen = info.get('generation', 'unknown')
                battle_type = info.get('type', 'unknown')
                randbats_table.add_row(fmt, gen, battle_type)
            
            console.print(randbats_table)
            
            console.print("\n[bold cyan]Smogon Formats:[/bold cyan]")
            smogon_table = Table()
            smogon_table.add_column("Format", style="cyan")
            smogon_table.add_column("Generation", style="yellow")
            smogon_table.add_column("Type", style="green")
            
            for fmt in SMOGON_FORMATS:
                info = get_smogon_format_info(fmt)
                gen = info.get('generation', 'unknown')
                battle_type = info.get('type', 'unknown')
                smogon_table.add_row(fmt, gen, battle_type)
            
            console.print(smogon_table)
        else:
            # Show only RandBats formats (backward compatibility)
            table = Table(title="Available RandBats Formats")
            table.add_column("Format", style="cyan")
            table.add_column("Generation", style="yellow")
            table.add_column("Type", style="green")
            table.add_column("Description", style="white")
            
            for fmt in RANDBATS_FORMATS:
                info = get_randbats_format_info(fmt)
                gen = info.get('generation', 'unknown')
                battle_type = info.get('type', 'unknown')
                
                # Generate description
                if 'doubles' in fmt:
                    desc = "Double battle format"
                elif 'letsgo' in fmt:
                    desc = "Let's Go Pikachu/Eevee format"
                elif 'bdsp' in fmt:
                    desc = "Brilliant Diamond/Shining Pearl format"
                elif 'baby' in fmt:
                    desc = "Baby Pokemon format"
                else:
                    desc = "Random battle format"
                
                table.add_row(fmt, gen, battle_type, desc)
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]Failed to show formats: {e}[/red]")
        raise click.Abort()


@main.command()
@click.pass_context
def info(ctx):
    """Show package information."""
    try:
        data = PokemonData()
        cache_info = data.get_cache_info()
        
        # Create info table
        table = Table(title="Pokemon Data Package Info")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Cache Directory", cache_info['cache_dir'])
        table.add_row("RandBats Formats", str(len(cache_info['randbats_formats'])))
        table.add_row("Smogon Formats", str(len(cache_info['smogon_formats'])))
        table.add_row("Total RandBats Pokemon", str(cache_info['total_randbats_pokemon']))
        
        if 'last_update' in cache_info:
            table.add_row("Last RandBats Update", cache_info['last_update'])
        
        console.print(table)
        
        # Show format details
        if cache_info['randbats_format_counts']:
            format_table = Table(title="RandBats Format Details")
            format_table.add_column("Format", style="cyan")
            format_table.add_column("Pokemon Count", style="green")
            
            for fmt, count in cache_info['randbats_format_counts'].items():
                format_table.add_row(fmt, str(count))
            
            console.print(format_table)
            
    except Exception as e:
        console.print(f"[red]Failed to get info: {e}[/red]")
        raise click.Abort()


# Display functions
def display_randbats_data(pokemon_data: dict, pokemon_name: str, format_name: Optional[str]):
    """Display RandBats Pokemon data."""
    console.print(f"\n[bold cyan]{pokemon_name}[/bold cyan]")
    if format_name:
        console.print(f"[dim]Format: {format_name}[/dim]")
    
    # Display basic info
    if 'level' in pokemon_data:
        console.print(f"Level: {pokemon_data['level']}")
    
    if 'abilities' in pokemon_data:
        console.print(f"Abilities: {', '.join(pokemon_data['abilities'])}")
    
    if 'items' in pokemon_data:
        console.print(f"Items: {', '.join(pokemon_data['items'])}")
    
    if 'moves' in pokemon_data:
        console.print(f"Moves: {', '.join(pokemon_data['moves'])}")


def display_smogon_set(set_data: dict, pokemon_name: str, format_name: str, set_name: str):
    """Display a specific Smogon set."""
    console.print(f"\n[bold cyan]{pokemon_name}[/bold cyan] - [bold yellow]{set_name}[/bold yellow]")
    console.print(f"[dim]Format: {format_name}[/dim]")
    
    if 'item' in set_data:
        console.print(f"Item: {set_data['item']}")
    
    if 'ability' in set_data:
        console.print(f"Ability: {set_data['ability']}")
    
    if 'nature' in set_data:
        console.print(f"Nature: {set_data['nature']}")
    
    if 'evs' in set_data:
        evs = set_data['evs']
        ev_str = ', '.join([f"{stat}: {value}" for stat, value in evs.items()])
        console.print(f"EVs: {ev_str}")
    
    if 'moves' in set_data:
        console.print(f"Moves: {', '.join(set_data['moves'])}")


def display_smogon_sets(sets_data: dict, pokemon_name: str, format_name: str):
    """Display all Smogon sets for a Pokemon."""
    console.print(f"\n[bold cyan]{pokemon_name}[/bold cyan]")
    console.print(f"[dim]Format: {format_name}[/dim]")
    
    for set_name, set_data in sets_data.items():
        console.print(f"\n[bold yellow]{set_name}:[/bold yellow]")
        
        if 'item' in set_data:
            console.print(f"  Item: {set_data['item']}")
        
        if 'ability' in set_data:
            console.print(f"  Ability: {set_data['ability']}")
        
        if 'nature' in set_data:
            console.print(f"  Nature: {set_data['nature']}")
        
        if 'evs' in set_data:
            evs = set_data['evs']
            ev_str = ', '.join([f"{stat}: {value}" for stat, value in evs.items()])
            console.print(f"  EVs: {ev_str}")
        
        if 'moves' in set_data:
            console.print(f"  Moves: {', '.join(set_data['moves'])}")


def display_unified_results(results: dict, pokemon_name: str):
    """Display unified results from both RandBats and Smogon."""
    console.print(f"\n[bold cyan]{pokemon_name}[/bold cyan]")
    
    if 'randbats' in results:
        console.print("\n[bold green]RandBats Data:[/bold green]")
        for format_name, data in results['randbats'].items():
            console.print(f"\n[dim]Format: {format_name}[/dim]")
            display_randbats_data(data, pokemon_name, None)
    
    if 'smogon' in results:
        console.print("\n[bold green]Smogon Sets:[/bold green]")
        for format_name, sets_data in results['smogon'].items():
            console.print(f"\n[dim]Format: {format_name}[/dim]")
            display_smogon_sets(sets_data, pokemon_name, format_name)


def display_pokemon_list(pokemon_list: List[str], format_name: str, source: str):
    """Display a list of Pokemon."""
    console.print(f"\n[bold cyan]{source} Pokemon in {format_name}:[/bold cyan]")
    
    # Display in columns
    for i in range(0, len(pokemon_list), 4):
        row = pokemon_list[i:i+4]
        console.print("  " + "  ".join(f"{pokemon:<20}" for pokemon in row))
    
    console.print(f"\n[dim]Total: {len(pokemon_list)} Pokemon[/dim]")


# Backward compatibility - redirect old commands to randbats subcommands
@main.command()
@click.option('--format', '-f', 'format_name', help='Specific format to update')
@click.option('--all', 'update_all', is_flag=True, help='Update all formats')
@click.option('--force', is_flag=True, help='Force update even if no changes detected')
@click.pass_context
def update_legacy(ctx, format_name, update_all, force):
    """Update RandBats Pokemon random battle data (legacy command)."""
    # Call the randbats update function directly
    from .core import PokemonData
    from .formats import RANDBATS_FORMATS, resolve_randbats_formats
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing...", total=None)
        
        try:
            data = PokemonData(auto_update=False)
            
            if update_all:
                formats_to_update = RANDBATS_FORMATS
                progress.update(task, description="Updating all RandBats formats...")
            elif format_name:
                formats_to_update = resolve_randbats_formats([format_name])
                progress.update(task, description=f"Updating {format_name}...")
            else:
                formats_to_update = data.get_randbats_formats()
                progress.update(task, description="Updating loaded RandBats formats...")
            
            if not formats_to_update:
                console.print("[yellow]No RandBats formats to update[/yellow]")
                return
            
            if force:
                updated = data.updater.force_update(formats_to_update)
            else:
                updated = data.updater.update_formats(formats_to_update)
            
            if updated:
                console.print(f"[green]✓ Updated {len(updated)} RandBats formats: {', '.join(updated)}[/green]")
            else:
                console.print("[yellow]No RandBats updates needed[/yellow]")
                
        except Exception as e:
            console.print(f"[red]RandBats update failed: {e}[/red]")
            raise click.Abort()


@main.command()
@click.argument('pokemon_name')
@click.option('--format', '-f', 'format_name', help='Specific format to search in')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def get_legacy(ctx, pokemon_name, format_name, output_json):
    """Get RandBats Pokemon data (legacy command)."""
    try:
        data = PokemonData()
        pokemon_data = data.get_randbats(pokemon_name, format_name)
        
        if pokemon_data is None:
            console.print(f"[red]Pokemon '{pokemon_name}' not found in RandBats data[/red]")
            raise click.Abort()
        
        if output_json:
            console.print(json.dumps(pokemon_data, indent=2))
        else:
            display_randbats_data(pokemon_data, pokemon_name, format_name)
            
    except Exception as e:
        console.print(f"[red]Failed to get RandBats Pokemon data: {e}[/red]")
        raise click.Abort()


@main.command()
@click.option('--format', '-f', 'format_name', help='Specific format to list')
@click.option('--count', is_flag=True, help='Show only count')
@click.pass_context
def list_legacy(ctx, format_name, count):
    """List Pokemon in RandBats format(s) (legacy command)."""
    try:
        data = PokemonData()
        
        if format_name:
            formats_to_list = resolve_randbats_formats([format_name])
        else:
            formats_to_list = data.get_randbats_formats()
        
        if not formats_to_list:
            console.print("[yellow]No RandBats formats available[/yellow]")
            return
        
        if count:
            for fmt in formats_to_list:
                pokemon_list = data.list_randbats_pokemon(fmt)
                console.print(f"{fmt}: {len(pokemon_list)} Pokemon")
        else:
            for fmt in formats_to_list:
                pokemon_list = data.list_randbats_pokemon(fmt)
                display_pokemon_list(pokemon_list, fmt, "RandBats")
                
    except Exception as e:
        console.print(f"[red]Failed to list RandBats Pokemon: {e}[/red]")
        raise click.Abort() 