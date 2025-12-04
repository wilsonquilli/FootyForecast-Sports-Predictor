"""
API Integration Module for Football Data
This module provides integration with real football data APIs

Supports:
- API-Football via RapidAPI (IMPLEMENTED)
- Simulated data fallback (for testing)
"""

import requests
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from data_generator import FootballDataGenerator

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables only.")


class FootballDataAPI:
    """
    Football data API integration
    
    This is a framework that can be extended to use real APIs.
    Currently uses simulated data as a placeholder.
    """
    
    def __init__(self, api_key: Optional[str] = None, use_real_api: bool = False):
        """
        Initialize the API client
        
        Args:
            api_key: API key for the football data service (RapidAPI key)
            use_real_api: If True, use real API; if False, use simulated data
        """
        # Load from environment if not provided
        self.api_key = api_key or os.getenv('FOOTBALL_API_KEY')
        self.api_host = os.getenv('FOOTBALL_API_HOST', 'v3.football.api-sports.io')
        
        # Check environment variable override
        env_use_real = os.getenv('USE_REAL_API', 'false').lower() == 'true'
        self.use_real_api = use_real_api or env_use_real
        
        self.data_generator = FootballDataGenerator()
        
        # API endpoints
        self.base_url = f"https://{self.api_host}"
        
        # Cache for API responses to avoid repeated calls
        self.cache = {}
        
        if self.use_real_api and not self.api_key:
            print("\n⚠️  Warning: Real API enabled but no API key found!")
            print("   Set FOOTBALL_API_KEY in .env file or pass api_key parameter")
            print("   Falling back to simulated data...\n")
            self.use_real_api = False
        
    def get_team_data(self, team_name: str) -> Dict:
        """
        Get team data including player ratings and recent form
        
        Args:
            team_name: Name of the team
            
        Returns:
            Dictionary with team data
        """
        if self.use_real_api:
            return self._fetch_real_team_data(team_name)
        else:
            return self._simulate_team_data(team_name)
    
    def _fetch_real_team_data(self, team_name: str) -> Dict:
        """
        Fetch real team data from API-Football (via RapidAPI)
        
        Args:
            team_name: Name of the team
            
        Returns:
            Dictionary with team data
        """
        # Check cache first
        cache_key = f"team_{team_name.lower()}"
        if cache_key in self.cache:
            print(f"  ℹ️  Using cached data for {team_name}")
            return self.cache[cache_key]
        
        headers = {
            'x-rapidapi-host': self.api_host,
            'x-rapidapi-key': self.api_key
        }
        
        try:
            # 1. Search for team
            print(f"  🔍 Searching for team: {team_name}...")
            search_url = f"{self.base_url}/teams"
            params = {'name': team_name}
            
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 429:
                print("  ⚠️  Rate limit exceeded. Using simulated data.")
                return self._simulate_team_data(team_name)
            
            if response.status_code != 200:
                print(f"  ⚠️  API Error {response.status_code}. Using simulated data.")
                return self._simulate_team_data(team_name)
            
            data = response.json()
            teams = data.get('response', [])
            
            if not teams:
                print(f"  ⚠️  Team '{team_name}' not found. Using simulated data.")
                return self._simulate_team_data(team_name)
            
            # Get the first match (usually the most relevant)
            team_info = teams[0]['team']
            team_id = team_info['id']
            team_name_official = team_info['name']
            
            print(f"  ✓ Found: {team_name_official} (ID: {team_id})")
            
            # 2. Get team statistics for current season
            print(f"  📊 Fetching team statistics...")
            current_year = datetime.now().year
            stats_url = f"{self.base_url}/teams/statistics"
            
            # Try current season, fallback to previous if needed
            season = current_year if datetime.now().month >= 7 else current_year - 1
            
            # Get team's league (try common leagues)
            league_id = self._get_team_league(team_id, season, headers)
            
            stats_params = {
                'team': team_id,
                'season': season,
                'league': league_id
            }
            
            stats_response = requests.get(stats_url, headers=headers, params=stats_params, timeout=10)
            stats_data = stats_response.json() if stats_response.status_code == 200 else {}
            
            # 3. Get recent fixtures
            print(f"  📅 Fetching recent matches...")
            fixtures_url = f"{self.base_url}/fixtures"
            fixtures_params = {
                'team': team_id,
                'last': 5
            }
            
            fixtures_response = requests.get(fixtures_url, headers=headers, params=fixtures_params, timeout=10)
            fixtures_data = fixtures_response.json() if fixtures_response.status_code == 200 else {}
            
            # Process the data
            player_ratings = self._convert_stats_to_ratings(stats_data, team_name_official)
            recent_form = self._extract_form_from_fixtures(fixtures_data, team_id)
            
            result = {
                'team_name': team_name_official,
                'player_ratings': player_ratings,
                'recent_form': recent_form,
                'team_id': team_id,
                'source': 'api-football'
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            print(f"  ✓ Data fetched successfully!")
            return result
            
        except requests.exceptions.Timeout:
            print(f"  ⚠️  API timeout. Using simulated data.")
            return self._simulate_team_data(team_name)
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Network error: {e}. Using simulated data.")
            return self._simulate_team_data(team_name)
        except Exception as e:
            print(f"  ⚠️  Unexpected error: {e}. Using simulated data.")
            return self._simulate_team_data(team_name)
    
    def _get_team_league(self, team_id: int, season: int, headers: dict) -> int:
        """Get the league ID for a team"""
        # Common league IDs
        major_leagues = {
            39: "Premier League",
            140: "La Liga", 
            78: "Bundesliga",
            135: "Serie A",
            61: "Ligue 1",
            2: "UEFA Champions League"
        }
        
        # Try to get team info to find their league
        try:
            url = f"{self.base_url}/teams"
            params = {'id': team_id}
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                # For simplicity, return Premier League as default
                # In production, you'd determine this from team's actual league
                return 39  # Premier League
        except:
            pass
        
        return 39  # Default to Premier League
    
    def _convert_stats_to_ratings(self, stats_data: Dict, team_name: str) -> List[float]:
        """
        Convert team statistics to player ratings
        
        Args:
            stats_data: Statistics data from API
            team_name: Name of the team
            
        Returns:
            List of 11 player ratings
        """
        import numpy as np
        
        response = stats_data.get('response', {})
        
        if not response:
            # No stats available, use moderate ratings
            print(f"  ℹ️  No statistics available, using estimated ratings")
            return self.data_generator.generate_player_ratings(mean_rating=75).tolist()
        
        # Extract key metrics
        fixtures = response.get('fixtures', {})
        goals = response.get('goals', {})
        
        # Calculate performance score
        wins = fixtures.get('wins', {}).get('total', 0) or 0
        draws = fixtures.get('draws', {}).get('total', 0) or 0
        losses = fixtures.get('losses', {}).get('total', 0) or 0
        total_matches = wins + draws + losses
        
        if total_matches > 0:
            win_rate = wins / total_matches
        else:
            win_rate = 0.4  # Default
        
        # Goals scoring
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
        
        print(f"  📈 Calculated team strength: {base_rating:.1f}/100")
        
        # Generate 11 player ratings around this base
        ratings = np.random.normal(base_rating, 6, 11)
        ratings = np.clip(ratings, 50, 99)
        
        return ratings.tolist()
    
    def _simulate_team_data(self, team_name: str) -> Dict:
        """
        Simulate team data (for testing without API)
        
        Args:
            team_name: Name of the team
            
        Returns:
            Dictionary with simulated team data
        """
        # Generate realistic ratings based on team name patterns
        # (in real implementation, this would fetch from API)
        
        # Simple heuristic: "better" sounding teams get higher ratings
        top_teams = ['manchester', 'barcelona', 'real madrid', 'bayern', 'liverpool', 
                     'city', 'united', 'juventus', 'psg', 'chelsea', 'arsenal']
        
        base_rating = 75
        if any(top in team_name.lower() for top in top_teams):
            base_rating = 85
        
        player_ratings = self.data_generator.generate_player_ratings(
            mean_rating=base_rating,
            std_rating=8
        ).tolist()
        
        recent_form = self.data_generator.generate_recent_form()
        
        return {
            'team_name': team_name,
            'player_ratings': player_ratings,
            'recent_form': recent_form,
            'source': 'simulated'
        }
    
    def get_match_data(self, home_team: str, away_team: str) -> Tuple[Dict, Dict]:
        """
        Get data for both teams in a match
        
        Args:
            home_team: Home team name
            away_team: Away team name
            
        Returns:
            Tuple of (home_team_data, away_team_data)
        """
        print(f"📥 Fetching data for {home_team}...")
        home_data = self.get_team_data(home_team)
        
        print(f"📥 Fetching data for {away_team}...")
        away_data = self.get_team_data(away_team)
        
        return home_data, away_data
    
    def _extract_player_ratings(self, squad_data: Dict) -> List[float]:
        """
        Extract player ratings from squad data
        
        In a real implementation, you might:
        - Use player market values
        - Use player performance stats
        - Use FIFA/PES ratings
        - Calculate custom ratings from stats
        """
        # Placeholder implementation
        players = squad_data.get('squad', [])[:11]
        ratings = []
        
        for player in players:
            # Example: convert market value to rating
            # market_value = player.get('marketValue', 1000000)
            # rating = min(99, 50 + (market_value / 1000000) * 5)
            rating = 75  # Default
            ratings.append(rating)
        
        # Ensure we have exactly 11 players
        while len(ratings) < 11:
            ratings.append(70)
        
        return ratings[:11]
    
    def _extract_form_from_fixtures(self, fixtures_data: Dict, team_id: int) -> List[int]:
        """
        Extract recent form from fixture results
        
        Args:
            fixtures_data: Recent fixtures data from API
            team_id: ID of the team
            
        Returns:
            List of results (3=win, 1=draw, 0=loss)
        """
        fixtures = fixtures_data.get('response', [])
        
        if not fixtures:
            print(f"  ℹ️  No recent fixtures found, using default form")
            return [1, 1, 1, 1, 1]  # Default to draws
        
        form = []
        form_display = []
        
        for fixture in fixtures[-5:]:  # Last 5 matches
            # Check if match is finished
            status = fixture.get('fixture', {}).get('status', {}).get('short', '')
            if status not in ['FT', 'AET', 'PEN']:  # Only count finished matches
                continue
                
            teams = fixture.get('teams', {})
            goals = fixture.get('goals', {})
            
            home_team_id = teams.get('home', {}).get('id')
            home_goals = goals.get('home') or 0
            away_goals = goals.get('away') or 0
            
            is_home = (home_team_id == team_id)
            
            if is_home:
                if home_goals > away_goals:
                    form.append(3)
                    form_display.append('W')
                elif home_goals == away_goals:
                    form.append(1)
                    form_display.append('D')
                else:
                    form.append(0)
                    form_display.append('L')
            else:
                if away_goals > home_goals:
                    form.append(3)
                    form_display.append('W')
                elif away_goals == home_goals:
                    form.append(1)
                    form_display.append('D')
                else:
                    form.append(0)
                    form_display.append('L')
        
        # Ensure exactly 5 results
        while len(form) < 5:
            form.insert(0, 1)  # Add draws at the beginning (older matches)
            form_display.insert(0, 'D')
        
        form = form[-5:]  # Take only last 5
        form_display = form_display[-5:]
        
        print(f"  📋 Recent form: {' '.join(form_display)} ({sum(form)} pts)")
        
        return form


# Example usage and configuration guide
if __name__ == "__main__":
    print("="*70)
    print("FOOTBALL DATA API INTEGRATION")
    print("="*70)
    print("\nThis module provides integration with football data APIs.")
    print("\nCurrently configured for SIMULATED data.")
    print("\nTo use real APIs, you need to:")
    print("  1. Sign up for a football data API service:")
    print("     - API-Football: https://www.api-football.com/")
    print("     - Football-Data.org: https://www.football-data.org/")
    print("     - RapidAPI Football: https://rapidapi.com/")
    print("\n  2. Get your API key")
    print("\n  3. Implement the _fetch_real_team_data() method")
    print("\n  4. Set use_real_api=True when creating FootballDataAPI")
    print("\n" + "="*70)
    
    # Example with simulated data
    api = FootballDataAPI(use_real_api=False)
    
    print("\nExample: Fetching simulated data...")
    home_data, away_data = api.get_match_data("Manchester City", "Liverpool")
    
    print(f"\n{home_data['team_name']}:")
    print(f"  Average Rating: {sum(home_data['player_ratings'])/len(home_data['player_ratings']):.1f}")
    print(f"  Recent Form: {home_data['recent_form']}")
    
    print(f"\n{away_data['team_name']}:")
    print(f"  Average Rating: {sum(away_data['player_ratings'])/len(away_data['player_ratings']):.1f}")
    print(f"  Recent Form: {away_data['recent_form']}")

