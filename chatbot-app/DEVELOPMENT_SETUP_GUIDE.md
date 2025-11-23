# Development Setup Guide - Quick Start

This guide provides step-by-step instructions for junior developers to set up the chatbot application development environment from scratch.

## Prerequisites Checklist

Before starting, ensure you have the following installed:

### Required Software
- **Node.js**: Version 18.0.0 or higher
- **Python**: Version 3.9 or higher  
- **Docker**: Version 20.0 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: Latest version
- **PostgreSQL**: Version 13+ (or use Docker)
- **Redis**: Version 6.0+ (or use Docker)

### Development Tools (Recommended)
- **VS Code** with extensions:
  - TypeScript and JavaScript Language Features
  - Python extension
  - Docker extension
  - Kubernetes extension
- **Postman** or **Insomnia** for API testing
- **pgAdmin** for database management

## Step 1: Clone and Navigate to Project

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd chatbot-app

# Verify you're in the right directory
pwd
# Should show: .../chatbot-app
```

## Step 2: Environment Configuration

### Create Backend Environment Files

#### API Gateway (.env)
```bash
cp backend/.env.example backend/gateway/.env
```

Edit `backend/gateway/.env`:
```bash
NODE_ENV=development
PORT=8080
FRONTEND_URL=http://localhost:3000

# Database (for gateway health checks)
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=dev-secret-key-change-in-production
```

#### Auth Service (.env)
```bash
cp backend/.env.example backend/auth/.env
```

Edit `backend/auth/.env`:
```bash
NODE_ENV=development
PORT=3001
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot
REDIS_URL=redis://localhost:6379
SESSION_SECRET=dev-session-secret
JWT_SECRET=dev-jwt-secret
FRONTEND_URL=http://localhost:3000
OAUTH_CALLBACK_BASE_URL=http://localhost:3001/api/auth

# OAuth Configuration (get these from respective providers)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=your-microsoft-tenant-id
```

#### Chat Service (.env)
```bash
cp backend/.env.example backend/chat/.env
```

Edit `backend/chat/.env`:
```bash
NODE_ENV=development
PORT=3002
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot
REDIS_URL=redis://localhost:6379
AI_SERVICE_URL=http://localhost:3007
FRONTEND_URL=http://localhost:3000
```

### Create Frontend Environment Files

#### Shell Application (.env)
Create `frontend/shell/.env`:
```bash
VITE_API_URL=http://localhost:8080
VITE_WS_URL=http://localhost:3002
VITE_APP_ENV=development
```

#### Chat Application (.env)
Create `frontend/chat/.env`:
```bash
VITE_API_URL=http://localhost:8080
VITE_WS_URL=http://localhost:3002
VITE_APP_ENV=development
```

## Step 3: Start Infrastructure Services

### Using Docker Compose (Recommended)

Create `docker-compose.dev.yml` in the root directory:
```yaml
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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

Start infrastructure:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

Verify services are running:
```bash
docker-compose -f docker-compose.dev.yml ps
```

## Step 4: Database Setup

### Initialize Database Schema

```bash
# Navigate to infrastructure directory
cd infrastructure/database

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python migrate.py up

# Initialize with basic schema
psql -h localhost -U postgres -d chatbot -f init.sql
```

Verify database connection:
```bash
psql -h localhost -U postgres -d chatbot -c "\dt"
```

You should see tables: users, conversations, messages, and extended schema tables.

## Step 5: Install Dependencies

### Backend Services

#### Install Node.js Dependencies
```bash
# Auth Service
cd backend/auth
npm install

# Chat Service  
cd ../chat
npm install

# Admin Service
cd ../admin
npm install

# Gateway Service
cd ../gateway
npm install
```

#### Install Python Dependencies
```bash
# AI Service
cd ../ai
pip install -r requirements.txt

# Data Service
cd ../data
pip install -r requirements.txt

# Personalization Service
cd ../personalization
pip install -r requirements.txt

# Testing Framework
cd ../testing
pip install -r requirements.txt
```

### Frontend Applications

```bash
# Shell Application
cd ../../frontend/shell
npm install

# Chat Application
cd ../chat
npm install

# Auth Application
cd ../auth
npm install

# Admin Application
cd ../admin
npm install

# Profile Application
cd ../profile
npm install

# Shared UI Components
cd ../../shared-ui
npm install
```

## Step 6: Start Development Servers

### Terminal 1: Start Infrastructure
```bash
# Ensure services are running
docker-compose -f docker-compose.dev.yml ps
```

### Terminal 2: Start Backend Services
```bash
# Start API Gateway (Required first)
cd backend/gateway
npm run dev
# Gateway should start on http://localhost:8080
```

### Terminal 3: Start Auth Service
```bash
cd backend/auth
npm run dev
# Auth should start on http://localhost:3001
```

### Terminal 4: Start Chat Service
```bash
cd backend/chat
npm run dev
# Chat should start on http://localhost:3002
```

### Terminal 5: Start AI Service
```bash
cd backend/ai
uvicorn src.main:app --reload --host 0.0.0.0 --port 3007
# AI should start on http://localhost:3007
```

### Terminal 6: Start Data Service
```bash
cd backend/data
uvicorn src.server:app --reload --host 0.0.0.0 --port 3006
# Data should start on http://localhost:3006
```

### Terminal 7: Start Personalization Service
```bash
cd backend/personalization
uvicorn src.main:app --reload --host 0.0.0.0 --port 3005
# Personalization should start on http://localhost:3005
```

### Terminal 8: Start Frontend Applications
```bash
# Start Shell (Main App)
cd frontend/shell
npm start
# Shell should start on http://localhost:3000

# In a new terminal, start Chat
cd frontend/chat
npm start
# Chat should start on http://localhost:3002
```

## Step 7: Verify Installation

### Health Check Endpoints

Test that all services are responding:

```bash
# API Gateway
curl http://localhost:8080/health

# Auth Service
curl http://localhost:3001/health

# Chat Service  
curl http://localhost:3002/health

# AI Service
curl http://localhost:3007/health

# Data Service
curl http://localhost:3006/health

# Personalization Service
curl http://localhost:3005/health
```

All endpoints should return `{"status": "OK"}` or similar success messages.

### Test API Gateway
```bash
curl http://localhost:8080/
```

Should return service information:
```json
{
  "message": "Chatbot API Gateway",
  "version": "1.0.0",
  "services": {
    "auth": "http://localhost:3001",
    "chat": "http://localhost:3002",
    "admin": "http://localhost:3003",
    "personalization": "http://localhost:3005",
    "data": "http://localhost:3006",
    "ai": "http://localhost:3007"
  }
}
```

### Test Database Connection
```bash
# Connect to database and verify tables
psql -h localhost -U postgres -d chatbot -c "\dt"
```

### Test Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

## Step 8: Run Tests

### Backend Tests
```bash
cd backend/testing

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific service tests
pytest -m ai
pytest -m data
pytest -m personalization

# Run API tests
pytest -m api
```

### Frontend Tests
```bash
# Run tests for specific frontend apps
cd frontend/chat
npm test

cd frontend/auth
npm test
```

## Step 9: Access the Application

### Main Application
- **Shell App**: http://localhost:3000
- **Chat App**: http://localhost:3002  
- **Auth App**: http://localhost:3003
- **Admin App**: http://localhost:3004
- **Profile App**: http://localhost:3005

### API Documentation
- **Gateway**: http://localhost:8080/docs
- **AI Service**: http://localhost:3007/docs
- **Data Service**: http://localhost:3006/docs
- **Personalization Service**: http://localhost:3005/docs

### Monitoring
- **Prometheus**: http://localhost:9090 (if using Kubernetes)
- **Grafana**: http://localhost:3000 (if using Kubernetes)

## Common Issues and Troubleshooting

### Port Conflicts
If you get port conflicts:
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.dev.yml logs postgres

# Restart PostgreSQL
docker-compose -f docker-compose.dev.yml restart postgres
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose -f docker-compose.dev.yml logs redis

# Test Redis connection
redis-cli -h localhost -p 6379 ping
```

### Node.js Dependencies Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Python Dependencies Issues
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies in virtual environment
pip install -r requirements.txt
```

### Docker Issues
```bash
# Restart Docker services
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

# Check Docker logs
docker-compose -f docker-compose.dev.yml logs
```

## Development Workflow

### Starting Development
1. Start infrastructure: `docker-compose -f docker-compose.dev.yml up -d`
2. Start backend services (multiple terminals)
3. Start frontend applications
4. Run tests to verify setup
5. Access application at http://localhost:3000

### Daily Development
1. Pull latest changes: `git pull`
2. Run tests: `pytest && npm test`
3. Start development servers
4. Make changes and test
5. Run linting and formatting
6. Commit and push changes

### Stopping Development
1. Stop all development servers (Ctrl+C in each terminal)
2. Stop infrastructure: `docker-compose -f docker-compose.dev.yml down`

## Next Steps

Once setup is complete:

1. **Explore the Codebase**: Start with the gateway service and API routes
2. **Review Architecture**: Study the comprehensive technical index
3. **Understand APIs**: Check the API specifications document
4. **Run Tests**: Familiarize yourself with the testing framework
5. **Make Changes**: Start with small bug fixes or feature additions

## Getting Help

### Documentation
- **Comprehensive Technical Index**: `COMPREHENSIVE_TECHNICAL_INDEX.md`
- **API Specifications**: `API_SPECIFICATIONS.md`
- **Database Schema**: `infrastructure/database/README.md`

### Community
- Check existing issues in the repository
- Review pull requests for code patterns
- Ask questions in team channels

### Logs and Debugging
- Check service logs in terminal outputs
- Use browser developer tools for frontend issues
- Monitor database queries with pgAdmin
- Check Redis data with redis-cli

This setup guide provides everything needed to get the chatbot application running locally for development. Follow each step carefully and refer to the comprehensive technical index for detailed architecture information.