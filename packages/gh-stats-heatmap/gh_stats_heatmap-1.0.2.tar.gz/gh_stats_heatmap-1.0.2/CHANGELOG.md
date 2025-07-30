# 📝 Changelog

All notable changes to the GitHub Stats Heatmap Viewer project will be documented in this file.

## [1.0.1] - 2025-01-14

### 🎉 Released
- **PyPI Package Fixed**: Successfully published with all plugins and dependencies included
- **Easy Installation**: Multiple installation methods now working (pipx, pip, Homebrew)
- **Complete Package**: All features, plugins, and themes properly included

### 🐛 Fixed
- **Missing Plugins Error**: Added plugins directory to PyPI package
- **Dependency Issues**: Proper inclusion of all required packages (rich, typer, requests)
- **Package Structure**: Complete package with themes, plugins, and all features
- **Installation Methods**: All installation methods now work correctly

### 📚 Documentation
- **Enhanced Installation Guide**: Added pipx as recommended installation method
- **API Token Documentation**: Comprehensive guide for GitHub API tokens
- **Troubleshooting**: Added common installation issues and solutions
- **Badges**: Added PyPI version and license badges to README

### 🚀 Installation Methods
- **pipx** (Recommended): `pipx install gh-stats-heatmap`
- **PyPI**: `pip install gh-stats-heatmap`
- **Homebrew**: `brew tap gizmet/tap && brew install gizmet/tap/ghstats`

## [1.0.0] - 2025-01-14

### 🚀 Released
- **PyPI Package**: Available at https://pypi.org/project/gh-stats-heatmap/
- **Homebrew Tap**: Available via `brew tap gizmet/tap && brew install gizmet/tap/ghstats`
- **GitHub Release**: https://github.com/Gizmet/github-contribution-heatmap-viewer/releases/tag/v1.0.0

### 🚀 Added
- **Live Refresh Mode**: Real-time auto-updating displays with `--live` and `--watch` flags
- **Demo Mode**: Automatic fallback to realistic sample data when rate limited
- **Rate Limit Protection**: Smart detection and handling of GitHub API rate limits
- **Data Caching**: Uses cached data when API calls fail to maintain continuity
- **Status Indicators**: Clear visual feedback showing LIVE/RATE LIMITED/DEMO status
- **Smart Refresh Intervals**: Minimum 30-second intervals to prevent rate limiting
- **Enhanced Error Handling**: Retry logic with exponential backoff and graceful degradation
- **Live Compare Mode**: Side-by-side live comparison of multiple users
- **Rate Limit Information**: Real-time display of remaining API requests and reset times

### 🔧 Improved
- **GitHub API Error Handling**: Better detection of rate limiting and 404 errors
- **Live Refresh Reliability**: More robust implementation with fallback mechanisms
- **User Experience**: Clear status messages and error feedback
- **Documentation**: Comprehensive README updates with live refresh examples

### 🐛 Fixed
- **Rate Limit Detection**: Proper handling of GitHub API 403 rate limit errors
- **Error Recovery**: Automatic retry and fallback when API calls fail
- **Display Continuity**: Maintains display even when API is unavailable

### 📚 Documentation
- **Live Refresh Guide**: Complete documentation of new live refresh features
- **Demo Mode Explanation**: Details about automatic fallback behavior
- **Status Indicators**: Clear explanation of different status types
- **Error Handling**: Documentation of retry logic and fallback mechanisms
- Added Homebrew tap install instructions and tap repo link to README and documentation.

## [Unreleased] - 2025-01-14

### 🚀 Added
- **Live Refresh Mode**: Real-time auto-updating displays with `--live` and `--watch` flags
- **Demo Mode**: Automatic fallback to realistic sample data when rate limited
- **Rate Limit Protection**: Smart detection and handling of GitHub API rate limits
- **Data Caching**: Uses cached data when API calls fail to maintain continuity
- **Status Indicators**: Clear visual feedback showing LIVE/RATE LIMITED/DEMO status
- **Smart Refresh Intervals**: Minimum 30-second intervals to prevent rate limiting
- **Enhanced Error Handling**: Retry logic with exponential backoff and graceful degradation
- **Live Compare Mode**: Side-by-side live comparison of multiple users
- **Rate Limit Information**: Real-time display of remaining API requests and reset times

### 🔧 Improved
- **GitHub API Error Handling**: Better detection of rate limiting and 404 errors
- **Live Refresh Reliability**: More robust implementation with fallback mechanisms
- **User Experience**: Clear status messages and error feedback
- **Documentation**: Comprehensive README updates with live refresh examples

### 🐛 Fixed
- **Rate Limit Detection**: Proper handling of GitHub API 403 rate limit errors
- **Error Recovery**: Automatic retry and fallback when API calls fail
- **Display Continuity**: Maintains display even when API is unavailable

### 📚 Documentation
- **Live Refresh Guide**: Complete documentation of new live refresh features
- **Demo Mode Explanation**: Details about automatic fallback behavior
- **Status Indicators**: Clear explanation of different status types
- **Error Handling**: Documentation of retry logic and fallback mechanisms

## [Previous Versions]

### Core Features
- ✅ Custom Theme Files
- ✅ Compare Mode Polish  
- ✅ Stats & Sparklines Enrichment
- ✅ Interactive TUI Mode
- ✅ Live Refresh Mode

### Bug Fixes
- ✅ GraphQL Authorization Header Inconsistency
- ✅ Potential Division by Zero in Stats Calculation
- ✅ Missing Error Handling in Global Leaderboard Plugin
- ✅ Incorrect Entry Point in setup.py
- ✅ Potential IndexError in Global Leaderboard Rendering

---

## 🎯 Feature Status

| Feature | Status | Version |
|---------|--------|---------|
| Custom Theme Files | ✅ Complete | v1.0 |
| Compare Mode | ✅ Complete | v1.0 |
| Advanced Analytics | ✅ Complete | v1.0 |
| Interactive TUI | ✅ Complete | v1.0 |
| Live Refresh Mode | ✅ Complete | v1.0 |
| One-Click Install | ⏳ Pending | v1.1 |

---

*For detailed bug reports and fixes, see [BUGS.md](BUGS.md)* 