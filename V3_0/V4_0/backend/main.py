"""
FastAPI Backend Framework - V4_0 Blackjack AI System

RESTful API endpoints, WebSocket support, CORS configuration,
rate limiting ve authentication middleware içerir.
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uvicorn
import logging
import time
import json
import asyncio
from datetime import datetime, timedelta
import secrets
from collections import defaultdict

# AI Engine imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_engine'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))  # V3_0 root
from api_wrapper import AIModelWrapper, GameState, ResponseFormatter

# V3_0 Advanced Systems
try:
    from faz4_budget_optimization import FAZ4BudgetOptimizer, create_faz4_budget_optimizer
    from risk_analysis import RiskAnalyzer
    from faz4_enhanced_multi_player_system import FAZ4EnhancedMultiPlayerEnv
    BUDGET_OPTIMIZER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"V3_0 advanced systems not available: {e}")
    BUDGET_OPTIMIZER_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Blackjack AI V4.0 API",
    description="Advanced Blackjack AI System with Web Interface",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# Rate limiting
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.requests_per_minute:
            self.requests[client_id].append(now)
            return True
        
        return False

rate_limiter = RateLimiter(requests_per_minute=100)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"  # Production'da kaldırılacak
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.herokuapp.com", "*.vercel.app"]
)

# AI Model Wrapper
ai_wrapper = AIModelWrapper()

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_sessions[session_id] = {
            "websocket": websocket,
            "connected_at": datetime.now(),
            "last_activity": datetime.now()
        }
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from sessions
        session_id = None
        for sid, session in self.user_sessions.items():
            if session["websocket"] == websocket:
                session_id = sid
                break
        
        if session_id:
            del self.user_sessions[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# Pydantic Models
class GameStateRequest(BaseModel):
    player_total: int = Field(..., ge=4, le=21, description="Player's total card value")
    dealer_up: int = Field(..., ge=1, le=11, description="Dealer's up card value")
    usable_ace: bool = Field(False, description="Whether player has usable ace")
    true_count: float = Field(0.0, description="True count for card counting")
    bankroll: float = Field(10000.0, description="Current bankroll")
    session_id: Optional[str] = Field(None, description="Session identifier")
    # New fields for advanced analysis
    risk_score: Optional[float] = Field(50.0, ge=0, le=100, description="Risk tolerance score (0-100)")
    budget_score: Optional[float] = Field(50.0, ge=0, le=100, description="Budget management score (0-100)")
    table_heat: Optional[float] = Field(0.0, ge=0, le=100, description="Table heat level (0-100)")
    player_position: Optional[int] = Field(0, ge=0, le=7, description="Player position at table")
    total_players: Optional[int] = Field(4, ge=1, le=7, description="Total players at table")
    card_history: Optional[List[Dict]] = Field([], description="Card history for analysis")

class PredictionRequest(BaseModel):
    model_name: str = Field(..., description="AI model to use")
    game_state: GameStateRequest

class ModelInfoResponse(BaseModel):
    name: str
    status: str
    load_time: float
    memory_usage: float
    total_requests: int
    error_count: int

class PredictionResponse(BaseModel):
    success: bool
    action: Optional[int] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    model_name: Optional[str] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    # Advanced analysis fields
    risk_level: Optional[str] = None
    bet_suggestion: Optional[float] = None
    budget_analysis: Optional[Dict] = None
    player_segmentation: Optional[Dict] = None
    table_analysis: Optional[Dict] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    models_available: int
    active_connections: int

# Authentication
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token verification - production'da JWT kullanılacak"""
    token = credentials.credentials
    # TODO: Implement proper JWT verification
    if not token or token != "demo_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

# Rate limiting dependency
def check_rate_limit(client_id: str = "default"):
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return True

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Blackjack AI V4.0 API",
        "version": "4.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="4.0.0",
        models_available=len(ai_wrapper.get_available_models()),
        active_connections=len(manager.active_connections)
    )

@app.get("/models", response_model=List[str])
async def get_available_models():
    """Get available AI models"""
    return ai_wrapper.get_available_models()

@app.get("/models/{model_name}", response_model=ModelInfoResponse)
async def get_model_info(model_name: str):
    """Get specific model information"""
    info = ai_wrapper.get_model_status(model_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    return ModelInfoResponse(
        name=info.name,
        status=info.status.value,
        load_time=info.load_time,
        memory_usage=info.memory_usage,
        total_requests=info.total_requests,
        error_count=info.error_count
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_action(
    request: PredictionRequest,
    token: str = Depends(verify_token),
    rate_limit: bool = Depends(check_rate_limit)
):
    """Get AI prediction for game action with advanced analysis"""
    start_time = time.time()
    
    try:
        # Validate game state
        validation_error = ResponseFormatter.validate_game_state(request.game_state.dict())
        if validation_error:
            return PredictionResponse(
                success=False,
                error=validation_error
            )
        
        # Convert to GameState
        game_state = GameState(
            player_total=request.game_state.player_total,
            dealer_up=request.game_state.dealer_up,
            usable_ace=request.game_state.usable_ace,
            true_count=request.game_state.true_count,
            bankroll=request.game_state.bankroll,
            session_id=request.game_state.session_id
        )
        
        # Get basic prediction
        response = ai_wrapper.predict_action(request.model_name, game_state)
        formatted = ResponseFormatter.format_success_response(response)
        
        # Advanced analysis if V3_0 systems are available
        risk_level = "medium"
        bet_suggestion = 100.0
        budget_analysis = {}
        player_segmentation = {}
        table_analysis = {}
        
        if BUDGET_OPTIMIZER_AVAILABLE:
            try:
                # Risk level calculation
                confidence = formatted["data"]["confidence"]
                if confidence > 0.8:
                    risk_level = "low"
                elif confidence < 0.5:
                    risk_level = "high"
                
                # Budget optimization
                risk_score = request.game_state.risk_score or 50.0
                budget_score = request.game_state.budget_score or 50.0
                base_bet = (budget_score / 100) * 1000
                risk_multiplier = 1.0 if risk_level == "medium" else (1.2 if risk_level == "low" else 0.8)
                bet_suggestion = round(base_bet * risk_multiplier * confidence)
                
                # Budget analysis
                budget_analysis = {
                    "base_bet": base_bet,
                    "risk_multiplier": risk_multiplier,
                    "confidence_multiplier": confidence,
                    "recommended_bet": bet_suggestion,
                    "budget_utilization": (bet_suggestion / 10000) * 100
                }
                
                # Table analysis
                table_analysis = {
                    "heat_level": request.game_state.table_heat or 0.0,
                    "player_position": request.game_state.player_position or 0,
                    "total_players": request.game_state.total_players or 4,
                    "table_momentum": "neutral"
                }
                
                # Player segmentation (mock data for now)
                player_segmentation = {
                    "left_player": {"type": "unknown", "confidence": 0.0},
                    "right_player": {"type": "unknown", "confidence": 0.0},
                    "across_player": {"type": "unknown", "confidence": 0.0}
                }
                
            except Exception as e:
                logger.warning(f"Advanced analysis error: {e}")
        
        processing_time = time.time() - start_time
        
        return PredictionResponse(
            success=True,
            action=formatted["data"]["action"],
            confidence=formatted["data"]["confidence"],
            reasoning=formatted["data"]["reasoning"],
            model_name=formatted["data"]["model_name"],
            processing_time=processing_time,
            risk_level=risk_level,
            bet_suggestion=bet_suggestion,
            budget_analysis=budget_analysis,
            player_segmentation=player_segmentation,
            table_analysis=table_analysis
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return PredictionResponse(
            success=False,
            error=str(e),
            processing_time=time.time() - start_time
        )

@app.post("/models/{model_name}/load")
async def load_model(
    model_name: str,
    force_reload: bool = False,
    token: str = Depends(verify_token)
):
    """Load AI model into memory"""
    try:
        info = ai_wrapper.load_model(model_name, force_reload)
        return {
            "success": True,
            "model_name": model_name,
            "status": info.status.value,
            "load_time": info.load_time,
            "message": f"Model {model_name} loaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@app.get("/cache/stats")
async def get_cache_stats():
    """Get model cache statistics"""
    return ai_wrapper.get_cache_stats()

@app.delete("/cache/clear")
async def clear_cache(token: str = Depends(verify_token)):
    """Clear model cache"""
    # TODO: Implement cache clearing
    return {"success": True, "message": "Cache cleared"}

# WebSocket endpoints

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Update last activity
            if session_id in manager.user_sessions:
                manager.user_sessions[session_id]["last_activity"] = datetime.now()
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                    websocket
                )
            
            elif message.get("type") == "predict":
                try:
                    # Extract prediction request
                    model_name = message.get("model_name", "ultimate_ai")
                    game_state_data = message.get("game_state", {})
                    
                    # Validate game state
                    validation_error = ResponseFormatter.validate_game_state(game_state_data)
                    if validation_error:
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "prediction_error",
                                "error": validation_error
                            }),
                            websocket
                        )
                        continue
                    
                    # Convert to GameState
                    game_state = GameState(
                        player_total=game_state_data["player_total"],
                        dealer_up=game_state_data["dealer_up"],
                        usable_ace=game_state_data.get("usable_ace", False),
                        true_count=game_state_data.get("true_count", 0.0),
                        bankroll=game_state_data.get("bankroll", 10000.0),
                        session_id=session_id
                    )
                    
                    # Get prediction
                    response = ai_wrapper.predict_action(model_name, game_state)
                    
                    # Send response
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "prediction",
                            "data": {
                                "action": response.action,
                                "confidence": response.confidence,
                                "reasoning": response.reasoning,
                                "model_name": response.model_name,
                                "processing_time": response.processing_time
                            }
                        }),
                        websocket
                    )
                    
                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "prediction_error",
                            "error": str(e)
                        }),
                        websocket
                    )
            
            elif message.get("type") == "health":
                # Send health status
                await manager.send_personal_message(
                    json.dumps({
                        "type": "health",
                        "data": {
                            "status": "healthy",
                            "models_available": len(ai_wrapper.get_available_models()),
                            "active_connections": len(manager.active_connections),
                            "timestamp": datetime.now().isoformat()
                        }
                    }),
                    websocket
                )
            
            else:
                # Unknown message type
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "error": f"Unknown message type: {message.get('type')}"
                    }),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# Startup and shutdown events

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 Blackjack AI V4.0 API starting up...")
    
    # Load default models
    try:
        default_models = ["ultimate_ai", "enhanced_adaptive", "adaptive_simple"]
        for model_name in default_models:
            ai_wrapper.load_model(model_name)
            logger.info(f"✅ Loaded model: {model_name}")
    except Exception as e:
        logger.error(f"❌ Error loading default models: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("🛑 Blackjack AI V4.0 API shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 