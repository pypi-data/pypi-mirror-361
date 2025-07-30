# 🎨 Custom Themes Guide

GitHub Stats Heatmap supports custom themes through JSON files, allowing you to create beautiful, personalized visualizations.

## 📋 Quick Start

### List Available Themes
```bash
ghstats --list-themes
```

### Create a Theme Template
```bash
ghstats --create-theme my-theme.json
```

### Use a Custom Theme
```bash
ghstats username --theme my-theme.json
ghstats username --theme github  # Use built-in theme
```

## 🏗️ Theme File Structure

A theme file is a JSON object with the following structure:

```json
{
  "name": "My Custom Theme",
  "author": "Your Name",
  "description": "A beautiful custom theme for GitHub stats",
  "blocks": {
    "0": "#161b22",
    "1": "#0e4429", 
    "2": "#006d32",
    "3": "#26a641"
  },
  "legend": {
    "0": "░",
    "1": "▒",
    "2": "▓", 
    "3": "█"
  },
  "text": "#ffffff",
  "background": "#0d1117"
}
```

### Field Descriptions

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | string | Theme name for display | Yes |
| `author` | string | Theme creator | No |
| `description` | string | Theme description | No |
| `blocks` | object | Color mapping for contribution levels | Yes |
| `legend` | object | Unicode block characters | No |
| `text` | string | Text color (hex) | No |
| `background` | string | Background color (hex) | No |

### Contribution Levels

The `blocks` object maps contribution counts to colors:

- `"0"`: No contributions (empty days)
- `"1"`: 1-3 contributions (low activity)
- `"2"`: 4-6 contributions (moderate activity)  
- `"3"`: 7+ contributions (high activity)

### Unicode Blocks

The `legend` object defines the visual blocks:

- `"0"`: Light block (░)
- `"1"`: Medium-light block (▒)
- `"2"`: Medium block (▓)
- `"3"`: Full block (█)

## 🎯 Built-in Themes

### GitHub
Official GitHub contribution graph colors.
```bash
ghstats username --theme github
```

### Dark
Optimized for dark terminals.
```bash
ghstats username --theme dark
```

### Light  
Optimized for light terminals.
```bash
ghstats username --theme light
```

### Matrix
Matrix-inspired green theme.
```bash
ghstats username --theme matrix
```

### Cyberpunk
Neon magenta, yellow, and blue.
```bash
ghstats username --theme cyberpunk
```

### Monochrome
Simple black and white.
```bash
ghstats username --theme monochrome
```

## 📁 Theme File Locations

The application looks for themes in these locations:

1. **Project themes**: `themes/*.json` (included with the app)
2. **User themes**: `~/.ghstats/themes/*.json` (user custom themes)

### Creating User Themes

1. Create the themes directory:
   ```bash
   mkdir -p ~/.ghstats/themes
   ```

2. Create a theme file:
   ```bash
   ghstats --create-theme ~/.ghstats/themes/my-theme.json
   ```

3. Edit the theme file and use it:
   ```bash
   ghstats username --theme my-theme
   ```

## 🎨 Color Guidelines

### Terminal Compatibility
- Use hex colors (`#RRGGBB`) for best compatibility
- Test themes in both light and dark terminals
- Consider color blindness accessibility

### Recommended Color Schemes

#### Dark Terminal Themes
```json
{
  "blocks": {
    "0": "#21262d",
    "1": "#0e4429", 
    "2": "#006d32",
    "3": "#26a641"
  }
}
```

#### Light Terminal Themes
```json
{
  "blocks": {
    "0": "#ebedf0",
    "1": "#9be9a8",
    "2": "#40c463", 
    "3": "#30a14e"
  }
}
```

#### High Contrast Themes
```json
{
  "blocks": {
    "0": "#000000",
    "1": "#333333",
    "2": "#666666",
    "3": "#ffffff"
  }
}
```

## 🔧 Advanced Customization

### Custom Block Characters
You can use any Unicode characters for blocks:

```json
{
  "legend": {
    "0": "·",
    "1": "○", 
    "2": "●",
    "3": "◆"
  }
}
```

### Gradient Themes
Create smooth color transitions:

```json
{
  "blocks": {
    "0": "#1a1a2e",
    "1": "#16213e",
    "2": "#0f3460", 
    "3": "#533483"
  }
}
```

### Branded Themes
Match your brand colors:

```json
{
  "blocks": {
    "0": "#f8f9fa",
    "1": "#e9ecef",
    "2": "#007bff", 
    "3": "#0056b3"
  }
}
```

## 🚀 Sharing Themes

### Community Themes
Share your themes with the community:

1. Create a theme file
2. Add it to your repository
3. Share the JSON file
4. Others can use it with `--theme path/to/theme.json`

### Theme Collections
Create theme collections by organizing multiple themes:

```
my-themes/
├── dark-variants/
│   ├── dark-blue.json
│   ├── dark-green.json
│   └── dark-purple.json
├── light-variants/
│   ├── light-blue.json
│   ├── light-green.json
│   └── light-purple.json
└── special/
    ├── retro.json
    ├── neon.json
    └── pastel.json
```

## 🐛 Troubleshooting

### Theme Not Loading
- Check file path and permissions
- Verify JSON syntax is valid
- Ensure required fields are present

### Colors Not Displaying
- Verify terminal supports colors
- Check hex color format (`#RRGGBB`)
- Test with built-in themes first

### Block Characters Not Showing
- Ensure terminal supports Unicode
- Try different block characters
- Check font compatibility

## 📝 Examples

### Minimal Theme
```json
{
  "name": "Minimal",
  "blocks": {
    "0": "#f0f0f0",
    "1": "#c0c0c0", 
    "2": "#808080",
    "3": "#404040"
  }
}
```

### Vibrant Theme
```json
{
  "name": "Vibrant",
  "description": "Bright and colorful theme",
  "blocks": {
    "0": "#2d3748",
    "1": "#f56565",
    "2": "#ed8936", 
    "3": "#48bb78"
  },
  "legend": {
    "0": "░",
    "1": "▒",
    "2": "▓",
    "3": "█"
  }
}
```

### Professional Theme
```json
{
  "name": "Professional",
  "author": "Design Team",
  "description": "Clean and professional appearance",
  "blocks": {
    "0": "#f7fafc",
    "1": "#bee3f8",
    "2": "#63b3ed", 
    "3": "#3182ce"
  },
  "text": "#2d3748",
  "background": "#ffffff"
}
```

---

**Happy theming!** 🎨 Create beautiful, personalized GitHub contribution visualizations that match your style and preferences. 