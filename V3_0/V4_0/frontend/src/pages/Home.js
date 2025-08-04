import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  PlayIcon, 
  ChartBarIcon, 
  CogIcon, 
  BeakerIcon,
  TrophyIcon,
  BoltIcon
} from '@heroicons/react/24/outline';

const Home = () => {
  const features = [
    {
      icon: BoltIcon,
      title: "Advanced AI Models",
      description: "8 different AI models with proven performance, from simple to ultimate 4-level hierarchical systems.",
      color: "bg-blue-500"
    },
    {
      icon: ChartBarIcon,
      title: "Real-time Analysis",
      description: "Live performance tracking, win rate analysis, and detailed game statistics.",
      color: "bg-green-500"
    },
    {
      icon: BeakerIcon,
      title: "Model Comparison",
      description: "Compare different AI strategies side-by-side with comprehensive metrics.",
      color: "bg-purple-500"
    },
    {
      icon: TrophyIcon,
      title: "Performance Tracking",
      description: "Track your progress with detailed analytics and performance insights.",
      color: "bg-yellow-500"
    }
  ];

  const stats = [
    { label: "AI Models", value: "8", description: "Different strategies" },
    { label: "Performance", value: "A+", description: "Top grade models" },
    { label: "ROI", value: "51%", description: "Best performing model" },
    { label: "Games Played", value: "100K+", description: "Tested hands" }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <motion.section 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center py-20"
      >
        <div className="max-w-4xl mx-auto px-4">
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-5xl md:text-7xl font-bold text-white mb-6"
          >
            Blackjack AI
            <span className="block text-4xl md:text-5xl text-green-400 mt-2">
              V4.0
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto"
          >
            Experience the future of blackjack with our advanced AI system. 
            Multiple models, real-time analysis, and proven performance.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link
              to="/game"
              className="inline-flex items-center px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200"
            >
              <PlayIcon className="w-6 h-6 mr-2" />
              Start Playing
            </Link>
            
            <Link
              to="/analysis"
              className="inline-flex items-center px-8 py-4 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-colors duration-200"
            >
              <ChartBarIcon className="w-6 h-6 mr-2" />
              View Analysis
            </Link>
          </motion.div>
        </div>
      </motion.section>

      {/* Stats Section */}
      <motion.section 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.8 }}
        className="py-16 bg-black bg-opacity-20"
      >
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1 + index * 0.1, duration: 0.5 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-green-400 mb-2">
                  {stat.value}
                </div>
                <div className="text-lg font-semibold text-white mb-1">
                  {stat.label}
                </div>
                <div className="text-sm text-gray-400">
                  {stat.description}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Features Section */}
      <motion.section 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 0.8 }}
        className="py-20"
      >
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Advanced Features
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Our V4.0 system brings together cutting-edge AI technology with 
              comprehensive analysis tools for the ultimate blackjack experience.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.4 + index * 0.1, duration: 0.6 }}
                className="bg-gray-800 bg-opacity-50 rounded-lg p-6 hover:bg-opacity-70 transition-all duration-200"
              >
                <div className={`inline-flex p-3 rounded-lg ${feature.color} mb-4`}>
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-300">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.8, duration: 0.8 }}
        className="py-20 bg-black bg-opacity-30"
      >
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Experience the Future?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of players who have already discovered the power of AI-driven blackjack.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/game"
              className="inline-flex items-center px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200"
            >
              <PlayIcon className="w-6 h-6 mr-2" />
              Start Playing Now
            </Link>
            
            <Link
              to="/models"
              className="inline-flex items-center px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200"
            >
              <BeakerIcon className="w-6 h-6 mr-2" />
              Explore Models
            </Link>
          </div>
        </div>
      </motion.section>

      {/* Quick Navigation */}
      <motion.section 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2.2, duration: 0.6 }}
        className="py-12"
      >
        <div className="max-w-4xl mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-6">
            <Link
              to="/game"
              className="group bg-gray-800 bg-opacity-50 rounded-lg p-6 hover:bg-opacity-70 transition-all duration-200"
            >
              <div className="flex items-center mb-4">
                <PlayIcon className="w-8 h-8 text-green-400 mr-3" />
                <h3 className="text-xl font-semibold text-white">Game Table</h3>
              </div>
              <p className="text-gray-300">
                Play blackjack with AI assistance and real-time predictions.
              </p>
            </Link>
            
            <Link
              to="/analysis"
              className="group bg-gray-800 bg-opacity-50 rounded-lg p-6 hover:bg-opacity-70 transition-all duration-200"
            >
              <div className="flex items-center mb-4">
                <ChartBarIcon className="w-8 h-8 text-blue-400 mr-3" />
                <h3 className="text-xl font-semibold text-white">AI Analysis</h3>
              </div>
              <p className="text-gray-300">
                View detailed performance analytics and AI insights.
              </p>
            </Link>
            
            <Link
              to="/settings"
              className="group bg-gray-800 bg-opacity-50 rounded-lg p-6 hover:bg-opacity-70 transition-all duration-200"
            >
              <div className="flex items-center mb-4">
                <CogIcon className="w-8 h-8 text-purple-400 mr-3" />
                <h3 className="text-xl font-semibold text-white">Settings</h3>
              </div>
              <p className="text-gray-300">
                Customize your experience and AI preferences.
              </p>
            </Link>
          </div>
        </div>
      </motion.section>
    </div>
  );
};

export default Home; 