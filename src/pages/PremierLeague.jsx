import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "./Pages.css";
import { useEffect, useState } from "react";
import { getJson, postJson } from "../lib/api";
import Haaland from "../assets/players/haaland.png";
import Thiago from "../assets/players/thiago.png";
import Welbeck from "../assets/players/welbeck.png";

const TEAM_LOGOS = {
  Arsenal: "https://resources.premierleague.com/premierleague/badges/70/t3.png",
  "Aston Villa": "https://resources.premierleague.com/premierleague/badges/70/t7.png",
  Bournemouth: "https://resources.premierleague.com/premierleague/badges/70/t91.png",
  Brentford: "https://resources.premierleague.com/premierleague/badges/70/t94.png",
  Brighton: "https://resources.premierleague.com/premierleague/badges/70/t36.png",
  "Brighton & Hove Albion": "https://resources.premierleague.com/premierleague/badges/70/t36.png",
  Burnley: "https://resources.premierleague.com/premierleague/badges/70/t90.png",
  Chelsea: "https://resources.premierleague.com/premierleague/badges/70/t8.png",
  "Crystal Palace": "https://resources.premierleague.com/premierleague/badges/70/t31.png",
  Everton: "https://resources.premierleague.com/premierleague/badges/70/t11.png",
  Fulham: "https://resources.premierleague.com/premierleague/badges/70/t54.png",
  Liverpool: "https://resources.premierleague.com/premierleague/badges/70/t14.png",
  "Manchester City": "https://resources.premierleague.com/premierleague/badges/70/t43.png",
  "Manchester United": "https://resources.premierleague.com/premierleague/badges/70/t1.png",
  "Leeds United": "https://resources.premierleague.com/premierleague/badges/70/t2.png",
  "Leicester City": "https://resources.premierleague.com/premierleague/badges/70/t13.png",
  "Newcastle United": "https://resources.premierleague.com/premierleague/badges/70/t4.png",
  "Nottingham Forest": "https://resources.premierleague.com/premierleague/badges/70/t17.png",
  "Sheffield United": "https://resources.premierleague.com/premierleague/badges/70/t49.png",
  Southampton: "https://resources.premierleague.com/premierleague/badges/70/t20.png",
  "Tottenham Hotspur": "https://resources.premierleague.com/premierleague/badges/70/t6.png",
  "West Ham United": "https://resources.premierleague.com/premierleague/badges/70/t21.png",
  "Wolverhampton Wanderers": "https://resources.premierleague.com/premierleague/badges/70/t39.png",
  Wolves: "https://resources.premierleague.com/premierleague/badges/70/t39.png",
};

const PLAYER_PHOTOS = {
  "Erling Haaland": Haaland,
  "Igor Thiago": Thiago,
  "Danny Welbeck": Welbeck,
};

// Simple fake "form" (W/D/L) for the table (you can tweak)
const TEAM_FORM = {
  Arsenal: ["W", "W", "D", "W", "W"],
  "Manchester City": ["W", "D", "W", "W", "L"],
  Chelsea: ["W", "W", "W", "L", "D"],
  Sunderland: ["W", "D", "W", "L", "W"],
  "Tottenham Hotspur": ["L", "W", "W", "D", "W"],
};

const TEAM_ALIASES = {
  "manchester united fc": "Manchester United",
  "manchester city fc": "Manchester City",
  "tottenham hotspur fc": "Tottenham Hotspur",
  "west ham united fc": "West Ham United",
  "nottingham forest fc": "Nottingham Forest",
  "wolverhampton wanderers fc": "Wolverhampton Wanderers",
  "afc bournemouth": "Bournemouth",
  "brighton & hove albion": "Brighton & Hove Albion",
  "brighton and hove albion": "Brighton & Hove Albion",
  "crystal palace fc": "Crystal Palace",
  "fulham fc": "Fulham",
  "leeds united fc": "Leeds United",
  "leicester city fc": "Leicester City",
  "sheffield united fc": "Sheffield United",
  "burnley fc": "Burnley",
  "west bromwich albion": "West Bromwich Albion",
  "west bromwich albion fc": "West Bromwich Albion",
};

const getTeamLogo = (name) => {
  if (!name) return "";

  const cleaned = name.replace(/\bFC\b/gi, "").trim();
  const key = TEAM_ALIASES[cleaned.toLowerCase()] || cleaned;
  return TEAM_LOGOS[key] || "";
};

const extractPredictionView = (prediction) => {
  if (!prediction) {
    return {
      homeProb: 0,
      drawProb: 0,
      awayProb: 0,
      suggested: "",
      predictedScore: null,
    };
  }

  const probs = prediction.probs || prediction;
  const homeProb = probs.home_win ?? probs.home ?? 0;
  const drawProb = probs.draw ?? 0;
  const awayProb = probs.away_win ?? probs.away ?? 0;

  let suggested = prediction.suggested;

  // Prefer the explicit scoreline to decide the outcome when provided
  if (
    typeof prediction.home_score === "number" &&
    typeof prediction.away_score === "number"
  ) {
    if (prediction.home_score > prediction.away_score) suggested = "home";
    else if (prediction.home_score < prediction.away_score) suggested = "away";
    else suggested = "draw";
  }

  if (!suggested) {
    const best = Math.max(homeProb, drawProb, awayProb);
    if (best === homeProb) suggested = "home";
    else if (best === awayProb) suggested = "away";
    else suggested = "draw";
  }

  const predictedScore =
    typeof prediction.home_score === "number" &&
    typeof prediction.away_score === "number"
      ? {
          home: prediction.home_score,
          away: prediction.away_score,
        }
      : null;

  return {
    homeProb,
    drawProb,
    awayProb,
    suggested,
    predictedScore,
  };
};

function PremierLeague() {
  const [allMatches, setAllMatches] = useState([]); 
  const [matches, setMatches] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [matchdaySize, setMatchdaySize] = useState(5);
  const [tableData, setTableData] = useState([]);
  const [topScorers, setTopScorers] = useState([]);

  // NEW: predictions storage
  const [preds, setPreds] = useState({});  // { fixtureId: predictionObj }

  const predictionsPending = matches.length > 0 && Object.keys(preds).length === 0;

  // Fixtures
  useEffect(() => {
    getJson("/fixtures")
      .then((data) => {
        let fixtures = data.response ?? [];
        setAllMatches(fixtures);

        const today = new Date();

        let upcoming = fixtures.filter((match) => {
          const matchDate = new Date(match.fixture.date);
          return matchDate >= today;
        });

        upcoming.sort(
          (a, b) =>
            new Date(a.fixture.date).getTime() -
            new Date(b.fixture.date).getTime()
        );

        upcoming = upcoming.slice(0, matchdaySize);
        setMatches(upcoming);
      })
      .catch((err) => {
        console.error("Fixtures error:", err);
        setErrorMsg("Failed to load matches.");
      })
      .finally(() => setLoading(false));
  }, [matchdaySize]);

  // PL Table
  useEffect(() => {
    getJson("/table")
      .then((data) => setTableData(data.table ?? []))
      .catch((err) => console.error("Table error:", err));
  }, []);

  // Top scorers
  useEffect(() => {
    getJson("/top_scorers")
      .then((data) => {
        setTopScorers(data.scorers ?? []);
      })
      .catch((err) => console.error("Top Scorers error:", err));
  }, []);

  // NEW – REQUEST PREDICTIONS FOR EACH UPCOMING MATCH
  useEffect(() => {
    let cancelled = false;

    async function loadPredictions() {
      const next = {};

      // Clear previous predictions so the UI can show the loading
      // state while we fetch the new matchday selection.
      setPreds({});

      for (const m of matches) {
        try {
          const data = await postJson("/predict", {
            home_team: m.teams?.home?.name,
            away_team: m.teams?.away?.name,
            league: "EPL",
          });

          next[m.fixture.id] = data;
        } catch (err) {
          console.error("Prediction error:", err);
        }
      }

      if (!cancelled) {
        setPreds(next); // replace, do NOT merge
      }
    }

    loadPredictions();
    return () => (cancelled = true);
  }, [matches]);

  // Recent matches
  const recentResults = (() => {
    if (!allMatches.length) return [];
    const today = new Date();

    let past = allMatches.filter((match) => {
      const matchDate = new Date(match.fixture.date);
      return matchDate < today;
    });

    past.sort(
      (a, b) =>
        new Date(b.fixture.date).getTime() -
        new Date(a.fixture.date).getTime()
    );

    return past.slice(0, 5);
  })();

  const renderFormBadges = (team) => {
    const form = TEAM_FORM[team] || [];
    return form.map((result, idx) => (
      <span
        key={idx}
        className={`form-badge form-${result.toLowerCase()}`}
      >
        {result}
      </span>
    ));
  };

  const getPlayerInitials = (name) =>
    name
      .split(" ")
      .map((part) => part[0])
      .join("");

  return (
    <>
      <Navbar />
      <main className="page premier-league-page">

        {/* Upcoming matches */}
        <h1 className="page-title fade-in">
          Premier League – Upcoming Matches
        </h1>

        {loading && (
          <p className="status-msg fade-in">
            Loading upcoming matches...
          </p>
        )}
        {errorMsg && (
          <p className="status-msg error fade-in">{errorMsg}</p>
        )}

        {!loading && !errorMsg && matches.length === 0 && (
          <p className="status-msg fade-in">
            No upcoming fixtures found.
          </p>
        )}

        {/* Matchday Selector */}
        <section className="matchday-section fade-in">
          <h2 className="section-title">Matchday Selector</h2>
          <div className="matchday-controls">
            <label>
              Show next{" "}
              <select
                value={matchdaySize}
                onChange={(e) =>
                  setMatchdaySize(parseInt(e.target.value))
                }
              >
                <option value={5}>5 matches</option>
                <option value={10}>10 matches</option>
                <option value={15}>15 matches</option>
              </select>{" "}
              from the schedule
            </label>
          </div>
        </section>

        <div className="matches-grid fade-in">
          {matches.map((match) => {
            const homeName = match.teams.home.name;
            const awayName = match.teams.away.name;
            const homeLogo = getTeamLogo(homeName);
            const awayLogo = getTeamLogo(awayName);

            return (
              <div key={match.fixture.id} className="match-card">
                <div className="match-teams">
                  <div className="team">
                    {homeLogo && (
                      <img
                        src={homeLogo}
                        alt={homeName}
                        className="team-logo"
                      />
                    )}
                    <span className="team-name">{homeName}</span>
                  </div>

                  <span className="vs">vs</span>

                  <div className="team">
                    {awayLogo && (
                      <img
                        src={awayLogo}
                        alt={awayName}
                        className="team-logo"
                      />
                    )}
                    <span className="team-name">{awayName}</span>
                  </div>
                </div>

                <p className="match-date">
                  📅 {new Date(match.fixture.date).toLocaleString()}
                </p>

                {match.fixture.venue?.name && (
                  <p className="match-venue">
                    🏟 {match.fixture.venue.name}
                  </p>
                )}

                <p className="match-status status-upcoming">
                  UPCOMING
                </p>
              </div>
            );
          })}
        </div>

        <div className="section-divider" />

        <h1 className="page-title fade-in">Premier League Predictions</h1>
        {predictionsPending && (
          <p className="status-msg fade-in">Calculating predictions...</p>
        )}

        <section className="matches-grid fade-in">
          {matches.map((match) => {
            const homeName = match.teams.home.name;
            const awayName = match.teams.away.name;
            const homeLogo = getTeamLogo(homeName);
            const awayLogo = getTeamLogo(awayName);
            const prediction = preds[match.fixture.id];
            const predictionView = extractPredictionView(prediction);

            const outcomeLabel =
              predictionView.suggested === "draw"
                ? "Draw"
                : predictionView.suggested === "home"
                  ? homeName
                  : predictionView.suggested === "away"
                    ? awayName
                    : predictionView.suggested?.toString().toUpperCase() || "—";

            return (
              <div key={`pred-${match.fixture.id}`} className="match-card prediction-card">
                <div className="match-teams">
                  <div className="team">
                    {homeLogo && (
                      <img
                        src={homeLogo}
                        alt={homeName}
                        className="team-logo"
                      />
                    )}
                    <span className="team-name">{homeName}</span>
                  </div>

                  <span className="vs">vs</span>

                  <div className="team">
                    {awayLogo && (
                      <img
                        src={awayLogo}
                        alt={awayName}
                        className="team-logo"
                      />
                    )}
                    <span className="team-name">{awayName}</span>
                  </div>
                </div>

                <p className="match-date">
                  📅 {new Date(match.fixture.date).toLocaleString()}
                </p>

                {/* 🔥 NEW — LIVE PREDICTIONS RENDERED INSIDE EACH CARD */}
                {preds[match.fixture.id] ? (
                  <div className="prediction-block">
                    <p>
                      <strong>Prediction:</strong>{" "}
                      {outcomeLabel}
                    </p>
                    <p>
                      🏠 {homeName}:{" "}
                      {(predictionView.homeProb * 100).toFixed(1)}%
                      &nbsp;|&nbsp;
                      🤝 Draw:{" "}
                      {(predictionView.drawProb * 100).toFixed(1)}%
                      &nbsp;|&nbsp;
                      ✈️ {awayName}:{" "}
                      {(predictionView.awayProb * 100).toFixed(1)}%
                    </p>
                    {predictionView.predictedScore && (
                      <p className="predicted-score">
                        Predicted score: {homeName} {predictionView.predictedScore.home} – {predictionView.predictedScore.away} {awayName}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="status-msg">Fetching prediction...</p>
                )}
              </div>
            );
          })}
        </section>

        <div className="section-divider" />

        {/* Premier League Table */}
        <h1 className="page-title fade-in">Premier League Table</h1>
        <section className="table-section fade-in">
          <div className="table-wrapper">
            <table className="pl-table">
              <thead>
                <tr>
                  <th>Pos</th>
                  <th>Team</th>
                  <th>P</th>
                  <th>W</th>
                  <th>D</th>
                  <th>L</th>
                  <th>GF</th>
                  <th>GA</th>
                  <th>Pts</th>
                  <th>Form</th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((row) => (
                  <tr key={row.pos}>
                    <td>{row.pos}</td>
                    <td className="team-cell">
                    {getTeamLogo(row.team) && (
                      <img
                        src={getTeamLogo(row.team)}
                        alt={row.team}
                        className="table-team-logo"
                      />
                      )}
                      <span>{row.team}</span>
                    </td>
                    <td>{row.played}</td>
                    <td>{row.won}</td>
                    <td>{row.drawn}</td>
                    <td>{row.lost}</td>
                    <td>{row.gf}</td>
                    <td>{row.ga}</td>
                    <td>{row.points}</td>
                    <td>{renderFormBadges(row.team)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <div className="section-divider" />

        {/* Top Scorers */}
        <h1 className="page-title fade-in">
          Premier League – Top Scorers
        </h1>
        <section className="top-scorers-section fade-in">
          <div className="table-wrapper">
            <table className="pl-table top-scorers-table">
              <colgroup>
                <col className="col-rank" />
                <col className="col-team" />
                <col className="col-goals" />
              </colgroup>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player</th>
                  <th>Goals</th>
                </tr>
              </thead>
              <tbody>
                {topScorers.map((row, index) => (
                  <tr key={row.player}>
                    <td>{index + 1}</td>
                    <td className="team-cell player-cell">
                      {PLAYER_PHOTOS[row.player] ? (
                        <img
                          src={PLAYER_PHOTOS[row.player]}
                          alt={row.player}
                          className="player-photo"
                        />
                      ) : (
                        <div className="player-badge">
                          {getPlayerInitials(row.player)}
                        </div>
                      )}
                      <div className="player-info">
                        <span className="player-name">{row.player}</span>
                      </div>
                    </td>
                    <td className="team-cell top-scorer-team-cell">
                      {TEAM_LOGOS[row.team] && (
                        <img
                          src={getTeamLogo(row.team)}
                          alt={row.team}
                          className="table-team-logo"
                        />
                      )}
                      <span>{row.team}</span>
                    </td>
                    <td className="goals-cell">
                      <span className="goal-pill">{row.goals}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <div className="section-divider" />

        {/* Recent Results */}
        <h1 className="page-title fade-in">
          Premier League – Recent Matches
        </h1>
        <section className="recent-results fade-in">
          {recentResults.length === 0 && (
            <p className="status-msg">
              No recent results available yet in the current dataset.
            </p>
          )}
          <div className="matches-grid">
            {recentResults.map((match) => {
              const homeName = match.teams.home.name;
              const awayName = match.teams.away.name;
              const homeLogo = getTeamLogo(homeName);
              const awayLogo = getTeamLogo(awayName);

              return (
                <div key={match.fixture.id} className="match-card">
                  <div className="match-teams">
                    <div className="team">
                      {homeLogo && (
                        <img
                          src={homeLogo}
                          alt={homeName}
                          className="team-logo"
                        />
                      )}
                      <span className="team-name">{homeName}</span>
                    </div>

                    <span className="vs">vs</span>

                    <div className="team">
                      {awayLogo && (
                        <img
                          src={awayLogo}
                          alt={awayName}
                          className="team-logo"
                        />
                      )}
                      <span className="team-name">{awayName}</span>
                    </div>
                  </div>

                  <p className="match-date">
                    📅 {new Date(match.fixture.date).toLocaleString()}
                  </p>
                  <p className="match-venue">Final / Full-time</p>
                  <p className="match-status status-ft">FT</p>
                </div>
              );
            })}
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

export default PremierLeague;