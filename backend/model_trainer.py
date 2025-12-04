"""
Model Trainer for Football Score Prediction
Trains and evaluates ML models for predicting match scores
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from typing import Tuple, Dict, Any

# Try to import xgboost, but make it optional
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except (ImportError, Exception) as e:
    XGBOOST_AVAILABLE = False
    print(f"Warning: XGBoost not available ({e}). Will use Random Forest and Gradient Boosting only.")

from data_generator import FootballDataGenerator
from feature_engineering import FeatureEngineer


class FootballModelTrainer:
    """Trains ML models to predict football match scores"""
    
    def __init__(self, model_type: str = 'ensemble'):
        """
        Initialize the model trainer
        
        Args:
            model_type: Type of model ('random_forest', 'xgboost', 'gradient_boost', 'ensemble')
        """
        self.model_type = model_type
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.metrics = {}
    
    def create_model(self) -> Any:
        """
        Create the ML model based on model_type
        
        Returns:
            Instantiated model
        """
        if self.model_type == 'random_forest':
            return MultiOutputRegressor(
                RandomForestRegressor(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
            )
        elif self.model_type == 'xgboost':
            if not XGBOOST_AVAILABLE:
                raise ValueError("XGBoost is not available. Use 'random_forest' or 'gradient_boost' instead.")
            return MultiOutputRegressor(
                xgb.XGBRegressor(
                    n_estimators=200,
                    max_depth=8,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1
                )
            )
        elif self.model_type == 'gradient_boost':
            return MultiOutputRegressor(
                GradientBoostingRegressor(
                    n_estimators=200,
                    max_depth=8,
                    learning_rate=0.1,
                    random_state=42
                )
            )
        elif self.model_type == 'ensemble':
            # Will create ensemble in train method
            return None
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def prepare_data(self, n_samples: int = 5000) -> Tuple[pd.DataFrame, pd.DataFrame, 
                                                            pd.DataFrame, pd.DataFrame]:
        """
        Generate and prepare training data
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        print(f"Generating {n_samples} training samples...")
        generator = FootballDataGenerator()
        raw_data = generator.generate_dataset(n_samples=n_samples)
        
        print("Engineering features...")
        X, y = self.feature_engineer.engineer_features_from_dataframe(raw_data)
        
        print(f"Created {X.shape[1]} features from raw data")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
    
    def train(self, X_train: pd.DataFrame, y_train: pd.DataFrame) -> None:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training targets
        """
        if self.model_type == 'ensemble':
            print("Training ensemble model...")
            
            # Train Random Forest
            self.rf_model = MultiOutputRegressor(
                RandomForestRegressor(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=5,
                    random_state=42,
                    n_jobs=-1
                )
            )
            
            print("Training Random Forest...")
            self.rf_model.fit(X_train, y_train)
            
            # Train additional model (XGBoost if available, otherwise Gradient Boosting)
            if XGBOOST_AVAILABLE:
                print("Training XGBoost...")
                self.xgb_model = MultiOutputRegressor(
                    xgb.XGBRegressor(
                        n_estimators=200,
                        max_depth=8,
                        learning_rate=0.1,
                        random_state=42,
                        n_jobs=-1
                    )
                )
                self.xgb_model.fit(X_train, y_train)
                
                # Store both models
                self.model = {
                    'rf': self.rf_model,
                    'xgb': self.xgb_model
                }
            else:
                print("Training Gradient Boosting (XGBoost not available)...")
                self.gb_model = MultiOutputRegressor(
                    GradientBoostingRegressor(
                        n_estimators=200,
                        max_depth=8,
                        learning_rate=0.1,
                        random_state=42
                    )
                )
                self.gb_model.fit(X_train, y_train)
                
                # Store both models
                self.model = {
                    'rf': self.rf_model,
                    'gb': self.gb_model
                }
        else:
            print(f"Training {self.model_type} model...")
            self.model = self.create_model()
            self.model.fit(X_train, y_train)
        
        print("Training completed!")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features for prediction
            
        Returns:
            Predicted scores [home_goals, away_goals]
        """
        if self.model_type == 'ensemble':
            # Average predictions from both models
            rf_pred = self.model['rf'].predict(X)
            
            # Use XGBoost if available, otherwise Gradient Boosting
            if 'xgb' in self.model:
                second_pred = self.model['xgb'].predict(X)
            else:
                second_pred = self.model['gb'].predict(X)
            
            predictions = (rf_pred + second_pred) / 2
        else:
            predictions = self.model.predict(X)
        
        # Round and clip predictions to realistic values
        predictions = np.round(predictions).astype(int)
        predictions = np.clip(predictions, 0, 8)
        
        return predictions
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test targets
            
        Returns:
            Dictionary of evaluation metrics
        """
        predictions = self.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, predictions)
        
        # Calculate per-target metrics
        home_mae = mean_absolute_error(y_test['home_goals'], predictions[:, 0])
        away_mae = mean_absolute_error(y_test['away_goals'], predictions[:, 1])
        
        # Calculate exact match accuracy
        exact_match = np.mean(np.all(predictions == y_test.values, axis=1))
        
        # Calculate goal difference accuracy (correct winner prediction)
        y_test_diff = np.sign(y_test['home_goals'] - y_test['away_goals'])
        pred_diff = np.sign(predictions[:, 0] - predictions[:, 1])
        winner_accuracy = np.mean(y_test_diff == pred_diff)
        
        self.metrics = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'home_mae': home_mae,
            'away_mae': away_mae,
            'exact_match_accuracy': exact_match,
            'winner_accuracy': winner_accuracy
        }
        
        return self.metrics
    
    def print_evaluation(self, metrics: Dict[str, float] = None) -> None:
        """Print evaluation metrics in a readable format"""
        if metrics is None:
            metrics = self.metrics
        
        print("\n" + "="*50)
        print("MODEL EVALUATION RESULTS")
        print("="*50)
        print(f"Overall MAE:              {metrics['mae']:.3f} goals")
        print(f"Overall RMSE:             {metrics['rmse']:.3f} goals")
        print(f"R² Score:                 {metrics['r2']:.3f}")
        print(f"\nHome Goals MAE:           {metrics['home_mae']:.3f} goals")
        print(f"Away Goals MAE:           {metrics['away_mae']:.3f} goals")
        print(f"\nExact Match Accuracy:     {metrics['exact_match_accuracy']*100:.2f}%")
        print(f"Winner Prediction Acc:    {metrics['winner_accuracy']*100:.2f}%")
        print("="*50 + "\n")
    
    def save_model(self, filepath: str = 'football_predictor_model.pkl') -> None:
        """
        Save trained model to disk
        
        Args:
            filepath: Path to save the model
        """
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_engineer': self.feature_engineer,
            'metrics': self.metrics
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str = 'football_predictor_model.pkl') -> 'FootballModelTrainer':
        """
        Load trained model from disk
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            Loaded FootballModelTrainer instance
        """
        model_data = joblib.load(filepath)
        trainer = cls(model_type=model_data['model_type'])
        trainer.model = model_data['model']
        trainer.feature_engineer = model_data['feature_engineer']
        trainer.metrics = model_data['metrics']
        print(f"Model loaded from {filepath}")
        return trainer


if __name__ == "__main__":
    # Train and evaluate model
    trainer = FootballModelTrainer(model_type='ensemble')
    
    # Prepare data
    X_train, X_test, y_train, y_test = trainer.prepare_data(n_samples=5000)
    
    # Train model
    trainer.train(X_train, y_train)
    
    # Evaluate
    metrics = trainer.evaluate(X_test, y_test)
    trainer.print_evaluation()
    
    # Save model
    trainer.save_model('football_predictor_model.pkl')
    
    # Show sample predictions
    print("Sample Predictions:")
    print("-" * 50)
    sample_predictions = trainer.predict(X_test.head(10))
    sample_actual = y_test.head(10).values
    
    for i in range(10):
        pred = sample_predictions[i]
        actual = sample_actual[i]
        print(f"Match {i+1}: Predicted {pred[0]}-{pred[1]} | Actual {int(actual[0])}-{int(actual[1])}")

