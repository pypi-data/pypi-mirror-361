#!/usr/bin/env python3
"""GitHub contribution heatmap viewer for terminal."""

import argparse
import sys
import time
import signal
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout

from github_api import GitHubAPI
from render import HeatmapRenderer
from heatmap import HeatmapGenerator
from utils import format_number, create_theme_template
from plugins import PluginManager, GlobalLeaderboardPlugin

# Import TUI module
try:
    from tui import run_tui
    TUI_AVAILABLE = True
except ImportError:
    TUI_AVAILABLE = False

console = Console()


def setup_plugins() -> PluginManager:
    """Initialize and register available plugins."""
    manager = PluginManager()
    
    # Register built-in plugins
    try:
        manager.register(GlobalLeaderboardPlugin())
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load global leaderboard plugin: {e}[/yellow]")
    
    return manager


def show_plugin_help(plugin_manager: PluginManager):
    """Show available plugins and their descriptions."""
    plugins = plugin_manager.list_plugins()
    
    if not plugins:
        console.print("[yellow]No plugins available[/yellow]")
        return
    
    table = Table(title="Available Plugins")
    table.add_column("Plugin", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Token Required", style="yellow")
    
    for name, description in plugins.items():
        plugin = plugin_manager.get(name)
        token_required = "Yes" if plugin.requires_token() else "No"
        table.add_row(name, description, token_required)
    
    console.print(table)


def show_theme_help():
    """Show available themes and theme management options."""
    themes = HeatmapRenderer.list_available_themes()
    
    if not themes:
        console.print("[yellow]No themes available[/yellow]")
        return
    
    table = Table(title="🎨 Available Themes")
    table.add_column("Theme", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Type", style="yellow")
    
    for name, description in themes.items():
        theme_type = "Built-in" if name in ["dark", "light", "matrix", "cyberpunk", "monochrome"] else "Custom"
        table.add_row(name, description, theme_type)
    
    console.print(table)
    console.print("\n[bold]Theme Management:[/bold]")
    console.print("  [cyan]--create-theme[/cyan] [path]  Create a template theme file")
    console.print("  [cyan]--list-themes[/cyan]          List all available themes")
    console.print("  [cyan]--theme[/cyan] [name]         Use a specific theme")


def create_theme_file(output_path: str):
    """Create a template theme file."""
    if create_theme_template(output_path):
        console.print(f"[green]✓[/green] Theme template created at: [cyan]{output_path}[/cyan]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Edit the theme file to customize colors and blocks")
        console.print("2. Use [cyan]--theme[/cyan] with the theme name or file path")
        console.print("3. Share your theme with the community!")
    else:
        console.print(f"[red]✗[/red] Failed to create theme template at: [cyan]{output_path}[/cyan]")


def run_live_refresh(username: str, theme: str = "github", token: Optional[str] = None, 
                    compare_user: Optional[str] = None, refresh_interval: int = 60):
    """Run live refresh mode with auto-updating display."""
    api = GitHubAPI(token=token)
    heatmap_gen = HeatmapGenerator()
    renderer = HeatmapRenderer(console, theme=theme)
    
    # Handle compare mode renderer
    compare_renderer = None
    if compare_user:
        compare_renderer = HeatmapRenderer(console, theme=theme)
    
    # Signal handler for graceful exit
    def signal_handler(signum, frame):
        console.print("\n[yellow]Live refresh stopped[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    console.print(f"[bold green]🔄 Live Refresh Mode - {username}[/bold green]")
    console.print(f"[dim]Auto-refreshing every {refresh_interval} seconds. Press Ctrl+C to stop.[/dim]")
    
    last_update = None
    update_count = 0
    
    def generate_display():
        """Generate the current display content."""
        nonlocal last_update, update_count
        
        try:
            # Get current data
            user_data = api.get_user_data(username)
            if not user_data:
                return Panel("[red]User not found[/red]", title="Error")
            
            contributions = api.get_contributions(username)
            grid = heatmap_gen.generate(contributions)
            
            # Handle compare mode
            if compare_user:
                compare_data = api.get_user_data(compare_user)
                if not compare_data:
                    return Panel(f"[red]Compare user '{compare_user}' not found[/red]", title="Error")
                
                compare_contributions = api.get_contributions(compare_user)
                compare_grid = heatmap_gen.generate(compare_contributions)
                
                from render import render_compare
                content = render_compare(renderer, username, grid, compare_renderer, compare_user, compare_grid, 52)
            else:
                # Get global leaderboard if token provided
                global_leaderboard_data = None
                if token:
                    try:
                        plugin_manager = setup_plugins()
                        global_plugin = plugin_manager.get("global-leaderboard")
                        if global_plugin:
                            result = global_plugin.execute(token=token)
                            if "users" in result:
                                global_leaderboard_data = result["users"]
                    except Exception:
                        pass  # Silently fail for global leaderboard
                
                content = renderer.render(username, grid, 52, global_leaderboard=global_leaderboard_data)
            
            # Update counters
            update_count += 1
            last_update = time.strftime("%H:%M:%S")
            
            # Add live refresh info
            refresh_info = f"[dim]Last update: {last_update} | Updates: {update_count} | Next refresh in {refresh_interval}s[/dim]"
            
            # Create a simple text representation for live display
            if hasattr(content, 'renderable'):
                # If it's a Rich renderable, convert to string
                from rich.console import Console
                temp_console = Console(record=True)
                temp_console.print(content)
                content_str = temp_console.export_text()
            else:
                content_str = str(content)
            
            # Combine content with refresh info
            full_content = f"{content_str}\n\n{refresh_info}"
            
            return Panel(
                full_content,
                title=f"[bold cyan]🔄 Live GitHub Stats - {username}[/bold cyan]",
                border_style="bright_blue"
            )
            
        except Exception as e:
            return Panel(f"[red]Error: {e}[/red]", title="Error")
    
    # Run live display
    with Live(generate_display(), refresh_per_second=1, screen=True) as live:
        while True:
            time.sleep(refresh_interval)
            live.update(generate_display())


def run_simple_live_refresh(username: str, theme: str = "github", token: Optional[str] = None, 
                           compare_user: Optional[str] = None, refresh_interval: int = 60, demo_mode: bool = False):
    """Run a simpler live refresh mode that's more reliable."""
    api = GitHubAPI(token=token)
    heatmap_gen = HeatmapGenerator()
    renderer = HeatmapRenderer(console, theme=theme)
    
    console.print(f"[bold green]🔄 Live Refresh Mode - {username}[/bold green]")
    if demo_mode:
        console.print("[yellow]DEMO MODE: Using sample data due to rate limiting[/yellow]")
    console.print(f"[dim]Auto-refreshing every {refresh_interval} seconds. Press Ctrl+C to stop.[/dim]")
    
    update_count = 0
    last_successful_data = None
    last_successful_contributions = None
    consecutive_errors = 0
    max_consecutive_errors = 3
    rate_limited = False
    
    # Demo data generator
    def generate_demo_data():
        import random
        from datetime import date, timedelta
        
        demo_contributions = {}
        current_date = date.today()
        
        # Generate realistic contribution patterns
        for i in range(52 * 7):  # 52 weeks
            check_date = current_date - timedelta(days=i)
            # Higher activity on weekdays, lower on weekends
            weekday = check_date.weekday()
            base_prob = 0.4 if weekday < 5 else 0.1  # 40% on weekdays, 10% on weekends
            
            # Add some randomness and trends
            if random.random() < base_prob:
                # Vary contribution count based on day
                if weekday < 5:  # Weekdays
                    count = random.randint(1, 8)
                else:  # Weekends
                    count = random.randint(1, 3)
                demo_contributions[check_date.strftime('%Y-%m-%d')] = count
        
        return demo_contributions
    
    try:
        while True:
            # Clear screen
            console.clear()
            
            try:
                # Get current data
                if demo_mode:
                    user_data = {"login": username, "name": f"Demo {username}", "public_repos": 42}
                    contributions = generate_demo_data()
                    rate_limited = True
                else:
                    user_data = api.get_user_data(username)
                    if not user_data:
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            console.print(f"[red]User '{username}' not found after {consecutive_errors} attempts[/red]")
                            console.print("[yellow]This might be due to rate limiting. Consider using a GitHub token.[/yellow]")
                            console.print("[cyan]Switching to demo mode with sample data...[/cyan]")
                            demo_mode = True
                            user_data = {"login": username, "name": f"Demo {username}", "public_repos": 42}
                            contributions = generate_demo_data()
                            rate_limited = True
                        else:
                            console.print(f"[yellow]Warning: User data fetch failed (attempt {consecutive_errors}/{max_consecutive_errors})[/yellow]")
                            if last_successful_data:
                                console.print("[dim]Using cached data...[/dim]")
                                user_data = last_successful_data
                                rate_limited = True
                            else:
                                console.print("[red]No cached data available[/red]")
                                time.sleep(refresh_interval)
                                continue
                    else:
                        consecutive_errors = 0
                        last_successful_data = user_data
                        rate_limited = False
                    
                    contributions = api.get_contributions(username)
                    if not contributions:
                        console.print("[yellow]Warning: No contribution data available[/yellow]")
                        if last_successful_contributions:
                            console.print("[dim]Using cached contribution data...[/dim]")
                            contributions = last_successful_contributions
                            rate_limited = True
                        else:
                            contributions = {}
                    else:
                        last_successful_contributions = contributions
                
                grid = heatmap_gen.generate(contributions)
                
                # Handle compare mode
                if compare_user:
                    if demo_mode:
                        compare_data = {"login": compare_user, "name": f"Demo {compare_user}", "public_repos": 38}
                        compare_contributions = generate_demo_data()
                    else:
                        compare_data = api.get_user_data(compare_user)
                        if not compare_data:
                            console.print(f"[red]Compare user '{compare_user}' not found[/red]")
                            break
                        
                        compare_contributions = api.get_contributions(compare_user)
                        if not compare_contributions:
                            console.print(f"[yellow]Warning: No contribution data for compare user '{compare_user}'[/yellow]")
                            compare_contributions = {}
                    
                    compare_grid = heatmap_gen.generate(compare_contributions)
                    
                    from render import render_compare
                    content = render_compare(renderer, username, grid, renderer, compare_user, compare_grid, 52)
                else:
                    # Get global leaderboard if token provided
                    global_leaderboard_data = None
                    if token and not demo_mode:
                        try:
                            plugin_manager = setup_plugins()
                            global_plugin = plugin_manager.get("global-leaderboard")
                            if global_plugin:
                                result = global_plugin.execute(token=token)
                                if "users" in result:
                                    global_leaderboard_data = result["users"]
                        except Exception:
                            pass  # Silently fail for global leaderboard
                    
                    content = renderer.render(username, grid, 52, global_leaderboard=global_leaderboard_data)
                
                # Display content
                console.print(content)
                
                # Update counters
                update_count += 1
                last_update = time.strftime("%H:%M:%S")
                
                # Add live refresh info
                status_indicator = "[yellow]DEMO[/yellow]" if demo_mode else ("[yellow]RATE LIMITED[/yellow]" if rate_limited else "[green]LIVE[/green]")
                console.print(f"\n[dim]Last update: {last_update} | Updates: {update_count} | Status: {status_indicator} | Next refresh in {refresh_interval}s[/dim]")
                
                # Show rate limit info if available and not in demo mode
                if not demo_mode:
                    try:
                        rate_limit = api.get_rate_limit_info()
                        remaining = rate_limit.get("rate", {}).get("remaining", "unknown")
                        limit = rate_limit.get("rate", {}).get("limit", "unknown")
                        reset_time = rate_limit.get("rate", {}).get("reset", 0)
                        if reset_time:
                            from datetime import datetime
                            reset_datetime = datetime.fromtimestamp(reset_time)
                            reset_str = reset_datetime.strftime("%H:%M:%S")
                        else:
                            reset_str = "unknown"
                        console.print(f"[dim]Rate limit: {remaining}/{limit} requests remaining | Reset at {reset_str}[/dim]")
                    except Exception:
                        pass
                
            except Exception as e:
                consecutive_errors += 1
                console.print(f"[red]Error during update: {e}[/red]")
                if consecutive_errors >= max_consecutive_errors:
                    console.print(f"[red]Too many consecutive errors ({consecutive_errors}). Stopping live refresh.[/red]")
                    break
                else:
                    console.print(f"[yellow]Retrying in {refresh_interval} seconds... (attempt {consecutive_errors}/{max_consecutive_errors})[/yellow]")
            
            # Wait for next refresh
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Live refresh stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")


def run_plugin(plugin_name: str, plugin_manager: PluginManager, **kwargs):
    """Execute a specific plugin."""
    plugin = plugin_manager.get(plugin_name)
    if not plugin:
        console.print(f"[red]Plugin '{plugin_name}' not found[/red]")
        return
    
    if plugin.requires_token() and not kwargs.get('token'):
        console.print(f"[red]Plugin '{plugin_name}' requires a GitHub token[/red]")
        console.print("Set GITHUB_TOKEN environment variable or use --token")
        return
    
    result = plugin.execute(**kwargs)
    
    if "error" in result:
        console.print(f"[red]Plugin error: {result['error']}[/red]")
        return
    
    # Handle global leaderboard output
    if plugin_name == "global-leaderboard":
        users = result.get("users", [])
        if not users:
            console.print("[yellow]No users found[/yellow]")
            return
        
        table = Table(title="🌍 Global GitHub Contributors")
        table.add_column("Rank", style="cyan", justify="right")
        table.add_column("User", style="green")
        table.add_column("Name", style="white")
        table.add_column("Contributions", style="yellow", justify="right")
        table.add_column("Followers", style="blue", justify="right")
        
        for i, user in enumerate(users, 1):
            table.add_row(
                str(i),
                f"@{user['login']}",
                user['name'],
                format_number(user['contributions']),
                format_number(user['followers'])
            )
        
        console.print(table)
        console.print(f"[dim]Based on {result.get('total_fetched', 0)} users sampled[/dim]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub contribution heatmap viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ghstats username                    # View user's heatmap
  ghstats username --theme github     # Use GitHub theme
  ghstats username --theme custom.json # Use custom theme file
  ghstats username --compare user2    # Compare two users
  ghstats user1 --compare user2 --theme dark --theme2 matrix  # Compare with different themes
  ghstats username --tui              # Interactive TUI mode
  ghstats username --live             # Live refresh mode (30s minimum)
  ghstats username --watch            # Watch mode (alias for --live)
  ghstats username --live --refresh-interval 60  # Custom refresh interval
  ghstats username --compare user2 --live        # Live comparison
  ghstats --list-themes              # List available themes
  ghstats --create-theme my-theme.json # Create theme template
  ghstats --plugin list              # List available plugins
  ghstats --plugin global-leaderboard # Show top contributors
  ghstats --demo                      # Show demo/sample data (no API requests)
        """
    )
    
    parser.add_argument("username", nargs="?", help="GitHub username")
    parser.add_argument("--compare", help="Compare with another username")
    parser.add_argument("--theme", default="github", help="Color theme (built-in or custom file)")
    parser.add_argument("--theme2", help="Theme for second user in compare mode")
    parser.add_argument("--live", action="store_true", help="Live refresh mode")
    parser.add_argument("--watch", action="store_true", help="Watch mode with auto-refresh (alias for --live)")
    parser.add_argument("--refresh-interval", type=int, default=60, help="Refresh interval in seconds (default: 60)")
    parser.add_argument("--stats", action="store_true", help="Show detailed statistics")
    parser.add_argument("--leaderboard", help="Show repository/organization leaderboard")
    parser.add_argument("--token", help="GitHub API token (for private repos/leaderboards)")
    parser.add_argument("--plugin", help="Run a specific plugin")
    parser.add_argument("--list-plugins", action="store_true", help="List available plugins")
    parser.add_argument("--list-themes", action="store_true", help="List available themes")
    parser.add_argument("--create-theme", metavar="PATH", help="Create a theme template file")
    parser.add_argument("--global-leaderboard", action="store_true", help="Show global leaderboard at bottom")
    parser.add_argument("--tui", action="store_true", help="Run in TUI mode")
    parser.add_argument("--demo", action="store_true", help="Show demo/sample data (no API requests)")
    
    args = parser.parse_args()
    
    # Initialize plugin system
    plugin_manager = setup_plugins()
    
    # Handle theme management commands
    if args.list_themes:
        show_theme_help()
        return
    
    if args.create_theme:
        create_theme_file(args.create_theme)
        return
    
    # Handle plugin commands
    if args.list_plugins:
        show_plugin_help(plugin_manager)
        return
    
    if args.plugin:
        if args.plugin == "list":
            show_plugin_help(plugin_manager)
        else:
            run_plugin(args.plugin, plugin_manager, token=args.token)
        return
    
    # Handle TUI mode
    if args.tui:
        if not TUI_AVAILABLE:
            console.print("[red]TUI mode not available[/red]")
            console.print("Install required dependencies: pip install rich[all]")
            sys.exit(1)
        
        if not args.username:
            console.print("[red]Username required for TUI mode[/red]")
            sys.exit(1)
        
        console.print("[green]Starting TUI mode...[/green]")
        console.print("[dim]Press Ctrl+C to exit[/dim]")
        
        import asyncio
        try:
            asyncio.run(run_tui(args.username, args.theme, args.token))
        except KeyboardInterrupt:
            console.print("\n[yellow]TUI mode exited[/yellow]")
        return
    
    # Handle live refresh mode
    if args.live or args.watch:
        if not args.username:
            console.print("[red]Username required for live refresh mode[/red]")
            sys.exit(1)
        
        # Enforce minimum refresh interval to prevent rate limiting
        min_interval = 30  # 30 seconds minimum
        if args.refresh_interval < min_interval:
            console.print(f"[yellow]Warning: Refresh interval too low ({args.refresh_interval}s). Using minimum of {min_interval}s to prevent rate limiting.[/yellow]")
            args.refresh_interval = min_interval
        
        # Use the more robust simple live refresh implementation
        try:
            run_simple_live_refresh(
                username=args.username,
                theme=args.theme,
                token=args.token,
                compare_user=args.compare,
                refresh_interval=args.refresh_interval
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Live refresh stopped[/yellow]")
        return
    
    # Handle demo mode
    if args.demo:
        import random
        def generate_demo_data():
            # Generate a 7x52 grid with random data
            return [[random.randint(0, 10) for _ in range(52)] for _ in range(7)]
        grid = generate_demo_data()
        if args.compare:
            grid2 = generate_demo_data()
            renderer1 = HeatmapRenderer(console, theme=args.theme)
            renderer2 = HeatmapRenderer(console, theme=args.theme2 or args.theme)
            from render import render_compare
            output = render_compare(renderer1, args.username or 'demo1', grid, renderer2, args.compare, grid2, 52)
            console.print(output)
            return
        else:
            renderer = HeatmapRenderer(console, theme=args.theme)
            output = renderer.render(args.username or 'demo', grid, 52)
            console.print(output)
            return
    
    # Validate username is provided for main functionality
    if not args.username:
        console.print("[red]Username required for heatmap viewing[/red]")
        console.print("Use --help for usage information")
        sys.exit(1)
    
    # Initialize API and generators
    api = GitHubAPI(token=args.token)
    heatmap_gen = HeatmapGenerator()
    
    # Get global leaderboard if requested
    global_leaderboard_data = None
    if args.global_leaderboard:
        if not args.token:
            console.print("[yellow]Warning: Token required for global leaderboard. Skipping...[/yellow]")
        else:
            try:
                global_plugin = plugin_manager.get("global-leaderboard")
                if global_plugin:
                    result = global_plugin.execute(token=args.token)
                    if "users" in result:
                        global_leaderboard_data = result["users"]
                    elif "error" in result:
                        console.print(f"[yellow]Warning: Could not fetch global leaderboard: {result['error']}[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch global leaderboard: {e}[/yellow]")
    
    try:
        # Get user data
        user_data = api.get_user_data(args.username)
        if not user_data:
            console.print(f"[red]User '{args.username}' not found[/red]")
            sys.exit(1)
        
        # Get contributions
        contributions = api.get_contributions(args.username)
        grid = heatmap_gen.generate(contributions)
        
        # Handle compare mode
        if args.compare:
            compare_data = api.get_user_data(args.compare)
            if not compare_data:
                console.print(f"[red]User '{args.compare}' not found[/red]")
                sys.exit(1)
            
            compare_contributions = api.get_contributions(args.compare)
            compare_grid = heatmap_gen.generate(compare_contributions)
            
            # Create renderers for comparison
            renderer1 = HeatmapRenderer(console, theme=args.theme)
            renderer2 = HeatmapRenderer(console, theme=args.theme2 or args.theme)  # Use theme2 if specified, otherwise use theme
            
            from render import render_compare
            output = render_compare(renderer1, args.username, grid, renderer2, args.compare, compare_grid, 52)
            console.print(output)
            return
        
        # Handle leaderboard
        if args.leaderboard:
            if not args.token:
                console.print("[red]Token required for leaderboard feature[/red]")
                sys.exit(1)
            
            leaderboard = api.get_repo_leaderboard(args.leaderboard)
            if leaderboard:
                table = Table(title=f"🏆 {args.leaderboard} Contributors")
                table.add_column("Rank", style="cyan", justify="right")
                table.add_column("User", style="green")
                table.add_column("Contributions", style="yellow", justify="right")
                
                for i, (user, count) in enumerate(leaderboard, 1):
                    table.add_row(str(i), f"@{user}", format_number(count))
                
                console.print(table)
            return
        
        # Render heatmap
        renderer = HeatmapRenderer(console, theme=args.theme)
        output = renderer.render(args.username, grid, 52, global_leaderboard=global_leaderboard_data)
        console.print(output)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 