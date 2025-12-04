import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "./Pages.css";
import { useEffect, useState } from "react";
import { getJson, postJson } from "../lib/api";
import Mbappe from "../assets/players/mbappe.png";
import Ferran from "../assets/players/ferran.png";
import Lewa from "../assets/players/lewa.png";
import AthleticClub from "../assets/badges/AthleticClub.png";
import Atletico from "../assets/badges/AtleticoMadrid.png";
import Alaves from "../assets/badges/DeportivoAlaves.png";
import Elche from "../assets/badges/Elche.png";
import RealOviedo from "../assets/badges/RealOviedo.png";
import Villareal from "../assets/badges/Villareal.png";

const LALIGA_LOGOS = {
  "Real Madrid": "https://media.api-sports.io/football/teams/541.png",
  Barcelona: "https://media.api-sports.io/football/teams/529.png",
  Girona: "https://media.api-sports.io/football/teams/547.png",
  Atletico: Atletico,
  Sevilla: "https://media.api-sports.io/football/teams/536.png",
  Villareal: Villareal,
  Valencia: "https://media.api-sports.io/football/teams/532.png",
  Betis: "https://media.api-sports.io/football/teams/543.png",
  "Real Sociedad": "https://media.api-sports.io/football/teams/548.png",
  Osasuna: "https://media.api-sports.io/football/teams/727.png",
  Mallorca: "https://media.api-sports.io/football/teams/797.png",
  Alaves: Alaves,
  "Rayo Vallecano": "https://media.api-sports.io/football/teams/728.png",
  "Las Palmas": "https://media.api-sports.io/football/teams/798.png",
  Celta: "https://media.api-sports.io/football/teams/538.png",
  "Athletic Club": AthleticClub,
  Espanyol: "https://media.api-sports.io/football/teams/540.png",
  Cadiz: "https://media.api-sports.io/football/teams/724.png",
  Getafe: "https://media.api-sports.io/football/teams/546.png",
  Granada: "https://media.api-sports.io/football/teams/715.png",
  Elche: Elche,
  "Real Oviedo": RealOviedo,
};

const LALIGA_PLAYER_PHOTOS = {
  "Kylian Mbappe":
    Mbappe,
  "Ferran Torres":
    Ferran,
  "Robert Lewandowski":
    Lewa,
};

const LALIGA_TOP_SCORERS_FALLBACK = [
  { player: "Kylian Mbappe", team: "Real Madrid", goals: 16 },
  { player: "Ferran Torres", team: "Barcelona", goals: 8 },
  { player: "Robert Lewandowski", team: "Barcelona", goals: 8 },
];

const TEAM_ALIASES = {
  "atletico madrid": "Atletico",
  "atletico de madrid": "Atletico",
  "real sociedad de futbol": "Real Sociedad",
  "real betis": "Betis",
  "real betis balompie": "Betis",
  "real mallorca": "Mallorca",
  "athletic bilbao": "Athletic Club",
  "rayo vallecano de madrid": "Rayo Vallecano",
  "deportivo alaves": "Alaves",
  "real club celta de vigo": "Celta",
  "ud las palmas": "Las Palmas",
};

const LALIGA_ALIASES = {
  "real sociedad": "Real Sociedad",
  "rayo vallecano": "Rayo Vallecano",
  "las palmas": "Las Palmas",
  "athletic bilbao": "Athletic Club",
  "atletico madrid": "Atletico",
  "atletico de madrid": "Atletico",
  "real betis": "Betis",
};

// Placeholder form (optional)
const LALIGA_FORM = {
  "Real Madrid": ["W", "W", "W", "D", "L"],
  Barcelona: ["W", "W", "W", "W", "L"],
  Atletico: ["W", "W", "L", "W", "L"],
  Girona: ["L", "W", "W", "W", "L"],
  Betis: ["W", "W", "W", "W", "L"],
};

const buildFallbackFixtures = () => {
  const addDays = (days, hours) => {
    const d = new Date();
    d.setDate(d.getDate() + days);
    d.setHours(hours, 0, 0, 0);
    return d.toISOString();
  };

  return [
    {
      fixture: {
        id: 9001,
        date: addDays(2, 15),
        venue: { name: "Santiago Bernabéu" },
      },
      teams: {
        home: { name: "Real Madrid" },
        away: { name: "Barcelona" },
      },
    },
    {
      fixture: {
        id: 9002,
        date: addDays(2, 20),
        venue: { name: "Cívitas Metropolitano" },
      },
      teams: {
        home: { name: "Atletico" },
        away: { name: "Sevilla" },
      },
    },
    {
      fixture: {
        id: 9003,
        date: addDays(3, 13),
        venue: { name: "Estadi Montilivi" },
      },
      teams: {
        home: { name: "Girona" },
        away: { name: "Valencia" },
      },
    },
    {
      fixture: {
        id: 9004,
        date: addDays(3, 17),
        venue: { name: "Reale Arena" },
      },
      teams: {
        home: { name: "Real Sociedad" },
        away: { name: "Athletic Club" },
      },
    },
    {
      fixture: {
        id: 9005,
        date: addDays(4, 18),
        venue: { name: "Estadio de la Cerámica" },
      },
      teams: {
        home: { name: "Villarreal" },
        away: { name: "Betis" },
      },
    },
    {
      fixture: {
        id: 9006,
        date: addDays(4, 20),
        venue: { name: "El Sadar" },
      },
      teams: {
        home: { name: "Osasuna" },
        away: { name: "Celta" },
      },
    },
  ];
};

function LaLiga() {
  const [allMatches, setAllMatches] = useState([]);
  const [matches, setMatches] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [topScorers, setTopScorers] = useState(LALIGA_TOP_SCORERS_FALLBACK);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [matchdaySize, setMatchdaySize] = useState(6);

  const [preds, setPreds] = useState({}); // { fixtureId: { probs, suggested } }
  const predictionsPending = matches.length > 0 && Object.keys(preds).length === 0;

  const selectUpcoming = (fixtures, limit) => {
    const today = new Date();

    const sorted = [...fixtures].sort(
      (a, b) =>
        new Date(a.fixture.date).getTime() - new Date(b.fixture.date).getTime()
    );

    const future = sorted.filter((match) => {
      const matchDate = new Date(match.fixture.date);
      return matchDate >= today;
    });

    if (future.length > 0) return future.slice(0, limit);

    return upcoming.slice(0, limit);
  };

  // -------------------------
  // Fixtures
  // -------------------------
  useEffect(() => {
    let cancelled = false;

    // Immediately seed the UI with a near-term fallback schedule so the page
    // always shows upcoming fixtures even before the API responds.
    const seeded = selectUpcoming(buildFallbackFixtures(), matchdaySize);
    if (!cancelled && seeded.length > 0) {
      setMatches(seeded);
    }

    async function loadFixtures() {
      try {
        const data = await getJson("/laliga_fixtures");
        const fixtures = data.response ?? [];
        let upcoming = selectUpcoming(fixtures, matchdaySize);

        if (upcoming.length === 0) {
          upcoming = selectUpcoming(FALLBACK_FIXTURES, matchdaySize);
        }

        if (!cancelled) {
          setAllMatches(fixtures);
          setMatches(upcoming);
          setErrorMsg("");
        }
      } catch (err) {
        console.error("LaLiga fixtures error:", err);
        const fallback = selectUpcoming(FALLBACK_FIXTURES, matchdaySize);
        if (!cancelled) {
          setAllMatches([]);
          setMatches(fallback);
          setErrorMsg("Failed to load LaLiga fixtures. Showing scheduled matches.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadFixtures();
    return () => {
      cancelled = true;
    };
  }, [matchdaySize]);

  // -------------------------
  // Table
  // -------------------------
  useEffect(() => {
    getJson("/laliga_table")
      .then((data) => {
        setTableData(data.table ?? []);
      })
      .catch((err) => console.error(err));
  }, []);

  // -------------------------
  // Top Scorers
  // -------------------------
  useEffect(() => {
    getJson("/laliga_top_scorers")
      .then((data) => {
        const scorers = data.scorers ?? [];
        setTopScorers(scorers.length > 0 ? scorers : LALIGA_TOP_SCORERS_FALLBACK);
      })
      .catch((err) => {
        console.error(err);
        setTopScorers(LALIGA_TOP_SCORERS_FALLBACK);
      });
  }, []);

  // -------------------------
  // Recent Results
  // -------------------------
  useEffect(() => {
    getJson("/laliga_recent")
      .then((data) => {
        setRecent(data.response ?? []);
      })
      .catch((err) => console.error(err));
  }, []);

  // -------------------------
  // NEW: Fetch AI Predictions for each fixture
  // -------------------------
  useEffect(() => {
    if (matches.length === 0) return;

    let cancel = false;

    (async () => {
      const next = {};

      setPreds({});

      for (const m of matches) {
        try {
          const body = {
            home_team: m?.teams?.home?.name,
            away_team: m?.teams?.away?.name,
            league: "LaLiga",
          };

          const data = await postJson("/predict", body);

          if (!cancel && m.fixture?.id) {
            next[m.fixture.id] = data;
          }
        } catch (err) {
          console.error("Prediction error:", err);
        }
      }

      if (!cancel) {
        setPreds(next);
      }
    })();

    return () => {
      cancel = true;
    };
  }, [matches]);

  const renderFormBadges = (team, formOverride) =>
    (formOverride || LALIGA_FORM[team] || []).map((r, i) => (
      <span key={i} className={`form-badge form-${r.toLowerCase()}`}>
        {r}
      </span>
    ));

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

  const normalizeTeamName = (name) => {
    if (!name) return "";

    const cleaned = name.replace(/\bFC\b/gi, "").trim();
    const deAccented = cleaned
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

    const aliasKey = deAccented.toLowerCase();
    const alias = TEAM_ALIASES[aliasKey] || LALIGA_ALIASES[aliasKey];

    return alias || deAccented;
  };

  const getTeamLogo = (team) => {
    if (!team) return "";

    const cleaned = normalizeTeamName(team);

    const key = Object.keys(LALIGA_LOGOS).find(
      (k) => k.toLowerCase() === cleaned.toLowerCase()
    );

    return LALIGA_LOGOS[key] || "";
  };

  const getInitials = (name) =>
    name
      .split(" ")
      .map((n) => n[0])
      .join("");

  const formatGoalDiff = (gf, ga) => {
    const diff = (gf ?? 0) - (ga ?? 0);
    return diff > 0 ? `+${diff}` : diff.toString();
  };

  return (
    <>
      <Navbar />
      <main className="page laliga-page">

        {/* Upcoming Matches */}
        <h1 className="page-title fade-in">LaLiga – Upcoming Matches</h1>

        {loading && <p className="status-msg">Loading fixtures…</p>}
        {errorMsg && <p className="status-msg error">{errorMsg}</p>}
        {!loading && !errorMsg && matches.length === 0 && (
          <p className="status-msg fade-in">No upcoming fixtures found.</p>
        )}
        {predictionsPending && (
          <p className="status-msg fade-in">Calculating predictions...</p>
        )}

        {/* Matchday Selector */}
        <section className="matchday-section fade-in">
          <h2 className="section-title">Matchday Selector</h2>
          <div className="matchday-controls">
            <label>
              Show next{" "}
              <select
                value={matchdaySize}
                onChange={(e) => setMatchdaySize(parseInt(e.target.value))}
              >
                <option value={6}>6 matches</option>
                <option value={10}>10 matches</option>
                <option value={15}>15 matches</option>
              </select>{" "}
              from the schedule
            </label>
          </div>
        </section>

        <div className="matches-grid fade-in">
          {matches.map((match) => {
            const home = normalizeTeamName(match.teams.home.name);
            const away = normalizeTeamName(match.teams.away.name);
            const homeLogo = getTeamLogo(home);
            const awayLogo = getTeamLogo(away);
            const prediction = preds[match.fixture.id];
            const view = extractPredictionView(prediction);

            const outcomeLabel =
              view.suggested === "draw"
                ? "Draw"
                : view.suggested === "home"
                  ? home
                  : view.suggested === "away"
                    ? away
                    : view.suggested?.toString().toUpperCase() || "—";

            return (
              <div key={match.fixture.id} className="match-card">
                <div className="match-teams">
                  <div className="team">
                    {homeLogo && (
                      <img src={homeLogo} alt={home} className="team-logo" />
                    )}
                    <span className="team-name">{home}</span>
                  </div>

                  <span className="vs">vs</span>

                  <div className="team">
                    {awayLogo && (
                      <img src={awayLogo} alt={away} className="team-logo" />
                    )}
                    <span className="team-name">{away}</span>
                  </div>
                </div>

                <p className="match-date">
                  📅 {new Date(match.fixture.date).toLocaleString()}
                </p>

                <p className="match-venue">
                  🏟 {match.fixture.venue?.name ?? "Unknown Venue"}
                </p>

                <p className="match-status status-upcoming">UPCOMING</p>

                {prediction ? (
                  <div className="prediction-block">
                    <p>
                      <strong>Prediction:</strong> {outcomeLabel}
                    </p>
                    <p>
                      🏠 {home}: {(view.homeProb * 100).toFixed(1)}% &nbsp;|&nbsp;
                      🤝 Draw: {(view.drawProb * 100).toFixed(1)}% &nbsp;|&nbsp;
                      ✈️ {away}: {(view.awayProb * 100).toFixed(1)}%
                    </p>
                    {view.predictedScore && (
                      <p className="predicted-score">
                        Predicted score: {home} {view.predictedScore.home} – {view.predictedScore.away} {away}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="status-msg">Fetching prediction...</p>
                )}
              </div>
            );
          })}
        </div>

        <div className="section-divider" />

        {/* LaLiga Table */}
        <h1 className="page-title fade-in">LaLiga Table</h1>
        <section className="table-section fade-in">
          <div className="table-wrapper">
            <table className="ll-table">
              <thead>
                <tr>
                  <th>Pos</th>
                  <th>Team</th>
                  <th>Pl</th>
                  <th>W</th>
                  <th>D</th>
                  <th>L</th>
                  <th>+/-</th>
                  <th>GD</th>
                  <th>Pts</th>
                  <th>Form</th>
                </tr>
              </thead>

              <tbody>
                {tableData.map((row) => {
                  const normalizedTeam = normalizeTeamName(row.team);
                  const teamLogo = getTeamLogo(normalizedTeam);

                  return (
                    <tr key={row.pos}>
                      <td>{row.pos}</td>

                      <td className="team-cell">
                        {teamLogo && (
                          <img
                            src={teamLogo}
                            alt={normalizedTeam}
                            className="table-team-logo"
                          />
                        )}
                        {normalizedTeam}
                      </td>

                      <td>{row.played}</td>
                      <td>{row.won}</td>
                      <td>{row.drawn}</td>
                      <td>{row.lost}</td>
                      <td>{`${row.gf}:${row.ga}`}</td>
                      <td>{formatGoalDiff(row.gf, row.ga)}</td>
                      <td>{row.points}</td>
                      <td>{renderFormBadges(normalizedTeam, row.form)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        <div className="section-divider" />

        {/* Top Scorers */}
        <h1 className="page-title fade-in">LaLiga – Top Scorers</h1>
        <section className="top-scorers-section fade-in">
          <div className="table-wrapper">
            <table className="ll-table">
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
                      {LALIGA_PLAYER_PHOTOS[row.player] ? (
                        <img
                          src={LALIGA_PLAYER_PHOTOS[row.player]}
                          alt={row.player}
                          className="player-photo"
                        />
                      ) : (
                        <div className="player-badge">{getInitials(row.player)}</div>
                      )}

                      <div className="player-info">
                        <span className="player-name">{row.player}</span>
                      </div>
                    </td>

                    <td className="team-cell top-scorer-team-cell">
                      {getTeamLogo(row.team) && (
                        <img
                          src={getTeamLogo(row.team)}
                          className="table-team-logo"
                          alt={normalizeTeamName(row.team)}
                        />
                      )}
                      <span>{normalizeTeamName(row.team)}</span>
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
        <h1 className="page-title fade-in">LaLiga – Recent Matches</h1>
        <section className="recent-results fade-in">
          <div className="matches-grid">
            {recent.map((match) => {
              const home = normalizeTeamName(match.teams.home.name);
              const away = normalizeTeamName(match.teams.away.name);
              const homeLogo = getTeamLogo(home);
              const awayLogo = getTeamLogo(away);

              return (
                <div key={match.fixture.id} className="match-card">
                  <div className="match-teams">
                    <div className="team">
                      {homeLogo && (
                        <img src={homeLogo} alt={home} className="team-logo" />
                      )}
                      <span className="team-name">{home}</span>
                    </div>

                    <span className="vs">vs</span>

                    <div className="team">
                      {awayLogo && (
                        <img src={awayLogo} alt={away} className="team-logo" />
                      )}
                      <span className="team-name">{away}</span>
                    </div>
                  </div>

                  <p className="match-date">
                    📅 {new Date(match.fixture.date).toLocaleString()}
                  </p>

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

export default LaLiga;