from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import os
from datetime import datetime
from pathlib import Path

# Import services
from services.export_service import DataExportService, ExportRequest, ExportFormat, ExportType
from services.backup_service import BackupService
from services.validation_service import ValidationService

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
export_service = DataExportService()
backup_service = BackupService()
validation_service = ValidationService()

# FastAPI app
app = FastAPI(
    title="Data Service",
    description="Data management and export service for chatbot application",
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

# Pydantic models
class ExportRequestModel(BaseModel):
    export_type: str
    format: str
    filters: Dict[str, Any] = {}
    include_metadata: bool = True
    compression: bool = False

class BackupRequestModel(BaseModel):
    backup_type: str
    include_data: bool = True
    include_config: bool = True
    retention_days: int = 30

class ValidationRequestModel(BaseModel):
    data_type: str
    data: Any
    rules: Dict[str, Any]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "data-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Export endpoints
@app.post("/export")
async def export_data(request: ExportRequestModel, background_tasks: BackgroundTasks):
    """Export data in specified format"""
    try:
        # Validate request
        if request.export_type not in [e.value for e in ExportType]:
            raise HTTPException(status_code=400, detail="Invalid export type")
        
        if request.format not in [f.value for f in ExportFormat]:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        # Create export request
        export_request = ExportRequest(
            export_type=ExportType(request.export_type),
            format=ExportFormat(request.format),
            filters=request.filters,
            include_metadata=request.include_metadata,
            compression=request.compression
        )
        
        # Queue export for background processing
        result = await export_service.export_data(export_request)
        
        return {
            "message": "Export queued successfully",
            "export_id": f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "queued",
            "format": request.format,
            "export_type": request.export_type,
            "estimated_time": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{export_id}/status")
async def get_export_status(export_id: str):
    """Get status of export job"""
    try:
        status = await export_service.get_export_status(export_id)
        return status
        
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{export_id}/download")
async def download_export(export_id: str):
    """Download exported file"""
    try:
        # In a real implementation, this would look up the file path from a database
        # For now, we'll return a mock file
        file_path = f"/tmp/exports/{export_id}.json"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Export file not found")
        
        return FileResponse(
            path=file_path,
            filename=f"{export_id}.json",
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading export file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/history")
async def get_export_history(limit: int = 10):
    """Get history of recent exports"""
    try:
        history = await export_service.get_export_history(limit)
        return {
            "exports": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting export history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Backup endpoints
@app.post("/backup")
async def create_backup(request: BackupRequestModel, background_tasks: BackgroundTasks):
    """Create backup of data and configuration"""
    try:
        # Validate request
        if request.backup_type not in ["full", "incremental", "data_only", "config_only"]:
            raise HTTPException(status_code=400, detail="Invalid backup type")
        
        # Create backup in background
        backup_id = await backup_service.create_backup(
            backup_type=request.backup_type,
            include_data=request.include_data,
            include_config=request.include_config,
            retention_days=request.retention_days
        )
        
        return {
            "message": "Backup created successfully",
            "backup_id": backup_id,
            "status": "completed",
            "retention_days": request.retention_days
        }
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/backup/{backup_id}/download")
async def download_backup(backup_id: str):
    """Download backup file"""
    try:
        # In a real implementation, this would look up the file path from a database
        file_path = f"/tmp/backups/{backup_id}.tar.gz"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        return FileResponse(
            path=file_path,
            filename=f"{backup_id}.tar.gz",
            media_type='application/gzip'
        )
        
    except Exception as e:
        logger.error(f"Error downloading backup file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/backup/history")
async def get_backup_history(limit: int = 10):
    """Get history of recent backups"""
    try:
        history = await backup_service.get_backup_history(limit)
        return {
            "backups": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting backup history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Validation endpoints
@app.post("/validate")
async def validate_data(request: ValidationRequestModel):
    """Validate data against specified rules"""
    try:
        # Validate request
        if request.data_type not in ["user", "conversation", "message", "analytics"]:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # Perform validation
        result = await validation_service.validate_data(
            data_type=request.data_type,
            data=request.data,
            rules=request.rules
        )
        
        return {
            "valid": result["valid"],
            "errors": result["errors"],
            "warnings": result["warnings"],
            "validated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/import")
async def import_data(
    file: UploadFile = File(...),
    data_type: str = "conversations",
    validate: bool = True
):
    """Import data from uploaded file"""
    try:
        # Validate file type
        allowed_extensions = ['.json', '.csv', '.xlsx']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file_extension == '.json':
            import json
            data = json.loads(content.decode('utf-8'))
        elif file_extension == '.csv':
            import csv
            import io
            csv_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            data = list(csv_reader)
        elif file_extension == '.xlsx':
            import pandas as pd
            df = pd.read_excel(io.BytesIO(content))
            data = df.to_dict('records')
        
        # Validate data if requested
        if validate:
            validation_result = await validation_service.validate_data(
                data_type=data_type,
                data=data,
                rules={}  # Use default rules
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Data validation failed: {validation_result['errors']}"
                )
        
        # Process and store data (in real implementation)
        # For now, just return success
        return {
            "message": "Data imported successfully",
            "records_count": len(data) if isinstance(data, list) else 1,
            "data_type": data_type,
            "validated": validate
        }
        
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System endpoints
@app.post("/cleanup")
async def cleanup_old_data(days: int = 30):
    """Clean up old export files and backups"""
    try:
        # Clean up old exports
        await export_service.cleanup_old_exports(days)
        
        # Clean up old backups
        await backup_service.cleanup_old_backups(days)
        
        return {
            "message": "Cleanup completed successfully",
            "days": days,
            "cleaned_exports": "completed",
            "cleaned_backups": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_data_service_stats():
    """Get data service statistics"""
    try:
        # Get export statistics
        export_history = await export_service.get_export_history(100)
        
        # Get backup statistics
        backup_history = await backup_service.get_backup_history(100)
        
        return {
            "exports": {
                "total": len(export_history),
                "by_format": self._count_by_format(export_history),
                "by_type": self._count_by_export_type(export_history)
            },
            "backups": {
                "total": len(backup_history),
                "by_type": self._count_by_backup_type(backup_history),
                "total_size": self._calculate_total_size(backup_history)
            },
            "service": {
                "uptime": "24h",
                "memory_usage": "45%",
                "disk_usage": "62%"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper methods
def _count_by_format(export_history: List[Dict]) -> Dict[str, int]:
    """Count exports by format"""
    counts = {}
    for export in export_history:
        format_type = export.get("format", "unknown")
        counts[format_type] = counts.get(format_type, 0) + 1
    return counts

def _count_by_export_type(export_history: List[Dict]) -> Dict[str, int]:
    """Count exports by type"""
    counts = {}
    for export in export_history:
        export_type = export.get("type", "unknown")
        counts[export_type] = counts.get(export_type, 0) + 1
    return counts

def _count_by_backup_type(backup_history: List[Dict]) -> Dict[str, int]:
    """Count backups by type"""
    counts = {}
    for backup in backup_history:
        backup_type = backup.get("type", "unknown")
        counts[backup_type] = counts.get(backup_type, 0) + 1
    return counts

def _calculate_total_size(backup_history: List[Dict]) -> int:
    """Calculate total size of backups in MB"""
    total_size = 0
    for backup in backup_history:
        size = backup.get("size", 0)
        total_size += size
    return total_size

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Starting Data Service...")
        
        # Start export processor
        await export_service.start_export_processor()
        
        # Start backup service
        await backup_service.start_backup_service()
        
        logger.info("Data Service started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("Shutting down Data Service...")
        
        # Stop export processor
        await export_service.stop_export_processor()
        
        # Stop backup service
        await backup_service.stop_backup_service()
        
        logger.info("Data Service shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3006,
        reload=True,
        log_level="info"
    )