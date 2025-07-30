<p align="center">
  <img src="image.png" alt="GitHub Stats Heatmap Logo" width="220"/>
</p>

<h1 align="center">🕵️‍♂️ GitHub Stats Heatmap</h1>
<p align="center">
  <strong>Your GitHub activity, visualized — hacker style.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#installation">Installation</a> •
  <a href="#live-refresh-mode">Live Refresh</a> •
  <a href="#plugin-system">Plugins</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a> •
  <a href="CHANGELOG.md">Changelog</a>
</p>

---

## 🆕 What's New

### ⚡ Live Refresh Mode (Latest)
Experience real-time GitHub stats with auto-updating displays! Perfect for demos, monitoring, and live presentations.

**New Features:**
- 🔄 **Real-time Updates**: Auto-refresh every 30+ seconds
- 🛡️ **Rate Limit Protection**: Smart handling of GitHub API limits
- 🎭 **Demo Mode**: Seamless fallback to realistic sample data
- 📊 **Status Indicators**: Clear visual feedback (LIVE/RATE LIMITED/DEMO)
- 💾 **Data Caching**: Maintains display even when API is unavailable

```bash
# Try it now!
ghstats yourusername --live
```

See the [Live Refresh Mode](#-live-refresh-mode) section for complete details.

---

## ✨ Features

<div align="center">

| Category | Features |
|----------|----------|
| **🎯 Core** | Zero-config heatmaps • Rich terminal output • Cross-platform |
| **🎨 Themes** | GitHub, dark, light, matrix, cyberpunk, monochrome • Custom JSON themes |
| **📊 Analytics** | Streaks, trends, busiest month, activity patterns • Multiple sparklines • Advanced analytics • Smart insights |
| **🔄 Compare** | Side-by-side user comparison • Per-user themes • Diff highlighting • Overlap analysis |
| **🏆 Leaderboards** | Repository/organization contributors • Global top contributors |
| **🔌 Plugins** | Extensible plugin system • Global leaderboard plugin |
| **🎮 TUI** | Interactive terminal UI • Multiple views • Cell selection • Theme switching |
| **⚡ Live** | Real-time refresh mode • Auto-updating displays • Rate limit protection • Demo mode • Smart caching |

</div>

## 🚀 Quick Start

```bash
# Install from PyPI
pip install gh-stats-heatmap

# Instant visualization
ghstats yourusername

# Compare two developers
ghstats user1 --compare user2

# With global context
ghstats username --global-leaderboard --token YOUR_TOKEN

# Live refresh for demos
ghstats username --live

# Live refresh with custom interval
ghstats username --live --refresh-interval 60
```

## 📦 Installation

### 🌍 PyPI Install (Recommended)
```bash
pip install gh-stats-heatmap
```

### 🍺 Homebrew Install (macOS/Linux)
```bash
# Add the tap
brew tap gizmet/tap

# Install ghstats
brew install gizmet/tap/ghstats
```

You can also view and contribute to the Homebrew formula at: [https://github.com/Gizmet/homebrew-tap](https://github.com/Gizmet/homebrew-tap)

### 🔧 From Source
```bash
git clone https://github.com/Gizmet/github-contribution-heatmap-viewer
cd github-contribution-heatmap-viewer
pip install -e .
```

## 🎯 Usage Examples

<div align="center">

| Command | Result |
|---------|--------|
| `ghstats torvalds` | View Linus's contributions |
| `ghstats gizmet --theme matrix` | Cyberpunk-style heatmap |
| `ghstats user1 --compare user2` | Side-by-side comparison |
| `ghstats user1 --compare user2 --theme dark --theme2 matrix` | Enhanced comparison with different themes |
| `ghstats --plugin global-leaderboard` | Top GitHub contributors |
| `ghstats username --tui` | Interactive TUI mode |
| `ghstats username --live` | Real-time updates |
| `ghstats username --live --refresh-interval 30` | Custom refresh interval |
| `ghstats username --watch` | Watch mode (alias for --live) |

</div>

## 🔌 Plugin System

### Available Plugins
```bash
ghstats --list-plugins
```

### 🌍 Global Leaderboard Plugin
Shows top GitHub contributors worldwide using GraphQL API:

```bash
# Standalone plugin
ghstats --plugin global-leaderboard --token YOUR_TOKEN

# Integrated with heatmap
ghstats username --global-leaderboard --token YOUR_TOKEN
```

**Features:**
- 🔄 **Resilient** - Retry logic, fallback data, network error handling
- 📊 **Rich Data** - Contributions, followers, rankings
- 🎨 **Beautiful Output** - Formatted tables with proper alignment
- ⚡ **Fast** - Optimized GraphQL queries with pagination

## 🎮 Interactive TUI Mode

Experience your GitHub stats with an interactive terminal interface:

```bash
# Launch TUI mode
ghstats username --tui

# TUI with custom theme
ghstats username --tui --theme matrix

# TUI with API token
ghstats username --tui --token YOUR_TOKEN
```

**Features:**
- **📊 Multiple Views**: Heatmap, stats, compare, and settings views
- **🎯 Interactive Navigation**: Switch views and explore data
- **🎨 Theme Switching**: Change themes on the fly
- **📈 Detailed Analytics**: Comprehensive statistics tables
- **🔄 Data Refresh**: Reload data without restarting

**Navigation:**
- `h` = Heatmap view
- `s` = Stats view  
- `v` = Compare view
- `o` = Settings view
- `t` = Change theme
- `r` = Refresh data
- `q` = Quit

See [TUI.md](TUI.md) for complete documentation.

## 🎨 Themes

### Built-in Themes
- `github` - GitHub's official colors
- `dark` - Dark terminal aesthetic
- `light` - Light terminal friendly
- `matrix` - Green terminal matrix vibe
- `cyberpunk` - Neon magenta/yellow/cyan
- `monochrome` - Clean black and white

### Custom Themes
Create your own with JSON:

```json
{
  "name": "My Theme",
  "colors": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
}
```

## 📈 Sample Output

```
╭───────────────────────────────── 🕵️‍♂️ GitHub Stats Heatmap ──────────────────────────────╮
│                                                                                           │
│  GitHub Contributions: torvalds (Past 52 Weeks)                                           │
│                                                                                           │
│  M  ▓███▓▓█▓▒▓█▓▓████▒░█▓█▒█▓█▓█▒▓█▒█▓▓░██▓█▒████▓█▓███▓                                  │
│  T  █▓▒▒▒▒░▒██▒▒▒▓▒▒▒██░▓▓▒▒▓▒██▓▒▒▒▒▒▒██▓▓▒▓▓▓░██▒▓▓▒▒░                                  │
│  W  █▓▒▒▓▒▒▒██░▒▒░▓░▓██▒▓▓▒░▒▓██▒▒▒▓██▒██▓▒▒█▒▓▓██▒█▒▓█░                                  │
│  T  ▓░▒▓░▓█▓██▓▒▓▒▒▓▓██▒▒▓░▒▒░██▒▒▒█▓▓▒██▒██▓▓█▒██▒█▓▓▒░                                  │
│  F  █▒▓▓▒▓████▓▓██▓▓▒███▓█▓▒▒███▒██▒███████▓▒▓████▓█▓▓▓░                                  │
│  S  ████▓▓█▓▓█████████████▓███████████▓████████████▓███░                                  │
│  S  █▒▓███▒▒▓██▒█░▒▒▓▒█▓██▒▒▓▒█▓████▒▓▓█▒▓██▒██▓█▓▓█▓▓▓░                                  │
│                                                                                           │
│  Weekly Activity: ▄▂▂▂▂▂▃▁▆▅▃▂▂▂▂▂▂▇▄▂▂▃▁▂▂▂▇▄▂▂▂▂▃▃▂█▅▂▃▃▂▂▃▂▇▄▂▃▂▂▂▁              │
│  Monthly Trend: ▁▁▁▁█▂                                                                     │
│  Consistency: ███████████████████████████████████████████▃▁▁▁▁▁                           │
│  Trend: 📈 Accelerating | Peak: This week (24 contributions) | Consistency: ✅ Good (85%)   │
│                                                                                           │
│  Legend: ░ = 0 ▒ = 1-3 ▓ = 4-6 █ = 7+                                                     │
│                                                                                           │
│  ⚡ Current streak: 1 days | 📊 Total contributions: 2885 | 📅 Active days: 344/364       │
│  (94.5%) | 🏆 Longest streak: 66 days | 📈 This month: 170 | 📉 Inactive weeks: 0 | 📅    │
│  Busiest week: 157 contributions (Week 36) | 🥇 Most active weekday: S | 🌟 Busiest       │
│  month: May | 😴 Least active weekday: T | 📆 Avg/week: 55.5 | 📈 Trend: Up (+241)        │
│                                                                                           │
│  🎯 Consistency: 85/100 | ⚡ Pattern: Weekday focused (Monday peak, Tuesday low)           │
│  🌱 Seasonal: Strong Summer preference | 🚀 Momentum: +25% | 🌅 Weekend work: 15%         │
│  ⏰ Peak hours: Early week focus (Monday peak) | 😴 Burnout risk: Low (healthy pace)      │
│  🎯 Improvement: High potential (few gaps)                                                │
│                                                                                           │
│  💭 You've contributed 2885 times in the last 52 weeks. Your consistency is excellent.    │
│  You're a weekday warrior. You show a strong summer preference. You're gaining momentum.  │
│  You prefer weekday work. You have great potential for growth. You're on a 1-day streak   │
│  with increasing activity.                                                                 │
│                                                                                           │
│  🌍 Global GitHub Contributors                                                            │
│  ┌──────┬───────────────────┬───────────────────┬───────────────┬───────────┐             │
│  │ Rank │ User              │ Name              │ Contributions │ Followers │             │
│  ├──────┼───────────────────┼───────────────────┼───────────────┼───────────┤             │
│  │    1 │ @Charles-Chrismann │ Charles Chrismann │      12,290 │    16,017 │              │
│  │    2 │ @lllyasviel        │ lllyasviel        │       9,121 │    19,979 │              │
│  │    3 │ @phodal            │ Fengda Huang      │       9,052 │    20,351 │              │
│  │    4 │ @skydoves          │ Jaewoong Eum      │       7,045 │    12,058 │              │
│  │    5 │ @jeresig           │ John Resig        │       6,066 │    18,881 │              │
│  └──────┴───────────────────┴───────────────────┴───────────────┴───────────┘             │
│                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

## 🛠️ API Tokens

**When you need tokens:**
- 🔒 Private repository data
- 🏆 Repository/organization leaderboards  
- 🌍 Global leaderboard plugin
- 📊 Integrated global leaderboard feature

**When you DON'T need tokens:**
- ✅ Public profile heatmaps
- ✅ Basic statistics
- ✅ Compare mode (public users)
- ✅ Theme customization

Create tokens at: https://github.com/settings/tokens

## 🔧 Plugin Development

Extend functionality with custom plugins:

```python
from plugins.base import GhStatsPlugin

class MyPlugin(GhStatsPlugin):
    def name(self) -> str:
        return "my-plugin"
    
    def description(self) -> str:
        return "My custom plugin"
    
    def requires_token(self) -> bool:
        return False
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # Your plugin logic here
        return {"success": True, "data": "..."}
```

## 📋 Roadmap

<div align="center">

| Status | Feature | Description |
|--------|---------|-------------|
| ✅ **Complete** | Core heatmap rendering | Beautiful terminal output with Unicode blocks |
| ✅ **Complete** | Theme system | Built-in + custom JSON themes |
| ✅ **Complete** | Statistics engine | Streaks, trends, patterns, analytics |
| ✅ **Complete** | Compare mode | Side-by-side user comparison |
| ✅ **Complete** | Plugin architecture | Extensible plugin system |
| ✅ **Complete** | Global leaderboard | Top GitHub contributors worldwide |
| ✅ **Complete** | Live refresh | Real-time updates |
| 🔄 **In Progress** | Export features | PNG, HTML, JSON export |
| 🔄 **In Progress** | TUI mode | Interactive terminal UI |
| 📋 **Planned** | Team analytics | Organization insights |
| 📋 **Planned** | Historical trends | Year-over-year comparisons |
| 📋 **Planned** | Custom metrics | User-defined contribution types |

</div>

## 🏗️ Project Structure

```
github-contribution-heatmap-viewer/
├── ghstats.py              # CLI entry point
├── github_api.py           # GitHub API integration
├── heatmap.py              # Grid generation logic
├── render.py               # Rich terminal rendering
├── utils.py                # Utility functions
├── plugins/                # Plugin system
│   ├── __init__.py         # Plugin manager
│   ├── base.py             # Base plugin class
│   └── global_leaderboard.py # Global leaderboard plugin
├── tests/                  # Test suite
├── themes/                 # Theme definitions
└── README.md               # This file
```

## 🧪 Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Run with coverage
pytest --cov=.

# Format code
black .

# Lint code
flake8 .
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. **🍴 Fork** the repository
2. **🌱 Create** a feature branch: `git checkout -b feature/amazing-thing`
3. **💥 Commit** your changes: `git commit -m 'Add amazing thing'`
4. **🚀 Push** to the branch: `git push origin feature/amazing-thing`
5. **📬 Open** a Pull Request

**Guidelines:**
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for new features
- Write clear commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Rich** - Beautiful terminal rendering
- **GitHub API** - Data source
- **Unicode** - For the glorious ░▒▓█ blocks
- **committers.top** - Inspiration for global leaderboards

---

<div align="center">

**Made with ❤️ for developers who live in the terminal**

⭐ **Star this repo if you find it useful!** ⭐

</div> 

## ⚡ Live Refresh Mode

Experience real-time GitHub stats with auto-updating displays perfect for demos, monitoring, and live presentations:

```bash
# Basic live refresh (30s minimum interval)
ghstats username --live

# Custom refresh interval
ghstats username --live --refresh-interval 60

# Watch mode (alias for --live)
ghstats username --watch

# Live refresh with compare mode
ghstats username --compare user2 --live

# Live refresh with custom theme
ghstats username --live --theme matrix
```

### 🎯 Live Refresh Features

- **🔄 Auto-Updating**: Real-time data refresh with customizable intervals
- **🛡️ Rate Limit Protection**: Automatic detection and graceful handling of GitHub API rate limits
- **🎭 Demo Mode**: Seamless fallback to realistic sample data when rate limited
- **📊 Status Indicators**: Clear visual feedback (LIVE/RATE LIMITED/DEMO)
- **💾 Data Caching**: Uses cached data when API calls fail
- **⏰ Smart Intervals**: Minimum 30-second intervals to prevent rate limiting
- **🎨 Theme Support**: Full theme compatibility in live mode
- **🔄 Compare Mode**: Side-by-side live comparison of multiple users

### 🎭 Demo Mode

When rate limited, the live refresh automatically switches to demo mode:

- **Realistic Data**: Generates authentic-looking contribution patterns
- **Weekday Patterns**: Higher activity on weekdays, lower on weekends
- **Random Variation**: Natural-looking contribution counts and patterns
- **Seamless Transition**: No interruption to the live display

### 📊 Status Display

Live refresh provides comprehensive status information:

```
Last update: 14:30:25 | Updates: 15 | Status: LIVE | Next refresh in 60s
Rate limit: 4850/5000 requests remaining | Reset at 15:00:00
```

**Status Types:**
- `[green]LIVE[/green]` - Real-time data from GitHub API
- `[yellow]RATE LIMITED[/yellow]` - Using cached data due to rate limits
- `[yellow]DEMO[/yellow]` - Using sample data in demo mode

### 🛡️ Error Handling

- **Retry Logic**: Automatic retry with exponential backoff
- **Graceful Degradation**: Falls back to cached data when API fails
- **Rate Limit Awareness**: Detects and handles GitHub API rate limits
- **User Feedback**: Clear error messages and status updates

📖 **For detailed documentation, see [LIVE_REFRESH.md](LIVE_REFRESH.md)** 