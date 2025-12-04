"""
Quick script to test the predictor with a real-life game
Usage: python test_real_game.py "Team 1" "Team 2"
"""

import sys
from prediction_agent import FootballPredictionAgent
from api_integration import FootballDataAPI
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def test_real_game(home_team: str, away_team: str):
    """Test prediction with a real game"""
    
    print("\n" + "="*70)
    print(" "*20 + "REAL GAME PREDICTION TEST")
    print("="*70)
    
    # Initialize agent
    print("\n📊 Loading prediction model...")
    agent = FootballPredictionAgent()
    
    if agent.trainer is None:
        print("⚠️  No model found. Training new model (this will take a minute)...")
        agent.train_model(n_samples=5000)
    else:
        print("✓ Model loaded successfully!")
    
    # Initialize API client
    api_key = os.getenv('FOOTBALL_API_KEY')
    use_real_api = os.getenv('USE_REAL_API', 'false').lower() == 'true'
    
    api_client = FootballDataAPI(api_key=api_key, use_real_api=use_real_api)
    
    if api_client.use_real_api:
        print("✓ Real API enabled - fetching actual team data!")
    else:
        print("ℹ️  Using simulated data (set USE_REAL_API=true in .env for real data)")
    
    # Fetch team data
    print(f"\n📥 Fetching data for {home_team} vs {away_team}...")
    print("-"*70)
    
    home_data, away_data = api_client.get_match_data(home_team, away_team)
    
    print("\n" + "="*70)
    print("TEAM DATA SUMMARY")
    print("="*70)
    
    print(f"\n🏠 {home_data['team_name']} (Home):")
    print(f"   Average Rating: {sum(home_data['player_ratings'])/len(home_data['player_ratings']):.1f}/100")
    print(f"   Recent Form: {home_data['recent_form']} ({sum(home_data['recent_form'])} pts)")
    print(f"   Data Source: {home_data.get('source', 'unknown')}")
    
    print(f"\n✈️  {away_data['team_name']} (Away):")
    print(f"   Average Rating: {sum(away_data['player_ratings'])/len(away_data['player_ratings']):.1f}/100")
    print(f"   Recent Form: {away_data['recent_form']} ({sum(away_data['recent_form'])} pts)")
    print(f"   Data Source: {away_data.get('source', 'unknown')}")
    
    # Make prediction
    print("\n" + "="*70)
    print("🤖 MAKING PREDICTION...")
    print("="*70)
    
    prediction = agent.predict_match_detailed(
        home_team_name=home_data['team_name'],
        away_team_name=away_data['team_name'],
        home_team_players=home_data['player_ratings'],
        away_team_players=away_data['player_ratings'],
        home_last_5_results=home_data['recent_form'],
        away_last_5_results=away_data['recent_form']
    )
    
    print(prediction)
    
    # Additional insights
    pred_dict = agent.predict_match(
        home_team_players=home_data['player_ratings'],
        away_team_players=away_data['player_ratings'],
        home_last_5_results=home_data['recent_form'],
        away_last_5_results=away_data['recent_form']
    )
    
    total_goals = pred_dict['home_score'] + pred_dict['away_score']
    
    print("\n" + "="*70)
    print("BETTING INSIGHTS")
    print("="*70)
    print(f"\n📈 Prediction Summary:")
    print(f"   • Winner: {pred_dict['result']}")
    print(f"   • Total Goals: {total_goals}")
    print(f"   • Goal Difference: {abs(pred_dict['home_score'] - pred_dict['away_score'])}")
    
    print(f"\n🎯 Betting Suggestions:")
    if pred_dict['result'] == 'Home Win':
        print(f"   • 1X2: Home Win ({home_data['team_name']})")
    elif pred_dict['result'] == 'Away Win':
        print(f"   • 1X2: Away Win ({away_data['team_name']})")
    else:
        print(f"   • 1X2: Draw")
    
    if total_goals > 2.5:
        print(f"   • Over/Under: Over 2.5 goals")
    else:
        print(f"   • Over/Under: Under 2.5 goals")
    
    if pred_dict['home_score'] > 0 and pred_dict['away_score'] > 0:
        print(f"   • Both Teams to Score: Yes")
    else:
        print(f"   • Both Teams to Score: No")
    
    print("\n" + "="*70)
    print("⚠️  Note: This is a prediction model. Actual results may vary!")
    print("="*70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        home_team = sys.argv[1]
        away_team = sys.argv[2]
        test_real_game(home_team, away_team)
    else:
        print("Usage: python test_real_game.py \"Home Team\" \"Away Team\"")
        print("\nExample:")
        print('  python test_real_game.py "Manchester City" "Liverpool"')
        print('  python test_real_game.py "Barcelona" "Real Madrid"')
        print('  python test_real_game.py "Bayern Munich" "Borussia Dortmund"')
        print("\nOr run without arguments to use default teams:")
        
        # Default example
        print("\n" + "="*70)
        print("Running with example teams...")
        print("="*70)
        test_real_game("Manchester City", "Liverpool")

