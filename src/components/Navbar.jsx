import { Link } from "react-router-dom";
import { useState } from "react";
import "./Components.css";
import Logo from "../assets/logo.png";
import { motion } from "framer-motion";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const toggleMenu = () => setMenuOpen(!menuOpen);

  const navLinks = [
    { to: "/", label: "Home" },
    { to: "/premierleague", label: "Premier League" },
    { to: "/laliga", label: "LaLiga" },
    { to: "/nfl", label: "NFL" },
  ];

  return (
    <nav className="navbar-container">
      <Link to="/" className="logo">
        <motion.img src={Logo} alt="FootyForecast" whileHover={{ scale: 1.1 }} />
        <motion.h1 whileHover={{ scale: 1.05, color: "#00e676" }}>
          FootyForecast
        </motion.h1>
      </Link>

      <motion.div
        className={`hamburger ${menuOpen ? "open" : ""}`}
        onClick={toggleMenu}
        whileTap={{ scale: 0.9 }}
      >
        <span></span>
        <span></span>
        <span></span>
      </motion.div>

      <div className={`nav-links ${menuOpen ? "active" : ""}`}>
        {navLinks.map((link, i) => (
          <motion.div key={i} whileHover={{ scale: 1.1 }}>
            <Link to={link.to} onClick={() => setMenuOpen(false)}>
              {link.label}
            </Link>
          </motion.div>
        ))}
      </div>
    </nav>
  );
}

export default Navbar;