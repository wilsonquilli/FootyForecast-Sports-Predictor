import os
import datetime
import requests
import numpy as np

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from prediction_agent import FootballPredictionAgent
from data_generator import FootballDataGenerator
from team_logos import TEAM_LOGOS

# ---------------------------------------------------------
# INIT
# ---------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# MODEL INIT
# ---------------------------------------------------------
print("Initializing Prediction Agent...")
agent = FootballPredictionAgent()

if agent.trainer is None:
    print("No trained model found. Training for first time...")
    agent.train_model(n_samples=5000, model_type="ensemble")
else:
    print("Model loaded successfully.")

# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"message": "FootyForecast API running (EPL, LaLiga, ML Predictions Enabled)"}


# ---------------------------------------------------------
# UNIFIED PREDICTION ENDPOINT (UI + Detailed)
# ---------------------------------------------------------
@app.post("/predict")
def predict_match(data: dict):
    # SIMPLE MODE (frontend)
    if "home_team" in data and "away_team" in data:
        home_players, home_form = _build_team_profile(data["home_team"])
        away_players, away_form = _build_team_profile(data["away_team"])

        # Allow overrides from caller when provided
        home_players = data.get("home_team_players", home_players)
        away_players = data.get("away_team_players", away_players)
        home_form = data.get("home_last_5_results", home_form)
        away_form = data.get("away_last_5_results", away_form)

        result = agent.predict_match_detailed(
            home_team_name=data["home_team"],
            away_team_name=data["away_team"],
            home_team_players=home_players,
            away_team_players=away_players,
            home_last_5_results=home_form,
            away_last_5_results=away_form,
        )

        # 🔥 NEW: GUARANTEE a non-null result
        if not result:
            result = {"home_win": 0.34, "draw": 0.33, "away_win": 0.33}

        return _normalize_prediction_output(result)

    # DETAILED MODE
    if "home_team_name" in data and "away_team_name" in data:
        result = agent.predict_match_detailed(
            home_team_name=data["home_team_name"],
            away_team_name=data["away_team_name"],
            home_team_players=data["home_team_players"],
            away_team_players=data["away_team_players"],
            home_last_5_results=data["home_last_5_results"],
            away_last_5_results=data["away_last_5_results"],
        )

        if not result:
            result = {"home_win": 0.34, "draw": 0.33, "away_win": 0.33}

        return _normalize_prediction_output(result)

    return {"error": "Invalid payload"}

# ---------------------------------------------------------
# NORMALIZE OUTPUT FOR FRONTEND
# Guarantees consistent structure across ALL models
# ---------------------------------------------------------
def _normalize_prediction_output(result):
    # If NOTHING valid was returned
    if not result:
        return {
            "probs": {
                "home_win": 0.34,
                "draw": 0.33,
                "away_win": 0.33
            },
            "suggested": "home"
        }

    # If purely a string
    if isinstance(result, str):
        return {
            "probs": {
                "home_win": 0.34,
                "draw": 0.33,
                "away_win": 0.33
            },
            "suggested": result.lower() if result.lower() in ["home", "away", "draw"] else "home"
        }

    # If wrong shape but dict
    if isinstance(result, dict):
        home = float(result.get("home_win", result.get("home", 0.34)))
        draw = float(result.get("draw", 0.33))
        away = float(result.get("away_win", result.get("away", 0.33)))

        # Ensure the probabilities always sum to 1.0 before returning to the
        # frontend. This guards against upstream sources that might provide
        # slightly off totals (e.g., 1.04) which then render as percentages
        # exceeding 100% in the UI.
        total = home + draw + away
        if total <= 0:
            home, draw, away = 0.34, 0.33, 0.33
            total = 1.0

        probs = {
            "home_win": home / total,
            "draw": draw / total,
            "away_win": away / total,
        }

        suggested = result.get("suggested")
        if not suggested:
            suggested = max(probs, key=probs.get).replace("_win", "")

        normalized = {"probs": probs, "suggested": suggested}

        # Preserve extra context when available so the frontend can
        # show scorelines alongside probabilities.
        if "home_score" in result:
            normalized["home_score"] = result["home_score"]
        if "away_score" in result:
            normalized["away_score"] = result["away_score"]
        if "report" in result:
            normalized["report"] = result["report"]

        return normalized

    # Default fallback
    return {
        "probs": {
            "home_win": 0.34,
            "draw": 0.33,
            "away_win": 0.33
        },
        "suggested": "home"
    }


# ---------------------------------------------------------
# BATCH PREDICTION
# ---------------------------------------------------------
@app.post("/batch_predict")
def batch_predict(match_list: list):
    results = agent.batch_predict(match_list)
    return [_normalize_prediction_output(r) for r in results]


# ---------------------------------------------------------
# TEAM PROFILE LOOKUPS
# Introduces team-specific strength and form so predictions
# vary by opponent instead of using uniform placeholder data
# ---------------------------------------------------------

TEAM_STRENGTHS = {
    "arsenal": 87,
    "aston villa": 82,
    "bournemouth": 76,
    "brentford": 78,
    "brighton": 79,
    "chelsea": 84,
    "crystal palace": 75,
    "everton": 77,
    "fulham": 78,
    "liverpool": 88,
    "manchester city": 90,
    "manchester united": 83,
    "newcastle united": 82,
    "nottingham forest": 74,
    "southampton": 73,
    "tottenham hotspur": 85,
    "west ham united": 80,
    "wolverhampton wanderers": 76,
    "sunderland afc": 72,
    "afc bournemouth": 76,
}

# encoded as 3/1/0 (win/draw/loss)
TEAM_FORM = {
    "arsenal": [3, 3, 1, 3, 3],
    "aston villa": [3, 1, 3, 0, 1],
    "bournemouth": [1, 3, 0, 1, 0],
    "brentford": [3, 3, 0, 1, 3],
    "brighton": [1, 3, 1, 0, 3],
    "chelsea": [3, 3, 3, 0, 1],
    "crystal palace": [1, 0, 1, 3, 0],
    "everton": [0, 1, 3, 0, 1],
    "fulham": [1, 1, 0, 3, 1],
    "liverpool": [3, 3, 3, 1, 3],
    "manchester city": [3, 3, 1, 3, 3],
    "manchester united": [3, 1, 0, 3, 3],
    "newcastle united": [3, 1, 3, 1, 0],
    "nottingham forest": [0, 1, 0, 1, 0],
    "southampton": [1, 1, 3, 0, 1],
    "tottenham hotspur": [3, 0, 3, 1, 3],
    "west ham united": [1, 3, 1, 0, 3],
    "wolverhampton wanderers": [1, 0, 1, 1, 3],
    "sunderland afc": [3, 3, 1, 0, 3],
    "afc bournemouth": [1, 3, 0, 1, 0],
}


def _normalize_team_key(name: str) -> str:
    key = name.lower().replace("fc", "").replace("afc", "").strip()
    return " ".join(key.split())


def _build_team_profile(team_name: str):
    """Return synthetic player ratings and recent form for the given team.

    This keeps the ML model fed with team-dependent features even when
    the caller does not pass explicit player ratings or form.
    """

    key = _normalize_team_key(team_name)
    base_rating = TEAM_STRENGTHS.get(key, 76)
    form = TEAM_FORM.get(key, [1, 1, 1, 1, 1])

    # deterministic noise per team so results stay stable across calls
    rng = np.random.default_rng(abs(hash(key)) % (2**32))
    players = rng.normal(loc=base_rating, scale=3.2, size=11)
    players = np.clip(players, 65, 95).round(1).tolist()

    return players, form


# ---------------------------------------------------------
# FIXTURES / TABLES / OTHER DATA
# ---------------------------------------------------------

EPL_FIXTURES_URL = "https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/en.1.json"
EPL_STANDINGS_URL = "https://raw.githubusercontent.com/openfootball/standings/master/2025-26/en.1.standing.json"
LIVE_SCORES_URL = "https://livescore-api-proxy.vercel.app/epl-live"


@app.get("/fixtures")
def get_epl_fixtures():
    resp = requests.get(EPL_FIXTURES_URL)
    data = resp.json()

    normalized = []
    for match in data.get("matches", []):
        normalized.append({
            "fixture": {
                "id": f"{match['team1']}_{match['team2']}_{match['date']}",
                "date": match["date"] + "T12:00:00",
                "venue": {"name": "Unknown"}
            },

            "teams": {
                "home": {"name": match["team1"]},
                "away": {"name": match["team2"]},
            }
        })

    return {"response": normalized}


@app.get("/logos")
def get_logos():
    return TEAM_LOGOS


@app.get("/table")
def get_table():
    return {
        "table": [
            {"pos": 1, "team": "Arsenal", "played": 12, "won": 10, "drawn": 1, "lost": 1, "gf": 28, "ga": 9, "points": 31},
            {"pos": 2, "team": "Manchester City", "played": 12, "won": 9, "drawn": 2, "lost": 1, "gf": 30, "ga": 12, "points": 29},
            {"pos": 3, "team": "Chelsea", "played": 12, "won": 8, "drawn": 2, "lost": 2, "gf": 24, "ga": 14, "points": 26},
            {"pos": 4, "team": "Sunderland", "played": 12, "won": 7, "drawn": 3, "lost": 2, "gf": 20, "ga": 13, "points": 24},
            {"pos": 5, "team": "Tottenham Hotspur", "played": 12, "won": 7, "drawn": 2, "lost": 3, "gf": 22, "ga": 15, "points": 23},
        ]
    }


@app.get("/recent_results")
def get_recent_results():
    resp = requests.get(EPL_FIXTURES_URL)
    matches = resp.json().get("matches", [])

    today = datetime.date.today()
    past = [m for m in matches if datetime.date.fromisoformat(m["date"]) < today]

    past.sort(key=lambda m: m["date"], reverse=True)
    return {"results": past[:5]}


@app.get("/matchdays")
def get_matchdays():
    resp = requests.get(EPL_FIXTURES_URL)
    matches = resp.json().get("matches", [])

    rounds = sorted(list(set([m["round"] for m in matches])))
    return {"matchdays": rounds}


@app.get("/live_scores")
def live_scores():
    try:
        resp = requests.get(LIVE_SCORES_URL)
        return resp.json()
    except:
        return {"live": []}


@app.get("/top_scorers")
def get_top_scorers():
    return {
        "scorers": [
            {"player": "Erling Haaland", "team": "Manchester City", "goals": 15},
            {"player": "Igor Thiago", "team": "Brentford", "goals": 11},
            {"player": "Danny Welbeck", "team": "Brighton", "goals": 7},
        ]
    }


# ---------------------------------------------------------
# LALIGA
# ---------------------------------------------------------
def _build_laliga_fixtures():
    """Generate a rolling set of fixtures that always fall in the near future.

    This keeps the LaLiga page populated even when the live API is unavailable.
    """

    base = datetime.datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)

    slots = [
        (1, 17, "Real Oviedo", "Mallorca", "Estadio Municipal Carlos Tartiere"),
        (1, 20, "Villareal", "Getafe", "Estadio de la Cermica"),
        (2, 13, "Deportivo Alaves", "Real Sociedad", "Estadio de Mendizorroza"),
        (2, 15, "Real Betis", "Barcelona", "Estadio La Cartuja de Sevilla"),
        (2, 18, "Athletic Club", "Atletico Madrid", "Estadio de San Mames"),
        (2, 21, "Elche", "Girona", "Estadio Manuel Martinez Valero"),
        (2, 23, "Valencia", "Sevilla", "Estadio de Mestalla"),
        (3, 11, "Espanyol", "Rayo Vallecano", "RCDE Stadium"),
        (3, 13, "Real Madrid", "Celta Vigo", "Estadio Bernabeu"),
        (3, 15, "Osasuna", "Levante", "Estadio El Sadar"),
        (3, 18, "Real Sociedad", "Girona", "Estadio Municipal de Anoeta"),
        (3, 20, "Atletico Madrid", "Valencia", "Riyadh Air Metropolitano"),
        (4, 12, "Mallorca", "Elche", "Estadi Mallorca Son Moix"),
        (4, 14, "Barcelona", "Osasuna", "Spotify Camp Nou"),
        (4, 16, "Getafe", "Espanyol", "Estadio Coliseum"),
    ]

    fixtures = []
    for idx, slot in enumerate(slots, start=1):
        day_offset, hour, home, away, venue = slot
        kickoff = base + datetime.timedelta(days=day_offset)
        kickoff = kickoff.replace(hour=hour, minute=0, second=0, microsecond=0)

        fixtures.append(
            {
                "fixture": {"id": 9000 + idx, "date": kickoff.isoformat() + "Z", "venue": {"name": venue}},
                "teams": {"home": {"name": home}, "away": {"name": away}},
            }
        )

    return fixtures


@app.get("/laliga_fixtures")
def laliga_fixtures():
    """Expose LaLiga fixtures in the same response shape the frontend expects."""

    return {"response": _build_laliga_fixtures()}


@app.get("/laliga_table")
def laliga_table():
    return {
        "table": [
            {
                "pos": 1,
                "team": "Barcelona",
                "played": 15,
                "won": 12,
                "drawn": 1,
                "lost": 2,
                "gf": 42,
                "ga": 17,
                "points": 37,
                "form": ["W", "W", "W", "W", "W"],
            },
            {
                "pos": 2,
                "team": "Real Madrid",
                "played": 15,
                "won": 11,
                "drawn": 3,
                "lost": 1,
                "gf": 32,
                "ga": 13,
                "points": 36,
                "form": ["W", "D", "D", "D", "W"],
            },
            {
                "pos": 3,
                "team": "Villareal",
                "played": 14,
                "won": 10,
                "drawn": 2,
                "lost": 2,
                "gf": 29,
                "ga": 13,
                "points": 32,
                "form": ["W", "W", "W", "W", "W"],
            },
            {
                "pos": 4,
                "team": "Atletico Madrid",
                "played": 15,
                "won": 9,
                "drawn": 4,
                "lost": 2,
                "gf": 28,
                "ga": 14,
                "points": 31,
                "form": ["W", "W", "W", "W", "L"],
            },
            {
                "pos": 5,
                "team": "Real Betis",
                "played": 14,
                "won": 6,
                "drawn": 6,
                "lost": 2,
                "gf": 22,
                "ga": 14,
                "points": 24,
                "form": ["L", "W", "D", "D", "W"],
            },
        ]
    }


@app.get("/laliga_top_scorers")
def laliga_top_scorers():
    return {
        "scorers": [
            {
                "player": "Kylian Mbappe",
                "team": "Real Madrid",
                "goals": 16,
                "photo_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Kylian_Mbapp%C3%A9_France.jpg",
            },
            {
                "player": "Ferran Torres",
                "team": "FC Barcelona",
                "goals": 8,
                "photo_url": "https://upload.wikimedia.org/wikipedia/commons/8/8f/Ferran_Torres_%282%29_%28cropped%29.jpg",
            },
            {
                "player": "Robert Lewandowski",
                "team": "FC Barcelona",
                "goals": 8,
                "photo_url": "https://upload.wikimedia.org/wikipedia/commons/8/89/Robert_Lewandowski_2023.jpg",
            },
        ]
    }


@app.get("/laliga_recent")
def laliga_recent():
    return {
        "response": [
            {
                "fixture": {"id": 201, "date": "2025-12-01T15:00:00"},
                "teams": {"home": {"name": "Valencia"}, "away": {"name": "Rayo Vallecano"}},
            },
            {
                "fixture": {"id": 202, "date": "2025-12-02T15:00:00"},
                "teams": {"home": {"name": "Barcelona"}, "away": {"name": "Atletico"}},
            },
            {
                "fixture": {"id": 203, "date": "2025-12-03T13:00:00"},
                "teams": {"home": {"name": "Athletic Club"}, "away": {"name": "Real Madrid"}},
            },
        ]
    }