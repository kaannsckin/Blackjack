import React from 'react';
import { motion } from 'framer-motion';
import { 
  PlayIcon, 
  StopIcon,
  PlusIcon,
  MinusIcon
} from '@heroicons/react/24/outline';

const BlackjackTable = ({ 
  gameState, 
  onStartGame, 
  onStopGame, 
  onAddCard,
  onUpdatePlayerCount,
  onUpdatePlayerPosition,
  onUpdateBet
}) => {
  const {
    isActive = false,
    playerCount = 4,
    playerPosition = 0,
    dealerCards = [],
    playerCards = [],
    otherPlayers = [],
    currentBet = 100,
    bankroll = 10000
  } = gameState;

  // Generate player positions based on count
  const generatePlayerPositions = (count) => {
    const positions = [];
    const angleStep = 120 / (count - 1); // 120 degrees spread
    
    for (let i = 0; i < count; i++) {
      const angle = -60 + (i * angleStep); // Start from -60 degrees
      positions.push({
        id: i,
        angle: angle,
        isCurrentPlayer: i === playerPosition,
        cards: i === playerPosition ? playerCards : otherPlayers[i]?.cards || [],
        bet: i === playerPosition ? currentBet : otherPlayers[i]?.bet || 0
      });
    }
    return positions;
  };

  const playerPositions = generatePlayerPositions(playerCount);

  const getCardDisplay = (card) => {
    if (!card) return null;
    
    const suitSymbols = {
      '♠': '♠',
      '♥': '♥',
      '♦': '♦',
      '♣': '♣'
    };

    return {
      value: card.value,
      suit: suitSymbols[card.suit],
      color: ['♥', '♦'].includes(card.suit) ? 'text-red-600' : 'text-gray-800',
      isVisible: card.isVisible !== false
    };
  };

  const getChipColor = (value) => {
    if (value >= 1000) return 'bg-purple-600';
    if (value >= 500) return 'bg-black';
    if (value >= 100) return 'bg-green-600';
    if (value >= 25) return 'bg-red-600';
    if (value >= 5) return 'bg-blue-600';
    return 'bg-white';
  };

  const getChipTextColor = (value) => {
    if (value >= 1000) return 'text-white';
    if (value >= 500) return 'text-white';
    if (value >= 100) return 'text-white';
    if (value >= 25) return 'text-white';
    if (value >= 5) return 'text-white';
    return 'text-gray-800';
  };

  return (
    <div className="relative w-full max-w-6xl mx-auto">
      {/* Blackjack Table */}
      <div className="relative bg-gradient-to-b from-green-800 to-green-900 rounded-t-full border-8 border-amber-800 shadow-2xl">
        {/* Table felt pattern */}
        <div className="absolute inset-0 bg-green-700 opacity-20 rounded-t-full"></div>
        
        {/* Table rules text */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 text-white text-sm font-semibold text-center">
          <div>BLACKJACK PAYS 3 TO 2</div>
          <div>DEALER MUST HIT SOFT 17</div>
          <div>INSURANCE PAYS 2 TO 1</div>
        </div>

        {/* Dealer Area */}
        <div className="absolute top-16 left-1/2 transform -translate-x-1/2 text-center">
          <div className="text-white font-bold mb-2">DEALER</div>
          
          {/* Card Shoe */}
          <div className="absolute -left-20 top-0">
            <div className="w-12 h-8 bg-gray-600 rounded border-2 border-gray-400 flex items-center justify-center">
              <div className="w-8 h-6 bg-red-800 rounded border border-red-600"></div>
            </div>
          </div>

          {/* Chip Rack */}
          <div className="absolute -right-20 top-0">
            <div className="w-16 h-8 bg-gray-800 rounded border-2 border-gray-600 flex items-center justify-center space-x-1">
              <div className="w-3 h-3 bg-purple-600 rounded-full border border-purple-400"></div>
              <div className="w-3 h-3 bg-black rounded-full border border-gray-400"></div>
              <div className="w-3 h-3 bg-green-600 rounded-full border border-green-400"></div>
              <div className="w-3 h-3 bg-red-600 rounded-full border border-red-400"></div>
              <div className="w-3 h-3 bg-blue-600 rounded-full border border-blue-400"></div>
            </div>
          </div>

          {/* Dealer Cards */}
          <div className="flex space-x-2 justify-center">
            {dealerCards.map((card, index) => {
              const cardDisplay = getCardDisplay(card);
              if (!cardDisplay) return null;
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`w-12 h-16 bg-white rounded border-2 border-gray-300 flex flex-col items-center justify-center ${
                    !cardDisplay.isVisible ? 'bg-blue-800 border-blue-600' : ''
                  }`}
                >
                  {cardDisplay.isVisible ? (
                    <>
                      <div className={`text-xs font-bold ${cardDisplay.color}`}>
                        {cardDisplay.value}
                      </div>
                      <div className={`text-lg ${cardDisplay.color}`}>
                        {cardDisplay.suit}
                      </div>
                    </>
                  ) : (
                    <div className="text-white text-xs">🂠</div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Player Positions */}
        {playerPositions.map((position) => (
          <motion.div
            key={position.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: position.id * 0.1 }}
            className={`absolute transform -translate-x-1/2 -translate-y-1/2 ${
              position.isCurrentPlayer ? 'z-10' : 'z-5'
            }`}
            style={{
              left: `${50 + Math.cos(position.angle * Math.PI / 180) * 35}%`,
              top: `${50 + Math.sin(position.angle * Math.PI / 180) * 35}%`
            }}
          >
            {/* Player Betting Area */}
            <div className={`w-24 h-16 border-2 rounded-lg flex flex-col items-center justify-center ${
              position.isCurrentPlayer 
                ? 'border-yellow-400 bg-yellow-400 bg-opacity-20' 
                : 'border-yellow-600 bg-yellow-600 bg-opacity-10'
            }`}>
              
              {/* Player Bet Chip */}
              {position.bet > 0 && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`w-8 h-8 rounded-full border-2 border-white flex items-center justify-center ${getChipColor(position.bet)}`}
                >
                  <span className={`text-xs font-bold ${getChipTextColor(position.bet)}`}>
                    ${position.bet}
                  </span>
                </motion.div>
              )}

              {/* Player Cards */}
              <div className="flex space-x-1 mt-1">
                {position.cards.map((card, cardIndex) => {
                  const cardDisplay = getCardDisplay(card);
                  if (!cardDisplay) return null;
                  
                  return (
                    <motion.div
                      key={cardIndex}
                      initial={{ opacity: 0, rotateY: 180 }}
                      animate={{ opacity: 1, rotateY: 0 }}
                      transition={{ delay: cardIndex * 0.2 }}
                      className="w-8 h-10 bg-white rounded border border-gray-300 flex flex-col items-center justify-center"
                    >
                      <div className={`text-xs font-bold ${cardDisplay.color}`}>
                        {cardDisplay.value}
                      </div>
                      <div className={`text-sm ${cardDisplay.color}`}>
                        {cardDisplay.suit}
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Player Label */}
              <div className={`text-xs font-semibold mt-1 ${
                position.isCurrentPlayer ? 'text-yellow-300' : 'text-gray-300'
              }`}>
                {position.isCurrentPlayer ? 'SİZ' : `Oyuncu ${position.id + 1}`}
              </div>
            </div>
          </motion.div>
        ))}

        {/* Game Controls */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-4">
          {!isActive ? (
            <button
              onClick={onStartGame}
              className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
            >
              <PlayIcon className="w-5 h-5 mr-2" />
              Oyunu Başlat
            </button>
          ) : (
            <button
              onClick={onStopGame}
              className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
            >
              <StopIcon className="w-5 h-5 mr-2" />
              Oyunu Durdur
            </button>
          )}
        </div>
      </div>

      {/* Table Configuration Panel */}
      <div className="mt-6 bg-gray-800 bg-opacity-50 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-4">Masa Ayarları</h3>
        
        <div className="grid md:grid-cols-3 gap-4">
          {/* Player Count */}
          <div>
            <label className="block text-gray-300 text-sm mb-2">
              Oyuncu Sayısı: {playerCount}
            </label>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onUpdatePlayerCount(Math.max(1, playerCount - 1))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
              >
                <MinusIcon className="w-4 h-4" />
              </button>
              <span className="text-white font-semibold min-w-[40px] text-center">
                {playerCount}
              </span>
              <button
                onClick={() => onUpdatePlayerCount(Math.min(7, playerCount + 1))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
              >
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Player Position */}
          <div>
            <label className="block text-gray-300 text-sm mb-2">
              Pozisyonunuz: {playerPosition + 1}
            </label>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onUpdatePlayerPosition(Math.max(0, playerPosition - 1))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
              >
                <MinusIcon className="w-4 h-4" />
              </button>
              <span className="text-white font-semibold min-w-[40px] text-center">
                {playerPosition + 1}
              </span>
              <button
                onClick={() => onUpdatePlayerPosition(Math.min(playerCount - 1, playerPosition + 1))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
              >
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Current Bet */}
          <div>
            <label className="block text-gray-300 text-sm mb-2">
              Bahis: ${currentBet}
            </label>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onUpdateBet(Math.max(10, currentBet - 10))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
              >
                <MinusIcon className="w-4 h-4" />
              </button>
              <span className="text-white font-semibold min-w-[60px] text-center">
                ${currentBet}
              </span>
              <button
                onClick={() => onUpdateBet(Math.min(bankroll, currentBet + 10))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
              >
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Bankroll Display */}
        <div className="mt-4 text-center">
          <span className="text-gray-300 text-sm">Bütçe: </span>
          <span className="text-green-400 font-bold">${bankroll.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

export default BlackjackTable; 