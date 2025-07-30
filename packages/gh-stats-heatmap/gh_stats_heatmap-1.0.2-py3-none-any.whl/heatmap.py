"""
Heatmap data processing and grid generation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict


class HeatmapGenerator:
    """Generates heatmap grid data from contribution counts."""
    
    def __init__(self):
        self.weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']  # Monday to Sunday
    
    def generate(self, contributions: Dict[str, int], weeks: int = 52) -> List[List[int]]:
        """
        Generate a 7xN grid representing contribution data (GitHub style: Sunday-Saturday rows, weeks as columns).
        """
        from datetime import date
        # Find the most recent Sunday before or on today
        end_date = datetime.now().date()
        days_since_sunday = (end_date.weekday() + 1) % 7
        last_sunday = end_date - timedelta(days=days_since_sunday)
        # Calculate the first date to display
        start_date = last_sunday - timedelta(weeks=weeks-1)
        # Initialize grid: 7 rows (days, Sunday=0) x weeks columns
        grid = [[0 for _ in range(weeks)] for _ in range(7)]
        # Fill the grid column by column (week by week)
        for week in range(weeks):
            for day in range(7):
                d = start_date + timedelta(days=week*7 + day)
                date_str = d.strftime('%Y-%m-%d')
                grid[day][week] = contributions.get(date_str, 0)
        return grid
    
    def get_intensity_levels(self, grid: List[List[int]]) -> Tuple[int, int, int, int]:
        """
        Calculate intensity levels for the legend.
        Returns (level1, level2, level3, level4) where:
        - level1: 0 contributions
        - level2: 1-9 contributions  
        - level3: 10-19 contributions
        - level4: 20+ contributions
        """
        all_values = [cell for row in grid for cell in row]
        
        if not all_values:
            return 0, 1, 10, 20
        
        max_val = max(all_values)
        
        if max_val == 0:
            return 0, 1, 10, 20
        elif max_val <= 9:
            return 0, 1, max_val, max_val + 1
        elif max_val <= 19:
            return 0, 1, 10, max_val + 1
        else:
            return 0, 1, 10, 20
    
    def get_contribution_stats(self, grid: List[List[int]]) -> Dict[str, int]:
        """Calculate comprehensive contribution statistics."""
        all_values = [cell for row in grid for cell in row]
        
        total_contributions = sum(all_values)
        days_with_contributions = sum(1 for val in all_values if val > 0)
        total_days = len(all_values)
        
        # Calculate current streak
        current_streak = 0
        max_streak = 0
        temp_streak = 0
        
        # Go through days in reverse order (most recent first)
        for week in reversed(list(zip(*grid))):  # Transpose to get weeks as rows
            for day in reversed(week):
                if day > 0:
                    temp_streak += 1
                    if current_streak == 0:  # First streak we encounter
                        current_streak = temp_streak
                else:
                    max_streak = max(max_streak, temp_streak)
                    temp_streak = 0
        
        max_streak = max(max_streak, temp_streak)
        
        # Additional stats
        from datetime import datetime
        all_dates = []
        today = datetime.now().date()
        for week_idx in range(len(grid[0])):
            for day_idx in range(7):
                date = today - timedelta(days=(len(grid[0]) - week_idx - 1) * 7 + (6 - day_idx))
                all_dates.append((date, grid[day_idx][week_idx]))
        
        # Contributions this month
        this_month = today.month
        contrib_this_month = sum(val for (date, val) in all_dates if date.month == this_month and val > 0)
        
        # Inactive weeks
        week_sums = [sum(grid[day][w] for day in range(7)) for w in range(len(grid[0]))]
        inactive_weeks = sum(1 for s in week_sums if s == 0)
        
        # Busiest week
        busiest_week = max(week_sums) if week_sums else 0
        busiest_week_idx = week_sums.index(busiest_week) if busiest_week else -1
        
        # Most active weekday
        weekday_sums = [sum(row) for row in grid]
        most_active_weekday_idx = weekday_sums.index(max(weekday_sums)) if weekday_sums else -1
        
        # Busiest month
        month_counts = {}
        for date, val in all_dates:
            if val > 0:
                month = date.strftime('%B')
                month_counts[month] = month_counts.get(month, 0) + val
        busiest_month = max(month_counts, key=month_counts.get) if month_counts else None
        
        # Least active weekday
        least_active_weekday_idx = weekday_sums.index(min(weekday_sums)) if weekday_sums else -1
        
        # Average per week
        avg_per_week = sum(week_sums) / len(week_sums) if week_sums and len(week_sums) > 0 else 0
        
        # Trend (compare first half vs second half)
        if len(week_sums) >= 2:
            mid = len(week_sums) // 2
            trend = sum(week_sums[mid:]) - sum(week_sums[:mid])
        else:
            trend = 0
        
        # Enhanced analytics
        consistency_score = self._calculate_consistency_score(week_sums)
        productivity_pattern = self._analyze_productivity_pattern(weekday_sums)
        seasonal_trend = self._analyze_seasonal_trend(month_counts)
        momentum_score = self._calculate_momentum_score(week_sums)
        weekend_ratio = self._calculate_weekend_ratio(grid)
        peak_hours_estimate = self._estimate_peak_hours(grid)
        burnout_risk = self._assess_burnout_risk(week_sums, current_streak)
        improvement_potential = self._calculate_improvement_potential(week_sums, total_contributions)
        
        return {
            'total_contributions': total_contributions,
            'days_with_contributions': days_with_contributions,
            'total_days': total_days,
            'current_streak': current_streak,
            'max_streak': max_streak,
            'average_per_day': total_contributions / total_days if total_days > 0 else 0,
            'contrib_this_month': contrib_this_month,
            'inactive_weeks': inactive_weeks,
            'busiest_week': busiest_week,
            'busiest_week_idx': busiest_week_idx,
            'most_active_weekday_idx': most_active_weekday_idx,
            'busiest_month': busiest_month,
            'least_active_weekday_idx': least_active_weekday_idx,
            'avg_per_week': avg_per_week,
            'trend': trend,
            # Enhanced analytics
            'consistency_score': consistency_score,
            'productivity_pattern': productivity_pattern,
            'seasonal_trend': seasonal_trend,
            'momentum_score': momentum_score,
            'weekend_ratio': weekend_ratio,
            'peak_hours_estimate': peak_hours_estimate,
            'burnout_risk': burnout_risk,
            'improvement_potential': improvement_potential,
        }
    
    def _calculate_consistency_score(self, week_sums: List[int]) -> float:
        """Calculate consistency score (0-100) based on weekly variance."""
        if not week_sums or len(week_sums) < 2:
            return 0.0
        
        mean = sum(week_sums) / len(week_sums)
        if mean == 0:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in week_sums) / len(week_sums)
        std_dev = variance ** 0.5
        
        # Lower standard deviation = higher consistency
        # Normalize to 0-100 scale
        consistency = max(0, 100 - (std_dev / mean * 100))
        return min(100, consistency)
    
    def _analyze_productivity_pattern(self, weekday_sums: List[int]) -> str:
        """Analyze productivity pattern across weekdays."""
        if not weekday_sums:
            return "No data"
        
        max_day = max(weekday_sums)
        min_day = min(weekday_sums)
        
        if max_day == 0:
            return "No activity"
        
        # Find peak and low days
        peak_day_idx = weekday_sums.index(max_day)
        low_day_idx = weekday_sums.index(min_day)
        
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        peak_day = weekdays[peak_day_idx]
        low_day = weekdays[low_day_idx]
        
        # Analyze pattern
        if peak_day_idx < 5 and low_day_idx < 5:  # Both weekdays
            return f"Weekday focused ({peak_day} peak, {low_day} low)"
        elif peak_day_idx >= 5 and low_day_idx >= 5:  # Both weekends
            return f"Weekend focused ({peak_day} peak, {low_day} low)"
        else:  # Mixed
            return f"Balanced ({peak_day} peak, {low_day} low)"
    
    def _analyze_seasonal_trend(self, month_counts: Dict[str, int]) -> str:
        """Analyze seasonal contribution patterns."""
        if not month_counts:
            return "No seasonal data"
        
        # Group by seasons
        seasons = {
            'Winter': ['December', 'January', 'February'],
            'Spring': ['March', 'April', 'May'],
            'Summer': ['June', 'July', 'August'],
            'Fall': ['September', 'October', 'November']
        }
        
        season_totals = {}
        for season, months in seasons.items():
            season_totals[season] = sum(month_counts.get(month, 0) for month in months)
        
        if not season_totals:
            return "No seasonal data"
        
        max_season = max(season_totals, key=season_totals.get)
        max_contrib = season_totals[max_season]
        
        if max_contrib == 0:
            return "No seasonal pattern"
        
        # Calculate seasonality strength
        total = sum(season_totals.values())
        seasonality_strength = (max_contrib / total) if total > 0 else 0
        
        if seasonality_strength > 0.4:
            return f"Strong {max_season} preference"
        elif seasonality_strength > 0.3:
            return f"Moderate {max_season} preference"
        else:
            return "No clear seasonal pattern"
    
    def _calculate_momentum_score(self, week_sums: List[int]) -> float:
        """Calculate momentum score based on recent activity vs earlier activity."""
        if len(week_sums) < 4:
            return 0.0
        
        # Compare last quarter vs first quarter
        quarter_size = len(week_sums) // 4
        if quarter_size == 0:
            return 0.0
        
        recent_avg = sum(week_sums[-quarter_size:]) / quarter_size
        early_avg = sum(week_sums[:quarter_size]) / quarter_size
        
        if early_avg == 0:
            return 100.0 if recent_avg > 0 else 0.0
        
        momentum = ((recent_avg - early_avg) / early_avg) * 100
        return max(-100, min(100, momentum))
    
    def _calculate_weekend_ratio(self, grid: List[List[int]]) -> float:
        """Calculate ratio of weekend vs weekday contributions."""
        weekday_total = sum(grid[i][j] for i in range(5) for j in range(len(grid[0])))
        weekend_total = sum(grid[i][j] for i in range(5, 7) for j in range(len(grid[0])))
        
        total = weekday_total + weekend_total
        if total == 0:
            return 0.0
        
        return (weekend_total / total) * 100
    
    def _estimate_peak_hours(self, grid: List[List[int]]) -> str:
        """Estimate peak working hours based on contribution patterns."""
        # This is a simplified estimation based on weekday patterns
        weekday_sums = [sum(row) for row in grid[:5]]  # Monday to Friday
        
        if not weekday_sums or sum(weekday_sums) == 0:
            return "No weekday pattern"
        
        # Analyze which days have highest activity
        max_day_idx = weekday_sums.index(max(weekday_sums))
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        if max_day_idx == 0:  # Monday
            return "Early week focus (Monday peak)"
        elif max_day_idx == 4:  # Friday
            return "Late week focus (Friday peak)"
        elif max_day_idx == 2:  # Wednesday
            return "Mid-week focus (Wednesday peak)"
        else:
            return f"Weekday balanced ({weekdays[max_day_idx]} peak)"
    
    def _assess_burnout_risk(self, week_sums: List[int], current_streak: int) -> str:
        """Assess burnout risk based on activity patterns."""
        if not week_sums:
            return "No data"
        
        # High activity + long streak = potential burnout risk
        recent_weeks = week_sums[-4:] if len(week_sums) >= 4 else week_sums
        recent_avg = sum(recent_weeks) / len(recent_weeks)
        
        if recent_avg > 20 and current_streak > 30:
            return "High (consider breaks)"
        elif recent_avg > 15 and current_streak > 20:
            return "Moderate (monitor activity)"
        elif recent_avg > 10 and current_streak > 10:
            return "Low (healthy pace)"
        else:
            return "Minimal (sustainable)"
    
    def _calculate_improvement_potential(self, week_sums: List[int], total_contributions: int) -> str:
        """Calculate improvement potential based on consistency gaps."""
        if not week_sums or total_contributions == 0:
            return "No data"
        
        # Find weeks with zero activity
        zero_weeks = sum(1 for week in week_sums if week == 0)
        total_weeks = len(week_sums)
        
        if zero_weeks == 0:
            return "Excellent consistency"
        elif zero_weeks <= total_weeks * 0.1:  # Less than 10% zero weeks
            return "High potential (few gaps)"
        elif zero_weeks <= total_weeks * 0.25:  # Less than 25% zero weeks
            return "Moderate potential (some gaps)"
        else:
            return "High potential (many gaps)" 