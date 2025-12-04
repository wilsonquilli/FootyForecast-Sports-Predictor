"""
Historical Data Fetcher for Training
Fetches real historical match data from API-Football for model training
"""

import requests
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class HistoricalDataFetcher:
    """Fetches historical match data for training"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the historical data fetcher"""
        self.api_key = api_key or os.getenv('FOOTBALL_API_KEY')
        self.api_host = os.getenv('FOOTBALL_API_HOST', 'v3.football.api-sports.io')
        self.base_url = f"https://{self.api_host}"
        
        if not self.api_key:
            raise ValueError("API key required. Set FOOTBALL_API_KEY in .env file")
        
        self.headers = {
            'x-rapidapi-host': self.api_host,
            'x-rapidapi-key': self.api_key
        }
        
        # Rate limiting: free tier is 100 requests/day
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _make_request(self, url: str, params: Dict) -> Dict:
        """Make API request with rate limiting"""
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 429:
                print("⚠️  Rate limit exceeded. Please wait or upgrade your API plan.")
                return {}
            
            if response.status_code != 200:
                print(f"⚠️  API Error {response.status_code}")
                return {}
            
            return response.json()
        except Exception as e:
            print(f"⚠️  Request error: {e}")
            return {}
    
    def get_league_fixtures(self, league_id: int, season: int, limit: int = 100) -> List[Dict]:
        """
        Get historical fixtures from a league
        
        Args:
            league_id: League ID (39=Premier League, 140=La Liga, etc.)
            season: Season year (e.g., 2023) - may be ignored for free tier
            limit: Maximum number of fixtures to fetch
            
        Returns:
            List of fixture dictionaries
        """
        print(f"📥 Fetching fixtures for league {league_id}...")
        
        # For free tier, we can only access recent dates (last 3 days)
        # Fetch all fixtures from available dates, then filter by league
        from datetime import datetime, timedelta
        
        all_fixtures = []
        today = datetime.now()
        
        # Try last 3 days (free tier limit)
        for days_ago in range(3):
            date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            url = f"{self.base_url}/fixtures"
            # Don't filter by league in params - get all matches then filter
            params = {
                'date': date,
                'status': 'FT'
            }
            
            data = self._make_request(url, params)
            errors = data.get('errors', {})
            
            if errors:
                # Check if it's a date restriction error
                error_msg = str(errors)
                if 'Free plans do not have access' in error_msg:
                    continue  # Skip this date
            
            fixtures = data.get('response', [])
            
            # Filter by league
            for fixture in fixtures:
                league_info = fixture.get('league', {})
                if league_info.get('id') == league_id:
                    all_fixtures.append(fixture)
            
            if len(all_fixtures) >= limit:
                break
        
        if not all_fixtures:
            # Fallback: try with league filter directly (may not work on free tier)
            url = f"{self.base_url}/fixtures"
            params = {
                'league': league_id,
                'season': season,
                'status': 'FT'
            }
            data = self._make_request(url, params)
            all_fixtures = data.get('response', [])
        
        if not all_fixtures:
            print(f"⚠️  No fixtures found for league {league_id}")
            print("   Note: Free tier only allows access to last 3 days of matches")
            return []
        
        # Limit results
        all_fixtures = all_fixtures[:limit]
        print(f"✓ Found {len(all_fixtures)} finished matches")
        
        return all_fixtures
    
    def get_team_statistics_at_date(self, team_id: int, league_id: int, 
                                   season: int, date: str) -> Dict:
        """
        Get team statistics up to a specific date
        
        Args:
            team_id: Team ID
            league_id: League ID
            season: Season year
            date: Date string (YYYY-MM-DD)
            
        Returns:
            Team statistics dictionary
        """
        # For simplicity, we'll use season statistics
        # In a full implementation, you'd fetch statistics up to the specific date
        url = f"{self.base_url}/teams/statistics"
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        data = self._make_request(url, params)
        return data.get('response', {})
    
    def get_team_recent_form(self, team_id: int, before_date: str, limit: int = 5) -> List[int]:
        """
        Get team's recent form (last N matches) before a specific date
        
        Args:
            team_id: Team ID
            before_date: Date string (YYYY-MM-DD) - get matches before this date
            limit: Number of recent matches to get
            
        Returns:
            List of results (3=win, 1=draw, 0=loss)
        """
        url = f"{self.base_url}/fixtures"
        params = {
            'team': team_id,
            'last': limit,
            'status': 'FT'
        }
        
        data = self._make_request(url, params)
        fixtures = data.get('response', [])
        
        form = []
        for fixture in fixtures:
            # Check if match is before the target date
            fixture_date = fixture.get('fixture', {}).get('date', '')
            if fixture_date and fixture_date > before_date:
                continue
            
            teams = fixture.get('teams', {})
            goals = fixture.get('goals', {})
            
            home_team_id = teams.get('home', {}).get('id')
            home_goals = goals.get('home') or 0
            away_goals = goals.get('away') or 0
            
            is_home = (home_team_id == team_id)
            
            if is_home:
                if home_goals > away_goals:
                    form.append(3)  # Win
                elif home_goals == away_goals:
                    form.append(1)  # Draw
                else:
                    form.append(0)  # Loss
            else:
                if away_goals > home_goals:
                    form.append(3)  # Win
                elif away_goals == home_goals:
                    form.append(1)  # Draw
                else:
                    form.append(0)  # Loss
        
        # Ensure exactly 5 results (pad with draws if needed)
        while len(form) < 5:
            form.insert(0, 1)
        
        return form[:5]
    
    def convert_stats_to_ratings(self, stats: Dict) -> List[float]:
        """
        Convert team statistics to player ratings
        
        Args:
            stats: Team statistics dictionary
            
        Returns:
            List of 11 player ratings
        """
        if not stats:
            # Default moderate ratings
            return np.random.normal(75, 8, 11).clip(50, 99).tolist()
        
        # Extract performance metrics
        fixtures = stats.get('fixtures', {})
        goals = stats.get('goals', {})
        
        wins = fixtures.get('wins', {}).get('total', 0) or 0
        draws = fixtures.get('draws', {}).get('total', 0) or 0
        losses = fixtures.get('losses', {}).get('total', 0) or 0
        total_matches = wins + draws + losses
        
        if total_matches > 0:
            win_rate = wins / total_matches
        else:
            win_rate = 0.4
        
        goals_for = goals.get('for', {}).get('total', {}).get('total', 0) or 0
        goals_against = goals.get('against', {}).get('total', {}).get('total', 0) or 0
        
        if total_matches > 0:
            avg_goals_for = goals_for / total_matches
            avg_goals_against = goals_against / total_matches
        else:
            avg_goals_for = 1.5
            avg_goals_against = 1.0
        
        # Calculate base rating (60-95 range)
        base_rating = 60 + (win_rate * 20) + (avg_goals_for * 5) - (avg_goals_against * 3)
        base_rating = max(60, min(92, base_rating))
        
        # Generate 11 player ratings around this base
        ratings = np.random.normal(base_rating, 6, 11)
        ratings = np.clip(ratings, 50, 99)
        
        return ratings.tolist()
    
    def fetch_training_data(self, league_ids: List[int], season: int, 
                           max_matches: int = 500) -> pd.DataFrame:
        """
        Fetch historical match data for training
        
        Args:
            league_ids: List of league IDs to fetch from
            season: Season year
            max_matches: Maximum number of matches to fetch
            
        Returns:
            DataFrame with training data in same format as synthetic data
        """
        print(f"\n{'='*70}")
        print(f"FETCHING HISTORICAL TRAINING DATA")
        print(f"{'='*70}")
        print(f"Leagues: {league_ids}")
        print(f"Season: {season}")
        print(f"Max matches: {max_matches}")
        print(f"{'='*70}\n")
        
        all_matches = []
        
        for league_id in league_ids:
            fixtures = self.get_league_fixtures(league_id, season, limit=max_matches // len(league_ids))
            
            for fixture in fixtures:
                try:
                    fixture_data = fixture.get('fixture', {})
                    teams_data = fixture.get('teams', {})
                    goals_data = fixture.get('goals', {})
                    
                    # Extract match info
                    home_team = teams_data.get('home', {})
                    away_team = teams_data.get('away', {})
                    home_team_id = home_team.get('id')
                    away_team_id = away_team.get('id')
                    home_goals = goals_data.get('home') or 0
                    away_goals = goals_data.get('away') or 0
                    match_date = fixture_data.get('date', '')
                    
                    if not all([home_team_id, away_team_id, match_date]):
                        continue
                    
                    # Get team statistics (season stats)
                    print(f"  Processing: {home_team.get('name')} vs {away_team.get('name')} ({home_goals}-{away_goals})")
                    
                    home_stats = self.get_team_statistics_at_date(home_team_id, league_id, season, match_date)
                    away_stats = self.get_team_statistics_at_date(away_team_id, league_id, season, match_date)
                    
                    # Get recent form (before match date)
                    home_form = self.get_team_recent_form(home_team_id, match_date, limit=5)
                    away_form = self.get_team_recent_form(away_team_id, match_date, limit=5)
                    
                    # Convert stats to ratings
                    home_ratings = self.convert_stats_to_ratings(home_stats)
                    away_ratings = self.convert_stats_to_ratings(away_stats)
                    
                    # Create match data in same format as synthetic data
                    match_data = {
                        # Home team player ratings
                        **{f'home_player_{i+1}_rating': home_ratings[i] for i in range(11)},
                        # Away team player ratings
                        **{f'away_player_{i+1}_rating': away_ratings[i] for i in range(11)},
                        # Home team recent form
                        **{f'home_match_{i+1}_result': home_form[i] for i in range(5)},
                        # Away team recent form
                        **{f'away_match_{i+1}_result': away_form[i] for i in range(5)},
                        # Target variables (actual match results)
                        'home_goals': home_goals,
                        'away_goals': away_goals
                    }
                    
                    all_matches.append(match_data)
                    
                    # Progress update
                    if len(all_matches) % 10 == 0:
                        print(f"  ✓ Processed {len(all_matches)} matches...")
                    
                    # Rate limiting check
                    if len(all_matches) >= max_matches:
                        break
                        
                except Exception as e:
                    print(f"  ⚠️  Error processing match: {e}")
                    continue
            
            if len(all_matches) >= max_matches:
                break
        
        print(f"\n✓ Successfully fetched {len(all_matches)} historical matches")
        
        return pd.DataFrame(all_matches)


def main():
    """Example usage"""
    import sys
    
    # Check for API key
    api_key = os.getenv('FOOTBALL_API_KEY')
    if not api_key:
        print("⚠️  Error: FOOTBALL_API_KEY not found in environment")
        print("   Please set it in .env file or export it")
        print("\n   Example:")
        print("   export FOOTBALL_API_KEY='your_key_here'")
        sys.exit(1)
    
    fetcher = HistoricalDataFetcher(api_key=api_key)
    
    # Major European leagues
    # 39 = Premier League, 140 = La Liga, 78 = Bundesliga, 135 = Serie A, 61 = Ligue 1
    league_ids = [39, 140, 78]  # Start with top 3 leagues
    season = 2023  # Last completed season
    
    print("\n⚠️  Note: This will make many API calls!")
    print(f"   Free tier: 100 requests/day")
    print(f"   Each match uses ~4-5 requests")
    print(f"   Estimated: ~20-25 matches max on free tier\n")
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Fetch data (limited to avoid rate limits)
    max_matches = 20  # Conservative for free tier
    
    df = fetcher.fetch_training_data(league_ids, season, max_matches=max_matches)
    
    if len(df) > 0:
        # Save to CSV
        output_file = 'historical_training_data.csv'
        df.to_csv(output_file, index=False)
        print(f"\n✓ Saved {len(df)} matches to {output_file}")
        print(f"\nData shape: {df.shape}")
        print(f"\nFirst few rows:")
        print(df.head())
    else:
        print("\n⚠️  No data fetched. Check API key and rate limits.")


if __name__ == "__main__":
    main()

