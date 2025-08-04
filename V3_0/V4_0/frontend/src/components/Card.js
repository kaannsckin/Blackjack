import React from 'react';
import { motion } from 'framer-motion';

const Card = ({ card, index = 0, isDealer = false, onClick = null }) => {
  if (!card) return null;

  const cardDisplay = getCardDisplay(card);
  const isHidden = !card.isVisible;

  const cardVariants = {
    hidden: { 
      opacity: 0, 
      y: 50, 
      rotateY: isHidden ? 180 : 0,
      scale: 0.8 
    },
    visible: { 
      opacity: 1, 
      y: 0, 
      rotateY: isHidden ? 180 : 0,
      scale: 1,
      transition: {
        delay: index * 0.1,
        duration: 0.3,
        ease: "easeOut"
      }
    },
    hover: {
      y: -5,
      scale: 1.05,
      transition: { duration: 0.2 }
    }
  };

  const flipVariants = {
    hidden: { rotateY: 180 },
    visible: { rotateY: 0 }
  };

  return (
    <motion.div
      className={`relative ${onClick ? 'cursor-pointer' : ''}`}
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={onClick ? "hover" : ""}
      onClick={onClick}
      style={{
        perspective: '1000px'
      }}
    >
      {/* Card Container */}
      <div className="relative w-16 h-24 md:w-20 md:h-28 lg:w-24 lg:h-32">
        {/* Card Back (Hidden) */}
        {isHidden && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg border-2 border-blue-400 shadow-lg"
            variants={flipVariants}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.3, delay: 0.5 }}
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-white text-xs font-bold">🂠</div>
            </div>
            <div className="absolute top-1 left-1 text-white text-xs">♠</div>
            <div className="absolute bottom-1 right-1 text-white text-xs">♠</div>
          </motion.div>
        )}

        {/* Card Front */}
        {!isHidden && (
          <motion.div
            className={`absolute inset-0 bg-white rounded-lg border-2 shadow-lg ${
              cardDisplay.color === 'red' ? 'border-red-500' : 'border-gray-800'
            }`}
            variants={flipVariants}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.3, delay: 0.5 }}
          >
            {/* Card Content */}
            <div className="absolute inset-0 p-1">
              {/* Top Left */}
              <div className={`text-xs font-bold ${
                cardDisplay.color === 'red' ? 'text-red-600' : 'text-gray-800'
              }`}>
                {card.value}
              </div>
              
              {/* Center */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className={`text-2xl md:text-3xl lg:text-4xl ${
                  cardDisplay.color === 'red' ? 'text-red-600' : 'text-gray-800'
                }`}>
                  {card.suit}
                </div>
              </div>
              
              {/* Bottom Right */}
              <div className={`absolute bottom-1 right-1 text-xs font-bold ${
                cardDisplay.color === 'red' ? 'text-red-600' : 'text-gray-800'
              }`}>
                {card.value}
              </div>
            </div>

            {/* Card Pattern */}
            <div className="absolute inset-0 opacity-5">
              <div className="w-full h-full bg-gradient-to-br from-gray-400 to-transparent rounded-lg"></div>
            </div>
          </motion.div>
        )}

        {/* Glow Effect */}
        <div className={`absolute inset-0 rounded-lg ${
          cardDisplay.color === 'red' 
            ? 'shadow-red-500/20' 
            : 'shadow-blue-500/20'
        }`}></div>
      </div>
    </motion.div>
  );
};

// Utility function to get card display info
const getCardDisplay = (card) => {
  if (!card.isVisible) {
    return { display: '🂠', color: 'gray' };
  }

  const suitSymbols = {
    '♠': '♠',
    '♥': '♥',
    '♦': '♦',
    '♣': '♣'
  };

  return {
    display: `${card.value}${suitSymbols[card.suit]}`,
    color: card.color
  };
};

export default Card; 