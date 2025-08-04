/**
 * Blackjack Game Engine
 * Handles game logic, card dealing, and winner determination
 */

// Card suits and values
const SUITS = ['♠', '♥', '♦', '♣'];
const VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

class Card {
  constructor(suit, value) {
    this.suit = suit;
    this.value = value;
    this.isVisible = true;
  }

  get displayValue() {
    return this.value;
  }

  get numericValue() {
    if (this.value === 'A') return 11;
    if (['J', 'Q', 'K'].includes(this.value)) return 10;
    return parseInt(this.value);
  }

  get color() {
    return ['♥', '♦'].includes(this.suit) ? 'red' : 'black';
  }

  toString() {
    return `${this.value}${this.suit}`;
  }
}

class Deck {
  constructor() {
    this.cards = [];
    this.reset();
  }

  reset() {
    this.cards = [];
    for (const suit of SUITS) {
      for (const value of VALUES) {
        this.cards.push(new Card(suit, value));
      }
    }
    this.shuffle();
  }

  shuffle() {
    for (let i = this.cards.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.cards[i], this.cards[j]] = [this.cards[j], this.cards[i]];
    }
  }

  deal() {
    if (this.cards.length === 0) {
      this.reset();
    }
    return this.cards.pop();
  }

  remainingCards() {
    return this.cards.length;
  }
}

class BlackjackGame {
  constructor() {
    this.deck = new Deck();
    this.playerHand = [];
    this.dealerHand = [];
    this.gameState = 'waiting'; // waiting, betting, playing, dealer, finished
    this.result = null; // win, lose, push
    this.bet = 0;
    this.bankroll = 10000;
    this.gameHistory = [];
  }

  // Start a new game
  startGame(betAmount) {
    if (betAmount > this.bankroll) {
      throw new Error('Insufficient bankroll');
    }

    this.bet = betAmount;
    this.bankroll -= betAmount;
    this.playerHand = [];
    this.dealerHand = [];
    this.gameState = 'playing';
    this.result = null;

    // Deal initial cards
    this.playerHand.push(this.deck.deal());
    this.dealerHand.push(this.deck.deal());
    this.playerHand.push(this.deck.deal());
    this.dealerHand.push(this.deck.deal());

    // Hide dealer's second card
    this.dealerHand[1].isVisible = false;

    // Check for blackjack
    if (this.calculateHandValue(this.playerHand) === 21) {
      this.gameState = 'dealer';
      this.revealDealerCards();
      this.determineWinner();
    }

    return this.getGameState();
  }

  // Player actions
  hit() {
    if (this.gameState !== 'playing') {
      throw new Error('Cannot hit in current game state');
    }

    this.playerHand.push(this.deck.deal());
    const playerValue = this.calculateHandValue(this.playerHand);

    if (playerValue > 21) {
      this.gameState = 'finished';
      this.result = 'lose';
      this.endGame();
    } else if (playerValue === 21) {
      this.gameState = 'dealer';
      this.revealDealerCards();
      this.determineWinner();
    }

    return this.getGameState();
  }

  stand() {
    if (this.gameState !== 'playing') {
      throw new Error('Cannot stand in current game state');
    }

    this.gameState = 'dealer';
    this.revealDealerCards();
    this.playDealerHand();
    this.determineWinner();

    return this.getGameState();
  }

  double() {
    if (this.gameState !== 'playing' || this.playerHand.length !== 2) {
      throw new Error('Cannot double in current game state');
    }

    if (this.bet > this.bankroll) {
      throw new Error('Insufficient bankroll for double');
    }

    this.bankroll -= this.bet;
    this.bet *= 2;

    this.playerHand.push(this.deck.deal());
    const playerValue = this.calculateHandValue(this.playerHand);

    if (playerValue > 21) {
      this.gameState = 'finished';
      this.result = 'lose';
    } else {
      this.gameState = 'dealer';
      this.revealDealerCards();
      this.playDealerHand();
      this.determineWinner();
    }

    this.endGame();
    return this.getGameState();
  }

  // Dealer logic
  revealDealerCards() {
    this.dealerHand.forEach(card => card.isVisible = true);
  }

  playDealerHand() {
    while (this.calculateHandValue(this.dealerHand) < 17) {
      this.dealerHand.push(this.deck.deal());
    }
  }

  // Calculate hand value
  calculateHandValue(hand) {
    let value = 0;
    let aces = 0;

    for (const card of hand) {
      if (card.value === 'A') {
        aces += 1;
        value += 11;
      } else {
        value += card.numericValue;
      }
    }

    // Adjust for aces
    while (value > 21 && aces > 0) {
      value -= 10;
      aces -= 1;
    }

    return value;
  }

  // Determine winner
  determineWinner() {
    const playerValue = this.calculateHandValue(this.playerHand);
    const dealerValue = this.calculateHandValue(this.dealerHand);

    if (playerValue > 21) {
      this.result = 'lose';
    } else if (dealerValue > 21) {
      this.result = 'win';
    } else if (playerValue > dealerValue) {
      this.result = 'win';
    } else if (dealerValue > playerValue) {
      this.result = 'lose';
    } else {
      this.result = 'push';
    }

    this.gameState = 'finished';
    this.endGame();
  }

  // End game and update bankroll
  endGame() {
    if (this.result === 'win') {
      this.bankroll += this.bet * 2;
    } else if (this.result === 'push') {
      this.bankroll += this.bet;
    }

    // Add to game history
    this.gameHistory.push({
      playerHand: [...this.playerHand],
      dealerHand: [...this.dealerHand],
      result: this.result,
      bet: this.bet,
      timestamp: new Date().toISOString()
    });

    this.bet = 0;
  }

  // Get current game state
  getGameState() {
    return {
      gameState: this.gameState,
      playerHand: this.playerHand,
      dealerHand: this.dealerHand,
      playerValue: this.calculateHandValue(this.playerHand),
      dealerValue: this.calculateHandValue(this.dealerHand.filter(card => card.isVisible)),
      dealerUpCard: this.dealerHand[0],
      result: this.result,
      bet: this.bet,
      bankroll: this.bankroll,
      canHit: this.gameState === 'playing',
      canStand: this.gameState === 'playing',
      canDouble: this.gameState === 'playing' && this.playerHand.length === 2 && this.bankroll >= this.bet
    };
  }

  // Reset game
  reset() {
    this.deck = new Deck();
    this.playerHand = [];
    this.dealerHand = [];
    this.gameState = 'waiting';
    this.result = null;
    this.bet = 0;
  }

  // Get game statistics
  getStats() {
    const totalGames = this.gameHistory.length;
    const wins = this.gameHistory.filter(game => game.result === 'win').length;
    const losses = this.gameHistory.filter(game => game.result === 'lose').length;
    const pushes = this.gameHistory.filter(game => game.result === 'push').length;

    return {
      totalGames,
      wins,
      losses,
      pushes,
      winRate: totalGames > 0 ? (wins / totalGames) * 100 : 0,
      totalWagered: this.gameHistory.reduce((sum, game) => sum + game.bet, 0),
      netProfit: this.bankroll - 10000
    };
  }

  // Get available actions for current state
  getAvailableActions() {
    const actions = [];

    if (this.gameState === 'waiting') {
      actions.push('start');
    } else if (this.gameState === 'playing') {
      actions.push('hit', 'stand');
      if (this.playerHand.length === 2 && this.bankroll >= this.bet) {
        actions.push('double');
      }
    }

    return actions;
  }

  // Get game state for AI prediction
  getAIState() {
    return {
      player_total: this.calculateHandValue(this.playerHand),
      dealer_up: this.dealerHand[0]?.numericValue || 0,
      usable_ace: this.playerHand.some(card => card.value === 'A' && this.calculateHandValue(this.playerHand) <= 21),
      true_count: 0, // Would be calculated in a real card counting system
      bankroll: this.bankroll
    };
  }
}

// Utility functions
export const createNewGame = () => new BlackjackGame();

export const calculateHandValue = (hand) => {
  let value = 0;
  let aces = 0;

  for (const card of hand) {
    if (card.value === 'A') {
      aces += 1;
      value += 11;
    } else {
      value += card.numericValue;
    }
  }

  while (value > 21 && aces > 0) {
    value -= 10;
    aces -= 1;
  }

  return value;
};

export const isBlackjack = (hand) => {
  return hand.length === 2 && calculateHandValue(hand) === 21;
};

export const isBust = (hand) => {
  return calculateHandValue(hand) > 21;
};

export const getCardDisplay = (card) => {
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

export default BlackjackGame; 