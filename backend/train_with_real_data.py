"""
Train Model on Real Historical Data
Fetches real match data from API-Football and trains the model
"""

import os
import sys
import pandas as pd
from model_trainer import FootballModelTrainer
from historical_data_fetcher import HistoricalDataFetcher

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def train_on_real_data(league_ids: list = None, season: int = 2023, 
                      max_matches: int = 100, model_type: str = 'ensemble',
                      save_path: str = 'football_predictor_model_real.pkl'):
    """
    Train model on real historical data
    
    Args:
        league_ids: List of league IDs (default: Premier League, La Liga, Bundesliga)
        season: Season year to fetch data from
        max_matches: Maximum number of matches to fetch
        model_type: Model type ('random_forest', 'gradient_boost', 'ensemble')
        save_path: Path to save trained model
    """
    print("\n" + "="*70)
    print(" "*15 + "TRAINING ON REAL HISTORICAL DATA")
    print("="*70)
    
    # Check for API key
    api_key = os.getenv('FOOTBALL_API_KEY')
    if not api_key:
        print("\n⚠️  Error: FOOTBALL_API_KEY not found!")
        print("   Please set it in .env file:")
        print("   FOOTBALL_API_KEY=your_key_here")
        print("\n   Get free API key: https://rapidapi.com/api-sports/api/api-football")
        return False
    
    # Default leagues: Top 5 European leagues + Champions League + Europa League
    if league_ids is None:
        league_ids = [39, 140, 78, 135, 61, 2, 3]  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League, Europa League
    
    league_names = {
        39: "Premier League",
        140: "La Liga",
        78: "Bundesliga",
        135: "Serie A",
        61: "Ligue 1",
        2: "Champions League",
        3: "Europa League"
    }
    
    print(f"\n📊 Configuration:")
    print(f"   Leagues: {[league_names.get(lid, f'League {lid}') for lid in league_ids]}")
    print(f"   Season: {season}")
    print(f"   Max matches: {max_matches}")
    print(f"   Model type: {model_type}")
    
    print(f"\n⚠️  API Usage:")
    print(f"   Each match uses ~4-5 API requests")
    print(f"   Total requests: ~{max_matches * 4}-{max_matches * 5}")
    print(f"   Free tier limit: 100 requests/day")
    
    if max_matches * 4 > 100:
        print(f"\n⚠️  Warning: This exceeds free tier limit!")
        print(f"   Consider reducing max_matches or upgrading API plan")
        print("   Continuing anyway (may hit rate limits)...")
        # Auto-continue for non-interactive use
    
    # Fetch historical data
    print("\n" + "="*70)
    print("FETCHING HISTORICAL DATA")
    print("="*70)
    
    fetcher = HistoricalDataFetcher(api_key=api_key)
    
    try:
        df = fetcher.fetch_training_data(league_ids, season, max_matches=max_matches)
    except Exception as e:
        print(f"\n✗ Error fetching data: {e}")
        return False
    
    if len(df) == 0:
        print("\n✗ No data fetched. Check API key and rate limits.")
        return False
    
    print(f"\n✓ Fetched {len(df)} historical matches")
    
    # Check if we have enough data
    if len(df) < 50:
        print(f"\n⚠️  Warning: Only {len(df)} matches. Recommended: 100+ for good performance")
        print("   Continuing anyway (you can always fetch more data later)...")
        # Auto-continue for non-interactive use
    
    # Train model
    print("\n" + "="*70)
    print("TRAINING MODEL")
    print("="*70)
    
    trainer = FootballModelTrainer(model_type=model_type)
    
    # Prepare data using real historical data
    print("\n📊 Preparing training data from historical matches...")
    from feature_engineering import FeatureEngineer
    
    feature_engineer = FeatureEngineer()
    X, y = feature_engineer.engineer_features_from_dataframe(df)
    
    print(f"✓ Created {X.shape[1]} features from {len(df)} matches")
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"✓ Training set: {len(X_train)} matches")
    print(f"✓ Test set: {len(X_test)} matches")
    
    # Train
    print("\n🤖 Training model...")
    trainer.feature_engineer = feature_engineer
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
    print(f"Trained on: {len(df)} real historical matches")
    print(f"\nTo use this model:")
    print(f"  agent = FootballPredictionAgent(model_path='{save_path}')")
    
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train model on real historical data')
    parser.add_argument('--leagues', nargs='+', type=int, 
                       default=[39, 140, 78],
                       help='League IDs (39=Premier League, 140=La Liga, 78=Bundesliga, etc.)')
    parser.add_argument('--season', type=int, default=2023,
                       help='Season year (default: 2023)')
    parser.add_argument('--max-matches', type=int, default=100,
                       help='Maximum number of matches to fetch (default: 100)')
    parser.add_argument('--model-type', type=str, default='ensemble',
                       choices=['random_forest', 'gradient_boost', 'ensemble'],
                       help='Model type (default: ensemble)')
    parser.add_argument('--output', type=str, default='football_predictor_model_real.pkl',
                       help='Output model path (default: football_predictor_model_real.pkl)')
    
    args = parser.parse_args()
    
    success = train_on_real_data(
        league_ids=args.leagues,
        season=args.season,
        max_matches=args.max_matches,
        model_type=args.model_type,
        save_path=args.output
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

