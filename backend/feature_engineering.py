"""
Feature Engineering for Football Match Predictions
Processes player ratings and team performance data into ML-ready features
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple


class FeatureEngineer:
    """Processes raw match data into engineered features"""
    
    def __init__(self):
        """Initialize the feature engineer"""
        self.feature_names = []
    
    def calculate_team_statistics(self, player_ratings: List[float]) -> Dict[str, float]:
        """
        Calculate aggregate statistics from player ratings
        
        Args:
            player_ratings: List of player ratings for a team
            
        Returns:
            Dictionary of statistical features
        """
        ratings_array = np.array(player_ratings)
        
        return {
            'mean_rating': np.mean(ratings_array),
            'median_rating': np.median(ratings_array),
            'max_rating': np.max(ratings_array),
            'min_rating': np.min(ratings_array),
            'std_rating': np.std(ratings_array),
            'rating_range': np.max(ratings_array) - np.min(ratings_array),
            # Top 3 players average (key players)
            'top3_avg': np.mean(sorted(ratings_array, reverse=True)[:3]),
            # Bottom 3 players average (weak links)
            'bottom3_avg': np.mean(sorted(ratings_array)[:3])
        }
    
    def calculate_form_features(self, recent_results: List[int]) -> Dict[str, float]:
        """
        Calculate form features from recent match results
        
        Args:
            recent_results: List of recent match results (3=win, 1=draw, 0=loss)
            
        Returns:
            Dictionary of form features
        """
        results_array = np.array(recent_results)
        
        # Count wins, draws, losses
        wins = np.sum(results_array == 3)
        draws = np.sum(results_array == 1)
        losses = np.sum(results_array == 0)
        
        # Calculate weighted form (recent matches weighted more)
        weights = np.array([0.1, 0.15, 0.2, 0.25, 0.3])  # Most recent has highest weight
        weighted_form = np.sum(results_array * weights)
        
        return {
            'total_points': np.sum(results_array),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': wins / len(recent_results),
            'weighted_form': weighted_form,
            # Momentum: last 2 games vs first 3 games
            'momentum': np.mean(results_array[-2:]) - np.mean(results_array[:3])
        }
    
    def engineer_features_from_raw(self, 
                                   home_players: List[float],
                                   away_players: List[float],
                                   home_form: List[int],
                                   away_form: List[int]) -> pd.DataFrame:
        """
        Convert raw match data into engineered features
        
        Args:
            home_players: Home team player ratings (11 players)
            away_players: Away team player ratings (11 players)
            home_form: Home team last 5 results
            away_form: Away team last 5 results
            
        Returns:
            DataFrame with engineered features
        """
        features = {}
        
        # Home team features
        home_stats = self.calculate_team_statistics(home_players)
        for key, value in home_stats.items():
            features[f'home_{key}'] = value
        
        home_form_features = self.calculate_form_features(home_form)
        for key, value in home_form_features.items():
            features[f'home_{key}'] = value
        
        # Away team features
        away_stats = self.calculate_team_statistics(away_players)
        for key, value in away_stats.items():
            features[f'away_{key}'] = value
        
        away_form_features = self.calculate_form_features(away_form)
        for key, value in away_form_features.items():
            features[f'away_{key}'] = value
        
        # Comparative features (home vs away)
        features['rating_diff'] = home_stats['mean_rating'] - away_stats['mean_rating']
        features['form_diff'] = home_form_features['total_points'] - away_form_features['total_points']
        features['top3_diff'] = home_stats['top3_avg'] - away_stats['top3_avg']
        features['momentum_diff'] = home_form_features['momentum'] - away_form_features['momentum']
        
        # Overall strength indicators
        features['total_strength'] = home_stats['mean_rating'] + away_stats['mean_rating']
        features['strength_ratio'] = home_stats['mean_rating'] / (away_stats['mean_rating'] + 1e-6)
        
        # Home advantage indicator (can be expanded with historical data)
        features['home_advantage'] = 1  # Binary indicator that this team is home
        
        return pd.DataFrame([features])
    
    def engineer_features_from_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Convert a dataframe of raw match data into engineered features
        
        Args:
            df: DataFrame with raw player ratings and form data
            
        Returns:
            Tuple of (features_df, targets_df)
        """
        all_features = []
        
        for idx, row in df.iterrows():
            # Extract home player ratings
            home_players = [row[f'home_player_{i+1}_rating'] for i in range(11)]
            # Extract away player ratings
            away_players = [row[f'away_player_{i+1}_rating'] for i in range(11)]
            # Extract home form
            home_form = [row[f'home_match_{i+1}_result'] for i in range(5)]
            # Extract away form
            away_form = [row[f'away_match_{i+1}_result'] for i in range(5)]
            
            # Engineer features
            features = self.engineer_features_from_raw(
                home_players, away_players, home_form, away_form
            )
            all_features.append(features)
        
        features_df = pd.concat(all_features, ignore_index=True)
        targets_df = df[['home_goals', 'away_goals']]
        
        self.feature_names = features_df.columns.tolist()
        
        return features_df, targets_df
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names


if __name__ == "__main__":
    # Example usage
    from data_generator import FootballDataGenerator
    
    # Generate sample data
    generator = FootballDataGenerator()
    raw_data = generator.generate_dataset(n_samples=10)
    
    # Engineer features
    engineer = FeatureEngineer()
    features, targets = engineer.engineer_features_from_dataframe(raw_data)
    
    print("Engineered Features Shape:", features.shape)
    print("\nFeature Names:")
    print(engineer.get_feature_names())
    print("\nFirst few rows of features:")
    print(features.head())
    print("\nTargets:")
    print(targets.head())

