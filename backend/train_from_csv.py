"""
Train Model from CSV File
Loads historical match data from CSV and trains the model
Useful if you've already fetched data or have your own dataset
"""

import pandas as pd
import sys
from model_trainer import FootballModelTrainer
from feature_engineering import FeatureEngineer
from sklearn.model_selection import train_test_split


def train_from_csv(csv_path: str, model_type: str = 'ensemble',
                   save_path: str = 'football_predictor_model_real.pkl'):
    """
    Train model from CSV file with historical match data
    
    Args:
        csv_path: Path to CSV file with match data
        model_type: Model type ('random_forest', 'gradient_boost', 'ensemble')
        save_path: Path to save trained model
    """
    print("\n" + "="*70)
    print(" "*15 + "TRAINING FROM CSV DATA")
    print("="*70)
    
    # Load data
    print(f"\n📂 Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"\n✗ Error: File not found: {csv_path}")
        return False
    except Exception as e:
        print(f"\n✗ Error loading CSV: {e}")
        return False
    
    print(f"✓ Loaded {len(df)} matches")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Validate data format
    required_columns = []
    for prefix in ['home_player_', 'away_player_']:
        for i in range(1, 12):
            required_columns.append(f'{prefix}{i}_rating')
    for prefix in ['home_match_', 'away_match_']:
        for i in range(1, 6):
            required_columns.append(f'{prefix}{i}_result')
    required_columns.extend(['home_goals', 'away_goals'])
    
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"\n✗ Error: Missing required columns: {missing[:5]}...")
        print(f"   Expected format: Same as synthetic data generator")
        return False
    
    # Check data quality
    if len(df) < 50:
        print(f"\n⚠️  Warning: Only {len(df)} matches. Recommended: 100+ for good performance")
    
    # Prepare data
    print("\n📊 Preparing training data...")
    feature_engineer = FeatureEngineer()
    X, y = feature_engineer.engineer_features_from_dataframe(df)
    
    print(f"✓ Created {X.shape[1]} features from {len(df)} matches")
    
    # Split data
    print("\n📊 Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"✓ Training set: {len(X_train)} matches")
    print(f"✓ Test set: {len(X_test)} matches")
    
    # Train model
    print("\n" + "="*70)
    print("TRAINING MODEL")
    print("="*70)
    
    trainer = FootballModelTrainer(model_type=model_type)
    trainer.feature_engineer = feature_engineer
    
    print(f"\n🤖 Training {model_type} model...")
    trainer.train(X_train, y_train)
    
    # Evaluate
    print("\n📈 Evaluating model...")
    metrics = trainer.evaluate(X_test, y_test)
    trainer.print_evaluation()
    
    # Save model
    print(f"\n💾 Saving model to {save_path}...")
    trainer.save_model(save_path)
    
    print("\n" + "="*70)
    print("✓ TRAINING COMPLETE!")
    print("="*70)
    print(f"\nModel saved to: {save_path}")
    print(f"Trained on: {len(df)} matches from {csv_path}")
    print(f"\nTo use this model:")
    print(f"  agent = FootballPredictionAgent(model_path='{save_path}')")
    
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train model from CSV file')
    parser.add_argument('csv_path', type=str,
                       help='Path to CSV file with match data')
    parser.add_argument('--model-type', type=str, default='ensemble',
                       choices=['random_forest', 'gradient_boost', 'ensemble'],
                       help='Model type (default: ensemble)')
    parser.add_argument('--output', type=str, default='football_predictor_model_real.pkl',
                       help='Output model path (default: football_predictor_model_real.pkl)')
    
    args = parser.parse_args()
    
    success = train_from_csv(
        csv_path=args.csv_path,
        model_type=args.model_type,
        save_path=args.output
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python train_from_csv.py <csv_file> [--model-type ensemble] [--output model.pkl]")
        print("\nExample:")
        print("  python train_from_csv.py historical_training_data.csv")
        print("  python train_from_csv.py my_data.csv --model-type ensemble --output my_model.pkl")
        sys.exit(1)
    
    main()

