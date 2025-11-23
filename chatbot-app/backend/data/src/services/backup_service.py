import asyncio
import logging
import tarfile
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
import aiofiles
from dataclasses import dataclass

@dataclass
class BackupRequest:
    backup_type: str
    include_data: bool
    include_config: bool
    retention_days: int

@dataclass
class BackupResult:
    backup_id: str
    file_path: str
    file_size: int
    backup_type: str
    created_at: datetime
    retention_until: datetime

class BackupService:
    def __init__(self, storage_path: str = "/tmp/backups"):
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.backup_queue = asyncio.Queue()
        self.is_processing = False
        
    async def start_backup_service(self):
        """Start the backup service"""
        self.is_processing = True
        asyncio.create_task(self._process_backup_queue())
        self.logger.info("Backup service started")
    
    async def stop_backup_service(self):
        """Stop the backup service"""
        self.is_processing = False
        self.logger.info("Backup service stopped")
    
    async def _process_backup_queue(self):
        """Process backup requests from the queue"""
        while self.is_processing:
            try:
                backup_request = await asyncio.wait_for(
                    self.backup_queue.get(), 
                    timeout=1.0
                )
                
                # Process the backup
                result = await self._create_backup(backup_request)
                
                # Log completion
                self.logger.info(f"Backup completed: {result.backup_type} - {result.backup_id}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing backup queue: {e}")
    
    async def create_backup(self, backup_type: str, include_data: bool = True, 
                          include_config: bool = True, retention_days: int = 30) -> str:
        """Create a backup"""
        try:
            # Create backup request
            backup_request = BackupRequest(
                backup_type=backup_type,
                include_data=include_data,
                include_config=include_config,
                retention_days=retention_days
            )
            
            # Add to queue for processing
            await self.backup_queue.put(backup_request)
            
            # Return backup ID
            return f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise
    
    async def _create_backup(self, request: BackupRequest) -> BackupResult:
        """Internal method to create backup"""
        start_time = datetime.utcnow()
        
        try:
            # Generate backup ID
            backup_id = f"backup_{start_time.strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup file path
            backup_file = self.storage_path / f"{backup_id}.tar.gz"
            
            # Create temporary directory for backup
            temp_dir = Path("/tmp") / f"backup_{backup_id}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # Add data to backup if requested
                if request.include_data:
                    await self._backup_data(temp_dir / "data")
                
                # Add config to backup if requested
                if request.include_config:
                    await self._backup_config(temp_dir / "config")
                
                # Add metadata
                metadata = {
                    "backup_id": backup_id,
                    "backup_type": request.backup_type,
                    "created_at": start_time.isoformat(),
                    "retention_days": request.retention_days,
                    "include_data": request.include_data,
                    "include_config": request.include_config
                }
                
                metadata_file = temp_dir / "metadata.json"
                async with aiofiles.open(metadata_file, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2))
                
                # Create tar.gz archive
                await self._create_tar_gz(backup_file, temp_dir)
                
                # Get file size
                file_size = backup_file.stat().st_size
                
                # Calculate retention until date
                retention_until = start_time + timedelta(days=request.retention_days)
                
                return BackupResult(
                    backup_id=backup_id,
                    file_path=str(backup_file),
                    file_size=file_size,
                    backup_type=request.backup_type,
                    created_at=start_time,
                    retention_until=retention_until
                )
                
            finally:
                # Clean up temporary directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise
    
    async def _backup_data(self, data_dir: Path):
        """Backup application data"""
        try:
            # Create data directory structure
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup database (mock implementation)
            db_backup = data_dir / "database"
            db_backup.mkdir(exist_ok=True)
            
            # Create mock database backup file
            db_file = db_backup / "chatbot_backup.sql"
            mock_db_content = """
-- Chatbot Database Backup
-- Backup Date: {date}

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    admin_id UUID REFERENCES users(id),
    title VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    sender_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50) DEFAULT 'text'
);

-- Insert sample data
INSERT INTO users (id, email, password_hash, name, role) VALUES
    ('user_001', 'john.doe@example.com', 'hashed_password_1', 'John Doe', 'user'),
    ('user_002', 'jane.smith@example.com', 'hashed_password_2', 'Jane Smith', 'user'),
    ('admin_001', 'admin@example.com', 'hashed_password_3', 'Admin User', 'admin');

INSERT INTO conversations (id, user_id, title, status) VALUES
    ('conv_001', 'user_001', 'Account Setup', 'resolved'),
    ('conv_002', 'user_002', 'Billing Inquiry', 'open');

INSERT INTO messages (id, conversation_id, sender_id, content, message_type) VALUES
    ('msg_001', 'conv_001', 'user_001', 'Hello, I need help setting up my account', 'text'),
    ('msg_002', 'conv_001', 'admin_001', 'I''d be happy to help you with account setup!', 'text'),
    ('msg_003', 'conv_002', 'user_002', 'I have a question about my billing', 'text');
            """.format(date=datetime.utcnow().isoformat())
            
            async with aiofiles.open(db_file, 'w') as f:
                await f.write(mock_db_content)
            
            # Backup user files (mock implementation)
            files_backup = data_dir / "files"
            files_backup.mkdir(exist_ok=True)
            
            # Create mock user files
            user_files = [
                "user_001_profile.json",
                "user_002_profile.json",
                "conversation_logs.json"
            ]
            
            for filename in user_files:
                file_path = files_backup / filename
                mock_content = json.dumps({
                    "file": filename,
                    "created_at": datetime.utcnow().isoformat(),
                    "data": "Mock file content"
                }, indent=2)
                
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(mock_content)
            
            self.logger.info(f"Data backup completed: {data_dir}")
            
        except Exception as e:
            self.logger.error(f"Error backing up data: {e}")
            raise
    
    async def _backup_config(self, config_dir: Path):
        """Backup application configuration"""
        try:
            # Create config directory structure
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup environment variables
            env_file = config_dir / ".env.backup"
            mock_env_content = """
# Chatbot Application Configuration
# Backup Date: {date}

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Services
AUTH_SERVICE_URL=http://localhost:3001
CHAT_SERVICE_URL=http://localhost:3002
ADMIN_SERVICE_URL=http://localhost:3003
PERSONALIZATION_SERVICE_URL=http://localhost:3004
AI_SERVICE_URL=http://localhost:3005
DATA_SERVICE_URL=http://localhost:3006

# Frontend
FRONTEND_URL=http://localhost:3000
            """.format(date=datetime.utcnow().isoformat())
            
            async with aiofiles.open(env_file, 'w') as f:
                await f.write(mock_env_content)
            
            # Backup Kubernetes configurations
            k8s_dir = config_dir / "kubernetes"
            k8s_dir.mkdir(exist_ok=True)
            
            # Create mock Kubernetes configs
            k8s_files = {
                "namespace.yaml": """
apiVersion: v1
kind: Namespace
metadata:
  name: chatbot-app
""",
                "configmap.yaml": """
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: chatbot-app
data:
  database-url: "postgresql://postgres:password@postgres:5432/chatbot"
  redis-url: "redis://redis:6379"
  jwt-secret: "your-secret-key-here"
""",
                "deployment.yaml": """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-app
  namespace: chatbot-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot-app
  template:
    metadata:
      labels:
        app: chatbot-app
    spec:
      containers:
      - name: chatbot-app
        image: chatbot-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database-url
"""
            }
            
            for filename, content in k8s_files.items():
                file_path = k8s_dir / filename
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(content)
            
            # Backup Docker configurations
            docker_dir = config_dir / "docker"
            docker_dir.mkdir(exist_ok=True)
            
            docker_compose_file = docker_dir / "docker-compose.yml"
            mock_docker_content = """
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: chatbot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  chatbot-app:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/chatbot
      - REDIS_URL=redis://redis:6379

volumes:
  postgres_data:
  redis_data:
            """
            
            async with aiofiles.open(docker_compose_file, 'w') as f:
                await f.write(mock_docker_content)
            
            self.logger.info(f"Config backup completed: {config_dir}")
            
        except Exception as e:
            self.logger.error(f"Error backing up config: {e}")
            raise
    
    async def _create_tar_gz(self, output_file: Path, source_dir: Path):
        """Create a tar.gz archive"""
        try:
            with tarfile.open(output_file, 'w:gz') as tar:
                tar.add(source_dir, arcname=source_dir.name)
            
            self.logger.info(f"Archive created: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating archive: {e}")
            raise
    
    async def get_backup_status(self, backup_id: str) -> Dict[str, Any]:
        """Get status of a backup job"""
        try:
            backup_file = self.storage_path / f"{backup_id}.tar.gz"
            
            if not backup_file.exists():
                return {
                    "backup_id": backup_id,
                    "status": "not_found",
                    "message": "Backup file not found"
                }
            
            file_size = backup_file.stat().st_size
            created_at = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            return {
                "backup_id": backup_id,
                "status": "completed",
                "file_size": file_size,
                "created_at": created_at.isoformat(),
                "file_path": str(backup_file)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting backup status: {e}")
            raise
    
    async def get_backup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history of recent backups"""
        try:
            backups = []
            
            # Get all backup files
            backup_files = list(self.storage_path.glob("backup_*.tar.gz"))
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Limit results
            backup_files = backup_files[:limit]
            
            for backup_file in backup_files:
                try:
                    backup_id = backup_file.stem
                    file_size = backup_file.stat().st_size
                    created_at = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    
                    backups.append({
                        "id": backup_id,
                        "type": "full",  # Default type, could be extracted from metadata
                        "size": file_size,
                        "created_at": created_at.isoformat(),
                        "status": "completed"
                    })
                except Exception as e:
                    self.logger.warning(f"Error processing backup file {backup_file}: {e}")
                    continue
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Error getting backup history: {e}")
            raise
    
    async def cleanup_old_backups(self, days: int = 30):
        """Clean up old backup files"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted_count = 0
            for backup_file in self.storage_path.glob("backup_*.tar.gz"):
                try:
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old backup file: {backup_file}")
                except Exception as e:
                    self.logger.warning(f"Error deleting backup file {backup_file}: {e}")
                    continue
            
            self.logger.info(f"Cleanup completed: {deleted_count} old backup files deleted")
            
        except Exception as e:
            self.logger.error(f"Error during backup cleanup: {e}")
            raise
    
    async def restore_backup(self, backup_id: str, restore_path: str = "/tmp/restore") -> Dict[str, Any]:
        """Restore a backup to specified path"""
        try:
            backup_file = self.storage_path / f"{backup_id}.tar.gz"
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # Create restore directory
            restore_dir = Path(restore_path)
            restore_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract backup
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(restore_dir)
            
            # Read metadata
            metadata_file = restore_dir / "metadata.json"
            if metadata_file.exists():
                async with aiofiles.open(metadata_file, 'r') as f:
                    metadata = json.loads(await f.read())
            else:
                metadata = {}
            
            return {
                "backup_id": backup_id,
                "status": "completed",
                "restore_path": str(restore_dir),
                "metadata": metadata,
                "restored_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {e}")
            raise