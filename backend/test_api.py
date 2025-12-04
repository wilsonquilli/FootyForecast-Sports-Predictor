"""
Test API Integration
Quick script to test if your API connection is working
"""

from api_integration import FootballDataAPI
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed")

def test_api():
    """Test the API integration"""
    print("="*70)
    print("API INTEGRATION TEST")
    print("="*70)
    
    # Check environment variables
    api_key = os.getenv('FOOTBALL_API_KEY')
    use_real_api = os.getenv('USE_REAL_API', 'false').lower() == 'true'
    
    print(f"\n📋 Configuration:")
    print(f"  API Key: {'✓ Set' if api_key and api_key != 'your_rapidapi_key_here' else '✗ Not set'}")
    print(f"  USE_REAL_API: {use_real_api}")
    
    # Initialize API client
    api = FootballDataAPI()
    
    if api.use_real_api:
        print(f"\n🌐 Testing REAL API connection...")
        print(f"  Endpoint: {api.base_url}")
        
        # Test with a well-known team
        test_team = "Manchester City"
        print(f"\n🔍 Fetching data for: {test_team}")
        print("-"*70)
        
        try:
            team_data = api.get_team_data(test_team)
            
            print(f"\n✅ SUCCESS! API is working!")
            print(f"\n📊 Results:")
            print(f"  Team: {team_data['team_name']}")
            print(f"  Team ID: {team_data.get('team_id', 'N/A')}")
            print(f"  Average Rating: {sum(team_data['player_ratings'])/len(team_data['player_ratings']):.1f}")
            
            form_str = ' '.join(['W' if r == 3 else 'D' if r == 1 else 'L' for r in team_data['recent_form']])
            print(f"  Recent Form: {form_str} ({sum(team_data['recent_form'])} pts)")
            print(f"  Data Source: {team_data.get('source', 'unknown')}")
            
            print(f"\n🎉 Your API integration is working perfectly!")
            print(f"   You can now use real data in the interactive predictor.")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            print(f"\nPossible issues:")
            print(f"  1. API key is invalid or expired")
            print(f"  2. Rate limit exceeded (100 requests/day on free tier)")
            print(f"  3. Network connection issues")
            print(f"  4. API service is down")
            print(f"\nThe system will fall back to simulated data.")
    
    else:
        print(f"\n📝 Using SIMULATED data (testing mode)")
        print(f"  This is perfect for testing the system without using API calls!")
        
        # Test with simulated data
        test_team = "Test Team"
        print(f"\n🔍 Generating simulated data for: {test_team}")
        print("-"*70)
        
        team_data = api.get_team_data(test_team)
        
        print(f"\n✅ Simulated data generated successfully!")
        print(f"\n📊 Results:")
        print(f"  Team: {team_data['team_name']}")
        print(f"  Average Rating: {sum(team_data['player_ratings'])/len(team_data['player_ratings']):.1f}")
        
        form_str = ' '.join(['W' if r == 3 else 'D' if r == 1 else 'L' for r in team_data['recent_form']])
        print(f"  Recent Form: {form_str} ({sum(team_data['recent_form'])} pts)")
        print(f"  Data Source: {team_data.get('source', 'unknown')}")
        
        print(f"\n💡 To use real API data:")
        print(f"   1. Get API key from: https://rapidapi.com/api-sports/api/api-football")
        print(f"   2. Add it to .env file")
        print(f"   3. Set USE_REAL_API=true")
        print(f"   4. Run this test again")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_api()

