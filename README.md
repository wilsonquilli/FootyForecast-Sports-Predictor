# FootyForecast

FootyForecast combines a FastAPI backend with a React/Vite frontend to deliver data-driven football predictions for upcoming fixtures. The project focuses on Premier League matchups, blending curated team strength/form profiles with machine learning models to produce win/draw/loss probabilities, suggested outcomes, and projected scorelines.

## Features
- **Prediction API** powered by `FootballPredictionAgent` with Poisson-informed probability shaping and strength/form lookups for realistic EPL outputs.
- **Interactive frontend** (React + Vite) that fetches predictions, shows probabilities, suggested picks, and club badges for each upcoming Premier League game.
- **Batch support** for generating multiple predictions in one call.

## Project structure
- `backend/` — FastAPI service, model pipeline, API integrations, and team metadata.
  - `main.py` exposes `/predict` and `/batch_predict` endpoints and initializes the prediction agent.
  - `prediction_agent.py` contains the ML-driven prediction logic and probability shaping.
  - `team_logos.py` maps normalized club names to badge URLs used by the frontend.
- `src/` — React application (Vite) rendering upcoming fixtures and the Premier League Predictions section.
  - `src/pages/PremierLeague.jsx` fetches fixtures, requests predictions, and displays badges alongside probabilities.

## Prerequisites
- Node.js 18+
- Python 3.10+

## Backend setup
1. Create a virtual environment and install dependencies:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Add an API-Football key to `.env` in the `backend/` directory:
   ```bash
   echo "API_KEY=your_api_football_key" > .env
   ```
3. Start the FastAPI server (default port 8000):
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Prediction endpoints
- `POST /predict` — accepts `{ "home_team": "Arsenal", "away_team": "Chelsea" }` and returns normalized probabilities plus optional scorelines and reports.
- `POST /batch_predict` — accepts a list of match objects (same shape as `/predict`) and returns an array of normalized prediction payloads.

## Frontend setup
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server (default port 5173):
   ```bash
   npm run dev
   ```
3. Ensure the frontend can reach the backend (by default it calls `http://localhost:8000`). Update the API base URL in the frontend if you host the backend elsewhere.

## How it works
1. The frontend fetches upcoming Premier League fixtures, normalizes team names, and requests predictions for each pairing.
2. The backend loads or trains the prediction model, enriches inputs with team-specific strength and form data, and produces probabilities.
3. The frontend renders a dedicated **Premier League Predictions** section showing badges, suggested outcomes, percentage chances, and any projected scores returned by the API.

## Testing and linting
- Frontend linting: `npm run lint`
- Backend tests/examples: use the scripts in `backend/` (e.g., `test_api.py` or `test_api_connection.py`) after activating the virtual environment.

## Deployment notes
- Expose the FastAPI server publicly or behind a reverse proxy, then configure the frontend to point to that URL.
- Keep your `.env` file (API key) private and consider environment-specific keys for staging/production.