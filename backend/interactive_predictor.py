"""
Interactive Football Match Predictor
Asks user for match details and makes predictions
"""

from prediction_agent import FootballPredictionAgent
from data_generator import FootballDataGenerator
from api_integration import FootballDataAPI
import sys
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class InteractivePredictor:
    """Interactive match prediction system"""
    
    def __init__(self):
        """Initialize the interactive predictor"""
        print("\n" + "="*70)
        print(" "*15 + "INTERACTIVE FOOTBALL PREDICTOR")
        print("="*70)
        print("\nInitializing prediction system...")
        
        self.agent = FootballPredictionAgent()
        
        # Train model if needed
        if self.agent.trainer is None:
            print("\nTraining prediction model (this will take a minute)...")
            self.agent.train_model(n_samples=5000)
            print("✓ Model ready!")
        else:
            print("✓ Model loaded successfully!")
        
        # Initialize API client
        api_key = os.getenv('FOOTBALL_API_KEY')
        use_real_api = os.getenv('USE_REAL_API', 'false').lower() == 'true'
        
        self.api_client = FootballDataAPI(api_key=api_key, use_real_api=use_real_api)
        
        if self.api_client.use_real_api:
            print("✓ Real API enabled (API-Football)")
        else:
            print("ℹ️  Using simulated data (set USE_REAL_API=true in .env to use real API)")
        
        # For generating data when in manual mode
        self.data_generator = FootballDataGenerator()
    
    def get_yes_no(self, prompt: str) -> bool:
        """Get yes/no response from user"""
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def get_player_ratings(self, team_name: str, auto: bool = False) -> list:
        """Get player ratings for a team"""
        if auto:
            # Fetch from API (real or simulated)
            team_data = self.api_client.get_team_data(team_name)
            ratings = team_data['player_ratings']
            return ratings
        else:
            print(f"\nEnter player ratings for {team_name} (11 players, rated 50-99):")
            print("  You can enter them space-separated, or comma-separated")
            print("  Example: 85 88 82 90 87 84 86 83 89 85 91")
            
            while True:
                try:
                    ratings_input = input(f"  {team_name} ratings: ").strip()
                    # Handle both space and comma separation
                    ratings_input = ratings_input.replace(',', ' ')
                    ratings = [float(r) for r in ratings_input.split()]
                    
                    if len(ratings) != 11:
                        print(f"  ✗ Error: Need exactly 11 players, got {len(ratings)}")
                        continue
                    
                    if not all(50 <= r <= 99 for r in ratings):
                        print("  ✗ Error: All ratings must be between 50 and 99")
                        continue
                    
                    return ratings
                except ValueError:
                    print("  ✗ Error: Please enter valid numbers")
    
    def get_recent_form(self, team_name: str, auto: bool = False) -> list:
        """Get recent form for a team"""
        if auto:
            # Fetch from API (real or simulated)
            team_data = self.api_client.get_team_data(team_name)
            form = team_data['recent_form']
            return form
        else:
            print(f"\nEnter last 5 match results for {team_name}:")
            print("  Use: W (win), D (draw), L (loss)")
            print("  Example: W W D L W")
            
            while True:
                form_input = input(f"  {team_name} last 5: ").strip().upper()
                results = form_input.replace(',', ' ').split()
                
                if len(results) != 5:
                    print(f"  ✗ Error: Need exactly 5 results, got {len(results)}")
                    continue
                
                # Convert to numeric format
                try:
                    form = []
                    for r in results:
                        if r in ['W', 'WIN']:
                            form.append(3)
                        elif r in ['D', 'DRAW']:
                            form.append(1)
                        elif r in ['L', 'LOSS', 'LOSE']:
                            form.append(0)
                        else:
                            raise ValueError(f"Invalid result: {r}")
                    return form
                except ValueError as e:
                    print(f"  ✗ Error: {e}. Use only W, D, or L")
    
    def predict_single_match(self):
        """Interactive single match prediction"""
        print("\n" + "="*70)
        print("MATCH PREDICTION")
        print("="*70)
        
        # Get team names
        print("\nEnter the teams playing:")
        home_team = input("  Home team: ").strip()
        away_team = input("  Away team: ").strip()
        
        if not home_team or not away_team:
            print("✗ Team names cannot be empty")
            return
        
        print(f"\n📊 Match: {home_team} (Home) vs {away_team} (Away)")
        
        # Ask if user wants to enter data manually or auto-fetch
        print("\n" + "-"*70)
        auto_mode = self.get_yes_no("Would you like to auto-fetch team data? (simulated)")
        
        if auto_mode:
            print("\n🔄 Fetching team data...")
        
        # Get data for both teams
        home_ratings = self.get_player_ratings(home_team, auto_mode)
        home_form = self.get_recent_form(home_team, auto_mode)
        
        away_ratings = self.get_player_ratings(away_team, auto_mode)
        away_form = self.get_recent_form(away_team, auto_mode)
        
        # Make prediction
        print("\n" + "-"*70)
        print("🤖 Analyzing match data and making prediction...")
        print("-"*70)
        
        prediction = self.agent.predict_match_detailed(
            home_team_name=home_team,
            away_team_name=away_team,
            home_team_players=home_ratings,
            away_team_players=away_ratings,
            home_last_5_results=home_form,
            away_last_5_results=away_form
        )
        
        print(prediction)
        
        # Additional insights
        self._show_additional_insights(home_team, away_team, prediction)
    
    def _show_additional_insights(self, home_team: str, away_team: str, prediction: dict):
        """Show additional prediction insights"""
        print("\n" + "="*70)
        print("BETTING INSIGHTS")
        print("="*70)
        
        total_goals = prediction['home_score'] + prediction['away_score']
        
        print(f"\n📈 Prediction Summary:")
        print(f"  • Winner: {prediction['result']}")
        print(f"  • Total Goals: {total_goals}")
        print(f"  • Goal Difference: {abs(prediction['home_score'] - prediction['away_score'])}")
        
        print(f"\n🎯 Betting Suggestions:")
        if prediction['result'] == 'Home Win':
            print(f"  • 1X2: Home Win ({home_team})")
        elif prediction['result'] == 'Away Win':
            print(f"  • 1X2: Away Win ({away_team})")
        else:
            print(f"  • 1X2: Draw")
        
        if total_goals > 2.5:
            print(f"  • Over/Under: Over 2.5 goals")
        else:
            print(f"  • Over/Under: Under 2.5 goals")
        
        if prediction['home_score'] > 0 and prediction['away_score'] > 0:
            print(f"  • Both Teams to Score: Yes")
        else:
            print(f"  • Both Teams to Score: No")
        
        print(f"\n⚠️  Note: This is a prediction model. Actual results may vary!")
        print("="*70)
    
    def predict_multiple_matches(self):
        """Predict multiple matches in batch"""
        print("\n" + "="*70)
        print("BATCH MATCH PREDICTION")
        print("="*70)
        
        num_matches = 0
        while True:
            try:
                num_matches = int(input("\nHow many matches would you like to predict? "))
                if num_matches > 0:
                    break
                else:
                    print("Please enter a positive number")
            except ValueError:
                print("Please enter a valid number")
        
        matches = []
        for i in range(num_matches):
            print(f"\n--- Match {i+1} of {num_matches} ---")
            
            home_team = input(f"  Home team: ").strip()
            away_team = input(f"  Away team: ").strip()
            
            auto_mode = self.get_yes_no("  Auto-fetch data?")
            
            if auto_mode:
                print(f"  🔄 Fetching data for {home_team} vs {away_team}...")
            
            home_ratings = self.get_player_ratings(home_team, auto_mode)
            home_form = self.get_recent_form(home_team, auto_mode)
            away_ratings = self.get_player_ratings(away_team, auto_mode)
            away_form = self.get_recent_form(away_team, auto_mode)
            
            matches.append({
                'match_id': f'M{i+1:03d}',
                'home_team': home_team,
                'away_team': away_team,
                'home_team_players': home_ratings,
                'away_team_players': away_ratings,
                'home_last_5_results': home_form,
                'away_last_5_results': away_form
            })
        
        # Make predictions
        print("\n" + "="*70)
        print("🤖 Making predictions for all matches...")
        print("="*70)
        
        predictions = self.agent.batch_predict(matches)
        
        # Display results
        print("\n" + "="*70)
        print("PREDICTION RESULTS")
        print("="*70)
        print()
        
        for i, (match, pred) in enumerate(zip(matches, predictions)):
            result_emoji = "🏆" if pred['result'] == 'Home Win' else "🤝" if pred['result'] == 'Draw' else "✈️"
            print(f"{i+1}. {match['home_team']} vs {match['away_team']}")
            print(f"   {result_emoji} Predicted: {pred['home_score']}-{pred['away_score']} ({pred['result']})")
            print(f"   Strength: {pred['home_team_strength']:.1f} vs {pred['away_team_strength']:.1f}")
            print(f"   Form: {pred['home_form_points']} pts vs {pred['away_form_points']} pts")
            print()
        
        print("="*70)
    
    def run(self):
        """Main interactive loop"""
        while True:
            print("\n" + "="*70)
            print("MAIN MENU")
            print("="*70)
            print("\n1. Predict a single match")
            print("2. Predict multiple matches")
            print("3. View model information")
            print("4. Exit")
            
            choice = input("\nSelect an option (1-4): ").strip()
            
            if choice == '1':
                self.predict_single_match()
                
                # Ask if user wants to predict another
                if not self.get_yes_no("\nPredict another match?"):
                    continue
            
            elif choice == '2':
                self.predict_multiple_matches()
            
            elif choice == '3':
                self.show_model_info()
            
            elif choice == '4':
                print("\n👋 Thanks for using Football Predictor!")
                print("="*70)
                sys.exit(0)
            
            else:
                print("Invalid option. Please select 1-4.")
    
    def show_model_info(self):
        """Display model information"""
        print("\n" + "="*70)
        print("MODEL INFORMATION")
        print("="*70)
        
        info = self.agent.get_model_info()
        
        print(f"\nStatus: {info['status']}")
        print(f"Model Type: {info['model_type']}")
        print(f"Number of Features: {info['features_count']}")
        
        if 'metrics' in info and info['metrics']:
            print("\nPerformance Metrics:")
            metrics = info['metrics']
            print(f"  • Winner Prediction Accuracy: {metrics.get('winner_accuracy', 0)*100:.1f}%")
            print(f"  • Average Goal Error (MAE): {metrics.get('mae', 0):.2f} goals")
            print(f"  • Exact Score Accuracy: {metrics.get('exact_match_accuracy', 0)*100:.1f}%")
        
        print("\n" + "="*70)


def main():
    """Main entry point"""
    try:
        predictor = InteractivePredictor()
        predictor.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

