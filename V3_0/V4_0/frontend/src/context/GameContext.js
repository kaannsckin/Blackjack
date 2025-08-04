import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Game state types
const GAME_ACTIONS = {
  START_GAME: 'START_GAME',
  DEAL_CARDS: 'DEAL_CARDS',
  PLAYER_HIT: 'PLAYER_HIT',
  PLAYER_STAND: 'PLAYER_STAND',
  PLAYER_DOUBLE: 'PLAYER_DOUBLE',
  PLAYER_SPLIT: 'PLAYER_SPLIT',
  DEALER_PLAY: 'DEALER_PLAY',
  END_GAME: 'END_GAME',
  RESET_GAME: 'RESET_GAME',
  UPDATE_BANKROLL: 'UPDATE_BANKROLL',
  SET_BET: 'SET_BET',
  AI_PREDICTION: 'AI_PREDICTION'
};

// Initial game state
const initialState = {
  // Game state
  isPlaying: false,
  gamePhase: 'waiting', // waiting, betting, playing, dealer, finished
  round: 0,
  
  // Player state
  playerHand: [],
  playerTotal: 0,
  playerAces: 0,
  playerBusted: false,
  playerStood: false,
  
  // Dealer state
  dealerHand: [],
  dealerUpCard: null,
  dealerTotal: 0,
  dealerAces: 0,
  dealerBusted: false,
  
  // Betting state
  bankroll: 10000,
  currentBet: 0,
  minBet: 10,
  maxBet: 1000,
  
  // Game history
  gameHistory: [],
  totalWins: 0,
  totalLosses: 0,
  totalPushes: 0,
  
  // AI state
  aiPrediction: null,
  aiConfidence: 0,
  aiReasoning: '',
  selectedModel: 'ultimate_ai',
  
  // Session state
  sessionId: null,
  startTime: null
};

// Game reducer
function gameReducer(state, action) {
  switch (action.type) {
    case GAME_ACTIONS.START_GAME:
      return {
        ...state,
        isPlaying: true,
        gamePhase: 'betting',
        round: state.round + 1,
        sessionId: action.payload.sessionId || `session_${Date.now()}`,
        startTime: new Date().toISOString()
      };
    
    case GAME_ACTIONS.DEAL_CARDS:
      return {
        ...state,
        gamePhase: 'playing',
        playerHand: action.payload.playerHand,
        playerTotal: action.payload.playerTotal,
        playerAces: action.payload.playerAces,
        dealerHand: action.payload.dealerHand,
        dealerUpCard: action.payload.dealerUpCard,
        dealerTotal: action.payload.dealerTotal,
        dealerAces: action.payload.dealerAces,
        playerBusted: false,
        playerStood: false,
        dealerBusted: false
      };
    
    case GAME_ACTIONS.PLAYER_HIT:
      return {
        ...state,
        playerHand: action.payload.hand,
        playerTotal: action.payload.total,
        playerAces: action.payload.aces,
        playerBusted: action.payload.busted
      };
    
    case GAME_ACTIONS.PLAYER_STAND:
      return {
        ...state,
        playerStood: true,
        gamePhase: 'dealer'
      };
    
    case GAME_ACTIONS.DEALER_PLAY:
      return {
        ...state,
        dealerHand: action.payload.hand,
        dealerTotal: action.payload.total,
        dealerAces: action.payload.aces,
        dealerBusted: action.payload.busted
      };
    
    case GAME_ACTIONS.END_GAME:
      const result = action.payload.result; // 'win', 'lose', 'push'
      const newHistory = [...state.gameHistory, {
        round: state.round,
        result,
        playerTotal: state.playerTotal,
        dealerTotal: state.dealerTotal,
        bet: state.currentBet,
        timestamp: new Date().toISOString()
      }];
      
      return {
        ...state,
        gamePhase: 'finished',
        gameHistory: newHistory,
        totalWins: result === 'win' ? state.totalWins + 1 : state.totalWins,
        totalLosses: result === 'lose' ? state.totalLosses + 1 : state.totalLosses,
        totalPushes: result === 'push' ? state.totalPushes + 1 : state.totalPushes,
        bankroll: action.payload.newBankroll
      };
    
    case GAME_ACTIONS.RESET_GAME:
      return {
        ...initialState,
        bankroll: state.bankroll,
        gameHistory: state.gameHistory,
        totalWins: state.totalWins,
        totalLosses: state.totalLosses,
        totalPushes: state.totalPushes,
        selectedModel: state.selectedModel
      };
    
    case GAME_ACTIONS.UPDATE_BANKROLL:
      return {
        ...state,
        bankroll: action.payload.bankroll
      };
    
    case GAME_ACTIONS.SET_BET:
      return {
        ...state,
        currentBet: action.payload.bet
      };
    
    case GAME_ACTIONS.AI_PREDICTION:
      return {
        ...state,
        aiPrediction: action.payload.prediction,
        aiConfidence: action.payload.confidence,
        aiReasoning: action.payload.reasoning
      };
    
    default:
      return state;
  }
}

// Create context
const GameContext = createContext();

// Provider component
export function GameProvider({ children }) {
  const [state, dispatch] = useReducer(gameReducer, initialState);
  
  // Load state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('blackjackGameState');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        // Restore non-sensitive state
        dispatch({
          type: 'RESTORE_STATE',
          payload: {
            bankroll: parsed.bankroll || initialState.bankroll,
            gameHistory: parsed.gameHistory || [],
            totalWins: parsed.totalWins || 0,
            totalLosses: parsed.totalLosses || 0,
            totalPushes: parsed.totalPushes || 0,
            selectedModel: parsed.selectedModel || 'ultimate_ai'
          }
        });
      } catch (error) {
        console.error('Error restoring game state:', error);
      }
    }
  }, []);
  
  // Save state to localStorage when it changes
  useEffect(() => {
    const stateToSave = {
      bankroll: state.bankroll,
      gameHistory: state.gameHistory,
      totalWins: state.totalWins,
      totalLosses: state.totalLosses,
      totalPushes: state.totalPushes,
      selectedModel: state.selectedModel
    };
    localStorage.setItem('blackjackGameState', JSON.stringify(stateToSave));
  }, [state.bankroll, state.gameHistory, state.totalWins, state.totalLosses, state.totalPushes, state.selectedModel]);
  
  // Game actions
  const gameActions = {
    startGame: (sessionId) => {
      dispatch({ type: GAME_ACTIONS.START_GAME, payload: { sessionId } });
    },
    
    dealCards: (playerHand, dealerHand) => {
      const playerTotal = calculateHandTotal(playerHand);
      const dealerTotal = calculateHandTotal(dealerHand);
      
      dispatch({
        type: GAME_ACTIONS.DEAL_CARDS,
        payload: {
          playerHand,
          playerTotal: playerTotal.total,
          playerAces: playerTotal.aces,
          dealerHand,
          dealerUpCard: dealerHand[0],
          dealerTotal: dealerTotal.total,
          dealerAces: dealerTotal.aces
        }
      });
    },
    
    playerHit: (newHand) => {
      const total = calculateHandTotal(newHand);
      dispatch({
        type: GAME_ACTIONS.PLAYER_HIT,
        payload: {
          hand: newHand,
          total: total.total,
          aces: total.aces,
          busted: total.total > 21
        }
      });
    },
    
    playerStand: () => {
      dispatch({ type: GAME_ACTIONS.PLAYER_STAND });
    },
    
    dealerPlay: (newHand) => {
      const total = calculateHandTotal(newHand);
      dispatch({
        type: GAME_ACTIONS.DEALER_PLAY,
        payload: {
          hand: newHand,
          total: total.total,
          aces: total.aces,
          busted: total.total > 21
        }
      });
    },
    
    endGame: (result, newBankroll) => {
      dispatch({
        type: GAME_ACTIONS.END_GAME,
        payload: { result, newBankroll }
      });
    },
    
    resetGame: () => {
      dispatch({ type: GAME_ACTIONS.RESET_GAME });
    },
    
    updateBankroll: (bankroll) => {
      dispatch({
        type: GAME_ACTIONS.UPDATE_BANKROLL,
        payload: { bankroll }
      });
    },
    
    setBet: (bet) => {
      dispatch({
        type: GAME_ACTIONS.SET_BET,
        payload: { bet }
      });
    },
    
    setAIPrediction: (prediction, confidence, reasoning) => {
      dispatch({
        type: GAME_ACTIONS.AI_PREDICTION,
        payload: { prediction, confidence, reasoning }
      });
    }
  };
  
  // Helper function to calculate hand total
  function calculateHandTotal(hand) {
    let total = 0;
    let aces = 0;
    
    for (const card of hand) {
      if (card.value === 'A') {
        aces += 1;
        total += 11;
      } else if (['K', 'Q', 'J'].includes(card.value)) {
        total += 10;
      } else {
        total += parseInt(card.value);
      }
    }
    
    // Adjust for aces
    while (total > 21 && aces > 0) {
      total -= 10;
      aces -= 1;
    }
    
    return { total, aces };
  }
  
  // Calculate win rate
  const totalGames = state.totalWins + state.totalLosses + state.totalPushes;
  const winRate = totalGames > 0 ? (state.totalWins / totalGames) * 100 : 0;
  
  const value = {
    state,
    actions: gameActions,
    winRate,
    totalGames
  };
  
  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  );
}

// Custom hook to use game context
export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
} 