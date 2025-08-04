import React from 'react';
import { motion } from 'framer-motion';
import Card from './Card';
import { 
  PlayIcon, 
  StopIcon,
  PlusIcon,
  MinusIcon
} from '@heroicons/react/24/outline';

const GameTable = ({ 
  gameState, 
  onHit, 
  onStand, 
  onDouble, 
  onNewGame, 
  onBetChange,
  aiPrediction = null 
}) => {
  const {
    playerHand = [],
    dealerHand = [],
    playerValue = 0,
    dealerValue = 0,
    gameState: currentGameState = 'waiting',
    bet = 0,
    bankroll = 10000,
    canHit = false,
    canStand = false,
    canDouble = false,
    result = null
  } = gameState;

  const isPlaying = currentGameState === 'playing';
  const isFinished = currentGameState === 'finished';
  const isWaiting = currentGameState === 'waiting';

  const getResultMessage = () => {
    if (!result) return '';
    switch (result) {
      case 'win': return '🎉 Kazandınız!';
      case 'lose': return '😔 Kaybettiniz!';
      case 'push': return '🤝 Berabere!';
      default: return '';
    }
  };

  const getResultColor = () => {
    switch (result) {
      case 'win': return 'text-green-400';
      case 'lose': return 'text-red-400';
      case 'push': return 'text-yellow-400';
      default: return 'text-gray-300';
    }
  };

  return (
    <div className="bg-green-800 bg-opacity-50 rounded-lg p-6 border-2 border-green-600">
      {/* Game Header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          Blackjack Masası
        </h2>
        <div className="flex justify-center space-x-4 text-sm text-gray-300">
          <span>Durum: {currentGameState}</span>
          <span>Bankroll: ${bankroll.toLocaleString()}</span>
          {bet > 0 && <span>Bahis: ${bet.toLocaleString()}</span>}
        </div>
      </div>

      {/* Dealer Area */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Dealer</h3>
          {dealerValue > 0 && (
            <span className="text-white font-bold">
              Toplam: {dealerValue}
            </span>
          )}
        </div>
        
        <div className="bg-gray-700 rounded-lg p-4 min-h-32 flex items-center justify-center">
          {dealerHand.length > 0 ? (
            <div className="flex space-x-2">
              {dealerHand.map((card, index) => (
                <Card
                  key={index}
                  card={card}
                  index={index}
                  isDealer={true}
                />
              ))}
            </div>
          ) : (
            <span className="text-gray-400">Kartlar dağıtılacak</span>
          )}
        </div>
      </div>

      {/* Player Area */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Oyuncu</h3>
          {playerValue > 0 && (
            <span className="text-white font-bold">
              Toplam: {playerValue}
            </span>
          )}
        </div>
        
        <div className="bg-gray-700 rounded-lg p-4 min-h-32 flex items-center justify-center">
          {playerHand.length > 0 ? (
            <div className="flex space-x-2">
              {playerHand.map((card, index) => (
                <Card
                  key={index}
                  card={card}
                  index={index}
                  isDealer={false}
                />
              ))}
            </div>
          ) : (
            <span className="text-gray-400">Kartlar dağıtılacak</span>
          )}
        </div>
      </div>

      {/* AI Prediction */}
      {aiPrediction && isPlaying && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 bg-blue-900 bg-opacity-50 rounded-lg p-4 border border-blue-500"
        >
          <h4 className="text-white font-semibold mb-2">🤖 AI Önerisi</h4>
          <div className="flex justify-between items-center">
            <div>
              <span className="text-gray-300">Aksiyon: </span>
              <span className="text-green-400 font-bold">
                {aiPrediction.action === 0 ? 'Stand' : 
                 aiPrediction.action === 1 ? 'Hit' : 
                 aiPrediction.action === 2 ? 'Double' : 'Split'}
              </span>
            </div>
            <div>
              <span className="text-gray-300">Güven: </span>
              <span className="text-blue-400 font-bold">
                {(aiPrediction.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <div className="mt-2 text-sm text-gray-300">
            {aiPrediction.reasoning}
          </div>
        </motion.div>
      )}

      {/* Result Message */}
      {isFinished && result && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`mb-6 text-center p-4 rounded-lg bg-gray-800 bg-opacity-50 ${getResultColor()}`}
        >
          <div className="text-2xl font-bold">{getResultMessage()}</div>
        </motion.div>
      )}

      {/* Game Controls */}
      <div className="flex flex-wrap justify-center gap-4">
        {/* New Game / Betting */}
        {isWaiting && (
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onBetChange(Math.max(10, bet - 10))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                <MinusIcon className="w-4 h-4" />
              </button>
              <span className="text-white font-semibold min-w-[60px] text-center">
                ${bet}
              </span>
              <button
                onClick={() => onBetChange(Math.min(bankroll, bet + 10))}
                className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            <button
              onClick={onNewGame}
              disabled={bet === 0 || bet > bankroll}
              className="flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-semibold rounded-lg transition-colors"
            >
              <PlayIcon className="w-5 h-5 mr-2" />
              Yeni Oyun
            </button>
          </div>
        )}

        {/* Game Actions */}
        {isPlaying && (
          <>
            <button
              onClick={onHit}
              className="flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
            >
              <PlusIcon className="w-5 h-5 mr-2" />
              Hit
            </button>
            
            <button
              onClick={onStand}
              className="flex items-center px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white font-semibold rounded-lg transition-colors"
            >
              <StopIcon className="w-5 h-5 mr-2" />
              Stand
            </button>
            
            {canDouble && (
              <button
                onClick={onDouble}
                className="flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors"
              >
                <PlusIcon className="w-5 h-5 mr-2" />
                Double
              </button>
            )}
          </>
        )}

        {/* Reset Game */}
        {isFinished && (
          <button
            onClick={() => onNewGame()}
            className="flex items-center px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors"
          >
            <PlayIcon className="w-5 h-5 mr-2" />
            Yeni Oyun
          </button>
        )}
      </div>

      {/* Game Status */}
      <div className="mt-6 text-center">
        <div className="text-sm text-gray-300">
          {isWaiting && "Bahis miktarını ayarlayın ve oyunu başlatın"}
          {isPlaying && "Kart çekin veya durun"}
          {isFinished && "Oyun bitti"}
        </div>
      </div>
    </div>
  );
};

export default GameTable; 