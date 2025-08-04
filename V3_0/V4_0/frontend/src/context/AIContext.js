import React, { createContext, useContext, useReducer, useEffect } from 'react';

// AI state types
const AI_ACTIONS = {
  SET_AVAILABLE_MODELS: 'SET_AVAILABLE_MODELS',
  SET_SELECTED_MODEL: 'SET_SELECTED_MODEL',
  SET_PREDICTION: 'SET_PREDICTION',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_PREDICTION: 'CLEAR_PREDICTION',
  UPDATE_MODEL_STATUS: 'UPDATE_MODEL_STATUS'
};

// Initial AI state
const initialState = {
  // Available models
  availableModels: [],
  selectedModel: 'ultimate_ai',
  
  // Model status
  modelStatus: {},
  loadingModels: false,
  
  // Current prediction
  currentPrediction: null,
  predictionLoading: false,
  predictionError: null,
  
  // API connection
  apiConnected: false,
  apiUrl: 'http://localhost:8000',
  
  // Statistics
  totalPredictions: 0,
  successfulPredictions: 0,
  averageConfidence: 0
};

// AI reducer
function aiReducer(state, action) {
  switch (action.type) {
    case AI_ACTIONS.SET_AVAILABLE_MODELS:
      return {
        ...state,
        availableModels: action.payload,
        loadingModels: false
      };
    
    case AI_ACTIONS.SET_SELECTED_MODEL:
      return {
        ...state,
        selectedModel: action.payload
      };
    
    case AI_ACTIONS.SET_PREDICTION:
      const newTotal = state.totalPredictions + 1;
      const newSuccessful = state.successfulPredictions + (action.payload.success ? 1 : 0);
      const newAvgConfidence = action.payload.confidence 
        ? (state.averageConfidence * state.totalPredictions + action.payload.confidence) / newTotal
        : state.averageConfidence;
      
      return {
        ...state,
        currentPrediction: action.payload,
        predictionLoading: false,
        predictionError: null,
        totalPredictions: newTotal,
        successfulPredictions: newSuccessful,
        averageConfidence: newAvgConfidence
      };
    
    case AI_ACTIONS.SET_LOADING:
      return {
        ...state,
        predictionLoading: action.payload
      };
    
    case AI_ACTIONS.SET_ERROR:
      return {
        ...state,
        predictionError: action.payload,
        predictionLoading: false
      };
    
    case AI_ACTIONS.CLEAR_PREDICTION:
      return {
        ...state,
        currentPrediction: null,
        predictionError: null
      };
    
    case AI_ACTIONS.UPDATE_MODEL_STATUS:
      return {
        ...state,
        modelStatus: {
          ...state.modelStatus,
          ...action.payload
        }
      };
    
    default:
      return state;
  }
}

// Create context
const AIContext = createContext();

// Provider component
export function AIProvider({ children }) {
  const [state, dispatch] = useReducer(aiReducer, initialState);
  
  // Load available models on mount
  useEffect(() => {
    aiActions.loadAvailableModels();
  }, []);
  
  // AI actions
  const aiActions = {
    loadAvailableModels: async () => {
      try {
        dispatch({ type: AI_ACTIONS.SET_LOADING, payload: true });
        
        const response = await fetch(`${state.apiUrl}/models`);
        if (response.ok) {
          const models = await response.json();
          dispatch({ type: AI_ACTIONS.SET_AVAILABLE_MODELS, payload: models });
          dispatch({ type: AI_ACTIONS.UPDATE_MODEL_STATUS, payload: { apiConnected: true } });
        } else {
          throw new Error('Failed to load models');
        }
      } catch (error) {
        console.error('Error loading models:', error);
        dispatch({ type: AI_ACTIONS.SET_ERROR, payload: error.message });
        dispatch({ type: AI_ACTIONS.UPDATE_MODEL_STATUS, payload: { apiConnected: false } });
      }
    },
    
    setSelectedModel: (modelName) => {
      dispatch({ type: AI_ACTIONS.SET_SELECTED_MODEL, payload: modelName });
    },
    
    getPrediction: async (gameState) => {
      try {
        dispatch({ type: AI_ACTIONS.SET_LOADING, payload: true });
        dispatch({ type: AI_ACTIONS.CLEAR_PREDICTION });
        
        const response = await fetch(`${state.apiUrl}/predict`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer demo_token'
          },
          body: JSON.stringify({
            model_name: state.selectedModel,
            game_state: gameState
          })
        });
        
        if (response.ok) {
          const prediction = await response.json();
          dispatch({ type: AI_ACTIONS.SET_PREDICTION, payload: prediction });
        } else {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Prediction failed');
        }
      } catch (error) {
        console.error('Error getting prediction:', error);
        dispatch({ type: AI_ACTIONS.SET_ERROR, payload: error.message });
      }
    },
    
    clearPrediction: () => {
      dispatch({ type: AI_ACTIONS.CLEAR_PREDICTION });
    },
    
    loadModel: async (modelName) => {
      try {
        const response = await fetch(`${state.apiUrl}/models/${modelName}/load`, {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer demo_token'
          }
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log(`Model ${modelName} loaded:`, result);
        } else {
          throw new Error(`Failed to load model ${modelName}`);
        }
      } catch (error) {
        console.error(`Error loading model ${modelName}:`, error);
        dispatch({ type: AI_ACTIONS.SET_ERROR, payload: error.message });
      }
    },
    
    getModelStatus: async (modelName) => {
      try {
        const response = await fetch(`${state.apiUrl}/models/${modelName}`);
        if (response.ok) {
          const status = await response.json();
          dispatch({ 
            type: AI_ACTIONS.UPDATE_MODEL_STATUS, 
            payload: { [modelName]: status } 
          });
          return status;
        }
      } catch (error) {
        console.error(`Error getting model status for ${modelName}:`, error);
      }
    }
  };
  
  // Helper functions
  const helpers = {
    getModelDisplayName: (modelName) => {
      const displayNames = {
        'ultimate_ai': 'Ultimate AI System',
        'enhanced_adaptive': 'Enhanced Adaptive AI',
        'adaptive_simple': 'Adaptive Simple AI',
        'practical_hybrid': 'Practical Hybrid AI',
        'multi_player': 'Multi-Player AI',
        'enhanced_simple': 'Enhanced Simple AI',
        'optimized_adaptive': 'Optimized Adaptive AI'
      };
      return displayNames[modelName] || modelName;
    },
    
    getModelGrade: (modelName) => {
      const grades = {
        'ultimate_ai': 'A+',
        'enhanced_adaptive': 'A',
        'adaptive_simple': 'A',
        'practical_hybrid': 'B+',
        'multi_player': 'B',
        'enhanced_simple': 'B',
        'optimized_adaptive': 'C'
      };
      return grades[modelName] || 'N/A';
    },
    
    getModelROI: (modelName) => {
      const rois = {
        'ultimate_ai': 51,
        'enhanced_adaptive': 48,
        'adaptive_simple': 51,
        'practical_hybrid': 45,
        'multi_player': 42,
        'enhanced_simple': 40,
        'optimized_adaptive': 35
      };
      return rois[modelName] || 0;
    },
    
    getActionName: (action) => {
      const actions = {
        0: 'Stand',
        1: 'Hit',
        2: 'Double',
        3: 'Split'
      };
      return actions[action] || 'Unknown';
    }
  };
  
  const value = {
    state,
    actions: aiActions,
    helpers
  };
  
  return (
    <AIContext.Provider value={value}>
      {children}
    </AIContext.Provider>
  );
}

// Custom hook to use AI context
export function useAI() {
  const context = useContext(AIContext);
  if (!context) {
    throw new Error('useAI must be used within an AIProvider');
  }
  return context;
} 