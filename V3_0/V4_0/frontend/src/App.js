import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Home from './pages/Home';
import GameTable from './pages/GameTable';
import BlackjackAssistant from './pages/BlackjackAssistant';
import AIAnalysis from './pages/AIAnalysis';
import ModelComparison from './pages/ModelComparison';
import Settings from './pages/Settings';
import Footer from './components/Footer';

// Context
import { GameProvider } from './context/GameContext';
import { AIProvider } from './context/AIContext';

function App() {
  return (
    <GameProvider>
      <AIProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-green-700">
            <Navbar />
            
            <motion.main 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="container mx-auto px-4 py-8"
            >
                      <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/game" element={<GameTable />} />
          <Route path="/assistant" element={<BlackjackAssistant />} />
          <Route path="/analysis" element={<AIAnalysis />} />
          <Route path="/models" element={<ModelComparison />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
            </motion.main>
            
            <Footer />
          </div>
        </Router>
      </AIProvider>
    </GameProvider>
  );
}

export default App; 