"""
Quick test to verify API key works
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('FOOTBALL_API_KEY')
api_host = os.getenv('FOOTBALL_API_HOST', 'v3.football.api-sports.io')

if not api_key:
    print("✗ API key not found in .env file")
    exit(1)

print("Testing API connection...")
print(f"API Host: {api_host}")
print(f"API Key: {api_key[:10]}...{api_key[-5:]} (hidden)")

headers = {
    'x-rapidapi-host': api_host,
    'x-rapidapi-key': api_key
}

# Test with a simple request - get Premier League teams
url = f"https://{api_host}/teams"
params = {'league': 39, 'season': 2023}

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        teams = data.get('response', [])
        print(f"\n✓ API connection successful!")
        print(f"✓ Found {len(teams)} teams in Premier League")
        if teams:
            print(f"  Example: {teams[0]['team']['name']}")
        print("\n✓ Ready to fetch historical data!")
    elif response.status_code == 401:
        print("\n✗ Authentication failed - check your API key")
    elif response.status_code == 429:
        print("\n⚠️  Rate limit exceeded - wait a bit and try again")
    else:
        print(f"\n✗ API Error: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"\n✗ Connection error: {e}")

