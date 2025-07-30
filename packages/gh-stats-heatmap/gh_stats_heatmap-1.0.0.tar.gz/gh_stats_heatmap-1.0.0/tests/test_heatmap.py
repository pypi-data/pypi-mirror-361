"""
Tests for the heatmap module.
"""

import pytest
from datetime import datetime, timedelta
from heatmap import HeatmapGenerator


class TestHeatmapGenerator:
    """Test cases for HeatmapGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = HeatmapGenerator()
    
    def test_generate_empty_contributions(self):
        """Test generating heatmap with no contributions."""
        contributions = {}
        grid = self.generator.generate(contributions, weeks=4)
        
        assert len(grid) == 7  # 7 days
        assert len(grid[0]) == 4  # 4 weeks
        assert all(cell == 0 for row in grid for cell in row)
    
    def test_generate_with_contributions(self):
        """Test generating heatmap with some contributions."""
        today = datetime.now().date()
        contributions = {
            today.strftime('%Y-%m-%d'): 5,
            (today - timedelta(days=1)).strftime('%Y-%m-%d'): 3,
            (today - timedelta(days=7)).strftime('%Y-%m-%d'): 1,
        }
        
        grid = self.generator.generate(contributions, weeks=2)
        
        assert len(grid) == 7
        assert len(grid[0]) == 2
        
        # Check that contributions are placed correctly
        total_contributions = sum(sum(row) for row in grid)
        assert total_contributions == 9  # 5 + 3 + 1
    
    def test_get_intensity_levels_zero_contributions(self):
        """Test intensity levels with no contributions."""
        grid = [[0 for _ in range(4)] for _ in range(7)]
        levels = self.generator.get_intensity_levels(grid)
        
        assert levels == (0, 1, 10, 20)
    
    def test_get_intensity_levels_with_contributions(self):
        """Test intensity levels with various contribution counts."""
        grid = [
            [0, 1, 5, 10],  # Monday
            [2, 3, 7, 15],  # Tuesday
            [0, 0, 0, 0],   # Wednesday
            [0, 0, 0, 0],   # Thursday
            [0, 0, 0, 0],   # Friday
            [0, 0, 0, 0],   # Saturday
            [0, 0, 0, 0],   # Sunday
        ]
        levels = self.generator.get_intensity_levels(grid)
        
        assert levels == (0, 1, 10, 20)
    
    def test_get_contribution_stats(self):
        """Test contribution statistics calculation."""
        grid = [
            [0, 1, 5, 10],  # Monday
            [2, 3, 7, 15],  # Tuesday
            [0, 0, 0, 0],   # Wednesday
            [0, 0, 0, 0],   # Thursday
            [0, 0, 0, 0],   # Friday
            [0, 0, 0, 0],   # Saturday
            [0, 0, 0, 0],   # Sunday
        ]
        stats = self.generator.get_contribution_stats(grid)
        
        assert stats['total_contributions'] == 43  # 0+1+5+10+2+3+7+15
        assert stats['days_with_contributions'] == 6  # 6 days with contributions
        assert stats['total_days'] == 28  # 7 days * 4 weeks
        assert stats['average_per_day'] == 43 / 28
    
    def test_weekdays_list(self):
        """Test that weekdays are correctly ordered."""
        expected = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        assert self.generator.weekdays == expected 