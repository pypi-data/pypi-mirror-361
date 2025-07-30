# 🔄 Compare Mode Guide

GitHub Stats Heatmap features an advanced comparison mode that allows you to compare two users' contribution patterns with detailed analysis and visual diffing.

## 📋 Quick Start

### Basic Comparison
```bash
ghstats user1 --compare user2
```

### Comparison with Different Themes
```bash
ghstats user1 --compare user2 --theme dark --theme2 matrix
```

### Compare with Custom Themes
```bash
ghstats user1 --compare user2 --theme my-theme.json --theme2 their-theme.json
```

## 🎯 Features

### Visual Diff Highlighting
- **Bold blocks**: Higher contributions than the other user
- **Dim blocks**: Both users contributed on the same day
- **Normal blocks**: Standard contribution levels

### Side-by-Side Statistics
- Total contributions comparison
- Active days analysis
- Streak comparisons
- Weekly averages
- Monthly contributions
- Difference calculations

### Overlap Analysis
- Days both users contributed
- Days only one user contributed
- Overlap percentages
- Pattern similarity analysis

### Per-User Themes
- Different themes for each user
- Visual distinction between users
- Custom theme support for both users

## 📊 Understanding the Output

### Grid Layout
```
M                      M
M  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█                    M
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
T  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒                    T
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒
```

- **Left grid**: First user (user1)
- **Right grid**: Second user (user2)
- **Bold blocks**: Higher contributions
- **Dim blocks**: Both contributed

### Statistics Table
```
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric              ┃ User1  ┃ User2    ┃ Difference ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Total Contributions │ 150    │ 89       │ +61        │
│ Active Days         │ 45     │ 32       │ +13        │
│ Current Streak      │ 7      │ 3        │ +4         │
│ Longest Streak      │ 15     │ 12       │ +3         │
│ Avg/Week            │ 2.9    │ 1.7      │ +1.2       │
│ This Month          │ 23     │ 15       │ +8         │
└─────────────────────┴────────┴──────────┴────────────┘
```

### Overlap Analysis
```
🔄 Overlap Analysis
📅 Total days analyzed: 364
🤝 Days both contributed: 12 (3.3% of total)
👤 Days only User1 contributed: 33
👤 Days only User2 contributed: 20
😴 Days neither contributed: 299
🎯 Overlap of active days: 18.5%

💡 Analysis: Somewhat similar contribution patterns
```

## 🎨 Theme Customization

### Using Different Themes
```bash
# Compare with contrasting themes
ghstats user1 --compare user2 --theme github --theme2 matrix

# Compare with custom themes
ghstats user1 --compare user2 --theme dark-blue.json --theme2 neon-green.json

# Use built-in themes
ghstats user1 --compare user2 --theme light --theme2 cyberpunk
```

### Theme Recommendations for Comparison

#### High Contrast Pairs
- `github` + `matrix` - Classic vs Matrix green
- `dark` + `light` - Dark vs light terminals
- `cyberpunk` + `monochrome` - Colorful vs minimal

#### Similar Theme Pairs
- `github` + `dark` - Both green-based
- `light` + `monochrome` - Both light-based
- `matrix` + `cyberpunk` - Both vibrant

## 📈 Use Cases

### Team Collaboration Analysis
```bash
# Compare team members
ghstats alice --compare bob --theme github --theme2 github

# Compare with different themes for clarity
ghstats alice --compare bob --theme dark --theme2 light
```

### Mentor-Student Comparison
```bash
# Compare learning progress
ghstats student --compare mentor --theme matrix --theme2 github
```

### Project Collaboration
```bash
# Compare contributors to a project
ghstats maintainer --compare contributor --theme cyberpunk --theme2 matrix
```

### Personal Progress Tracking
```bash
# Compare current vs previous period
ghstats current --compare previous --theme github --theme2 dark
```

## 🔍 Interpreting Results

### Similar Patterns
- **High overlap percentage**: Users have similar contribution habits
- **Similar streaks**: Both maintain consistent activity
- **Close averages**: Similar weekly contribution rates

### Different Patterns
- **Low overlap**: Users contribute on different days
- **Different streaks**: One user is more consistent
- **Large differences**: Significant activity level differences

### Complementary Patterns
- **Medium overlap**: Some coordination, some independence
- **Different peak days**: Users prefer different weekdays
- **Balanced differences**: Each user has strengths in different areas

## 🛠️ Advanced Usage

### Custom Theme Creation for Comparison
```bash
# Create themes optimized for comparison
ghstats --create-theme user1-theme.json
ghstats --create-theme user2-theme.json

# Edit themes for optimal contrast
# Use in comparison
ghstats user1 --compare user2 --theme user1-theme.json --theme2 user2-theme.json
```

### Batch Comparisons
```bash
# Compare multiple users (run separately)
ghstats user1 --compare user2 --theme github --theme2 matrix
ghstats user1 --compare user3 --theme github --theme2 cyberpunk
ghstats user2 --compare user3 --theme matrix --theme2 cyberpunk
```

### Integration with Other Features
```bash
# Compare with global leaderboard
ghstats user1 --compare user2 --theme github --theme2 matrix --global-leaderboard

# Compare with detailed stats
ghstats user1 --compare user2 --theme dark --theme2 light --stats
```

## 🎯 Best Practices

### Theme Selection
- **Choose contrasting themes** for clear visual distinction
- **Consider terminal background** when selecting themes
- **Test theme combinations** before sharing results

### User Selection
- **Compare similar users** for meaningful insights
- **Consider time periods** when comparing activity
- **Account for different timezones** and work patterns

### Analysis Focus
- **Look at overlap patterns** for collaboration insights
- **Compare streaks** for consistency analysis
- **Examine weekly patterns** for work habit differences

## 🐛 Troubleshooting

### No Differences Shown
- Users might have identical contribution patterns
- Check if both users have recent activity
- Verify usernames are correct

### Theme Not Loading
- Ensure theme files exist and are valid JSON
- Check file permissions for custom themes
- Verify theme names match available themes

### Poor Visual Contrast
- Try different theme combinations
- Consider terminal color support
- Use high-contrast theme pairs

## 📝 Examples

### Developer vs Designer
```bash
ghstats developer --compare designer --theme matrix --theme2 cyberpunk
```

### Open Source vs Corporate
```bash
ghstats opensource_user --compare corporate_user --theme github --theme2 dark
```

### Student vs Professional
```bash
ghstats student --compare professional --theme light --theme2 github
```

---

**Happy comparing!** 🔄 Discover patterns, analyze collaboration, and gain insights into contribution behaviors. 