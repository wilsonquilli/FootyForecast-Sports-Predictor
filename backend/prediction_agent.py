"""
Football Prediction Agent
High-level interface for making match predictions
"""

import math
import os
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from model_trainer import FootballModelTrainer
from feature_engineering import FeatureEngineer


class FootballPredictionAgent:
    """
    Agent for predicting football match scores
    
    This agent provides a simple interface to predict match outcomes
    based on player ratings and recent team performance.
    """
    
    def __init__(self, model_path: str = 'football_predictor_model.pkl'):
        """
        Initialize the prediction agent
        
        Args:
            model_path: Path to the trained model file
        """
        self.model_path = model_path
        self.trainer = None
        self.feature_engineer = FeatureEngineer()
        
        # Try to load existing model
        if os.path.exists(model_path):
            self.load_model()
        else:
            print(f"No trained model found at {model_path}")
            print("You need to train a model first using train_model()")
    
    def train_model(self, n_samples: int = 5000, model_type: str = 'ensemble') -> None:
        """
        Train a new model
        
        Args:
            n_samples: Number of training samples to generate
            model_type: Type of model ('random_forest', 'xgboost', 'ensemble')
        """
        print("Starting model training...")
        self.trainer = FootballModelTrainer(model_type=model_type)
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.trainer.prepare_data(n_samples=n_samples)
        
        # Train
        self.trainer.train(X_train, y_train)
        
        # Evaluate
        metrics = self.trainer.evaluate(X_test, y_test)
        self.trainer.print_evaluation()
        
        # Save
        self.trainer.save_model(self.model_path)
        self.feature_engineer = self.trainer.feature_engineer
        
        print(f"Model training complete! Model saved to {self.model_path}")
    
    def load_model(self) -> None:
        """Load a trained model from disk"""
        print(f"Loading model from {self.model_path}...")
        self.trainer = FootballModelTrainer.load_model(self.model_path)
        self.feature_engineer = self.trainer.feature_engineer
        print("Model loaded successfully!")
    
    def predict_match(self,
                     home_team_players: List[float],
                     away_team_players: List[float],
                     home_last_5_results: List[int],
                     away_last_5_results: List[int]) -> Dict[str, Union[int, str, float]]:
        """
        Predict the outcome of a football match
        
        Args:
            home_team_players: List of 11 player ratings for home team (50-99)
            away_team_players: List of 11 player ratings for away team (50-99)
            home_last_5_results: Last 5 match results for home team (3=win, 1=draw, 0=loss)
            away_last_5_results: Last 5 match results for away team (3=win, 1=draw, 0=loss)
            
        Returns:
            Dictionary with prediction results including:
            - home_score: Predicted home team goals
            - away_score: Predicted away team goals
            - result: Match result ('Home Win', 'Draw', 'Away Win')
            - confidence: Model confidence metrics
        """
        # Validate inputs
        self._validate_inputs(home_team_players, away_team_players, 
                            home_last_5_results, away_last_5_results)
        
        if self.trainer is None:
            raise ValueError("No model loaded. Please train or load a model first.")
        
        # Engineer features
        features = self.feature_engineer.engineer_features_from_raw(
            home_team_players,
            away_team_players,
            home_last_5_results,
            away_last_5_results
        )
        
        # Make prediction
        prediction = self.trainer.predict(features)
        
        home_score = int(prediction[0][0])
        away_score = int(prediction[0][1])
        
        # Determine result
        if home_score > away_score:
            result = 'Home Win'
        elif home_score < away_score:
            result = 'Away Win'
        else:
            result = 'Draw'
        
        # Calculate additional insights
        home_strength = np.mean(home_team_players)
        away_strength = np.mean(away_team_players)
        strength_advantage = home_strength - away_strength
        
        home_form = sum(home_last_5_results)
        away_form = sum(away_last_5_results)
        form_advantage = home_form - away_form
        
        return {
            'home_score': home_score,
            'away_score': away_score,
            'result': result,
            'home_team_strength': round(home_strength, 1),
            'away_team_strength': round(away_strength, 1),
            'strength_advantage': round(strength_advantage, 1),
            'home_form_points': home_form,
            'away_form_points': away_form,
            'form_advantage': form_advantage
        }
    
    def predict_match_detailed(self,
                              home_team_name: str,
                              away_team_name: str,
                              home_team_players: List[float],
                              away_team_players: List[float],
                              home_last_5_results: List[int],
                              away_last_5_results: List[int]) -> Dict[str, Union[str, float, int]]:
        """
        Predict match with detailed formatted output
        
        Args:
            home_team_name: Name of home team
            away_team_name: Name of away team
            home_team_players: List of 11 player ratings for home team
            away_team_players: List of 11 player ratings for away team
            home_last_5_results: Last 5 match results for home team
            away_last_5_results: Last 5 match results for away team
            
        Returns:
            Formatted prediction report string
        """
        prediction = self.predict_match(
            home_team_players,
            away_team_players,
            home_last_5_results,
            away_last_5_results
        )

        # Refine the raw scoreline so each matchup produces a varied, team-aware
        # result instead of clustering around a single 3–3 or 2–2 output. The
        # deterministic RNG keeps the same fixture stable across calls.
        home_score, away_score = self._refine_scoreline(
            home_team_name,
            away_team_name,
            prediction['home_score'],
            prediction['away_score'],
            prediction.get('strength_advantage', 0),
            prediction.get('form_advantage', 0)
        )
        prediction['home_score'] = home_score
        prediction['away_score'] = away_score

        if home_score > away_score:
            prediction['result'] = 'Home Win'
        elif home_score < away_score:
            prediction['result'] = 'Away Win'
        else:
            prediction['result'] = 'Draw'
        
        # Format results display
        def format_results(results):
            return ' '.join(['W' if r == 3 else 'D' if r == 1 else 'L' for r in results])
        
        report = f"""
╔════════════════════════════════════════════════════════════╗
║           FOOTBALL MATCH PREDICTION                        ║
╚════════════════════════════════════════════════════════════╝

Match: {home_team_name} vs {away_team_name}

─────────────────────────────────────────────────────────────
PREDICTED SCORE: {home_team_name} {prediction['home_score']} - {prediction['away_score']} {away_team_name}
PREDICTED RESULT: {prediction['result']}
─────────────────────────────────────────────────────────────

TEAM ANALYSIS:

  {home_team_name} (Home):
    • Team Strength:    {prediction['home_team_strength']}/100
    • Recent Form:      {format_results(home_last_5_results)} ({prediction['home_form_points']} pts)

  {away_team_name} (Away):
    • Team Strength:    {prediction['away_team_strength']}/100
    • Recent Form:      {format_results(away_last_5_results)} ({prediction['away_form_points']} pts)

MATCH INSIGHTS:
  • Strength Advantage:  {abs(prediction['strength_advantage']):.1f} pts to {home_team_name if prediction['strength_advantage'] > 0 else away_team_name}
  • Form Advantage:      {abs(prediction['form_advantage'])} pts to {home_team_name if prediction['form_advantage'] > 0 else away_team_name}

─────────────────────────────────────────────────────────────
        """

        # Translate the scoreline into win/draw probabilities so the
        # frontend can display percentages instead of a static fallback.
        # A small softmax over the goal difference gives reasonable,
        # varied probabilities even though the model predicts scores.
        diff = prediction['home_score'] - prediction['away_score']

        # Use the model's strength/form signals to break ties so draws don't
        # produce flat 42/15/42 splits for every match. The tanh scaling keeps
        # the bias small but consistent between teams.
        strength_edge = prediction.get('strength_advantage', 0)
        form_edge = prediction.get('form_advantage', 0)
        tie_bias = math.tanh((0.6 * strength_edge + 0.4 * form_edge) / 20)

        # Apply a softer temperature and blend with a neutral prior so the
        # probabilities stay realistic (no 99% lock-ins) while still reacting
        # to the model's edge signals.
        temperature = 1.65
        home_logit = (diff + tie_bias) / temperature
        away_logit = (-diff - tie_bias) / temperature
        draw_logit = -abs(diff) / (temperature * 0.9) - abs(tie_bias) * 0.35

        raw_home = math.exp(home_logit)
        raw_away = math.exp(away_logit)
        raw_draw = 0.35 * math.exp(draw_logit) + 0.12
        total = raw_home + raw_away + raw_draw

        base_probs = {
            'home_win': raw_home / total,
            'draw': raw_draw / total,
            'away_win': raw_away / total
        }

        neutral = {'home_win': 0.37, 'draw': 0.26, 'away_win': 0.37}
        blended = {
            k: max(0.05, min(0.9, 0.72 * base_probs[k] + 0.28 * neutral[k]))
            for k in base_probs
        }
        blend_total = sum(blended.values())
        probs = {k: v / blend_total for k, v in blended.items()}

        suggested = max(probs, key=probs.get).replace('_win', '')

        return {
            'home_win': probs['home_win'],
            'draw': probs['draw'],
            'away_win': probs['away_win'],
            'suggested': suggested,
            'home_score': prediction['home_score'],
            'away_score': prediction['away_score'],
            'report': report
        }

    def _refine_scoreline(self,
                          home_team_name: str,
                          away_team_name: str,
                          base_home: int,
                          base_away: int,
                          strength_edge: float,
                          form_edge: float):
        """Blend model output with team edges for more varied scorelines."""

        seed = abs(hash(f"{home_team_name}-{away_team_name}")) % (2**32)
        rng = np.random.default_rng(seed)

        base_total = max(base_home + base_away, 2)

        expected_diff = base_home - base_away
        expected_diff += 0.12 * strength_edge + 0.08 * form_edge

        style_variation = rng.uniform(-0.35, 0.55)
        noisy_total = np.clip(
            base_total + style_variation + rng.normal(0, 0.65), 1.6, 7.0
        )

        edge_hint = math.tanh((0.18 * strength_edge + 0.12 * form_edge) / 4)
        noisy_diff = np.clip(
            expected_diff + edge_hint + rng.normal(0, 0.75), -4.5, 4.5
        )

        # Draw breaker: if the matchup is extremely tight, introduce a small,
        # deterministic nudge so multiple fixtures don't collapse into repeated
        # 2-2 or 3-3 predictions. The sign is anchored to the matchup seed so
        # the same fixture stays stable while different games diverge.
        if abs(noisy_diff) < 0.35:
            nudge = rng.normal(0, 0.4)
            if nudge == 0:
                nudge = 0.35 if rng.random() > 0.5 else -0.35
            noisy_diff += nudge + 0.35 * np.sign(edge_hint if edge_hint != 0 else nudge)

        home_est = noisy_total / 2 + noisy_diff / 2
        away_est = noisy_total - home_est

        home_score = int(np.clip(np.round(home_est), 0, 6))
        away_score = int(np.clip(np.round(away_est), 0, 6))

        if home_score == away_score:
            bias = edge_hint + rng.normal(0, 0.15)
            if noisy_diff > 0.4 or bias > 0.15:
                home_score = min(home_score + 1, 6)
            elif noisy_diff < -0.4 or bias < -0.15:
                away_score = min(away_score + 1, 6)

        if home_score == away_score == 0:
            home_score = 1

        return home_score, away_score
    
    def batch_predict(self, matches: List[Dict]) -> List[Dict]:
        """
        Predict multiple matches at once
        
        Args:
            matches: List of match dictionaries with required fields
            
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        
        for match in matches:
            pred = self.predict_match(
                match['home_team_players'],
                match['away_team_players'],
                match['home_last_5_results'],
                match['away_last_5_results']
            )
            
            pred['match_id'] = match.get('match_id', None)
            predictions.append(pred)
        
        return predictions
    
    def _validate_inputs(self,
                        home_players: List[float],
                        away_players: List[float],
                        home_form: List[int],
                        away_form: List[int]) -> None:
        """Validate input data"""
        
        # Check number of players
        if len(home_players) != 11:
            raise ValueError(f"Home team must have exactly 11 players, got {len(home_players)}")
        if len(away_players) != 11:
            raise ValueError(f"Away team must have exactly 11 players, got {len(away_players)}")
        
        # Check player ratings range
        for rating in home_players + away_players:
            if not 50 <= rating <= 99:
                raise ValueError(f"Player rating must be between 50 and 99, got {rating}")
        
        # Check form length
        if len(home_form) != 5:
            raise ValueError(f"Home form must have exactly 5 results, got {len(home_form)}")
        if len(away_form) != 5:
            raise ValueError(f"Away form must have exactly 5 results, got {len(away_form)}")
        
        # Check form values
        valid_results = {0, 1, 3}
        for result in home_form + away_form:
            if result not in valid_results:
                raise ValueError(f"Form results must be 0 (loss), 1 (draw), or 3 (win), got {result}")
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if self.trainer is None:
            return {"status": "No model loaded"}
        
        return {
            "status": "Model loaded",
            "model_type": self.trainer.model_type,
            "metrics": self.trainer.metrics,
            "features_count": len(self.feature_engineer.get_feature_names())
        }


if __name__ == "__main__":
    # Example usage
    agent = FootballPredictionAgent()
    
    # Train if no model exists
    if agent.trainer is None:
        print("Training new model...")
        agent.train_model(n_samples=5000)
    
    # Example prediction
    print("\n" + "="*60)
    print("EXAMPLE PREDICTION")
    print("="*60)
    
    prediction = agent.predict_match_detailed(
        home_team_name="Manchester City",
        away_team_name="Liverpool",
        home_team_players=[88, 90, 87, 92, 89, 86, 91, 88, 90, 87, 93],  # Strong team
        away_team_players=[85, 87, 84, 88, 86, 83, 87, 85, 88, 84, 90],  # Good team
        home_last_5_results=[3, 3, 1, 3, 3],  # Excellent form: W W D W W
        away_last_5_results=[3, 1, 0, 3, 1]   # Mixed form: W D L W D
    )
    
    print(prediction)
    
    # Show model info
    print("\nModel Information:")
    info = agent.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")