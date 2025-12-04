import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "./Pages.css";
import { useEffect, useState } from "react";
import { postJson } from "../lib/api";
import Prescott from "../assets/players/Prescott.png";
import Maye from "../assets/players/Maye.png";

const DEFAULT_LOGO =
  "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/nfl.png";

const NFL_LOGOS = {
  "Arizona Cardinals": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/ari.png",
  "Atlanta Falcons": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/atl.png",
  "Baltimore Ravens": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/bal.png",
  "Buffalo Bills": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/buf.png",
  "Carolina Panthers": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/car.png",
  "Chicago Bears": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/chi.png",
  "Cincinnati Bengals": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/cin.png",
  "Cleveland Browns": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/cle.png",
  "Dallas Cowboys": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/dal.png",
  "Denver Broncos": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/den.png",
  "Detroit Lions": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/det.png",
  "Green Bay Packers": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/gb.png",
  "Houston Texans": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/hou.png",
  "Indianapolis Colts": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/ind.png",
  "Jacksonville Jaguars": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/jax.png",
  "Kansas City Chiefs": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/kc.png",
  "Las Vegas Raiders": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/lv.png",
  "Los Angeles Chargers": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/lac.png",
  "Los Angeles Rams": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/lar.png",
  "Miami Dolphins": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/mia.png",
  "Minnesota Vikings": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/min.png",
  "New England Patriots": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/ne.png",
  "New Orleans Saints": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/no.png",
  "New York Giants": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/nyg.png",
  "New York Jets": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/nyj.png",
  "Philadelphia Eagles": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/phi.png",
  "Pittsburgh Steelers": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/pit.png",
  "San Francisco 49ers": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/sf.png",
  "Seattle Seahawks": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/sea.png",
  "Tampa Bay Buccaneers": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/tb.png",
  "Tennessee Titans": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/ten.png",
  "Washington Commanders": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/wsh.png",
};

const NFL_STANDINGS = [
  {
    conference: "AFC",
    divisions: [
      {
        name: "East",
        teams: [
          {
            team: "Buffalo Bills",
            w: 12,
            l: 1,
            t: 0,
            pct: ".923",
            pf: 407,
            pa: 166,
            net: 241,
            div: "3-0",
            conf: "8-1",
            home: "6-0",
            away: "6-1",
            streak: "W9",
          },
          {
            team: "New England Patriots",
            w: 8,
            l: 6,
            t: 0,
            pct: ".571",
            pf: 321,
            pa: 276,
            net: 45,
            div: "3-2",
            conf: "6-3",
            home: "5-2",
            away: "3-4",
            streak: "L1",
          },
          {
            team: "Miami Dolphins",
            w: 8,
            l: 6,
            t: 0,
            pct: ".571",
            pf: 346,
            pa: 320,
            net: 26,
            div: "3-2",
            conf: "6-3",
            home: "4-3",
            away: "4-3",
            streak: "W1",
          },
          {
            team: "New York Jets",
            w: 3,
            l: 10,
            t: 0,
            pct: ".231",
            pf: 163,
            pa: 309,
            net: -146,
            div: "0-5",
            conf: "2-8",
            home: "2-5",
            away: "1-5",
            streak: "L6",
          },
        ],
      },
      {
        name: "North",
        teams: [
          {
            team: "Baltimore Ravens",
            w: 8,
            l: 5,
            t: 0,
            pct: ".615",
            pf: 301,
            pa: 209,
            net: 92,
            div: "2-3",
            conf: "5-4",
            home: "5-1",
            away: "3-4",
            streak: "W1",
          },
          {
            team: "Pittsburgh Steelers",
            w: 7,
            l: 6,
            t: 0,
            pct: ".538",
            pf: 278,
            pa: 243,
            net: 35,
            div: "3-1",
            conf: "6-3",
            home: "4-2",
            away: "3-4",
            streak: "L1",
          },
          {
            team: "Cincinnati Bengals",
            w: 6,
            l: 7,
            t: 0,
            pct: ".462",
            pf: 322,
            pa: 323,
            net: -1,
            div: "2-2",
            conf: "4-6",
            home: "3-3",
            away: "3-4",
            streak: "W1",
          },
          {
            team: "Cleveland Browns",
            w: 2,
            l: 11,
            t: 0,
            pct: ".154",
            pf: 187,
            pa: 304,
            net: -117,
            div: "0-4",
            conf: "0-9",
            home: "1-5",
            away: "1-6",
            streak: "W1",
          },
        ],
      },
      {
        name: "South",
        teams: [
          {
            team: "Jacksonville Jaguars",
            w: 10,
            l: 3,
            t: 0,
            pct: ".769",
            pf: 343,
            pa: 249,
            net: 94,
            div: "3-1",
            conf: "8-2",
            home: "6-0",
            away: "4-3",
            streak: "W4",
          },
          {
            team: "Houston Texans",
            w: 9,
            l: 5,
            t: 0,
            pct: ".643",
            pf: 340,
            pa: 280,
            net: 60,
            div: "3-2",
            conf: "8-3",
            home: "6-1",
            away: "3-4",
            streak: "L2",
          },
          {
            team: "Tennessee Titans",
            w: 7,
            l: 6,
            t: 0,
            pct: ".538",
            pf: 234,
            pa: 293,
            net: -59,
            div: "3-2",
            conf: "5-5",
            home: "5-1",
            away: "2-5",
            streak: "L1",
          },
          {
            team: "Indianapolis Colts",
            w: 5,
            l: 9,
            t: 0,
            pct: ".357",
            pf: 232,
            pa: 301,
            net: -69,
            div: "1-4",
            conf: "4-7",
            home: "2-5",
            away: "3-4",
            streak: "L3",
          },
        ],
      },
      {
        name: "West",
        teams: [
          {
            team: "Kansas City Chiefs",
            w: 10,
            l: 3,
            t: 0,
            pct: ".769",
            pf: 316,
            pa: 203,
            net: 113,
            div: "4-0",
            conf: "8-2",
            home: "5-1",
            away: "5-2",
            streak: "W2",
          },
          {
            team: "Denver Broncos",
            w: 8,
            l: 6,
            t: 0,
            pct: ".571",
            pf: 324,
            pa: 323,
            net: 1,
            div: "2-2",
            conf: "6-3",
            home: "5-2",
            away: "3-4",
            streak: "W2",
          },
          {
            team: "Las Vegas Raiders",
            w: 6,
            l: 7,
            t: 0,
            pct: ".462",
            pf: 274,
            pa: 250,
            net: 24,
            div: "1-4",
            conf: "3-6",
            home: "5-2",
            away: "1-5",
            streak: "W1",
          },
          {
            team: "Los Angeles Chargers",
            w: 2,
            l: 11,
            t: 0,
            pct: ".154",
            pf: 198,
            pa: 359,
            net: -161,
            div: "1-3",
            conf: "2-7",
            home: "2-4",
            away: "0-7",
            streak: "L5",
          },
        ],
      },
    ],
  },
  {
    conference: "NFC",
    divisions: [
      {
        name: "East",
        teams: [
          {
            team: "Philadelphia Eagles",
            w: 12,
            l: 1,
            t: 0,
            pct: ".923",
            pf: 356,
            pa: 179,
            net: 177,
            div: "4-0",
            conf: "9-0",
            home: "6-0",
            away: "6-1",
            streak: "W2",
          },
          {
            team: "Dallas Cowboys",
            w: 10,
            l: 3,
            t: 0,
            pct: ".769",
            pf: 387,
            pa: 282,
            net: 105,
            div: "4-1",
            conf: "8-2",
            home: "7-0",
            away: "3-3",
            streak: "W2",
          },
          {
            team: "Washington Commanders",
            w: 6,
            l: 7,
            t: 0,
            pct: ".462",
            pf: 292,
            pa: 300,
            net: -8,
            div: "2-4",
            conf: "5-5",
            home: "3-4",
            away: "3-3",
            streak: "W1",
          },
          {
            team: "New York Giants",
            w: 4,
            l: 9,
            t: 0,
            pct: ".308",
            pf: 203,
            pa: 307,
            net: -104,
            div: "2-2",
            conf: "3-6",
            home: "2-5",
            away: "2-4",
            streak: "W3",
          },
        ],
      },
      {
        name: "North",
        teams: [
          {
            team: "Chicago Bears",
            w: 9,
            l: 4,
            t: 0,
            pct: ".692",
            pf: 330,
            pa: 218,
            net: 112,
            div: "1-2",
            conf: "7-2",
            home: "5-1",
            away: "4-3",
            streak: "L1",
          },
          {
            team: "Detroit Lions",
            w: 7,
            l: 6,
            t: 0,
            pct: ".538",
            pf: 323,
            pa: 323,
            net: 0,
            div: "4-1",
            conf: "5-4",
            home: "4-2",
            away: "3-4",
            streak: "L2",
          },
          {
            team: "Green Bay Packers",
            w: 7,
            l: 6,
            t: 0,
            pct: ".538",
            pf: 294,
            pa: 286,
            net: 8,
            div: "1-2",
            conf: "5-4",
            home: "4-2",
            away: "3-4",
            streak: "L1",
          },
          {
            team: "Minnesota Vikings",
            w: 6,
            l: 7,
            t: 0,
            pct: ".462",
            pf: 306,
            pa: 304,
            net: 2,
            div: "2-4",
            conf: "6-3",
            home: "4-3",
            away: "2-4",
            streak: "W2",
          },
        ],
      },
      {
        name: "South",
        teams: [
          {
            team: "Tampa Bay Buccaneers",
            w: 8,
            l: 6,
            t: 0,
            pct: ".571",
            pf: 301,
            pa: 263,
            net: 38,
            div: "2-2",
            conf: "4-5",
            home: "5-3",
            away: "3-3",
            streak: "L1",
          },
          {
            team: "Carolina Panthers",
            w: 6,
            l: 7,
            t: 0,
            pct: ".462",
            pf: 242,
            pa: 278,
            net: -36,
            div: "3-1",
            conf: "4-5",
            home: "4-3",
            away: "2-4",
            streak: "W1",
          },
          {
            team: "New Orleans Saints",
            w: 5,
            l: 8,
            t: 0,
            pct: ".385",
            pf: 217,
            pa: 283,
            net: -66,
            div: "2-3",
            conf: "3-6",
            home: "3-3",
            away: "2-5",
            streak: "L1",
          },
          {
            team: "Atlanta Falcons",
            w: 3,
            l: 10,
            t: 0,
            pct: ".231",
            pf: 232,
            pa: 326,
            net: -94,
            div: "2-3",
            conf: "2-7",
            home: "2-4",
            away: "1-6",
            streak: "L2",
          },
        ],
      },
      {
        name: "West",
        teams: [
          {
            team: "Los Angeles Rams",
            w: 8,
            l: 5,
            t: 0,
            pct: ".615",
            pf: 291,
            pa: 214,
            net: 77,
            div: "5-0",
            conf: "7-1",
            home: "4-2",
            away: "4-3",
            streak: "W2",
          },
          {
            team: "Seattle Seahawks",
            w: 7,
            l: 6,
            t: 0,
            pct: ".538",
            pf: 315,
            pa: 304,
            net: 11,
            div: "2-3",
            conf: "6-3",
            home: "5-1",
            away: "2-5",
            streak: "W2",
          },
          {
            team: "San Francisco 49ers",
            w: 7,
            l: 7,
            t: 0,
            pct: ".500",
            pf: 315,
            pa: 315,
            net: 0,
            div: "1-3",
            conf: "3-7",
            home: "5-3",
            away: "2-4",
            streak: "L2",
          },
          {
            team: "Arizona Cardinals",
            w: 5,
            l: 9,
            t: 0,
            pct: ".357",
            pf: 262,
            pa: 327,
            net: -65,
            div: "1-3",
            conf: "2-6",
            home: "3-4",
            away: "2-5",
            streak: "W3",
          },
        ],
      },
    ],
  },
];

const NFL_SCHEDULE = [
  {
    fixture: {
      id: 2001,
      date: "2025-12-13T20:15:00",
      venue: { name: "Raymond James Stadium — Tampa, FL" },
    },
    teams: {
      home: { name: "Tampa Bay Buccaneers" },
      away: { name: "Atlanta Falcons" },
    },
  },
  {
    fixture: {
      id: 2002,
      date: "2025-12-14T13:00:00",
      venue: { name: "Soldier Field — Chicago, IL" },
    },
    teams: {
      home: { name: "Chicago Bears" },
      away: { name: "Cleveland Browns" },
    },
  },
  {
    fixture: {
      id: 2003,
      date: "2025-12-14T13:00:00",
      venue: { name: "SoFi Stadium — Inglewood, CA" },
    },
    teams: {
      home: { name: "Los Angeles Chargers" },
      away: { name: "Baltimore Ravens" },
    },
  },
  {
    fixture: {
      id: 2004,
      date: "2025-12-14T13:00:00",
      venue: { name: "GEHA Field at Arrowhead Stadium — Kansas City, MO" },
    },
    teams: {
      home: { name: "Kansas City Chiefs" },
      away: { name: "Denver Broncos" },
    },
  },
  {
    fixture: {
      id: 2005,
      date: "2025-12-14T13:00:00",
      venue: { name: "Gillette Stadium — Foxborough, MA" },
    },
    teams: {
      home: { name: "New England Patriots" },
      away: { name: "Buffalo Bills" },
    },
  },
  {
    fixture: {
      id: 2006,
      date: "2025-12-14T13:00:00",
      venue: { name: "MetLife Stadium — East Rutherford, NJ" },
    },
    teams: {
      home: { name: "New York Giants" },
      away: { name: "Washington Commanders" },
    },
  },
  {
    fixture: {
      id: 2007,
      date: "2025-12-14T13:00:00",
      venue: { name: "Lincoln Financial Field — Philadelphia, PA" },
    },
    teams: {
      home: { name: "Philadelphia Eagles" },
      away: { name: "Tennessee Titans" },
    },
  },
  {
    fixture: {
      id: 2008,
      date: "2025-12-14T13:00:00",
      venue: { name: "EverBank Stadium — Jacksonville, FL" },
    },
    teams: {
      home: { name: "Jacksonville Jaguars" },
      away: { name: "Las Vegas Raiders" },
    },
  },
  {
    fixture: {
      id: 2009,
      date: "2025-12-14T13:00:00",
      venue: { name: "NRG Stadium — Houston, TX" },
    },
    teams: {
      home: { name: "Houston Texans" },
      away: { name: "New Orleans Saints" },
    },
  },
  {
    fixture: {
      id: 2010,
      date: "2025-12-14T16:25:00",
      venue: { name: "Lumen Field — Seattle, WA" },
    },
    teams: {
      home: { name: "Seattle Seahawks" },
      away: { name: "Arizona Cardinals" },
    },
  },
  {
    fixture: {
      id: 2011,
      date: "2025-12-14T16:25:00",
      venue: { name: "SoFi Stadium — Inglewood, CA" },
    },
    teams: {
      home: { name: "Los Angeles Rams" },
      away: { name: "Green Bay Packers" },
    },
  },
  {
    fixture: {
      id: 2012,
      date: "2025-12-14T16:25:00",
      venue: { name: "AT&T Stadium — Arlington, TX" },
    },
    teams: {
      home: { name: "Dallas Cowboys" },
      away: { name: "Carolina Panthers" },
    },
  },
  {
    fixture: {
      id: 2013,
      date: "2025-12-14T16:25:00",
      venue: { name: "Acrisure Stadium — Pittsburgh, PA" },
    },
    teams: {
      home: { name: "Pittsburgh Steelers" },
      away: { name: "Cincinnati Bengals" },
    },
  },
  {
    fixture: {
      id: 2014,
      date: "2025-12-14T16:25:00",
      venue: { name: "Levi's Stadium — Santa Clara, CA" },
    },
    teams: {
      home: { name: "San Francisco 49ers" },
      away: { name: "Tennessee Titans" },
    },
  },
  {
    fixture: {
      id: 2015,
      date: "2025-12-14T16:25:00",
      venue: { name: "U.S. Bank Stadium — Minneapolis, MN" },
    },
    teams: {
      home: { name: "Minnesota Vikings" },
      away: { name: "Indianapolis Colts" },
    },
  },
  {
    fixture: {
      id: 2016,
      date: "2025-12-15T20:15:00",
      venue: { name: "Acrisure Stadium — Pittsburgh, PA" },
    },
    teams: {
      home: { name: "Pittsburgh Steelers" },
      away: { name: "Miami Dolphins" },
    },
  },
];

const NFL_FORM = {
  "Philadelphia Eagles": ["W", "W", "L", "W", "W"],
  "Kansas City Chiefs": ["W", "L", "W", "W", "D"],
};

const FALLBACK_PREDICTIONS = {
  2001: { homeProb: 0.46, drawProb: 0.04, awayProb: 0.5, suggested: "away" },
  2002: { homeProb: 0.41, drawProb: 0.07, awayProb: 0.52, suggested: "away" },
  2003: { homeProb: 0.49, drawProb: 0.05, awayProb: 0.46, suggested: "home" },
  2004: { homeProb: 0.63, drawProb: 0.04, awayProb: 0.33, suggested: "home" },
  2005: { homeProb: 0.34, drawProb: 0.06, awayProb: 0.6, suggested: "away" },
  2006: { homeProb: 0.53, drawProb: 0.05, awayProb: 0.42, suggested: "home" },
  2007: { homeProb: 0.68, drawProb: 0.04, awayProb: 0.28, suggested: "home" },
  2008: { homeProb: 0.58, drawProb: 0.05, awayProb: 0.37, suggested: "home" },
  2009: { homeProb: 0.51, drawProb: 0.05, awayProb: 0.44, suggested: "home" },
  2010: { homeProb: 0.55, drawProb: 0.05, awayProb: 0.4, suggested: "home" },
  2011: { homeProb: 0.47, drawProb: 0.05, awayProb: 0.48, suggested: "away" },
  2012: { homeProb: 0.66, drawProb: 0.05, awayProb: 0.29, suggested: "home" },
  2013: { homeProb: 0.52, drawProb: 0.05, awayProb: 0.43, suggested: "home" },
  2014: { homeProb: 0.64, drawProb: 0.04, awayProb: 0.32, suggested: "home" },
  2015: { homeProb: 0.45, drawProb: 0.06, awayProb: 0.49, suggested: "away" },
  2016: { homeProb: 0.44, drawProb: 0.06, awayProb: 0.5, suggested: "away" },
};

function NFL() {
  const [matches, setMatches] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [topScorers, setTopScorers] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [matchdaySize, setMatchdaySize] = useState(5);

  // NEW: Predictions state
  const [preds, setPreds] = useState({});
  const predictionsPending = matches.some(
    (m) => !preds[m.fixture.id] && !FALLBACK_PREDICTIONS[m.fixture.id]
  );

  // -------------------------
  // Upcoming Fixtures (placeholder)
  // -------------------------
  useEffect(() => {
    setMatches(NFL_SCHEDULE.slice(0, matchdaySize));
    setLoading(false);
  }, [matchdaySize]);

  // -------------------------
  // Prediction Engine (NEW)
  // -------------------------
  useEffect(() => {
    let cancelled = false;

    (async () => {
      const next = {};

      for (const m of matches) {
        try {
          const data = await postJson("/predict", {
            home_team: m.teams.home.name,
            away_team: m.teams.away.name,
            league: "NFL",
          });

          if (!cancelled && m.fixture?.id) next[m.fixture.id] = data;
        } catch (e) {
          // don’t break NFL page
        }
      }

      if (!cancelled) setPreds((p) => ({ ...p, ...next }));
    })();

    return () => {
      cancelled = true;
    };
  }, [matches]);

  // -------------------------
  // Table (placeholder)
  // -------------------------
  useEffect(() => {
    setTableData(NFL_STANDINGS);
  }, []);

  // -------------------------
  // Top Scorers (placeholder)
  // -------------------------
  useEffect(() => {
    const fakeScorers = [
      { player: "Drake Maye", team: "New England Patriots", Yards: 3412, image: Maye},
      { player: "Dak Prescott", team: "Dallas Cowboys", Yards: 3261, image: Prescott},
    ];
    setTopScorers(fakeScorers);
  }, []);

  // -------------------------
  // Recent Results (placeholder)
  // -------------------------
  useEffect(() => {
    const fakeRecent = [
      {
        fixture: { id: 10, date: "2025-12-01T20:00:00" },
        teams: {
          home: { name: "New England Patriots" },
          away: { name: "New York Giants" },
        },
      },
    ];
    setRecent(fakeRecent);
  }, []);

  // -------------------------
  // Helpers
  // -------------------------
  const getLogo = (team) => NFL_LOGOS[team] || DEFAULT_LOGO;

  const renderFormBadges = (team) =>
    (NFL_FORM[team] || []).map((r, i) => (
      <span key={i} className={`form-badge form-${r.toLowerCase()}`}>
        {r}
      </span>
    ));

  const extractPredictionView = (fixtureId) => {
    const fallback = FALLBACK_PREDICTIONS[fixtureId];
    const prediction = preds[fixtureId];
    const source = prediction ?? fallback ?? {};

    const homeProb = source.probs?.home_win ?? source.homeProb ?? 0;
    const awayProb = source.probs?.away_win ?? source.awayProb ?? 0;
    const drawProb = source.probs?.draw ?? source.drawProb ?? 0;
    const suggestedRaw = source.suggested ?? (homeProb >= awayProb ? "home" : "away");
    const suggested =
      typeof suggestedRaw === "string" ? suggestedRaw.toLowerCase() : suggestedRaw;

    return { homeProb, awayProb, drawProb, suggested };
  };

  const getInitials = (name) =>
    name
      .split(" ")
      .map((n) => n[0])
      .join("");

  return (
    <>
      <Navbar />
      <main className="page nfl-page">
        {/* Upcoming Matches */}
        <h1 className="page-title fade-in">NFL – Upcoming Games</h1>

        {loading && <p className="status-msg">Loading games…</p>}
        {errorMsg && <p className="status-msg error">{errorMsg}</p>}

        <section className="matchday-section fade-in">
          <h2 className="section-title">Game Selector</h2>
          <div className="matchday-controls">
            <label>
              Show next{" "}
              <select
                value={matchdaySize}
                onChange={(e) => setMatchdaySize(parseInt(e.target.value))}
              >
                <option value={5}>5 games</option>
                <option value={10}>10 games</option>
                <option value={15}>15 games</option>
              </select>{" "}
              from the schedule
            </label>
          </div>
        </section>

        <div className="matches-grid fade-in">
          {matches.map((match) => {
            const home = match.teams.home.name;
            const away = match.teams.away.name;

            return (
              <div key={match.fixture.id} className="match-card nfl-match-card">
                <div className="match-teams">
                  <div className="team">
                    <img src={getLogo(home)} className="team-logo" />
                    <span className="team-name">{home}</span>
                  </div>

                  <span className="vs">vs</span>

                  <div className="team">
                    <img src={getLogo(away)} className="team-logo" />
                    <span className="team-name">{away}</span>
                  </div>
                </div>

                <p className="match-date">
                  📅 {new Date(match.fixture.date).toLocaleString()}
                </p>

                <p className="match-venue">
                  🏟 {match.fixture.venue?.name ?? "Unknown Stadium"}
                </p>

                <p className="match-status status-upcoming">UPCOMING</p>
              </div>
            );
          })}
        </div>

        <div className="section-divider" />

        {/* Predictions Section */}
        <h1 className="page-title fade-in">NFL Predictions</h1>
        {predictionsPending && (
          <p className="status-msg fade-in">Calculating predictions...</p>
        )}

        <section className="matches-grid fade-in">
          {matches.map((match) => {
            const home = match.teams.home.name;
            const away = match.teams.away.name;
            const view = extractPredictionView(match.fixture.id);

            const outcomeLabel =
              view.suggested === "draw"
                ? "Draw"
                : view.suggested === "home"
                  ? home
                  : view.suggested === "away"
                    ? away
                    : view.suggested?.toString().toUpperCase() || "—";

            return (
              <div key={`pred-${match.fixture.id}`} className="match-card prediction-card">
                <div className="match-teams">
                  <div className="team">
                    <img src={getLogo(home)} className="team-logo" />
                    <span className="team-name">{home}</span>
                  </div>

                  <span className="vs">vs</span>

                  <div className="team">
                    <img src={getLogo(away)} className="team-logo" />
                    <span className="team-name">{away}</span>
                  </div>
                </div>

                <p className="match-date">
                  📅 {new Date(match.fixture.date).toLocaleString()}
                </p>

                <div className="prediction-block">
                  <p>
                    <strong>Prediction:</strong> {outcomeLabel}
                  </p>
                  <p>
                    🏠 {home}: {(view.homeProb * 100).toFixed(1)}% &nbsp;|&nbsp;
                    🤝 Draw: {(view.drawProb * 100).toFixed(1)}% &nbsp;|&nbsp; ✈️ {away}: {(
                      view.awayProb * 100
                    ).toFixed(1)}%
                  </p>
                </div>
              </div>
            );
          })}
        </section>

        <div className="section-divider" />

        {/* NFL Table */}
        <h1 className="page-title fade-in">NFL Standings</h1>
        <section className="table-section fade-in">
          {tableData.map((conference) => (
            <div key={conference.conference} className="conference-block">
              <h2 className="section-title">{conference.conference}</h2>
              {conference.divisions.map((division) => (
                <div key={division.name} className="table-wrapper division-wrapper">
                  <h3 className="division-title">{division.name}</h3>
                  <table className="nfl-table">
                    <thead>
                      <tr>
                        <th>Pos</th>
                        <th>Team</th>
                        <th>W</th>
                        <th>L</th>
                        <th>T</th>
                        <th>PCT</th>
                        <th>PF</th>
                        <th>PA</th>
                        <th>Net</th>
                        <th>DIV</th>
                        <th>CONF</th>
                        <th>HOME</th>
                        <th>AWAY</th>
                        <th>STK</th>
                      </tr>
                    </thead>

                    <tbody>
                      {division.teams.map((row, index) => (
                        <tr key={row.team}>
                          <td>{index + 1}</td>

                          <td className="team-cell">
                            <img
                              src={getLogo(row.team)}
                              className="table-team-logo"
                            />
                            {row.team}
                          </td>

                          <td>{row.w}</td>
                          <td>{row.l}</td>
                          <td>{row.t}</td>
                          <td>{row.pct}</td>
                          <td>{row.pf}</td>
                          <td>{row.pa}</td>
                          <td>{row.net}</td>
                          <td>{row.div}</td>
                          <td>{row.conf}</td>
                          <td>{row.home}</td>
                          <td>{row.away}</td>
                          <td>{row.streak}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          ))}
        </section>

        <div className="section-divider" />

        {/* Top Scorers */}
        <h1 className="page-title fade-in">NFL – Top Players</h1>
        <section className="top-scorers-section fade-in">
          <div className="table-wrapper">
            <table className="nfl-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player</th>
                  <th>Yards</th>
                </tr>
              </thead>
              <tbody>
                {topScorers.map((row, index) => (
                  <tr key={row.player}>
                    <td>{index + 1}</td>
                    <td className="team-cell">
                      {row.image ? (
                        <img
                          src={row.image}
                          alt={row.player}
                          className="player-photo"
                        />
                      ) : (
                        <div className="player-badge">{getInitials(row.player)}</div>
                      )}
                      {row.player}
                    </td>
                    <td className="team-cell">
                      <img src={getLogo(row.team)} className="table-team-logo" />
                      {row.team}
                    </td>
                    <td>{row.Yards}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <div className="section-divider" />

        {/* Recent Games */}
        <h1 className="page-title fade-in">NFL – Recent Games</h1>
        <section className="recent-results fade-in">
          <div className="matches-grid">
            {recent.map((match) => {
              const home = match.teams.home.name;
              const away = match.teams.away.name;

              return (
                <div key={match.fixture.id} className="match-card nfl-match-card">
                  <div className="match-teams">
                    <div className="team">
                      <img src={getLogo(home)} className="team-logo" />
                      <span className="team-name">{home}</span>
                    </div>

                    <span className="vs">vs</span>

                    <div className="team">
                      <img src={getLogo(away)} className="team-logo" />
                      <span className="team-name">{away}</span>
                    </div>
                  </div>

                  <p className="match-date">
                    📅 {new Date(match.fixture.date).toLocaleString()}
                  </p>

                  <p className="match-status status-ft">FINAL</p>
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

export default NFL;