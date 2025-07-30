"""
Tests for the utils module.
"""

import pytest
from datetime import datetime, timedelta
from utils import (
    validate_username, get_weeks_ago_date, format_date_range,
    get_weekday_name, get_weekday_abbrev, is_weekend,
    calculate_streak, get_contribution_level, format_number,
    get_emoji_for_streak, sanitize_username, is_valid_date_string
)


class TestUsernameValidation:
    """Test username validation functions."""
    
    def test_valid_usernames(self):
        """Test valid GitHub usernames."""
        valid_usernames = [
            "gizmet",
            "user123",
            "user-name",
            "a",
            "a" * 39,  # Maximum length
        ]
        
        for username in valid_usernames:
            assert validate_username(username) is True
    
    def test_invalid_usernames(self):
        """Test invalid GitHub usernames."""
        invalid_usernames = [
            "",  # Empty
            "a" * 40,  # Too long
            "-username",  # Starts with hyphen
            "username-",  # Ends with hyphen
            "user--name",  # Consecutive hyphens
            "user name",  # Contains space
            "user@name",  # Contains special character
            "user.name",  # Contains dot
        ]
        
        for username in invalid_usernames:
            assert validate_username(username) is False


class TestDateFunctions:
    """Test date-related utility functions."""
    
    def test_get_weeks_ago_date(self):
        """Test getting date from weeks ago."""
        weeks = 4
        result = get_weeks_ago_date(weeks)
        
        assert isinstance(result, datetime)
        expected = datetime.now() - timedelta(weeks=weeks)
        # Allow for small time differences
        assert abs((result - expected).total_seconds()) < 1
    
    def test_format_date_range(self):
        """Test date range formatting."""
        weeks = 52
        result = format_date_range(weeks)
        
        assert isinstance(result, str)
        assert " - " in result
        assert result.count(" ") >= 3  # Should have month, day, year
    
    def test_weekday_functions(self):
        """Test weekday name and abbreviation functions."""
        # Test Monday (0)
        assert get_weekday_name(0) == "Monday"
        assert get_weekday_abbrev(0) == "M"
        
        # Test Sunday (6)
        assert get_weekday_name(6) == "Sunday"
        assert get_weekday_abbrev(6) == "S"
        
        # Test Wednesday (2)
        assert get_weekday_name(2) == "Wednesday"
        assert get_weekday_abbrev(2) == "W"
    
    def test_is_weekend(self):
        """Test weekend detection."""
        # Weekdays
        assert is_weekend(0) is False  # Monday
        assert is_weekend(1) is False  # Tuesday
        assert is_weekend(2) is False  # Wednesday
        assert is_weekend(3) is False  # Thursday
        assert is_weekend(4) is False  # Friday
        
        # Weekends
        assert is_weekend(5) is True   # Saturday
        assert is_weekend(6) is True   # Sunday


class TestContributionFunctions:
    """Test contribution-related utility functions."""
    
    def test_calculate_streak(self):
        """Test streak calculation."""
        today = datetime.now().date()
        contributions = {
            today.strftime('%Y-%m-%d'): 1,
            (today - timedelta(days=1)).strftime('%Y-%m-%d'): 1,
            (today - timedelta(days=2)).strftime('%Y-%m-%d'): 1,
            (today - timedelta(days=4)).strftime('%Y-%m-%d'): 1,  # Gap
        }
        
        streak = calculate_streak(contributions, days_back=10)
        assert streak == 3  # Should count 3 consecutive days
    
    def test_get_contribution_level(self):
        """Test contribution level descriptions."""
        assert get_contribution_level(0) == "No contributions"
        assert get_contribution_level(1) == "Low activity"
        assert get_contribution_level(3) == "Low activity"
        assert get_contribution_level(6) == "Moderate activity"
        assert get_contribution_level(10) == "High activity"
        assert get_contribution_level(15) == "Very high activity"
    
    def test_format_number(self):
        """Test number formatting."""
        assert format_number(0) == "0"
        assert format_number(999) == "999"
        assert format_number(1000) == "1.0K"
        assert format_number(1500) == "1.5K"
        assert format_number(1000000) == "1.0M"
        assert format_number(1500000) == "1.5M"
    
    def test_get_emoji_for_streak(self):
        """Test streak emoji selection."""
        assert get_emoji_for_streak(0) == "😴"
        assert get_emoji_for_streak(1) == "⚡"
        assert get_emoji_for_streak(7) == "🔥"
        assert get_emoji_for_streak(30) == "🚀"
        assert get_emoji_for_streak(100) == "💎"


class TestUtilityFunctions:
    """Test general utility functions."""
    
    def test_sanitize_username(self):
        """Test username sanitization."""
        assert sanitize_username("  GizMet  ") == "gizmet"
        assert sanitize_username("USER-NAME") == "user-name"
        assert sanitize_username("user123") == "user123"
    
    def test_is_valid_date_string(self):
        """Test date string validation."""
        assert is_valid_date_string("2023-12-25") is True
        assert is_valid_date_string("2023-13-01") is False  # Invalid month
        assert is_valid_date_string("2023-12-32") is False  # Invalid day
        assert is_valid_date_string("2023/12/25") is False  # Wrong format
        assert is_valid_date_string("not-a-date") is False
        assert is_valid_date_string("") is False 