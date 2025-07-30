"""
Rich-based terminal rendering for the heatmap.
"""

from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.columns import Columns
from utils import load_theme_file, find_theme_files

# Theme presets
THEMES = {
    "dark": {
        0: 'bright_black', 1: 'bright_green', 2: 'green', 3: 'bright_red'
    },
    "light": {
        0: 'grey93', 1: 'green3', 2: 'dark_green', 3: 'red3'
    },
    "matrix": {
        0: 'black', 1: 'green3', 2: 'green4', 3: 'bright_green'
    },
    "cyberpunk": {
        0: 'magenta', 1: 'yellow', 2: 'cyan', 3: 'bright_blue'
    },
    "monochrome": {
        0: 'white', 1: 'white', 2: 'white', 3: 'white'
    },
}

class HeatmapRenderer:
    """Renders heatmap data using Rich for beautiful terminal output."""
    
    def __init__(self, console: Console, theme: str = "dark", custom_theme: dict = None):
        self.console = console
        self.weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        self.theme = theme
        # Defaults
        self.blocks = {0: '░', 1: '▒', 2: '▓', 3: '█'}
        self.colors = THEMES.get(theme, THEMES["dark"])
        self.text_color = None
        self.background = None
        
        # Load theme from file if it's not a built-in theme
        if theme not in THEMES and not custom_theme:
            custom_theme = self._load_theme_from_file(theme)
        
        # Override with custom theme if provided
        if custom_theme:
            if "blocks" in custom_theme:
                self.colors = {int(k): v for k, v in custom_theme["blocks"].items()}
            if "legend" in custom_theme:
                self.blocks = {int(k): v for k, v in custom_theme["legend"].items()}
            if "text" in custom_theme:
                self.text_color = custom_theme["text"]
            if "background" in custom_theme:
                self.background = custom_theme["background"]
    
    def _load_theme_from_file(self, theme_name: str) -> Optional[dict]:
        """Load a theme from a JSON file."""
        # First check if it's a direct file path
        if theme_name.endswith('.json'):
            return load_theme_file(theme_name)
        
        # Then check available theme files
        available_themes = find_theme_files()
        theme_path = available_themes.get(theme_name.lower())
        
        if theme_path:
            return load_theme_file(theme_path)
        
        return None
    
    @staticmethod
    def list_available_themes() -> dict:
        """List all available themes (built-in and custom)."""
        themes = {}
        
        # Add built-in themes
        for theme_name in THEMES.keys():
            themes[theme_name] = f"Built-in {theme_name} theme"
        
        # Add custom themes from files
        available_themes = find_theme_files()
        for theme_name, theme_path in available_themes.items():
            try:
                theme_data = load_theme_file(theme_path)
                if theme_data and 'description' in theme_data:
                    themes[theme_name] = theme_data['description']
                else:
                    themes[theme_name] = f"Custom theme from {theme_path}"
            except:
                themes[theme_name] = f"Custom theme from {theme_path}"
        
        return themes
    
    def render(self, username: str, grid: List[List[int]], weeks: int, leaderboard: Optional[list] = None, global_leaderboard: Optional[list] = None) -> Panel:
        """Render the complete heatmap with header and legend."""
        
        # Create the main content
        content = []
        
        # Header
        header = f"GitHub Contributions: {username} (Past {weeks} Weeks)"
        content.append(f"[bold blue]{header}[/bold blue]\n")
        
        # Heatmap grid
        grid_text = self._render_grid(grid)
        content.append(grid_text)
        
        # Sparkline placeholder
        sparkline = self._render_sparkline(grid)
        content.append(sparkline)
        
        # Legend
        legend = self._render_legend(grid)
        content.append(f"\n{legend}")
        
        # Extended stats placeholder
        stats = self._render_stats(grid)
        if stats:
            content.append(f"\n{stats}")
        
        # Leaderboard
        if leaderboard:
            leaderboard_text = self._render_leaderboard(leaderboard)
            content.append(f"\n{leaderboard_text}")
        
        # Global leaderboard
        if global_leaderboard:
            global_leaderboard_text = self._render_global_leaderboard(global_leaderboard)
            content.append(f"\n{global_leaderboard_text}")
        
        # Combine everything
        full_content = "\n".join(content)
        
        return Panel(
            full_content,
            title="[bold cyan]🕵️‍♂️ GitHub Stats Heatmap[/bold cyan]",
            border_style="bright_blue",
            padding=(1, 2)
        )
    
    def _render_grid(self, grid: List[List[int]]) -> str:
        """Render the heatmap grid."""
        lines = []
        
        for day_idx, day_name in enumerate(self.weekdays):
            line_parts = [f"{day_name}  "]
            
            for week_idx in range(len(grid[0])):
                count = grid[day_idx][week_idx]
                block, color = self._get_block_and_color(count)
                line_parts.append(f"[{color}]{block}[/{color}]")
            
            lines.append("".join(line_parts))
        
        return "\n".join(lines)
    
    def _get_block_and_color(self, count: int) -> tuple:
        """Get the appropriate block character and color for a contribution count."""
        if count == 0:
            return self.blocks[0], self.colors[0]
        elif count <= 3:
            return self.blocks[1], self.colors[1]
        elif count <= 6:
            return self.blocks[2], self.colors[2]
        else:
            return self.blocks[3], self.colors[3]
    
    def _render_legend(self, grid: List[List[int]]) -> str:
        """Render the legend showing what each block represents."""
        # Calculate intensity levels
        all_values = [cell for row in grid for cell in row]
        max_val = max(all_values) if all_values else 0
        
        if max_val == 0:
            legend_parts = [
                f"[{self.colors[0]}]{self.blocks[0]}[/{self.colors[0]}] = 0"
            ]
        elif max_val <= 3:
            legend_parts = [
                f"[{self.colors[0]}]{self.blocks[0]}[/{self.colors[0]}] = 0",
                f"[{self.colors[1]}]{self.blocks[1]}[/{self.colors[1]}] = 1-{max_val}"
            ]
        elif max_val <= 6:
            legend_parts = [
                f"[{self.colors[0]}]{self.blocks[0]}[/{self.colors[0]}] = 0",
                f"[{self.colors[1]}]{self.blocks[1]}[/{self.colors[1]}] = 1-3",
                f"[{self.colors[2]}]{self.blocks[2]}[/{self.colors[2]}] = 4-{max_val}"
            ]
        else:
            legend_parts = [
                f"[{self.colors[0]}]{self.blocks[0]}[/{self.colors[0]}] = 0",
                f"[{self.colors[1]}]{self.blocks[1]}[/{self.colors[1]}] = 1-3",
                f"[{self.colors[2]}]{self.blocks[2]}[/{self.colors[2]}] = 4-6",
                f"[{self.colors[3]}]{self.blocks[3]}[/{self.colors[3]}] = 7+"
            ]
        
        return f"Legend: {' '.join(legend_parts)}"
    
    def _render_stats(self, grid: List[List[int]]) -> str:
        """Render enhanced contribution statistics with advanced analytics."""
        from heatmap import HeatmapGenerator
        
        heatmap_gen = HeatmapGenerator()
        stats = heatmap_gen.get_contribution_stats(grid)
        
        if stats['total_contributions'] == 0:
            return ""
        
        stat_lines = []
        
        # Core stats (existing)
        if stats.get('current_streak', 0) > 0:
            streak_emoji = "🔥" if stats['current_streak'] >= 7 else "⚡"
            stat_lines.append(f"{streak_emoji} Current streak: {stats['current_streak']} days")
        
        stat_lines.append(f"📊 Total contributions: {stats.get('total_contributions', 0)}")
        
        days_with_contributions = stats.get('days_with_contributions', 0)
        total_days = stats.get('total_days', 1)
        active_percentage = (days_with_contributions / total_days) * 100 if total_days > 0 else 0
        stat_lines.append(f"📅 Active days: {days_with_contributions}/{total_days} ({active_percentage:.1f}%)")
        
        if stats.get('max_streak', 0) > 0:
            stat_lines.append(f"🏆 Longest streak: {stats['max_streak']} days")
        
        stat_lines.append(f"📈 This month: {stats.get('contrib_this_month', 0)}")
        stat_lines.append(f"📉 Inactive weeks: {stats.get('inactive_weeks', 0)}")
        
        if stats.get('busiest_week', 0) > 0:
            busiest_week_idx = stats.get('busiest_week_idx', 0)
            stat_lines.append(f"📅 Busiest week: {stats['busiest_week']} contributions (Week {busiest_week_idx+1})")
        
        most_active_weekday_idx = stats.get('most_active_weekday_idx', -1)
        if most_active_weekday_idx >= 0:
            day = self.weekdays[most_active_weekday_idx]
            stat_lines.append(f"🥇 Most active weekday: {day}")
        
        if stats.get('busiest_month'):
            stat_lines.append(f"🌟 Busiest month: {stats['busiest_month']}")
        
        least_active_weekday_idx = stats.get('least_active_weekday_idx', -1)
        if least_active_weekday_idx >= 0:
            day = self.weekdays[least_active_weekday_idx]
            stat_lines.append(f"😴 Least active weekday: {day}")
        
        avg_per_week = stats.get('avg_per_week', 0)
        stat_lines.append(f"📆 Avg/week: {avg_per_week:.1f}")
        
        trend = stats.get('trend', 0)
        if trend > 0:
            stat_lines.append(f"📈 Trend: Up (+{trend})")
        elif trend < 0:
            stat_lines.append(f"📉 Trend: Down ({trend})")
        
        # Enhanced analytics (new)
        stat_lines.append("")  # Add spacing
        
        # Consistency score
        consistency_score = stats.get('consistency_score', 0)
        if consistency_score > 80:
            consistency_emoji = "🎯"
        elif consistency_score > 60:
            consistency_emoji = "✅"
        elif consistency_score > 40:
            consistency_emoji = "⚠️"
        else:
            consistency_emoji = "❌"
        stat_lines.append(f"{consistency_emoji} Consistency: {consistency_score:.0f}/100")
        
        # Productivity pattern
        productivity_pattern = stats.get('productivity_pattern', 'No data')
        stat_lines.append(f"⚡ Pattern: {productivity_pattern}")
        
        # Seasonal trend
        seasonal_trend = stats.get('seasonal_trend', 'No data')
        stat_lines.append(f"🌱 Seasonal: {seasonal_trend}")
        
        # Momentum score
        momentum_score = stats.get('momentum_score', 0)
        if momentum_score > 20:
            momentum_emoji = "🚀"
        elif momentum_score > 0:
            momentum_emoji = "📈"
        elif momentum_score > -20:
            momentum_emoji = "➡️"
        else:
            momentum_emoji = "📉"
        stat_lines.append(f"{momentum_emoji} Momentum: {momentum_score:+.0f}%")
        
        # Weekend ratio
        weekend_ratio = stats.get('weekend_ratio', 0)
        if weekend_ratio > 30:
            weekend_emoji = "🌅"
        elif weekend_ratio > 15:
            weekend_emoji = "🌆"
        else:
            weekend_emoji = "🏢"
        stat_lines.append(f"{weekend_emoji} Weekend work: {weekend_ratio:.0f}%")
        
        # Peak hours estimate
        peak_hours = stats.get('peak_hours_estimate', 'No data')
        stat_lines.append(f"⏰ Peak hours: {peak_hours}")
        
        # Burnout risk
        burnout_risk = stats.get('burnout_risk', 'No data')
        if 'High' in burnout_risk:
            burnout_emoji = "🔥"
        elif 'Moderate' in burnout_risk:
            burnout_emoji = "⚠️"
        elif 'Low' in burnout_risk:
            burnout_emoji = "✅"
        else:
            burnout_emoji = "😴"
        stat_lines.append(f"{burnout_emoji} Burnout risk: {burnout_risk}")
        
        # Improvement potential
        improvement_potential = stats.get('improvement_potential', 'No data')
        if 'High potential' in improvement_potential:
            improvement_emoji = "🎯"
        elif 'Moderate potential' in improvement_potential:
            improvement_emoji = "📈"
        elif 'Excellent' in improvement_potential:
            improvement_emoji = "🏆"
        else:
            improvement_emoji = "💡"
        stat_lines.append(f"{improvement_emoji} Improvement: {improvement_potential}")
        
        # Plain-language summary
        summary = self._render_summary(stats)
        if summary:
            stat_lines.append("")
            stat_lines.append(f"💭 {summary}")
        
        return " | ".join(stat_lines)

    def _render_summary(self, stats: dict) -> str:
        """Render enhanced plain-language summary with advanced insights."""
        if stats['total_contributions'] == 0:
            return ""
        
        # Core insights
        streak = stats['current_streak']
        busy_month = stats.get('busiest_month', 'N/A')
        busy_day = self.weekdays[stats['most_active_weekday_idx']] if stats['most_active_weekday_idx'] >= 0 else 'N/A'
        trend = stats['trend']
        trend_str = "increasing" if trend > 0 else ("decreasing" if trend < 0 else "steady")
        
        # Enhanced insights
        consistency_score = stats.get('consistency_score', 0)
        productivity_pattern = stats.get('productivity_pattern', 'No data')
        seasonal_trend = stats.get('seasonal_trend', 'No data')
        momentum_score = stats.get('momentum_score', 0)
        weekend_ratio = stats.get('weekend_ratio', 0)
        burnout_risk = stats.get('burnout_risk', 'No data')
        improvement_potential = stats.get('improvement_potential', 'No data')
        
        # Build summary
        summary_parts = []
        
        # Basic activity summary
        summary_parts.append(
            f"You've contributed {stats['total_contributions']} times in the last {stats['total_days']//7} weeks."
        )
        
        # Consistency insight
        if consistency_score > 80:
            summary_parts.append("Your consistency is excellent")
        elif consistency_score > 60:
            summary_parts.append("You maintain good consistency")
        elif consistency_score > 40:
            summary_parts.append("Your consistency could improve")
        else:
            summary_parts.append("Your activity is quite irregular")
        
        # Productivity pattern
        if "Weekday focused" in productivity_pattern:
            summary_parts.append("You're a weekday warrior")
        elif "Weekend focused" in productivity_pattern:
            summary_parts.append("You prefer weekend coding")
        elif "Balanced" in productivity_pattern:
            summary_parts.append("You maintain a balanced schedule")
        
        # Seasonal insight
        if "preference" in seasonal_trend:
            summary_parts.append(f"You show a {seasonal_trend.lower()}")
        
        # Momentum insight
        if momentum_score > 20:
            summary_parts.append("You're gaining momentum")
        elif momentum_score > 0:
            summary_parts.append("You're maintaining steady progress")
        elif momentum_score > -20:
            summary_parts.append("Your activity is stable")
        else:
            summary_parts.append("Your activity has declined recently")
        
        # Weekend work insight
        if weekend_ratio > 30:
            summary_parts.append("You're quite active on weekends")
        elif weekend_ratio > 15:
            summary_parts.append("You occasionally work on weekends")
        else:
            summary_parts.append("You prefer weekday work")
        
        # Burnout risk insight
        if "High" in burnout_risk:
            summary_parts.append("Consider taking breaks to avoid burnout")
        elif "Moderate" in burnout_risk:
            summary_parts.append("Monitor your activity levels")
        elif "Low" in burnout_risk:
            summary_parts.append("You're maintaining a healthy pace")
        
        # Improvement potential
        if "High potential" in improvement_potential:
            summary_parts.append("You have great potential for growth")
        elif "Excellent" in improvement_potential:
            summary_parts.append("You're already performing excellently")
        
        # Current status
        summary_parts.append(f"You're on a {streak}-day streak with {trend_str} activity.")
        
        return " ".join(summary_parts)
    
    def _render_sparkline(self, grid: List[List[int]]) -> str:
        """Render enhanced sparklines with multiple views and annotations."""
        lines = []
        
        # Calculate weekly sums
        weekly = [sum(week) for week in zip(*grid)]
        
        if not weekly:
            return ""
        
        # Weekly activity sparkline
        weekly_spark = self._create_sparkline(weekly, "Weekly Activity")
        lines.append(weekly_spark)
        
        # Monthly trend sparkline (simplified)
        monthly_trend = self._calculate_monthly_trend(grid)
        if monthly_trend:
            monthly_spark = self._create_sparkline(monthly_trend, "Monthly Trend")
            lines.append(monthly_spark)
        
        # Consistency sparkline (showing variance)
        consistency_spark = self._create_consistency_sparkline(weekly)
        lines.append(consistency_spark)
        
        # Add trend indicators
        trend_indicators = self._render_trend_indicators(weekly)
        if trend_indicators:
            lines.append(trend_indicators)
        
        return "\n".join(lines)
    
    def _create_sparkline(self, data: List[int], label: str) -> str:
        """Create a sparkline with the given data and label."""
        if not data:
            return ""
        
        try:
            from sparklines import sparklines
            spark = ''.join(sparklines(data))
        except ImportError:
            # Enhanced fallback with better Unicode blocks
            levels = '▁▂▃▄▅▆▇█'
            minv, maxv = min(data), max(data)
            rng = max(maxv - minv, 1)
            spark = ''.join(levels[(v - minv) * (len(levels)-1) // rng] for v in data)
        
        # Add color coding based on data characteristics
        avg = sum(data) / len(data)
        max_val = max(data)
        
        if max_val > avg * 2:
            spark = f"[bold green]{spark}[/bold green]"
        elif max_val > avg * 1.5:
            spark = f"[green]{spark}[/green]"
        elif max_val < avg * 0.5:
            spark = f"[red]{spark}[/red]"
        else:
            spark = f"[blue]{spark}[/blue]"
        
        return f"{label}: {spark}"
    
    def _calculate_monthly_trend(self, grid: List[List[int]]) -> List[int]:
        """Calculate monthly trend data for sparkline."""
        from datetime import datetime, timedelta
        
        # Group weeks by month
        monthly_data = {}
        today = datetime.now().date()
        
        for week_idx in range(len(grid[0])):
            for day_idx in range(7):
                date = today - timedelta(days=(len(grid[0]) - week_idx - 1) * 7 + (6 - day_idx))
                month_key = f"{date.year}-{date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += grid[day_idx][week_idx]
        
        # Return monthly totals in chronological order
        sorted_months = sorted(monthly_data.keys())
        return [monthly_data[month] for month in sorted_months[-6:]]  # Last 6 months
    
    def _create_consistency_sparkline(self, weekly: List[int]) -> str:
        """Create a consistency sparkline showing activity variance."""
        if len(weekly) < 2:
            return ""
        
        # Calculate moving average and variance
        window_size = min(4, len(weekly) // 2)
        consistency_data = []
        
        for i in range(len(weekly) - window_size + 1):
            window = weekly[i:i + window_size]
            avg = sum(window) / len(window)
            variance = sum((x - avg) ** 2 for x in window) / len(window)
            # Lower variance = higher consistency
            consistency = max(0, 10 - variance)
            consistency_data.append(int(consistency))
        
        if not consistency_data:
            return ""
        
        try:
            from sparklines import sparklines
            spark = ''.join(sparklines(consistency_data))
        except ImportError:
            levels = '▁▂▃▄▅▆▇█'
            minv, maxv = min(consistency_data), max(consistency_data)
            rng = max(maxv - minv, 1)
            spark = ''.join(levels[(v - minv) * (len(levels)-1) // rng] for v in consistency_data)
        
        # Color based on consistency
        avg_consistency = sum(consistency_data) / len(consistency_data)
        if avg_consistency > 7:
            spark = f"[bold green]{spark}[/bold green]"
        elif avg_consistency > 5:
            spark = f"[green]{spark}[/green]"
        elif avg_consistency > 3:
            spark = f"[yellow]{spark}[/yellow]"
        else:
            spark = f"[red]{spark}[/red]"
        
        return f"Consistency: {spark}"
    
    def _render_trend_indicators(self, weekly: List[int]) -> str:
        """Render trend indicators and insights."""
        if len(weekly) < 4:
            return ""
        
        lines = []
        
        # Recent vs earlier trend
        mid = len(weekly) // 2
        recent_avg = sum(weekly[mid:]) / len(weekly[mid:])
        earlier_avg = sum(weekly[:mid]) / len(weekly[:mid])
        
        if earlier_avg == 0:
            trend_direction = "📈 New activity started"
        elif recent_avg > earlier_avg * 1.2:
            trend_direction = "📈 Accelerating"
        elif recent_avg > earlier_avg * 0.8:
            trend_direction = "➡️ Stable"
        else:
            trend_direction = "📉 Declining"
        
        lines.append(f"Trend: {trend_direction}")
        
        # Peak detection
        max_week = max(weekly)
        max_week_idx = weekly.index(max_week)
        weeks_ago = len(weekly) - max_week_idx - 1
        
        if weeks_ago == 0:
            peak_info = "Peak: This week"
        elif weeks_ago == 1:
            peak_info = "Peak: Last week"
        else:
            peak_info = f"Peak: {weeks_ago} weeks ago"
        
        lines.append(f"Peak: {peak_info} ({max_week} contributions)")
        
        # Consistency insight
        zero_weeks = sum(1 for week in weekly if week == 0)
        total_weeks = len(weekly)
        consistency_pct = ((total_weeks - zero_weeks) / total_weeks) * 100
        
        if consistency_pct > 90:
            consistency_insight = "🎯 Excellent consistency"
        elif consistency_pct > 70:
            consistency_insight = "✅ Good consistency"
        elif consistency_pct > 50:
            consistency_insight = "⚠️ Inconsistent"
        else:
            consistency_insight = "❌ Very inconsistent"
        
        lines.append(f"Consistency: {consistency_insight} ({consistency_pct:.0f}% active weeks)")
        
        return " | ".join(lines)
    
    def _render_leaderboard(self, leaderboard: list) -> str:
        if not leaderboard:
            return ""
        lines = ["Top Repos:"]
        for i, (repo, count) in enumerate(leaderboard[:5], 1):
            lines.append(f"{i}. {repo} – {count} commits")
        return "\n".join(lines)

    def _render_global_leaderboard(self, global_leaderboard: list) -> str:
        """Render the global leaderboard section."""
        if not global_leaderboard:
            return ""
        
        lines = []
        lines.append("\n[bold cyan]🌍 Global GitHub Contributors[/bold cyan]")
        lines.append("┌──────┬───────────────────┬───────────────────┬───────────────┬───────────┐")
        lines.append("│ Rank │ User              │ Name              │ Contributions │ Followers │")
        lines.append("├──────┼───────────────────┼───────────────────┼───────────────┼───────────┤")
        
        for i, user in enumerate(global_leaderboard[:10], 1):
            rank = f"{i:4d}"
            login = user.get('login', 'unknown')
            username = f"@{login:<17}"[:18]  # Truncate to 17 chars + @
            name = user.get('name') or login  # Use login if name is None
            name = f"{name:<17}"[:17]  # Truncate to 17 chars
            contributions = f"{user.get('contributions', 0):>11,}"
            followers = f"{user.get('followers', 0):>9,}"
            lines.append(f"│ {rank} │ {username} │ {name} │ {contributions} │ {followers} │")
        
        lines.append("└──────┴───────────────────┴───────────────────┴───────────────┴───────────┘")
        lines.append(f"[dim]Based on {len(global_leaderboard)} users sampled[/dim]")
        
        return "\n".join(lines)
    
    def render_simple(self, username: str, grid: List[List[int]], weeks: int) -> str:
        """Render a simple version without Rich formatting (for fallback)."""
        lines = []
        
        # Header
        lines.append(f"GitHub Contributions: {username} (Past {weeks} Weeks)")
        lines.append("")
        
        # Grid
        for day_idx, day_name in enumerate(self.weekdays):
            line = f"{day_name}  "
            for week_idx in range(len(grid[0])):
                count = grid[day_idx][week_idx]
                block = self._get_simple_block(count)
                line += block
            lines.append(line)
        
        # Legend
        lines.append("")
        lines.append("Legend: ░=0 ▒=1-3 ▓=4-6 █=7+")
        
        return "\n".join(lines)
    
    def _get_simple_block(self, count: int) -> str:
        """Get simple block character without colors."""
        if count == 0:
            return '░'
        elif count <= 3:
            return '▒'
        elif count <= 6:
            return '▓'
        else:
            return '█' 

def render_compare(renderer1: HeatmapRenderer, user1: str, grid1: List[List[int]], renderer2: HeatmapRenderer, user2: str, grid2: List[List[int]], weeks: int, leaderboard1=None, leaderboard2=None) -> Panel:
    """Render an enhanced comparison between two users with diff highlighting and statistics."""
    
    # Calculate comparison statistics
    from heatmap import HeatmapGenerator
    heatmap_gen = HeatmapGenerator()
    stats1 = heatmap_gen.get_contribution_stats(grid1)
    stats2 = heatmap_gen.get_contribution_stats(grid2)
    
    # Create comparison content
    content = []
    
    # Header
    header = f"GitHub Contributions Comparison: {user1} vs {user2} (Past {weeks} Weeks)"
    content.append(f"[bold blue]{header}[/bold blue]\n")
    
    # Side-by-side heatmaps with diff highlighting
    comparison_grid = _render_comparison_grid(grid1, grid2, renderer1, renderer2)
    content.append(comparison_grid)
    
    # Comparison statistics
    comparison_stats = _render_comparison_stats(user1, stats1, user2, stats2)
    content.append(comparison_stats)
    
    # Overlapping days analysis
    overlap_analysis = _render_overlap_analysis(grid1, grid2, user1, user2)
    content.append(overlap_analysis)
    
    # Combine everything
    full_content = "\n".join(content)
    
    return Panel(
        full_content,
        title="[bold cyan]🔄 GitHub Stats Comparison[/bold cyan]",
        border_style="bright_blue",
        padding=(1, 2)
    )


def _render_comparison_grid(grid1: List[List[int]], grid2: List[List[int]], renderer1: HeatmapRenderer, renderer2: HeatmapRenderer) -> str:
    """Render side-by-side grids with diff highlighting."""
    lines = []
    
    # User labels
    user1_label = f"[bold green]{renderer1.weekdays[0]}[/bold green]  "
    user2_label = f"[bold blue]{renderer2.weekdays[0]}[/bold blue]  "
    
    # Add spacing to align grids
    spacing = " " * 20
    header_line = f"{user1_label}{spacing}{user2_label}"
    lines.append(header_line)
    
    # Render grids side by side
    for day_idx in range(7):
        line_parts = []
        
        # User 1 grid
        line_parts.append(f"{renderer1.weekdays[day_idx]}  ")
        for week_idx in range(len(grid1[0])):
            count1 = grid1[day_idx][week_idx]
            count2 = grid2[day_idx][week_idx]
            
            # Highlight differences
            if count1 != count2:
                if count1 > count2:
                    # User 1 has more contributions
                    block, color = renderer1._get_block_and_color(count1)
                    line_parts.append(f"[{color} bold]{block}[/{color} bold]")
                else:
                    # User 2 has more contributions
                    block, color = renderer2._get_block_and_color(count2)
                    line_parts.append(f"[{color} bold]{block}[/{color} bold]")
            else:
                # Same contribution level
                if count1 > 0:
                    # Both have contributions - highlight overlap
                    block, color = renderer1._get_block_and_color(count1)
                    line_parts.append(f"[{color} dim]{block}[/{color} dim]")
                else:
                    # Both have no contributions
                    block, color = renderer1._get_block_and_color(count1)
                    line_parts.append(f"[{color}]{block}[/{color}]")
        
        # Add spacing
        line_parts.append(spacing)
        
        # User 2 grid
        line_parts.append(f"{renderer2.weekdays[day_idx]}  ")
        for week_idx in range(len(grid2[0])):
            count1 = grid1[day_idx][week_idx]
            count2 = grid2[day_idx][week_idx]
            
            # Highlight differences
            if count1 != count2:
                if count2 > count1:
                    # User 2 has more contributions
                    block, color = renderer2._get_block_and_color(count2)
                    line_parts.append(f"[{color} bold]{block}[/{color} bold]")
                else:
                    # User 1 has more contributions
                    block, color = renderer1._get_block_and_color(count1)
                    line_parts.append(f"[{color} bold]{block}[/{color} bold]")
            else:
                # Same contribution level
                if count2 > 0:
                    # Both have contributions - highlight overlap
                    block, color = renderer2._get_block_and_color(count2)
                    line_parts.append(f"[{color} dim]{block}[/{color} dim]")
                else:
                    # Both have no contributions
                    block, color = renderer2._get_block_and_color(count2)
                    line_parts.append(f"[{color}]{block}[/{color}]")
        
        lines.append("".join(line_parts))
    
    # Add legends
    legend1 = renderer1._render_legend(grid1)
    legend2 = renderer2._render_legend(grid2)
    legend_line = f"{legend1}{spacing}{legend2}"
    lines.append(f"\n{legend_line}")
    
    # Add diff legend
    diff_legend = "[bold]Diff Legend:[/bold] [bold]Bold[/bold] = Higher contributions, [dim]Dim[/dim] = Both contributed"
    lines.append(f"\n{diff_legend}")
    
    return "\n".join(lines)


def _render_comparison_stats(user1: str, stats1: dict, user2: str, stats2: dict) -> str:
    """Render side-by-side comparison statistics."""
    lines = []
    lines.append("\n[bold]📊 Comparison Statistics[/bold]")
    
    # Create comparison table
    from rich.table import Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column(f"{user1}", style="green")
    table.add_column(f"{user2}", style="blue")
    table.add_column("Difference", style="yellow")
    
    # Total contributions
    total1 = stats1.get('total_contributions', 0)
    total2 = stats2.get('total_contributions', 0)
    diff = total1 - total2
    diff_str = f"{diff:+d}" if diff != 0 else "="
    table.add_row("Total Contributions", str(total1), str(total2), diff_str)
    
    # Active days
    active1 = stats1.get('days_with_contributions', 0)
    active2 = stats2.get('days_with_contributions', 0)
    diff = active1 - active2
    diff_str = f"{diff:+d}" if diff != 0 else "="
    table.add_row("Active Days", str(active1), str(active2), diff_str)
    
    # Current streak
    streak1 = stats1.get('current_streak', 0)
    streak2 = stats2.get('current_streak', 0)
    diff = streak1 - streak2
    diff_str = f"{diff:+d}" if diff != 0 else "="
    table.add_row("Current Streak", str(streak1), str(streak2), diff_str)
    
    # Max streak
    max_streak1 = stats1.get('max_streak', 0)
    max_streak2 = stats2.get('max_streak', 0)
    diff = max_streak1 - max_streak2
    diff_str = f"{diff:+d}" if diff != 0 else "="
    table.add_row("Longest Streak", str(max_streak1), str(max_streak2), diff_str)
    
    # Average per week
    avg1 = stats1.get('avg_per_week', 0)
    avg2 = stats2.get('avg_per_week', 0)
    diff = avg1 - avg2
    diff_str = f"{diff:+.1f}" if diff != 0 else "="
    table.add_row("Avg/Week", f"{avg1:.1f}", f"{avg2:.1f}", diff_str)
    
    # This month
    month1 = stats1.get('contrib_this_month', 0)
    month2 = stats2.get('contrib_this_month', 0)
    diff = month1 - month2
    diff_str = f"{diff:+d}" if diff != 0 else "="
    table.add_row("This Month", str(month1), str(month2), diff_str)
    
    # Convert table to string representation
    from rich.console import Console
    console = Console(record=True)
    console.print(table)
    return console.export_text()


def _render_overlap_analysis(grid1: List[List[int]], grid2: List[List[int]], user1: str, user2: str) -> str:
    """Analyze and display overlapping contribution days."""
    lines = []
    lines.append("\n[bold]🔄 Overlap Analysis[/bold]")
    
    # Calculate overlaps
    total_days = len(grid1) * len(grid1[0])
    both_contributed = 0
    only_user1 = 0
    only_user2 = 0
    neither_contributed = 0
    
    for day_idx in range(len(grid1)):
        for week_idx in range(len(grid1[0])):
            count1 = grid1[day_idx][week_idx]
            count2 = grid2[day_idx][week_idx]
            
            if count1 > 0 and count2 > 0:
                both_contributed += 1
            elif count1 > 0:
                only_user1 += 1
            elif count2 > 0:
                only_user2 += 1
            else:
                neither_contributed += 1
    
    # Calculate percentages
    total_active = both_contributed + only_user1 + only_user2
    overlap_percentage = (both_contributed / total_days) * 100 if total_days > 0 else 0
    overlap_of_active = (both_contributed / total_active) * 100 if total_active > 0 else 0
    
    lines.append(f"📅 Total days analyzed: {total_days}")
    lines.append(f"🤝 Days both contributed: {both_contributed} ({overlap_percentage:.1f}% of total)")
    lines.append(f"👤 Days only {user1} contributed: {only_user1}")
    lines.append(f"👤 Days only {user2} contributed: {only_user2}")
    lines.append(f"😴 Days neither contributed: {neither_contributed}")
    
    if total_active > 0:
        lines.append(f"🎯 Overlap of active days: {overlap_of_active:.1f}%")
    
    # Determine relationship
    if overlap_percentage > 50:
        relationship = "Very similar contribution patterns"
    elif overlap_percentage > 25:
        relationship = "Moderately similar contribution patterns"
    elif overlap_percentage > 10:
        relationship = "Somewhat similar contribution patterns"
    else:
        relationship = "Very different contribution patterns"
    
    lines.append(f"\n💡 Analysis: {relationship}")
    
    return "\n".join(lines) 