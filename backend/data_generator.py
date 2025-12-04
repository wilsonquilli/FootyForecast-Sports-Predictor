"""
Data Generator for Football Match Predictions
Generates synthetic training data based on realistic soccer statistics
"""

import numpy as np
import pandas as pd
from typing import Tuple, List


class FootballDataGenerator:
    """Generates synthetic football match data for training"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize the data generator
        
        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
    
    def generate_player_ratings(self, n_players: int = 11, 
                               mean_rating: float = 75, 
                               std_rating: float = 10) -> np.ndarray:
        """
        Generate player ratings for a team
        
        Args:
            n_players: Number of players (default 11)
            mean_rating: Average player rating
            std_rating: Standard deviation of ratings
            
        Returns:
            Array of player ratings
        """
        ratings = np.random.normal(mean_rating, std_rating, n_players)
        # Clip ratings between 50 and 99
        return np.clip(ratings, 50, 99)
    
    def generate_recent_form(self) -> List[int]:
        """
        Generate recent form (last 5 matches results)
        
        Returns:
            List of results: 3 = win, 1 = draw, 0 = loss
        """
        # Weighted probabilities for realistic distributions
        # Win: 40%, Draw: 30%, Loss: 30%
        results = np.random.choice([3, 1, 0], size=5, p=[0.40, 0.30, 0.30])
        return results.tolist()
    
    def calculate_expected_goals(self, 
                                team_strength: float, 
                                opponent_strength: float,
                                recent_form_points: int,
                                is_home: bool = True) -> float:
        """
        Calculate expected goals based on team characteristics
        
        Args:
            team_strength: Average player rating
            opponent_strength: Opponent average rating
            recent_form_points: Points from last 5 games
            is_home: Whether team is playing at home
            
        Returns:
            Expected number of goals
        """
        # Base goals calculation
        strength_diff = (team_strength - opponent_strength) / 10
        form_factor = (recent_form_points - 7.5) / 7.5  # Normalized around avg (7.5 points)
        home_advantage = 0.3 if is_home else 0
        
        # Expected goals with realistic soccer averages (1.0-2.5 goals per team)
        expected = 1.5 + (strength_diff * 0.15) + (form_factor * 0.3) + home_advantage
        
        # Add some randomness
        noise = np.random.normal(0, 0.3)
        expected = max(0, expected + noise)
        
        return expected
    
    def generate_match_result(self, expected_goals: float) -> int:
        """
        Generate actual match result from expected goals using Poisson distribution
        
        Args:
            expected_goals: Expected number of goals
            
        Returns:
            Actual number of goals scored
        """
        # Poisson distribution is realistic for soccer scores
        goals = np.random.poisson(expected_goals)
        # Cap at reasonable maximum
        return min(goals, 8)
    
    def generate_dataset(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Generate a complete dataset of football matches
        
        Args:
            n_samples: Number of matches to generate
            
        Returns:
            DataFrame with features and target variables
        """
        data = []
        
        for _ in range(n_samples):
            # Generate home team data
            home_players = self.generate_player_ratings()
            home_form = self.generate_recent_form()
            
            # Generate away team data
            away_players = self.generate_player_ratings()
            away_form = self.generate_recent_form()
            
            # Calculate team strengths
            home_strength = np.mean(home_players)
            away_strength = np.mean(away_players)
            
            home_form_points = sum(home_form)
            away_form_points = sum(away_form)
            
            # Calculate expected goals
            home_expected = self.calculate_expected_goals(
                home_strength, away_strength, home_form_points, is_home=True
            )
            away_expected = self.calculate_expected_goals(
                away_strength, home_strength, away_form_points, is_home=False
            )
            
            # Generate actual results
            home_goals = self.generate_match_result(home_expected)
            away_goals = self.generate_match_result(away_expected)
            
            # Create feature dictionary
            match_data = {
                # Home team player ratings
                **{f'home_player_{i+1}_rating': home_players[i] for i in range(11)},
                # Away team player ratings
                **{f'away_player_{i+1}_rating': away_players[i] for i in range(11)},
                # Home team recent form
                **{f'home_match_{i+1}_result': home_form[i] for i in range(5)},
                # Away team recent form
                **{f'away_match_{i+1}_result': away_form[i] for i in range(5)},
                # Target variables
                'home_goals': home_goals,
                'away_goals': away_goals
            }
            
            data.append(match_data)
        
        return pd.DataFrame(data)


if __name__ == "__main__":
    # Example usage
    generator = FootballDataGenerator()
    dataset = generator.generate_dataset(n_samples=100)
    
    print("Generated Dataset Shape:", dataset.shape)
    print("\nFirst few rows:")
    print(dataset.head())
    
    print("\nTarget variable distributions:")
    print(dataset[['home_goals', 'away_goals']].describe())

