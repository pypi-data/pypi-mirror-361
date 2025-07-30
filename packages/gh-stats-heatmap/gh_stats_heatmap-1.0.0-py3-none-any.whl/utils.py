"""
Utility functions for the GitHub stats heatmap.
"""

import re
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


def validate_username(username: str) -> bool:
    """
    Validate GitHub username format.
    
    GitHub usernames:
    - Must be 1-39 characters long
    - Can only contain alphanumeric characters and hyphens
    - Cannot start or end with a hyphen
    - Cannot have consecutive hyphens
    """
    if not username or len(username) > 39:
        return False
    
    # GitHub username regex pattern
    pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,37}[a-zA-Z0-9]$'
    return bool(re.match(pattern, username))


def load_theme_file(theme_path: str) -> Optional[Dict[str, Any]]:
    """
    Load a custom theme from a JSON file.
    
    Args:
        theme_path: Path to the theme JSON file
        
    Returns:
        Theme dictionary or None if loading fails
    """
    try:
        theme_file = Path(theme_path)
        if not theme_file.exists():
            return None
        
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
        
        # Validate theme structure
        if not isinstance(theme_data, dict):
            return None
        
        # Ensure required fields exist
        if 'blocks' not in theme_data:
            return None
        
        return theme_data
        
    except (json.JSONDecodeError, IOError, OSError):
        return None


def find_theme_files() -> Dict[str, str]:
    """
    Find all available theme files in the themes directory.
    
    Returns:
        Dictionary mapping theme names to file paths
    """
    themes = {}
    
    # Check themes directory in the project
    project_themes = Path(__file__).parent / "themes"
    if project_themes.exists():
        for theme_file in project_themes.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                if 'name' in theme_data:
                    themes[theme_data['name'].lower()] = str(theme_file)
            except (json.JSONDecodeError, IOError):
                continue
    
    # Check user's home directory for custom themes
    home_themes = Path.home() / ".ghstats" / "themes"
    if home_themes.exists():
        for theme_file in home_themes.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                if 'name' in theme_data:
                    themes[theme_data['name'].lower()] = str(theme_file)
            except (json.JSONDecodeError, IOError):
                continue
    
    return themes


def create_theme_template(output_path: str) -> bool:
    """
    Create a template theme file for users to customize.
    
    Args:
        output_path: Where to save the template
        
    Returns:
        True if successful, False otherwise
    """
    template = {
        "name": "My Custom Theme",
        "author": "Your Name",
        "description": "A beautiful custom theme for GitHub stats",
        "blocks": {
            "0": "#161b22",  # No contributions
            "1": "#0e4429",  # 1-3 contributions
            "2": "#006d32",  # 4-6 contributions
            "3": "#26a641"   # 7+ contributions
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
    
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        return True
    except (IOError, OSError):
        return False


def get_weeks_ago_date(weeks: int) -> datetime:
    """Get the date that was N weeks ago from today."""
    return datetime.now() - timedelta(weeks=weeks)


def format_date_range(weeks: int) -> str:
    """Format a date range string for display."""
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)
    
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"


def get_weekday_name(weekday: int) -> str:
    """Get weekday name from weekday number (0=Monday, 6=Sunday)."""
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return weekdays[weekday]


def get_weekday_abbrev(weekday: int) -> str:
    """Get weekday abbreviation from weekday number (0=Monday, 6=Sunday)."""
    abbrevs = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    return abbrevs[weekday]


def is_weekend(weekday: int) -> bool:
    """Check if a weekday is a weekend (Saturday or Sunday)."""
    return weekday in [5, 6]  # Saturday=5, Sunday=6


def calculate_streak(contributions: dict, days_back: int = 365) -> int:
    """
    Calculate the current contribution streak.
    
    Args:
        contributions: Dict mapping date strings to contribution counts
        days_back: How many days back to check for the streak
        
    Returns:
        Current streak length in days
    """
    current_date = datetime.now().date()
    streak = 0
    
    for i in range(days_back):
        check_date = current_date - timedelta(days=i)
        date_str = check_date.strftime('%Y-%m-%d')
        
        if contributions.get(date_str, 0) > 0:
            streak += 1
        else:
            break
    
    return streak


def get_contribution_level(count: int) -> str:
    """
    Get a human-readable contribution level description.
    
    Args:
        count: Number of contributions
        
    Returns:
        Description string
    """
    if count == 0:
        return "No contributions"
    elif count <= 3:
        return "Low activity"
    elif count <= 6:
        return "Moderate activity"
    elif count <= 10:
        return "High activity"
    else:
        return "Very high activity"


def format_number(num: int) -> str:
    """Format a number with appropriate suffixes (K, M, etc.)."""
    if num < 1000:
        return str(num)
    elif num < 1000000:
        return f"{num/1000:.1f}K"
    else:
        return f"{num/1000000:.1f}M"


def get_emoji_for_streak(streak: int) -> str:
    """Get an appropriate emoji for a streak length."""
    if streak == 0:
        return "😴"
    elif streak < 7:
        return "⚡"
    elif streak < 30:
        return "🔥"
    elif streak < 100:
        return "🚀"
    else:
        return "💎"


def sanitize_username(username: str) -> str:
    """Sanitize username for safe display and API calls."""
    return username.strip().lower()


def is_valid_date_string(date_str: str) -> bool:
    """Check if a string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False 