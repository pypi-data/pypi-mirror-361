# ⚡ Live Refresh Mode Guide

The Live Refresh Mode provides real-time GitHub stats with auto-updating displays, perfect for demos, monitoring, and live presentations.

## 🚀 Quick Start

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

## 🎯 Features

### 🔄 Auto-Updating Display
- Real-time data refresh with customizable intervals
- Minimum 30-second intervals to prevent rate limiting
- Smooth screen updates with clear status information

### 🛡️ Rate Limit Protection
- Automatic detection of GitHub API rate limits
- Graceful fallback to cached data when rate limited
- Clear status indicators showing current mode

### 🎭 Demo Mode
When rate limited, automatically switches to demo mode:
- Generates realistic contribution patterns
- Higher activity on weekdays, lower on weekends
- Natural-looking contribution counts and patterns
- Seamless transition with no interruption

### 📊 Status Indicators
Live refresh provides comprehensive status information:

```
Last update: 14:30:25 | Updates: 15 | Status: LIVE | Next refresh in 60s
Rate limit: 4850/5000 requests remaining | Reset at 15:00:00
```

**Status Types:**
- `[green]LIVE[/green]` - Real-time data from GitHub API
- `[yellow]RATE LIMITED[/yellow]` - Using cached data due to rate limits
- `[yellow]DEMO[/yellow]` - Using sample data in demo mode

## 🎨 Advanced Usage

### Compare Mode with Live Refresh
```bash
# Compare two users with live updates
ghstats user1 --compare user2 --live

# Compare with different themes
ghstats user1 --compare user2 --theme dark --theme2 matrix --live
```

### Custom Refresh Intervals
```bash
# Refresh every 2 minutes
ghstats username --live --refresh-interval 120

# Refresh every 5 minutes
ghstats username --live --refresh-interval 300
```

### Live Refresh with Global Leaderboard
```bash
# Live refresh with global leaderboard (requires token)
ghstats username --live --global-leaderboard --token YOUR_TOKEN
```

## 🛡️ Error Handling

### Rate Limit Detection
The system automatically detects when GitHub API rate limits are exceeded:
- Shows remaining requests and reset time
- Falls back to cached data when available
- Switches to demo mode if no cached data exists

### Retry Logic
- Automatic retry with exponential backoff
- Maximum 3 consecutive errors before switching to demo mode
- Clear error messages and status updates

### Graceful Degradation
- Uses cached data when API calls fail
- Maintains display continuity
- Provides clear feedback about current status

## 🎭 Demo Mode Details

### Realistic Data Generation
Demo mode generates authentic-looking contribution patterns:
- **Weekday Patterns**: 40% chance of contributions on weekdays, 10% on weekends
- **Contribution Counts**: 1-8 contributions on weekdays, 1-3 on weekends
- **Random Variation**: Natural-looking patterns with realistic distribution

### Seamless Transition
- Automatic switching when rate limited
- No interruption to the live display
- Clear indication of demo mode status

## 📊 Monitoring and Status

### Status Information
Live refresh displays comprehensive status information:
- **Update Counter**: Number of successful updates
- **Last Update Time**: Timestamp of most recent update
- **Next Refresh**: Countdown to next update
- **Rate Limit Info**: Remaining requests and reset time

### Error Messages
Clear error messages help users understand what's happening:
- Rate limit exceeded warnings
- Network error notifications
- Retry attempt counters

## 🔧 Troubleshooting

### Common Issues

**"Rate limit exceeded"**
- This is normal behavior when making frequent API calls
- The system will automatically switch to demo mode
- Consider using a GitHub token for higher rate limits

**"User not found"**
- Check the username spelling
- Ensure the user exists on GitHub
- Try with a different username

**"Too many consecutive errors"**
- Check your internet connection
- Verify GitHub API is accessible
- Consider increasing refresh interval

### Best Practices

1. **Use Appropriate Intervals**: 30-60 seconds minimum to avoid rate limiting
2. **Consider Using Tokens**: GitHub tokens provide higher rate limits
3. **Monitor Status**: Pay attention to status indicators for current mode
4. **Plan for Demos**: Demo mode ensures presentations continue smoothly

## 🎯 Use Cases

### Live Presentations
```bash
# Perfect for live demos
ghstats username --live --refresh-interval 60
```

### Monitoring
```bash
# Monitor your own activity
ghstats yourusername --live --refresh-interval 300
```

### Comparisons
```bash
# Live comparison of team members
ghstats user1 --compare user2 --live
```

### Development
```bash
# Quick testing with demo mode
ghstats testuser --live --refresh-interval 10
```

---

*For more information, see the main [README.md](README.md) and [CHANGELOG.md](CHANGELOG.md)* 