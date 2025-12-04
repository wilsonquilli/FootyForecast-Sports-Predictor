import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "./Pages.css";
import video from "../assets/ff-video.mov";
import PLlogo from "../assets/premier-league.png";
import LLlogo from "../assets/laliga.png";
import NFLlogo from "../assets/NFL.png";
import { motion, useScroll, useTransform } from "framer-motion";

const sectionVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, staggerChildren: 0.3 },
  },
};

const childVariants = {
  hidden: { opacity: 0, x: -30 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.6 } },
};

function Home() {
  const { scrollYProgress } = useScroll();
  const scale = useTransform(scrollYProgress, [0, 1], [1, 1.05]);

  const sections = [
    {
      title: "Premier League",
      img: PLlogo,
      text: "Stay ahead of the game with our data-driven Premier League predictions. From weekly match outcomes to form-based insights, get the edge you need for every fixture.",
      class: "home-premier-league",
    },
    {
      title: "LaLiga",
      img: LLlogo,
      text: "Experience the passion of Spanish football with our LaLiga predictions. From El Clásico showdowns to underdog surprises, we deliver match insights and forecasts for every round.",
      class: "home-laliga",
    },
    {
      title: "NFL",
      img: NFLlogo,
      text: "Get game-winning insights with our NFL predictions. From weekly matchups to playoff races, we break down the stats and trends that shape every game.",
      class: "home-nfl",
    },
  ];

  return (
    <>
      <Navbar />

      {/* HOME PAGE WRAPPER */}
      <main className="home-page">

        {/* HERO VIDEO SECTION */}
        <motion.section
          className="home-hero"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
        >
          <div className="video">
            <video src={video} controls autoPlay muted playsInline />
          </div>
        </motion.section>

        {/* FEATURED TITLE */}
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          Featured on FootyForecast
        </motion.h1>

        {/* FEATURED SECTIONS */}
        {sections.map((section, i) => (
          <motion.section
            key={i}
            className={section.class}
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            animate={{ y: [0, -5, 0] }}
            transition={{
              duration: 6,
              repeat: Infinity,
              repeatType: "loop",
              ease: "easeInOut",
            }}
          >
            <motion.div className="home-league-media" variants={childVariants} style={{ scale }}>
              <motion.img
                src={section.img}
                alt={section.title}
                variants={{
                  hidden: { opacity: 0, x: -40 },
                  visible: {
                    opacity: 1,
                    x: 0,
                    transition: { duration: 0.8 },
                  },
                }}
                whileHover={{ rotate: 5, scale: 1.1 }}
              />
            </motion.div>

            <motion.div className="home-league-copy" variants={childVariants}>
              <motion.h1 variants={childVariants}>{section.title}</motion.h1>
              <motion.p variants={childVariants}>{section.text}</motion.p>
            </motion.div>
          </motion.section>
        ))}
      </main>

      <Footer />
    </>
  );
}

export default Home;