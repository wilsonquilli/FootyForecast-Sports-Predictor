"""
Accumulate Training Data Over Time
Runs daily to collect matches from all top leagues and build a dataset
"""

import os
import pandas as pd
from datetime import datetime
from historical_data_fetcher import HistoricalDataFetcher
from dotenv import load_dotenv

load_dotenv()


def accumulate_data(days_to_collect: int = 30):
    """
    Collect matches over multiple days to build a training dataset
    
    Args:
        days_to_collect: Number of days to collect data (free tier = 3 days at a time)
    """
    api_key = os.getenv('FOOTBALL_API_KEY')
    if not api_key:
        print("⚠️  Error: FOOTBALL_API_KEY not found in .env file")
        return
    
    # All leagues: Top 5 + Champions League + Europa League
    league_ids = [39, 140, 78, 135, 61, 2, 3]
    league_names = {
        39: "Premier League",
        140: "La Liga",
        78: "Bundesliga",
        135: "Serie A",
        61: "Ligue 1",
        2: "Champions League",
        3: "Europa League"
    }
    
    print("="*70)
    print("ACCUMULATING TRAINING DATA")
    print("="*70)
    print(f"\nTarget Leagues:")
    for lid in league_ids:
        print(f"  • {league_names.get(lid, f'League {lid}')}")
    
    fetcher = HistoricalDataFetcher(api_key=api_key)
    
    # Load existing data if it exists
    csv_file = 'accumulated_training_data.csv'
    existing_data = pd.DataFrame()
    
    if os.path.exists(csv_file):
        existing_data = pd.read_csv(csv_file)
        print(f"\n✓ Found existing data: {len(existing_data)} matches")
    else:
        print(f"\n📝 Starting fresh dataset")
    
    # Fetch new data (last 3 days available on free tier)
    print(f"\n📥 Fetching matches from available dates...")
    
    all_new_matches = []
    for league_id in league_ids:
        fixtures = fetcher.get_league_fixtures(league_id, 2024, limit=100)
        
        for fixture in fixtures:
            try:
                fixture_data = fixture.get('fixture', {})
                teams_data = fixture.get('teams', {})
                goals_data = fixture.get('goals', {})
                
                home_team_id = teams_data.get('home', {}).get('id')
                away_team_id = teams_data.get('away', {}).get('id')
                home_goals = goals_data.get('home') or 0
                away_goals = goals_data.get('away') or 0
                match_date = fixture_data.get('date', '')
                
                if not all([home_team_id, away_team_id, match_date]):
                    continue
                
                # Check if match already exists
                match_id = f"{home_team_id}_{away_team_id}_{match_date}"
                if not existing_data.empty:
                    # Simple check - in production, use proper match ID
                    if len(existing_data[
                        (existing_data['home_goals'] == home_goals) & 
                        (existing_data['away_goals'] == away_goals)
                    ]) > 0:
                        continue  # Skip duplicates
                
                # Get team statistics
                league_info = fixture.get('league', {})
                league_id_actual = league_info.get('id')
                
                home_stats = fetcher.get_team_statistics_at_date(home_team_id, league_id_actual, 2024, match_date)
                away_stats = fetcher.get_team_statistics_at_date(away_team_id, league_id_actual, 2024, match_date)
                
                # Get recent form
                home_form = fetcher.get_team_recent_form(home_team_id, match_date, limit=5)
                away_form = fetcher.get_team_recent_form(away_team_id, match_date, limit=5)
                
                # Convert stats to ratings
                home_ratings = fetcher.convert_stats_to_ratings(home_stats)
                away_ratings = fetcher.convert_stats_to_ratings(away_stats)
                
                # Create match data
                match_data = {
                    **{f'home_player_{i+1}_rating': home_ratings[i] for i in range(11)},
                    **{f'away_player_{i+1}_rating': away_ratings[i] for i in range(11)},
                    **{f'home_match_{i+1}_result': home_form[i] for i in range(5)},
                    **{f'away_match_{i+1}_result': away_form[i] for i in range(5)},
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'match_date': match_date,
                    'league_id': league_id_actual
                }
                
                all_new_matches.append(match_data)
                
            except Exception as e:
                print(f"  ⚠️  Error processing match: {e}")
                continue
    
    if not all_new_matches:
        print("\n⚠️  No new matches found today")
        if not existing_data.empty:
            print(f"   Current dataset: {len(existing_data)} matches")
        return
    
    # Combine with existing data
    new_df = pd.DataFrame(all_new_matches)
    
    if not existing_data.empty:
        # Remove duplicates
        combined = pd.concat([existing_data, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=['home_goals', 'away_goals', 'match_date'], keep='first')
    else:
        combined = new_df
    
    # Save
    combined.to_csv(csv_file, index=False)
    
    print(f"\n✓ Added {len(new_df)} new matches")
    print(f"✓ Total matches in dataset: {len(combined)}")
    print(f"✓ Saved to {csv_file}")
    
    # Show breakdown by league
    if 'league_id' in combined.columns:
        print(f"\n📊 Matches by League:")
        league_counts = combined['league_id'].value_counts()
        for lid, count in league_counts.items():
            print(f"   {league_names.get(lid, f'League {lid}')}: {count} matches")
    
    return combined


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DAILY DATA ACCUMULATION")
    print("="*70)
    print("\nThis script collects matches from the last 3 days (free tier limit)")
    print("Run this daily to build a training dataset over time.\n")
    
    data = accumulate_data()
    
    if data is not None and len(data) > 0:
        print(f"\n💡 Next Steps:")
        print(f"   1. Run this script daily to collect more matches")
        print(f"   2. When you have 100+ matches, train the model:")
        print(f"      python train_from_csv.py accumulated_training_data.csv")
        print(f"   3. For full seasons, consider upgrading API plan")

