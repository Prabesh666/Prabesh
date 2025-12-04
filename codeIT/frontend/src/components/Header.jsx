import { motion } from "framer-motion";

const Header = () => {
  return (
    <motion.header
      className="app-header"
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="header-badge">CodeIT Institute of Nepal</div>
      <h1>CodeIT AI Assistant</h1>
      <p>Ask about courses, mentors, admissions, and everything CodeIT.</p>
    </motion.header>
  );
};

export default Header;
