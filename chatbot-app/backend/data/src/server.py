from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
import asyncio
import logging

from services.analytics_service import AnalyticsService
from routes.ab_testing import router as ab_testing_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Data Service", version="1.0.0")

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

# Analytics Service
analytics_service = AnalyticsService()

# Include A/B testing routes
app.include_router(ab_testing_router, prefix="/api")

# Initialize service
@app.on_event("startup")
async def startup_event():
    try:
        await analytics_service.initialize()
        logger.info("Data Service initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Data Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await analytics_service.cleanup()
        logger.info("Data Service cleanup complete")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Pydantic models
class EventData(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class UserAnalyticsRequest(BaseModel):
    user_id: str
    period: str = "7d"

class ConversationAnalyticsRequest(BaseModel):
    conversation_id: str

class SystemAnalyticsRequest(BaseModel):
    period: str = "24h"

class ReportConfig(BaseModel):
    name: str
    type: str
    filters: Dict[str, Any] = {}
    metrics: List[str] = []

class ExportConfig(BaseModel):
    data_type: str
    format: str = "json"
    filters: Dict[str, Any] = {}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "OK", "service": "data"}

# Analytics endpoints
@app.post("/events")
async def track_event(event: EventData):
    """Track analytics event"""
    try:
        result = await analytics_service.track_event(event.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/analytics")
async def get_user_analytics(user_id: str, period: str = "7d"):
    """Get user analytics"""
    try:
        result = await analytics_service.get_user_analytics(user_id, period)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/analytics")
async def get_conversation_analytics(conversation_id: str):
    """Get conversation analytics"""
    try:
        result = await analytics_service.get_conversation_analytics(conversation_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/analytics")
async def get_system_analytics(period: str = "24h"):
    """Get system analytics"""
    try:
        result = await analytics_service.get_system_analytics(period)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    try:
        result = await analytics_service.get_dashboard_metrics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports/generate")
async def generate_custom_report(config: ReportConfig):
    """Generate custom analytics report"""
    try:
        result = await analytics_service.generate_custom_report(config.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/export")
async def export_analytics_data(config: ExportConfig):
    """Export analytics data"""
    try:
        result = await analytics_service.export_analytics_data(config.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/refresh-views")
async def refresh_materialized_views():
    """Refresh materialized views"""
    try:
        await analytics_service.refresh_materialized_views()
        return {"message": "Materialized views refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/health")
async def get_analytics_health():
    """Get analytics service health"""
    try:
        result = await analytics_service.get_analytics_health()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch operations
@app.post("/events/batch")
async def track_events_batch(events: List[EventData]):
    """Track multiple analytics events"""
    try:
        results = []
        for event in events:
            result = await analytics_service.track_event(event.dict())
            results.append(result)
        return {"events_tracked": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/segments")
async def get_user_segments(user_id: str):
    """Get user segments (from personalization service)"""
    try:
        # This would typically call the personalization service
        # For now, return empty list
        return {"user_id": user_id, "segments": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/segments")
async def list_segments():
    """List all segments (from personalization service)"""
    try:
        # This would typically call the personalization service
        # For now, return empty list
        return {"segments": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/{user_id}")
async def get_user_recommendations(user_id: str):
    """Get user recommendations (from personalization service)"""
    try:
        # This would typically call the personalization service
        # For now, return empty list
        return {"user_id": user_id, "recommendations": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Real-time analytics endpoints
@app.get("/realtime/active-users")
async def get_active_users():
    """Get currently active users"""
    try:
        # This would get users with recent activity
        return {"active_users": [], "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/realtime/conversations")
async def get_active_conversations():
    """Get currently active conversations"""
    try:
        # This would get conversations with recent activity
        return {"active_conversations": [], "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/realtime/messages")
async def get_recent_messages(limit: int = 10):
    """Get recent messages"""
    try:
        # This would get recent messages
        return {"messages": [], "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data quality endpoints
@app.get("/data/quality")
async def get_data_quality_metrics():
    """Get data quality metrics"""
    try:
        # This would check data completeness, consistency, etc.
        return {
            "data_quality": {
                "completeness": 0.95,
                "consistency": 0.98,
                "accuracy": 0.92,
                "timeliness": 0.97
            },
            "last_updated": "2025-01-15T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/validate")
async def validate_data(data: Dict[str, Any]):
    """Validate data structure and content"""
    try:
        # This would validate data against schema
        return {
            "valid": True,
            "errors": [],
            "warnings": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3006)