import "./Components.css";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

function Footer() {
  const navigate = useNavigate();

  const linkHover = { scale: 1.1, color: "#00C853" };

  return (
    <footer>
      <div className="footer">
        &copy; 2025 FootyForecast |
        <motion.span
          className="footer-link"
          whileHover={linkHover}
          style={{ cursor: "pointer" }}
          onClick={() => navigate("/premierleague")}
        >
          Premier League
        </motion.span>{" "}
        |
        <motion.span
          className="footer-link"
          whileHover={linkHover}
          style={{ cursor: "pointer" }}
          onClick={() => navigate("/laliga")}
        >
          LaLiga
        </motion.span>{" "}
        |
        <motion.span
          className="footer-link"
          whileHover={linkHover}
          style={{ cursor: "pointer" }}
          onClick={() => navigate("/nfl")}
        >
          NFL
        </motion.span>
      </div>
    </footer>
  );
}

export default Footer;