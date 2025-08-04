import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAI } from '../context/AIContext';
import BlackjackTable from '../components/BlackjackTable';
import { 
  ChartBarIcon,
  ExclamationTriangleIcon,
  UserGroupIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const BlackjackAssistant = () => {
  const { state: aiState, actions: aiActions } = useAI();
  
  // Game State
  const [gameState, setGameState] = useState({
    isActive: false,
    currentRound: 0,
    playerPosition: 0,
    playerCount: 4,
    dealerCards: [],
    playerCards: [],
    otherPlayers: [],
    currentBet: 100,
    bankroll: 10000,
    playerTotal: 0,
    usableAce: false
  });

  // Risk & Budget Management
  const [riskProfile, setRiskProfile] = useState({
    riskScore: 50, // 0-100
    budgetScore: 50, // 0-100
    maxBetPercentage: 5, // % of bankroll
    stopLossPercentage: 15 // % of bankroll
  });

  // Table Analysis
  const [tableAnalysis] = useState({
    activePlayers: 0,
    tableHeat: 0, // 0-100
    playerTypes: [], // Array of player types
    tableMomentum: 'neutral' // hot, cold, neutral
  });

  // Card Tracking
  const [cardHistory, setCardHistory] = useState([]);

  // AI Analysis
  const [aiAnalysis, setAiAnalysis] = useState({
    riskLevel: 'medium',
    confidence: 0,
    recommendation: '',
    nextBetSuggestion: 0,
    reasoning: ''
  });

  // Player Segmentation
  const [playerSegmentation] = useState({
    leftPlayer: { type: 'unknown', confidence: 0, behavior: [] },
    rightPlayer: { type: 'unknown', confidence: 0, behavior: [] },
    acrossPlayer: { type: 'unknown', confidence: 0, behavior: [] }
  });

  // Initialize AI model
  useEffect(() => {
    aiActions.setSelectedModel('ultimate_ai');
  }, [aiActions]);

  // Get AI analysis when game state changes
  const getAIAnalysis = async () => {
    if (!gameState.isActive) return;

    console.log('Getting AI analysis...');

    const analysisData = {
      player_total: gameState.playerTotal,
      dealer_up: 5, // Dealer's up card is 5
      usable_ace: false,
      true_count: 0,
      bankroll: gameState.bankroll,
      risk_score: riskProfile.riskScore,
      budget_score: riskProfile.budgetScore,
      table_heat: tableAnalysis.tableHeat,
      player_position: gameState.playerPosition,
      total_players: gameState.playerCount,
      card_history: cardHistory
    };

    try {
      await aiActions.getPrediction(analysisData);
      
      // Process AI response and update analysis
      if (aiState.currentPrediction && aiState.currentPrediction.success) {
        processAIResponse(aiState.currentPrediction);
      } else {
        // Mock AI response for testing
        const mockResponse = {
          success: true,
          action: 1, // Hit
          confidence: 0.85,
          reasoning: "Dealer'ın açık kartı 5, sizin toplamınız 14. Bu durumda Hit yapmak mantıklı çünkü dealer'ın 17'ye kadar çekmesi gerekiyor ve sizin 14'ünüzle durmak riskli.",
          model_name: "ultimate_ai",
          processing_time: 0.001,
          risk_level: "medium",
          bet_suggestion: 120,
          budget_analysis: {
            base_bet: 100,
            risk_multiplier: 1.0,
            confidence_multiplier: 0.85,
            recommended_bet: 120,
            budget_utilization: 1.2
          },
          player_segmentation: {
            left_player: {"type": "unknown", "confidence": 0.0},
            right_player: {"type": "unknown", "confidence": 0.0},
            across_player: {"type": "unknown", "confidence": 0.0}
          },
          table_analysis: {
            heat_level: 30.0,
            player_position: 2,
            total_players: 5,
            table_momentum: "neutral"
          }
        };
        
        processAIResponse(mockResponse);
      }
    } catch (error) {
      console.error('AI Analysis error:', error);
      
      // Fallback mock response
      const mockResponse = {
        success: true,
        action: 1,
        confidence: 0.8,
        reasoning: "Dealer 5 gösteriyor, sizin 14'ünüz var. Hit yapmanızı öneriyorum.",
        risk_level: "medium",
        bet_suggestion: 100
      };
      
      processAIResponse(mockResponse);
    }
  };

  const processAIResponse = (prediction) => {
    console.log('Processing AI response:', prediction);
    
    const action = prediction.action;
    const confidence = prediction.confidence || 0.8;
    
    // Determine risk level based on confidence and action
    let riskLevel = prediction.risk_level || 'medium';
    if (confidence > 0.8) riskLevel = 'low';
    else if (confidence < 0.5) riskLevel = 'high';

    // Calculate next bet suggestion
    const nextBet = prediction.bet_suggestion || 100;

    setAiAnalysis({
      riskLevel,
      confidence: confidence * 100,
      recommendation: getActionName(action),
      nextBetSuggestion: nextBet,
      reasoning: prediction.reasoning || 'AI analysis based on current game state'
    });
    
    console.log('AI Analysis updated:', {
      riskLevel,
      confidence: confidence * 100,
      recommendation: getActionName(action),
      nextBetSuggestion: nextBet,
      reasoning: prediction.reasoning
    });
  };

  const getActionName = (action) => {
    switch (action) {
      case 0: return 'Stand';
      case 1: return 'Hit';
      case 2: return 'Double';
      case 3: return 'Split';
      default: return 'Unknown';
    }
  };

  // Start new game session
  const startSession = () => {
    console.log('Starting new game session...');
    
    // Initialize dealer cards
    const dealerCards = [
      { value: '5', suit: '♣', isVisible: true },
      { value: '?', suit: '?', isVisible: false }
    ];
    
    // Initialize player cards
    const playerCards = [
      { value: '4', suit: '♥', isVisible: true },
      { value: 'K', suit: '♣', isVisible: true }
    ];
    
    // Initialize other players
    const otherPlayers = [
      { cards: [], bet: 0 },
      { cards: [{ value: '9', suit: '♥', isVisible: true }, { value: '7', suit: '♠', isVisible: true }], bet: 100 },
      { cards: [], bet: 0 },
      { cards: [{ value: '10', suit: '♦', isVisible: true }, { value: 'A', suit: '♠', isVisible: true }], bet: 100 }
    ];
    
    setGameState(prev => ({ 
      ...prev, 
      isActive: true, 
      currentRound: 1,
      dealerCards: dealerCards,
      playerCards: playerCards,
      otherPlayers: otherPlayers,
      playerTotal: 14 // 4 + K = 14
    }));
    
    setCardHistory([
      { card: '5♣', player: 'dealer', timestamp: Date.now() },
      { card: '?', player: 'dealer', timestamp: Date.now() },
      { card: '4♥', player: 'player', timestamp: Date.now() },
      { card: 'K♣', player: 'player', timestamp: Date.now() }
    ]);
    
    // Trigger AI analysis
    setTimeout(() => {
      getAIAnalysis();
    }, 1000);
  };

  // Stop current session
  const stopSession = () => {
    setGameState(prev => ({ ...prev, isActive: false }));
  };

  // Update player count
  const updatePlayerCount = (count) => {
    setGameState(prev => ({ 
      ...prev, 
      playerCount: count,
      playerPosition: Math.min(prev.playerPosition, count - 1)
    }));
  };

  // Update player position
  const updatePlayerPosition = (position) => {
    setGameState(prev => ({ ...prev, playerPosition: position }));
  };

  // Update bet
  const updateBet = (bet) => {
    setGameState(prev => ({ ...prev, currentBet: bet }));
  };

  // Add card to history
  const addCard = (card, player = 'dealer') => {
    setCardHistory(prev => [...prev, { card, player, timestamp: Date.now() }]);
  };

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-4">
            Blackjack AI Asistanı
          </h1>
          <p className="text-xl text-gray-300">
            Risk analizi, bütçe optimizasyonu ve masa stratejisi
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Game Interface */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2 space-y-6"
          >
            {/* Blackjack Table */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-4">Blackjack Masası</h2>
              <BlackjackTable
                gameState={gameState}
                onStartGame={startSession}
                onStopGame={stopSession}
                onAddCard={addCard}
                onUpdatePlayerCount={updatePlayerCount}
                onUpdatePlayerPosition={updatePlayerPosition}
                onUpdateBet={updateBet}
              />
            </div>

            {/* AI Analysis */}
            {gameState.isActive && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-800 bg-opacity-50 rounded-lg p-6"
              >
                <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                  <ChartBarIcon className="w-8 h-8 mr-3 text-green-400" />
                  AI Analizi
                </h2>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="bg-gray-700 rounded-lg p-4">
                      <h3 className="text-white font-semibold mb-2">Risk Değerlendirmesi</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Risk Seviyesi:</span>
                          <span className={`font-semibold ${
                            aiAnalysis.riskLevel === 'low' ? 'text-green-400' :
                            aiAnalysis.riskLevel === 'medium' ? 'text-yellow-400' :
                            'text-red-400'
                          }`}>
                            {aiAnalysis.riskLevel.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Güven:</span>
                          <span className="text-blue-400 font-semibold">
                            {aiAnalysis.confidence.toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Önerilen Aksiyon:</span>
                          <span className="text-green-400 font-semibold">
                            {aiAnalysis.recommendation}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-700 rounded-lg p-4">
                      <h3 className="text-white font-semibold mb-2">Bütçe Önerisi</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Sonraki El Bahisi:</span>
                          <span className="text-green-400 font-semibold">
                            ${aiAnalysis.nextBetSuggestion}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Bütçe Kullanımı:</span>
                          <span className="text-blue-400 font-semibold">
                            {((aiAnalysis.nextBetSuggestion / 10000) * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-white font-semibold mb-2">AI Yorumu</h3>
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {aiAnalysis.reasoning || 'Oyun başladığında AI analizi burada görünecek...'}
                    </p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Card Input Panel */}
            {gameState.isActive && (
              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
                <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                  <ClockIcon className="w-8 h-8 mr-3 text-blue-400" />
                  Kart Takibi
                </h2>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-white font-semibold mb-4">Yeni Kart Ekle</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-gray-300 text-sm mb-2">Kart Değeri</label>
                        <select 
                          className="w-full bg-gray-600 text-white px-3 py-2 rounded-lg"
                          onChange={(e) => {
                            const cardValue = e.target.value;
                            if (cardValue) {
                              addCard(cardValue, 'player');
                              // Update player hand
                              const newCards = [...gameState.playerCards, { value: cardValue, suit: '♠', isVisible: true }];
                              setGameState(prev => ({
                                ...prev,
                                playerCards: newCards,
                                playerTotal: prev.playerTotal + (cardValue === 'A' ? 11 : ['J', 'Q', 'K'].includes(cardValue) ? 10 : parseInt(cardValue))
                              }));
                              // Trigger AI analysis
                              setTimeout(() => getAIAnalysis(), 500);
                            }
                          }}
                        >
                          <option value="">Kart seçin...</option>
                          <option value="A">A (As)</option>
                          <option value="2">2</option>
                          <option value="3">3</option>
                          <option value="4">4</option>
                          <option value="5">5</option>
                          <option value="6">6</option>
                          <option value="7">7</option>
                          <option value="8">8</option>
                          <option value="9">9</option>
                          <option value="10">10</option>
                          <option value="J">J (Vale)</option>
                          <option value="Q">Q (Kız)</option>
                          <option value="K">K (Papaz)</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-white font-semibold mb-4">Kart Geçmişi</h3>
                    <div className="max-h-48 overflow-y-auto space-y-2">
                      {cardHistory.length > 0 ? (
                        cardHistory.map((entry, index) => (
                          <div key={index} className="flex justify-between text-sm bg-gray-600 p-2 rounded">
                            <span className="text-gray-300">
                              {entry.player === 'dealer' ? 'Dealer' : 'Siz'}: {entry.card}
                            </span>
                            <span className="text-gray-400">
                              {new Date(entry.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-400 text-center">Henüz kart kaydı yok</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}


          </motion.div>

          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-6"
          >
            {/* Risk Profile */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <ExclamationTriangleIcon className="w-6 h-6 mr-2 text-red-400" />
                Risk Profili
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-2">
                    Risk Puanı: {riskProfile.riskScore}/100
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={riskProfile.riskScore}
                    onChange={(e) => setRiskProfile(prev => ({
                      ...prev,
                      riskScore: parseInt(e.target.value)
                    }))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 text-sm mb-2">
                    Bütçe Puanı: {riskProfile.budgetScore}/100
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={riskProfile.budgetScore}
                    onChange={(e) => setRiskProfile(prev => ({
                      ...prev,
                      budgetScore: parseInt(e.target.value)
                    }))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Max Bahis %</label>
                    <input
                      type="number"
                      value={riskProfile.maxBetPercentage}
                      onChange={(e) => setRiskProfile(prev => ({
                        ...prev,
                        maxBetPercentage: parseInt(e.target.value)
                      }))}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Stop Loss %</label>
                    <input
                      type="number"
                      value={riskProfile.stopLossPercentage}
                      onChange={(e) => setRiskProfile(prev => ({
                        ...prev,
                        stopLossPercentage: parseInt(e.target.value)
                      }))}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Player Segmentation */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <UserGroupIcon className="w-6 h-6 mr-2 text-purple-400" />
                Oyuncu Analizi
              </h3>
              
              <div className="space-y-4">
                {Object.entries(playerSegmentation).map(([position, player]) => (
                  <div key={position} className="bg-gray-700 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white font-semibold capitalize">
                        {position.replace('Player', ' Oyuncu')}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        player.confidence > 0.7 ? 'bg-green-600 text-white' :
                        player.confidence > 0.4 ? 'bg-yellow-600 text-white' :
                        'bg-gray-600 text-white'
                      }`}>
                        {player.confidence.toFixed(1)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-300">
                      Tip: {player.type}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                Hızlı İşlemler
              </h3>
              
              <div className="space-y-3">
                <button
                  onClick={getAIAnalysis}
                  disabled={!gameState.isActive}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors"
                >
                  AI Analizi Al
                </button>
                
                <button
                  onClick={() => setCardHistory([])}
                  className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors"
                >
                  Kart Geçmişini Temizle
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default BlackjackAssistant; 