import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useGame } from '../context/GameContext';
import { useAI } from '../context/AIContext';
import BlackjackGame from '../utils/gameEngine';
import GameTableComponent from '../components/GameTable';
import { 
  ChartBarIcon
} from '@heroicons/react/24/outline';

const GameTable = () => {
  const { state: aiState, actions: aiActions, helpers } = useAI();
  
  const [selectedModel, setSelectedModel] = useState('ultimate_ai');
  const [blackjackGame, setBlackjackGame] = useState(new BlackjackGame());
  const [currentBet, setCurrentBet] = useState(100);
  const [aiPrediction, setAiPrediction] = useState(null);

  // Initialize AI model
  useEffect(() => {
    aiActions.setSelectedModel(selectedModel);
  }, [selectedModel, aiActions]);

  // Get AI prediction when game state changes
  const getAIPrediction = async () => {
    if (blackjackGame.gameState === 'playing') {
      const aiState = blackjackGame.getAIState();
      await aiActions.getPrediction(aiState);
      setAiPrediction(aiState.currentPrediction);
    }
  };

  // Game actions
  const handleNewGame = () => {
    try {
      const newGame = new BlackjackGame();
      newGame.startGame(currentBet);
      setBlackjackGame(newGame);
      setAiPrediction(null);
    } catch (error) {
      alert(error.message);
    }
  };

  const handleHit = () => {
    try {
      blackjackGame.hit();
      setBlackjackGame({ ...blackjackGame });
      getAIPrediction();
    } catch (error) {
      alert(error.message);
    }
  };

  const handleStand = () => {
    try {
      blackjackGame.stand();
      setBlackjackGame({ ...blackjackGame });
    } catch (error) {
      alert(error.message);
    }
  };

  const handleDouble = () => {
    try {
      blackjackGame.double();
      setBlackjackGame({ ...blackjackGame });
    } catch (error) {
      alert(error.message);
    }
  };

  const handleBetChange = (newBet) => {
    setCurrentBet(Math.max(10, Math.min(blackjackGame.bankroll, newBet)));
  };

  const handleModelChange = (modelName) => {
    setSelectedModel(modelName);
    aiActions.setSelectedModel(modelName);
  };

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-4">
            Blackjack Oyun Masası
          </h1>
          <p className="text-xl text-gray-300">
            AI destekli blackjack deneyimi
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Game Table */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2"
          >
            <GameTableComponent
              gameState={blackjackGame.getGameState()}
              onHit={handleHit}
              onStand={handleStand}
              onDouble={handleDouble}
              onNewGame={handleNewGame}
              onBetChange={handleBetChange}
              aiPrediction={aiPrediction}
            />
          </motion.div>

          {/* AI Panel */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-6"
          >
            {/* Model Selection */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                AI Model Seçimi
              </h3>
              
              <div className="space-y-3">
                {aiState.availableModels.map((model) => (
                  <div
                    key={model}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedModel === model
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                    onClick={() => handleModelChange(model)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-semibold">
                          {helpers.getModelDisplayName(model)}
                        </div>
                        <div className="text-sm opacity-75">
                          Grade: {helpers.getModelGrade(model)} | ROI: {helpers.getModelROI(model)}%
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs opacity-75">
                          {model === 'ultimate_ai' && '⭐'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Game Statistics */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <ChartBarIcon className="w-6 h-6 mr-2 text-green-400" />
                Oyun İstatistikleri
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">Toplam Oyun:</span>
                  <span className="text-white font-semibold">{blackjackGame.gameHistory.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Kazanılan:</span>
                  <span className="text-green-400 font-semibold">
                    {blackjackGame.gameHistory.filter(game => game.result === 'win').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Kaybedilen:</span>
                  <span className="text-red-400 font-semibold">
                    {blackjackGame.gameHistory.filter(game => game.result === 'lose').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Beraberlik:</span>
                  <span className="text-yellow-400 font-semibold">
                    {blackjackGame.gameHistory.filter(game => game.result === 'push').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Kazanma Oranı:</span>
                  <span className="text-blue-400 font-semibold">
                    {blackjackGame.getStats().winRate.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Net Kar/Zarar:</span>
                  <span className={`font-semibold ${
                    blackjackGame.getStats().netProfit >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    ${blackjackGame.getStats().netProfit.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* AI Statistics */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                AI İstatistikleri
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">Toplam Tahmin:</span>
                  <span className="text-white font-semibold">{aiState.totalPredictions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Başarılı:</span>
                  <span className="text-green-400 font-semibold">{aiState.successfulPredictions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Ortalama Güven:</span>
                  <span className="text-blue-400 font-semibold">
                    {(aiState.averageConfidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">API Durumu:</span>
                  <span className={`font-semibold ${aiState.apiConnected ? 'text-green-400' : 'text-red-400'}`}>
                    {aiState.apiConnected ? 'Bağlı' : 'Bağlantı Yok'}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                Hızlı İşlemler
              </h3>
              
              <div className="space-y-3">
                <button
                  onClick={() => {
                    const newGame = new BlackjackGame();
                    setBlackjackGame(newGame);
                    setAiPrediction(null);
                  }}
                  className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors"
                >
                  Oyunu Sıfırla
                </button>
                
                <button
                  onClick={() => {
                    setCurrentBet(100);
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
                >
                  Bahisi Sıfırla
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default GameTable; 