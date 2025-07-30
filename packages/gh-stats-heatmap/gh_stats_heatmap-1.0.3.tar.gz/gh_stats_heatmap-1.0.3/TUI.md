# 🎮 Interactive TUI Mode Guide

GitHub Stats Heatmap features an interactive Terminal User Interface (TUI) that provides a rich, navigable experience for exploring your GitHub contribution data.

## 🚀 Quick Start

### Launch TUI Mode
```bash
# Basic TUI mode
ghstats username --tui

# TUI with custom theme
ghstats username --tui --theme matrix

# TUI with API token (for private data)
ghstats username --tui --token YOUR_TOKEN
```

### Standalone TUI
```bash
# Run TUI directly
python tui.py username --theme dark --token YOUR_TOKEN
```

## 🎯 Features

### Multiple Views
- **📊 Heatmap View**: Interactive contribution grid with cell selection
- **📈 Stats View**: Detailed analytics and insights
- **🔄 Compare View**: User comparison functionality
- **⚙️ Settings View**: Configuration and preferences

### Interactive Navigation
- **View Switching**: Seamlessly switch between different views
- **Cell Selection**: Click on heatmap cells for detailed information
- **Theme Switching**: Change themes on the fly
- **Data Refresh**: Reload data without restarting

### Rich Visualizations
- **Color-Coded Heatmaps**: Visual contribution intensity
- **Detailed Statistics**: Comprehensive analytics tables
- **Sparklines**: Activity trend visualizations
- **Smart Insights**: Plain-language summaries

## 🎮 Navigation

### View Commands
| Command | Action |
|---------|--------|
| `h` | Switch to Heatmap view |
| `s` | Switch to Stats view |
| `v` | Switch to Compare view |
| `o` | Switch to Settings view |
| `q` | Quit TUI mode |

### Interactive Commands
| Command | Action |
|---------|--------|
| `c` | Set comparison user |
| `t` | Change theme |
| `r` | Refresh data |
| `↑↓←→` | Navigate heatmap cells |

### Available Themes
- `dark` - Dark terminal aesthetic
- `light` - Light terminal friendly
- `github` - GitHub's official colors
- `matrix` - Green terminal matrix vibe
- `cyberpunk` - Neon magenta/yellow/cyan
- `monochrome` - Clean black and white

## 📊 Views Explained

### Heatmap View
The main view showing your contribution grid:

```
📊 Heatmap View - username
============================================================
M  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
T  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒
W  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
T  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
F  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
S  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
S  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Legend: ░ = 0 ▒ = 1-3 ▓ = 4-6 █ = 7+
```

**Features:**
- **Cell Selection**: Click on cells to see detailed information
- **Visual Highlighting**: Selected cells are highlighted
- **Date Information**: Shows exact date and contribution count
- **Sparklines**: Activity trends below the grid

### Stats View
Comprehensive analytics in table format:

```
📈 Stats View - username
============================================================
                                   📊 Detailed Statistics

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric               ┃ Value                                 ┃ Description                ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Total Contributions  │ 150                                   │ All-time contributions     │
│ Active Days          │ 45/364                                │ Days with activity         │
│ Current Streak       │ 7                                     │ Consecutive days           │
│ Longest Streak       │ 15                                    │ Best streak                │
│ This Month           │ 23                                    │ Current month              │
│ Avg/Week             │ 2.9                                   │ Weekly average             │
│ Consistency Score    │ 85/100                                │ Activity regularity        │
│ Productivity Pattern │ Weekday focused (Monday peak,         │ Work schedule preference   │
│                      │ Tuesday low)                          │                            │
│ Seasonal Trend       │ Strong Summer preference              │ Time-of-year patterns      │
│ Momentum Score       │ +25%                                  │ Recent vs earlier activity │
│ Weekend Work         │ 15%                                   │ Weekend contribution ratio │
│ Burnout Risk         │ Low (healthy pace)                    │ Health assessment          │
└──────────────────────┴───────────────────────────────────────┴────────────────────────────┘
```

**Metrics Included:**
- **Core Stats**: Total contributions, active days, streaks
- **Enhanced Analytics**: Consistency scores, productivity patterns
- **Health Metrics**: Burnout risk assessment
- **Trend Analysis**: Momentum and seasonal patterns

### Compare View
User comparison functionality:

```
🔄 Compare View
============================================================
Compare with: username2
Comparison functionality coming soon...
```

**Planned Features:**
- Side-by-side user comparison
- Difference highlighting
- Overlap analysis
- Statistical comparison

### Settings View
Configuration and preferences:

```
⚙️ Settings View
============================================================

Current Configuration:
• Username: username
• Theme: dark
• Weeks to show: 52
• Compare user: None
• Global leaderboard: No

Available Actions:
• Press 't' to change theme
• Press 'w' to change weeks to show
• Press 'c' to set comparison user
• Press 'g' to toggle global leaderboard
• Press 'r' to refresh data

Navigation:
• Press 'h' for heatmap view
• Press 's' for stats view
• Press 'v' for compare view
• Press 'o' for settings
• Press 'q' to quit
```

## 🎯 Use Cases

### Personal Development
- **Daily Check-ins**: Quick view of recent activity
- **Goal Tracking**: Monitor consistency and streaks
- **Pattern Analysis**: Identify optimal work times
- **Health Monitoring**: Track burnout risk

### Team Management
- **Team Overview**: Compare team member activity
- **Project Planning**: Understand contribution patterns
- **Performance Review**: Document consistent activity
- **Work-Life Balance**: Monitor weekend work patterns

### Presentations
- **Live Demos**: Interactive data exploration
- **Client Meetings**: Professional analytics display
- **Team Standups**: Quick activity overview
- **Conference Talks**: Engaging data visualization

## 🛠️ Technical Details

### Requirements
```bash
# Install with TUI support
pip install rich[all]

# Or install separately
pip install rich prompt_toolkit
```

### Architecture
- **Async Support**: Non-blocking user interface
- **Modular Design**: Separate views and components
- **Data Caching**: Efficient data loading and refresh
- **Error Handling**: Graceful error recovery

### Performance
- **Fast Loading**: Optimized data fetching
- **Smooth Navigation**: Responsive interface
- **Memory Efficient**: Minimal resource usage
- **Cross-Platform**: Works on all terminals

## 🎨 Customization

### Theme Switching
```bash
# Start with specific theme
ghstats username --tui --theme matrix

# Change theme during session
# Press 't' and select from available themes
```

### Configuration
- **Weeks to Show**: Adjust time range (default: 52 weeks)
- **Compare User**: Set comparison target
- **Global Leaderboard**: Toggle global context
- **Data Refresh**: Reload data on demand

## 🔧 Troubleshooting

### Common Issues

#### TUI Not Starting
```bash
# Check dependencies
pip install rich[all]

# Verify installation
python -c "import rich; print('Rich installed')"
```

#### Input Not Working
- Ensure terminal supports interactive input
- Check for conflicting terminal settings
- Try different terminal emulator

#### Display Issues
- Verify terminal supports colors
- Check terminal size (minimum 80x24)
- Ensure Unicode support

### Error Messages

#### "TUI mode not available"
```bash
# Install required dependencies
pip install rich[all]
```

#### "User not found"
- Verify username is correct
- Check internet connection
- Ensure user has public profile

#### "Token required"
```bash
# Use with token for private data
ghstats username --tui --token YOUR_TOKEN
```

## 📈 Best Practices

### Navigation
- **Use Shortcuts**: Learn keyboard shortcuts for efficiency
- **Explore Views**: Try all views to understand capabilities
- **Refresh Regularly**: Keep data current with refresh command
- **Save Settings**: Configure preferences for repeated use

### Data Interpretation
- **Focus on Trends**: Look at patterns over absolute numbers
- **Consider Context**: Account for life events and seasons
- **Monitor Health**: Pay attention to burnout risk indicators
- **Set Realistic Goals**: Base targets on historical patterns

### Presentation
- **Choose Appropriate Theme**: Match theme to audience
- **Prepare Data**: Refresh data before presentations
- **Practice Navigation**: Familiarize with interface
- **Have Backup**: Keep static output as backup

## 🚀 Future Enhancements

### Planned Features
- **Real-time Updates**: Live data refresh
- **Advanced Navigation**: Mouse support and keyboard shortcuts
- **Export Options**: Save views as images or reports
- **Custom Dashboards**: User-defined layouts
- **Team Views**: Multi-user comparison
- **Historical Analysis**: Year-over-year comparisons

### Community Contributions
- **Theme Development**: Create custom themes
- **Plugin Integration**: Extend with custom plugins
- **Feature Requests**: Suggest new capabilities
- **Bug Reports**: Help improve stability

---

**Happy exploring!** 🎮 Discover your patterns, analyze your productivity, and track your growth with the interactive TUI experience. 