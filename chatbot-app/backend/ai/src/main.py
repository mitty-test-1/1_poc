from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Import services
from services.nlp_processor import NLPProcessor
from services.intent_recognition import IntentRecognition
from services.sentiment_analysis import SentimentAnalysis
from services.response_generator import ResponseGenerator
from services.model_manager import ModelManager
from services.performance_monitor import PerformanceMonitor
from services.monitoring_service import MonitoringService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
nlp_processor = NLPProcessor()
intent_recognition = IntentRecognition()
sentiment_analysis = SentimentAnalysis()
response_generator = ResponseGenerator()
model_manager = ModelManager()
performance_monitor = PerformanceMonitor()
monitoring_service = MonitoringService()

# FastAPI app
app = FastAPI(
    title="AI/ML Service",
    description="Advanced AI and Machine Learning service for chatbot applications",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    response: str
    confidence: float
    intent: str
    sentiment: str
    entities: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class IntentRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class SentimentRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class TrainModelRequest(BaseModel):
    name: str
    type: str
    data: List[Any]
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class ModelInfo(BaseModel):
    name: str
    version: str
    status: str
    type: str
    created_at: str
    updated_at: str

class AlertRequest(BaseModel):
    alert_id: str

class ThresholdUpdateRequest(BaseModel):
    thresholds: Dict[str, float]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# NLP Processing endpoints
@app.post("/process")
async def process_message(request: MessageRequest):
    """Process a message and return AI response"""
    import time
    start_time = time.time()
    success = True
    
    try:
        # Process message with NLP
        nlp_result = await nlp_processor.process(
            request.message,
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Recognize intent
        intent_result = await intent_recognition.analyze(
            request.message,
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Analyze sentiment
        sentiment_result = await sentiment_analysis.analyze(
            request.message,
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Generate response
        response_result = await response_generator.generate(
            request.message,
            intent_result["intent"],
            nlp_result["entities"],
            sentiment_result["sentiment"],
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Record metrics
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="process",
            response_time=response_time,
            success=success,
            model_used="nlp_processor"
        )
        
        # Record accuracy
        monitoring_service.record_ai_accuracy(
            model="nlp_processor",
            task="message_processing",
            accuracy=response_result["confidence"]
        )
        
        return MessageResponse(
            response=response_result["response"],
            confidence=response_result["confidence"],
            intent=intent_result["intent"],
            sentiment=sentiment_result["sentiment"],
            entities=nlp_result["entities"],
            metadata={
                "nlp_processing": nlp_result,
                "intent_analysis": intent_result,
                "sentiment_analysis": sentiment_result,
                "response_generation": response_result,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )
        
    except Exception as e:
        success = False
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="process",
            response_time=response_time,
            success=success,
            model_used="nlp_processor"
        )
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/intent")
async def recognize_intent(request: IntentRequest):
    """Recognize intent from message"""
    import time
    start_time = time.time()
    success = True
    
    try:
        result = await intent_recognition.analyze(
            request.message,
            request.user_id,
            None,
            request.context
        )
        
        # Record metrics
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="intent_recognition",
            response_time=response_time,
            success=success,
            model_used="intent_classifier"
        )
        
        # Record accuracy
        monitoring_service.record_ai_accuracy(
            model="intent_classifier",
            task="intent_recognition",
            accuracy=result["confidence"]
        )
        
        return {
            "intent": result["intent"],
            "confidence": result["confidence"],
            "entities": result.get("entities", []),
            "metadata": result.get("metadata", {})
        }
        
    except Exception as e:
        success = False
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="intent_recognition",
            response_time=response_time,
            success=success,
            model_used="intent_classifier"
        )
        logger.error(f"Error recognizing intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment of message"""
    import time
    start_time = time.time()
    success = True
    
    try:
        result = await sentiment_analysis.analyze(
            request.message,
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Record metrics
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="sentiment_analysis",
            response_time=response_time,
            success=success,
            model_used="sentiment_analyzer"
        )
        
        # Record accuracy
        monitoring_service.record_ai_accuracy(
            model="sentiment_analyzer",
            task="sentiment_analysis",
            accuracy=result["confidence"]
        )
        
        return {
            "sentiment": result["sentiment"],
            "confidence": result["confidence"],
            "scores": result["scores"],
            "emotions": result["emotions"],
            "metadata": result.get("metadata", {})
        }
        
    except Exception as e:
        success = False
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="sentiment_analysis",
            response_time=response_time,
            success=success,
            model_used="sentiment_analyzer"
        )
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/follow-up")
async def generate_follow_up(request: MessageRequest):
    """Generate follow-up question or suggestion"""
    try:
        result = await response_generator.generate_follow_up(
            request.user_id,
            request.conversation_id
        )
        
        return {
            "follow_up": result["follow_up"],
            "confidence": result["confidence"],
            "type": result["type"],
            "context": result.get("context", {})
        }
        
    except Exception as e:
        logger.error(f"Error generating follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Model management endpoints
@app.get("/models")
async def get_available_models():
    """Get list of available models"""
    try:
        models = await model_manager.get_available_models()
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_name}/load")
async def load_model(model_name: str):
    """Load a specific model"""
    try:
        result = await model_manager.load_model(model_name)
        return result
        
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_name}/unload")
async def unload_model(model_name: str):
    """Unload a specific model"""
    try:
        result = await model_manager.unload_model(model_name)
        return result
        
    except Exception as e:
        logger.error(f"Error unloading model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        result = await model_manager.get_model_info(model_name)
        return result
        
    except Exception as e:
        logger.error(f"Error getting model info for {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/train")
async def train_model(request: TrainModelRequest):
    """Train a new model"""
    try:
        result = await model_manager.train_model({
            "name": request.name,
            "type": request.type,
            "data": request.data,
            "description": request.description,
            "tags": request.tags
        })
        return result
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """Delete a model"""
    try:
        result = await model_manager.delete_model(model_name)
        return result
        
    except Exception as e:
        logger.error(f"Error deleting model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{model_name}/performance")
async def get_model_performance(model_name: str):
    """Get model performance metrics"""
    try:
        result = await model_manager.get_model_performance(model_name)
        return result
        
    except Exception as e:
        logger.error(f"Error getting model performance for {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_name}/performance")
async def update_model_performance(model_name: str, performance_metrics: Dict[str, Any]):
    """Update model performance metrics"""
    try:
        result = await model_manager.update_model_performance(model_name, performance_metrics)
        
        # Record accuracy metrics
        if "accuracy" in performance_metrics:
            monitoring_service.record_ai_accuracy(
                model=model_name,
                task="model_performance",
                accuracy=performance_metrics["accuracy"]
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating model performance for {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Performance monitoring endpoints
@app.get("/monitoring/metrics")
async def get_system_metrics():
    """Get current system metrics"""
    try:
        result = await performance_monitor.get_system_metrics()
        return result
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/metrics/{metric_name}")
async def get_metrics_history(metric_name: str, hours: int = 24):
    """Get metrics history for a specific metric"""
    try:
        result = await performance_monitor.get_metrics_history(metric_name, hours)
        return {"metric_name": metric_name, "history": result}
        
    except Exception as e:
        logger.error(f"Error getting metrics history for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/alerts")
async def get_alerts(severity: Optional[str] = None, resolved: Optional[bool] = None):
    """Get alerts with optional filtering"""
    try:
        result = await performance_monitor.get_alerts(severity, resolved)
        return {"alerts": result}
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    try:
        result = await performance_monitor.resolve_alert(alert_id)
        return result
        
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/summary")
async def get_performance_summary(hours: int = 24):
    """Get performance summary"""
    try:
        # Get AI-specific monitoring data
        ai_metrics = monitoring_service.get_ai_metrics(hours)
        
        # Get general performance metrics
        general_metrics = await performance_monitor.get_performance_summary(hours)
        
        # Combine metrics
        combined_summary = {
            "ai_metrics": ai_metrics,
            "general_metrics": general_metrics,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return combined_summary
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/thresholds")
async def update_thresholds(request: ThresholdUpdateRequest):
    """Update monitoring thresholds"""
    try:
        result = await performance_monitor.update_thresholds(request.thresholds)
        return result
        
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/export")
async def export_metrics(format: str = "json", hours: int = 24):
    """Export metrics in specified format"""
    try:
        # Get AI-specific monitoring data
        ai_metrics = monitoring_service.export_metrics(format, hours)
        
        # Get general performance metrics
        general_metrics = await performance_monitor.export_metrics(format, hours)
        
        # Combine metrics
        combined_export = {
            "ai_metrics": ai_metrics,
            "general_metrics": general_metrics,
            "format": format,
            "hours": hours,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return combined_export
        
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User insights endpoint
@app.get("/users/{user_id}/insights")
async def get_user_insights(user_id: str):
    """Get user insights based on conversation history"""
    try:
        result = await response_generator.get_user_insights(user_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting user insights for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Intent and sentiment examples endpoints
@app.get("/examples/intent/{intent}")
async def get_intent_examples(intent: str):
    """Get example phrases for a specific intent"""
    try:
        result = await intent_recognition.get_intent_examples(intent)
        return {"intent": intent, "examples": result}
        
    except Exception as e:
        logger.error(f"Error getting intent examples for {intent}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/examples/sentiment/{sentiment}")
async def get_sentiment_examples(sentiment: str):
    """Get example phrases for a specific sentiment"""
    try:
        result = await sentiment_analysis.get_sentiment_examples(sentiment)
        return {"sentiment": sentiment, "examples": result}
        
    except Exception as e:
        logger.error(f"Error getting sentiment examples for {sentiment}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/examples/emotion/{emotion}")
async def get_emotion_examples(emotion: str):
    """Get example phrases for a specific emotion"""
    try:
        result = await sentiment_analysis.get_emotion_examples(emotion)
        return {"emotion": emotion, "examples": result}
        
    except Exception as e:
        logger.error(f"Error getting emotion examples for {emotion}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced chat endpoints
class GenerateResponseRequest(BaseModel):
    conversation_id: str
    message: str
    user_id: str
    context: Optional[Dict[str, Any]] = None

class SuggestionsRequest(BaseModel):
    conversation_id: str
    user_id: str
    context: Optional[Dict[str, Any]] = None

class SentimentAnalysisRequest(BaseModel):
    conversation_id: str

class SummaryRequest(BaseModel):
    conversation_id: str

@app.post("/generate-response")
async def generate_ai_response(request: GenerateResponseRequest):
    """Generate AI response for chat message"""
    import time
    start_time = time.time()
    success = True
    
    try:
        # Process message with NLP
        nlp_result = await nlp_processor.process(
            request.message,
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Recognize intent
        intent_result = await intent_recognition.analyze(
            request.message,
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Analyze sentiment
        sentiment_result = await sentiment_analysis.analyze(
            request.message,
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Generate response
        response_result = await response_generator.generate(
            request.message,
            intent_result["intent"],
            nlp_result["entities"],
            sentiment_result["sentiment"],
            request.user_id,
            request.conversation_id,
            request.context
        )
        
        # Record metrics
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="generate_response",
            response_time=response_time,
            success=success,
            model_used="response_generator"
        )
        
        # Record accuracy
        monitoring_service.record_ai_accuracy(
            model="response_generator",
            task="response_generation",
            accuracy=response_result["confidence"]
        )
        
        return {
            "response": response_result["response"],
            "confidence": response_result["confidence"],
            "intent": intent_result["intent"],
            "sentiment": sentiment_result["sentiment"],
            "entities": nlp_result["entities"],
            "suggestions": response_result.get("suggestions", []),
            "attachments": response_result.get("attachments", []),
            "metadata": {
                "nlp_processing": nlp_result,
                "intent_analysis": intent_result,
                "sentiment_analysis": sentiment_result,
                "response_generation": response_result,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
        
    except Exception as e:
        success = False
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_service.record_ai_request(
            request_type="generate_response",
            response_time=response_time,
            success=success,
            model_used="response_generator"
        )
        logger.error(f"Error generating AI response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggestions")
async def get_conversation_suggestions(request: SuggestionsRequest):
    """Get conversation suggestions"""
    try:
        # Get conversation history
        conversation_history = await response_generator.get_conversation_history(
            request.conversation_id,
            request.user_id
        )
        
        # Generate suggestions based on context
        suggestions = await response_generator.generate_suggestions(
            request.user_id,
            request.conversation_id,
            conversation_history,
            request.context
        )
        
        return {
            "suggestions": suggestions["suggestions"],
            "confidence": suggestions["confidence"],
            "context": suggestions.get("context", {}),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-sentiment")
async def analyze_conversation_sentiment(request: SentimentAnalysisRequest):
    """Analyze sentiment of entire conversation"""
    try:
        # Get conversation history
        conversation_history = await response_generator.get_conversation_history(
            request.conversation_id
        )
        
        # Analyze overall sentiment
        sentiment_result = await sentiment_analysis.analyze_conversation(
            conversation_history
        )
        
        return {
            "sentiment": sentiment_result["sentiment"],
            "confidence": sentiment_result["confidence"],
            "scores": sentiment_result["scores"],
            "emotions": sentiment_result["emotions"],
            "trend": sentiment_result.get("trend", "stable"),
            "metadata": sentiment_result.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"Error analyzing conversation sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summary")
async def generate_conversation_summary(request: SummaryRequest):
    """Generate conversation summary"""
    try:
        # Get conversation history
        conversation_history = await response_generator.get_conversation_history(
            request.conversation_id
        )
        
        # Generate summary
        summary_result = await response_generator.generate_summary(
            conversation_history,
            request.conversation_id
        )
        
        return {
            "summary": summary_result["summary"],
            "key_points": summary_result.get("key_points", []),
            "topics": summary_result.get("topics", []),
            "sentiment_trend": summary_result.get("sentiment_trend", "neutral"),
            "duration": summary_result.get("duration", 0),
            "message_count": summary_result.get("message_count", 0),
            "metadata": summary_result.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"Error generating conversation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Starting AI/ML Service...")
        
        # Start performance monitoring
        await performance_monitor.start_monitoring(interval=60)
        
        # Start AI monitoring service
        await monitoring_service.start_monitoring(interval=60)
        
        # Load default models
        await model_manager.load_model("intent_classifier")
        await model_manager.load_model("sentiment_analyzer")
        
        logger.info("AI/ML Service started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("Shutting down AI/ML Service...")
        
        # Stop performance monitoring
        await performance_monitor.stop_monitoring()
        
        # Stop AI monitoring service
        await monitoring_service.stop_monitoring()
        
        # Unload all models
        models = await model_manager.get_available_models()
        for model in models:
            if model["status"] == "loaded":
                await model_manager.unload_model(model["name"])
        
        logger.info("AI/ML Service shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3007,
        reload=True,
        log_level="info"
    )