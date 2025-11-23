# Chatbot Application - Developer Guide

[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.5+-blue.svg)](https://typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal.svg)](https://fastapi.tiangolo.com/)

A **modern, microservices-based chatbot application** built with React, Node.js, Python, and AI/ML capabilities. This system demonstrates enterprise-grade architecture with real-time communication, artificial intelligence processing, and scalable infrastructure.

## 🎯 Project Overview

This chatbot application provides:

- **Real-time chat functionality** with WebSocket communication
- **AI-powered natural language processing** and intent recognition
- **Multi-tenant support** with OAuth2 authentication (Google, GitHub, Microsoft)
- **Administrative dashboard** for conversation and user management
- **Analytics and reporting** with A/B testing capabilities
- **Personalization engine** for user-specific experiences
- **Microfrontend architecture** with independent, deployable frontend apps

### Key Capabilities

✅ **Microservices Architecture** - Independent, scalable backend services  
✅ **Real-time Communication** - WebSocket-based messaging with presence indicators  
✅ **AI/ML Integration** - NLP processing, sentiment analysis, intent recognition  
✅ **Multi-language Support** - Frontend and backend internationalization  
✅ **Production Ready** - Kubernetes deployment, monitoring, logging  
✅ **Developer Friendly** - Comprehensive testing, documentation, and tools  

---

## 🚀 Quick Start for Junior Developers

### 1. Prerequisites
Ensure you have installed:
- **Node.js** 18.0.0+ ([download](https://nodejs.org/))
- **Python** 3.9+ ([download](https://python.org/))
- **Docker** 20.0+ ([download](https://docker.com/))
- **Git** ([download](https://git-scm.com/))

### 2. Clone and Setup
```bash
git clone <repository-url>
cd chatbot-app

# Copy environment files and update with your settings
cp backend/.env.example backend/gateway/.env
cp backend/.env.example backend/auth/.env
cp backend/.env.example backend/chat/.env

# Create frontend environment files
echo "VITE_API_URL=http://localhost:8080" > frontend/shell/.env
echo "VITE_WS_URL=http://localhost:3002" > frontend/chat/.env
```

### 3. Start Infrastructure
```bash
# Start PostgreSQL and Redis with Docker
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f docker-compose.dev.yml ps
```

### 4. Database Setup
```bash
cd infrastructure/database

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python migrate.py up

# Initialize database schema
psql -h localhost -U postgres -d chatbot -f init.sql
```

### 5. Install Dependencies
```bash
# Backend services (Node.js)
cd backend/gateway && npm install
cd ../auth && npm install
cd ../chat && npm install
cd ../admin && npm install

# Backend services (Python)
cd ../ai && pip install -r requirements.txt
cd ../data && pip install -r requirements.txt
cd ../personalization && pip install -r requirements.txt

# Frontend applications
cd ../../frontend/shell && npm install
cd ../chat && npm install
cd ../auth && npm install
cd ../admin && npm install
cd ../profile && npm install

# Shared UI components
cd ../../shared-ui && npm install
```

### 6. Start Development Servers

You'll need **8 terminal windows** (or use a terminal multiplexer like `tmux`):

```bash
# Terminal 1: API Gateway
cd backend/gateway
npm run dev
# → http://localhost:8080

# Terminal 2: Auth Service
cd backend/auth
npm run dev
# → http://localhost:3001

# Terminal 3: Chat Service
cd backend/chat
npm run dev
# → http://localhost:3002

# Terminal 4: AI Service
cd backend/ai
uvicorn src.main:app --reload --host 0.0.0.0 --port 3007
# → http://localhost:3007

# Terminal 5: Data Service
cd backend/data
uvicorn src.server:app --reload --host 0.0.0.0 --port 3006
# → http://localhost:3006

# Terminal 6: Personalization Service
cd backend/personalization
uvicorn src.main:app --reload --host 0.0.0.0 --port 3005
# → http://localhost:3005

# Terminal 7: Shell Application (Main Frontend)
cd frontend/shell
npm start
# → http://localhost:3000

# Terminal 8: Chat Application
cd frontend/chat
npm start
# → http://localhost:3002
```

### 7. Verify Installation
```bash
# Test all services are responding
curl http://localhost:8080/health
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3005/health
curl http://localhost:3006/health
curl http://localhost:3007/health

# Should return {"status": "OK"} for each service
```

**🎉 You're all set! Access the application at http://localhost:3000**

For detailed setup instructions, see: **[DEVELOPMENT_SETUP_GUIDE.md](./DEVELOPMENT_SETUP_GUIDE.md)**

---

## 🏗️ System Architecture Summary

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
│  Shell │ Chat │ Auth │ Admin │ Profile (React + TypeScript)    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                        API Gateway                              │
│                   (Express.js + TypeScript)                     │
│           Routes requests to appropriate backend services       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                     Backend Services                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  Auth   │ │  Chat   │ │   AI    │ │  Data   │ │   ...   │   │
│  │  Node.js│ │ Node.js │ │ Python  │ │ Python  │ │   ...   │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                      Data Layer                                 │
│    ┌─────────────┐    ┌─────────────┐                          │
│    │ PostgreSQL  │    │    Redis    │                          │
│    │  Database   │    │    Cache    │                          │
│    └─────────────┘    └─────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### **Frontend Applications** (React + TypeScript)
- **Shell Application** - Main app orchestrator with Tailwind CSS
- **Chat Application** - Real-time messaging interface
- **Auth Application** - Login/registration flows
- **Admin Application** - Administrative dashboard
- **Profile Application** - User settings and preferences

#### **Backend Services** (Microservices Architecture)
| Service | Technology | Purpose | Port |
|---------|------------|---------|------|
| **API Gateway** | Node.js + Express | Request routing & middleware | 8080 |
| **Auth Service** | Node.js + Express | OAuth2, JWT, sessions | 3001 |
| **Chat Service** | Node.js + Socket.io | Real-time messaging | 3002 |
| **Admin Service** | Node.js + Express | Administrative functions | 3003 |
| **AI Service** | Python + FastAPI | NLP, intent recognition | 3007 |
| **Data Service** | Python + FastAPI | Analytics, reporting | 3006 |
| **Personalization** | Python + FastAPI | User insights, recommendations | 3005 |

#### **Infrastructure & Tools**
- **Database**: PostgreSQL 13+ with UUID primary keys
- **Cache**: Redis 6.0+ for sessions and caching
- **Container**: Docker with Kubernetes orchestration
- **Monitoring**: Prometheus + Grafana + AlertManager
- **Security**: OAuth2, JWT, CSRF protection, rate limiting

---

## 👨‍💻 For Junior Developers

This section is specifically designed for developers who are new to the project and want to start contributing quickly.

### What You Need to Know to Begin

#### **1. Understanding the System**
- **Start with the Gateway Service**: This is the central entry point that routes all requests
- **Learn WebSocket Basics**: The chat functionality uses real-time WebSocket communication
- **Understand Microservices**: Each service is independent and communicates via HTTP/REST APIs
- **Database Schema**: Core tables: `users`, `conversations`, `messages` with relationships

#### **2. Key Technologies to Learn**
- **TypeScript**: Used across all Node.js services and frontend applications
- **Python FastAPI**: Used for AI, data, and personalization services
- **React**: Modern functional components with hooks
- **Docker**: Containerization for consistent development environments
- **PostgreSQL**: Primary database with JSONB fields for flexibility

#### **3. Development Workflow**
```bash
# Start your development day
docker-compose -f docker-compose.dev.yml up -d  # Start infrastructure
cd backend/gateway && npm run dev               # Start gateway first
# Start other services in separate terminals

# Make changes and test
npm test              # Run tests
npm run lint          # Check code quality

# Check service logs for debugging
curl http://localhost:8080/health  # Check if gateway is working
```

#### **4. Common Development Tasks**

**Adding a New API Endpoint:**
1. Create route in appropriate service (e.g., `backend/chat/src/routes/`)
2. Add request/response validation schemas
3. Update API Gateway routes if needed
4. Write tests in `backend/testing/`
5. Document in API specifications

**Frontend Component Development:**
1. Use shared UI components from `shared-ui/src/components/`
2. Follow existing patterns in other frontend apps
3. Use TypeScript interfaces for type safety
4. Integrate with WebSocket for real-time features

**Database Changes:**
1. Create migration in `infrastructure/database/migrations/`
2. Update TypeScript interfaces/Python models
3. Test with sample data
4. Update documentation

#### **5. Where to Find Help**

**📚 Documentation Files:**
- **[COMPREHENSIVE_TECHNICAL_INDEX.md](./COMPREHENSIVE_TECHNICAL_INDEX.md)** - Complete system architecture
- **[DEVELOPMENT_SETUP_GUIDE.md](./DEVELOPMENT_SETUP_GUIDE.md)** - Detailed development setup
- **[API_SPECIFICATIONS.md](./API_SPECIFICATIONS.md)** - Complete API documentation

**🔧 Key Files to Study:**
- `backend/gateway/src/server.ts` - Main API gateway implementation
- `backend/chat/src/socket/socketHandler.ts` - WebSocket handling
- `backend/ai/src/services/nlp_processor.py` - AI processing pipeline
- `frontend/chat/src/components/ChatInterface.tsx` - Main chat UI component

**🧪 Testing:**
- Run all tests: `cd backend/testing && pytest`
- Frontend tests: `cd frontend/chat && npm test`
- API testing with Postman or curl commands

**🚨 Debugging Tips:**
- Check service logs in terminal outputs
- Use browser developer tools for frontend issues
- Monitor database with pgAdmin
- Check Redis data with `redis-cli`

### Quick Contribution Guide

#### **Finding Your First Task**
1. Look for `TODO` comments in the codebase
2. Check for open issues labeled "good first issue"
3. Fix failing tests
4. Improve documentation
5. Add unit tests for untested functions

#### **Making Your First Change**
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make minimal, focused changes
3. Run tests: `pytest && npm test`
4. Check code quality: `npm run lint`
5. Commit with clear message: `git commit -m "feat(service): add new endpoint"`
6. Push and create pull request

---

## 📁 Project Structure

```
chatbot-app/
├── 📄 README.md                           # This file - main entry point
├── 📄 COMPREHENSIVE_TECHNICAL_INDEX.md    # Complete system architecture
├── 📄 DEVELOPMENT_SETUP_GUIDE.md          # Detailed setup instructions
├── 📄 API_SPECIFICATIONS.md               # Complete API documentation
├── docker-compose.dev.yml                 # Development infrastructure
│
├── backend/                               # Backend microservices
│   ├── gateway/                          # API Gateway (Node.js)
│   ├── auth/                             # Authentication Service
│   ├── chat/                             # Real-time Chat Service
│   ├── admin/                            # Administrative Service
│   ├── ai/                               # AI/ML Processing (Python)
│   ├── data/                             # Analytics Service (Python)
│   ├── personalization/                  # Personalization Engine (Python)
│   └── testing/                          # Testing Framework
│
├── frontend/                              # Frontend microfrontends
│   ├── shell/                            # Main App Shell
│   ├── chat/                             # Chat Interface
│   ├── auth/                             # Authentication UI
│   ├── admin/                            # Admin Dashboard
│   └── profile/                           # User Profile Management
│
├── shared-ui/                             # Reusable UI components
│   └── src/components/                   # Shared React components
│
└── infrastructure/                        # Infrastructure & deployment
    ├── database/                         # Database schema & migrations
    ├── k8s/                              # Kubernetes configurations
    └── monitoring/                       # Monitoring setup
```

### Key Directory Explanations

#### **Backend Services Structure**
Each backend service follows this pattern:
```
service-name/
├── src/
│   ├── routes/           # API route handlers
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   ├── middleware/       # Custom middleware
│   ├── utils/            # Utility functions
│   ├── config/           # Configuration files
│   └── server.ts         # Service entry point
├── tests/                # Service-specific tests
├── Dockerfile           # Container configuration
└── package.json         # Dependencies
```

#### **Frontend Applications Structure**
Each frontend app follows this pattern:
```
app-name/
├── src/
│   ├── components/       # React components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API service functions
│   ├── utils/           # Utility functions
│   ├── types/           # TypeScript type definitions
│   └── App.tsx          # Main application
├── public/              # Static assets
├── webpack.config.js    # Build configuration
└── package.json         # Dependencies
```

---

## 🔧 Technology Stack Details

### Backend Technologies

#### **Node.js Services (TypeScript + Express.js)**
- **Gateway Service**: Request routing, rate limiting, metrics collection
- **Auth Service**: OAuth2 integration, JWT token management, session handling
- **Chat Service**: WebSocket communication, message persistence, real-time features
- **Admin Service**: Administrative functions, user management, data export

**Key Libraries:**
- **Framework**: Express.js 4.18+ with TypeScript
- **Authentication**: Passport.js, jsonwebtoken, bcryptjs
- **Database**: pg (PostgreSQL driver)
- **Real-time**: Socket.io for WebSocket communication
- **Security**: helmet, cors, csurf for security middleware
- **Validation**: Joi for request validation

#### **Python Services (FastAPI + AI/ML)**
- **AI Service**: NLP processing, intent recognition, sentiment analysis
- **Data Service**: Analytics, reporting, A/B testing framework
- **Personalization**: User behavior analysis, recommendation engine

**Key Libraries:**
- **Framework**: FastAPI 0.104+ with async/await
- **AI/ML**: scikit-learn, transformers, torch, spacy
- **Data Processing**: pandas, numpy, matplotlib, seaborn
- **Database**: SQLAlchemy with async support
- **HTTP**: httpx for service-to-service communication
- **Monitoring**: prometheus-client for metrics

### Frontend Technologies

#### **React Applications (TypeScript + Webpack)**
- **Module Federation**: Independent deployment of microfrontends
- **State Management**: React hooks, Context API
- **Styling**: Tailwind CSS + shared UI components
- **Real-time**: Socket.io-client for WebSocket communication

**Key Libraries:**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Webpack 5 with Module Federation
- **Routing**: React Router v6
- **Styling**: Tailwind CSS, shared component library
- **State**: React hooks, Context API
- **HTTP**: Axios for API communication
- **Real-time**: Socket.io-client

### Infrastructure Technologies

#### **Database & Caching**
- **PostgreSQL 13+**: Primary database with UUID primary keys
  - Extensions: uuid-ossp, jsonb for flexible data storage
  - Full-text search capabilities
  - Optimized indexes for performance

- **Redis 6.0+**: Caching and session storage
  - Session management for Express.js
  - WebSocket connection scaling with pub/sub
  - Response caching for AI services

#### **Containerization & Orchestration**
- **Docker**: Service containerization with multi-stage builds
- **Kubernetes**: Container orchestration with auto-scaling
- **Helm Charts**: Kubernetes package management
- **Nginx Ingress**: Load balancing and SSL termination

#### **Monitoring & Observability**
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and management
- **ServiceMonitor**: Kubernetes-native service discovery

---

## 📖 Documentation References

### Primary Documentation
1. **[📋 COMPREHENSIVE_TECHNICAL_INDEX.md](./COMPREHENSIVE_TECHNICAL_INDEX.md)**
   - Complete system architecture and design patterns
   - Detailed service documentation
   - Database schema and relationships
   - Performance and scalability details
   - Security implementation

2. **[🚀 DEVELOPMENT_SETUP_GUIDE.md](./DEVELOPMENT_SETUP_GUIDE.md)**
   - Step-by-step development environment setup
   - Prerequisites and tool installation
   - Configuration and environment setup
   - Common troubleshooting scenarios
   - Development workflow guidelines

3. **[🔌 API_SPECIFICATIONS.md](./API_SPECIFICATIONS.md)**
   - Complete REST API documentation
   - WebSocket event specifications
   - Request/response formats
   - Authentication flows
   - Rate limiting and error handling

### Quick Reference Guides

#### **Service Quick Links**
- **[Gateway Service](./backend/gateway/)** - API routing and middleware
- **[Auth Service](./backend/auth/)** - OAuth2 and JWT authentication
- **[Chat Service](./backend/chat/)** - Real-time messaging
- **[AI Service](./backend/ai/)** - NLP and ML processing
- **[Data Service](./backend/data/)** - Analytics and reporting

#### **Frontend Applications**
- **[Shell App](./frontend/shell/)** - Main application orchestrator
- **[Chat App](./frontend/chat/)** - Chat interface
- **[Auth App](./frontend/auth/)** - Authentication flows
- **[Admin App](./frontend/admin/)** - Administrative dashboard
- **[Shared UI](./shared-ui/)** - Reusable components

#### **Infrastructure**
- **[Database Schema](./infrastructure/database/)** - PostgreSQL setup
- **[Kubernetes Configs](./infrastructure/k8s/)** - Deployment configs
- **[Monitoring Setup](./infrastructure/monitoring/)** - Observability stack

### API Endpoints Quick Reference

#### **Core API Routes**
All API requests go through the Gateway Service at `http://localhost:8080`:

```http
# Authentication
POST /api/auth/login           # User login
POST /api/auth/logout          # User logout
GET  /api/auth/profile         # Get user profile
POST /api/auth/register        # User registration

# Chat Operations
GET  /api/chat/conversations   # List conversations
POST /api/chat/conversations   # Create conversation
GET  /api/chat/conversations/:id/messages  # Get messages
POST /api/chat/conversations/:id/messages  # Send message

# AI Processing
POST /api/ai/process-message   # Full AI pipeline processing
POST /api/ai/intent           # Intent recognition
POST /api/ai/sentiment        # Sentiment analysis
POST /api/ai/generate-response # Response generation

# Administration
GET  /api/admin/users         # List users (admin only)
GET  /api/admin/conversations # List all conversations
POST /api/admin/export        # Export data
GET  /api/admin/analytics     # System analytics

# Analytics & Personalization
GET  /api/data/analytics      # Analytics data
POST /api/data/ab-test        # A/B testing
GET  /api/personalization/user-profile/:id  # User profile
POST /api/personalization/recommendations   # Get recommendations
```

#### **WebSocket Events**
Real-time communication on `ws://localhost:3002`:

```javascript
// Client to Server
socket.emit('join_conversation', { conversation_id: 'uuid' });
socket.emit('leave_conversation', { conversation_id: 'uuid' });
socket.emit('typing_start', { conversation_id: 'uuid' });
socket.emit('typing_stop', { conversation_id: 'uuid' });
socket.emit('message_send', { 
  conversation_id: 'uuid', 
  content: 'Hello!',
  message_type: 'text'
});

// Server to Client
socket.on('message_received', (data) => { /* handle message */ });
socket.on('typing_start', (data) => { /* show typing indicator */ });
socket.on('conversation_updated', (data) => { /* update UI */ });
```

#### **Authentication Flow**
1. **Login**: `POST /api/auth/login` returns JWT token
2. **API Calls**: Include `Authorization: Bearer <token>` header
3. **WebSocket**: Include token in connection auth
4. **Refresh**: Use refresh token to get new access tokens

---

## 🛠️ Setup Instructions

### Prerequisites Installation

#### **Node.js Setup**
```bash
# Install Node.js 18+ from nodejs.org or use nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

#### **Python Setup**
```bash
# Install Python 3.9+ from python.org or use pyenv
brew install python@3.9  # macOS
# or
conda create -n chatbot python=3.9  # Anaconda
conda activate chatbot
```

#### **Docker Setup**
```bash
# Install Docker Desktop from docker.com
docker --version
docker-compose --version

# Start Docker service
# (Docker Desktop on macOS/Windows or systemctl on Linux)
```

### Development Environment Setup

#### **1. Environment Configuration**

Create and configure environment files:

```bash
# Backend .env files
cp backend/.env.example backend/gateway/.env
cp backend/.env.example backend/auth/.env
cp backend/.env.example backend/chat/.env
cp backend/.env.example backend/admin/.env

# Edit each .env file with your settings:
# - Database connection strings
# - Redis connection
# - JWT secrets (generate secure random strings)
# - OAuth provider credentials (Google, GitHub, Microsoft)
```

**Example gateway .env:**
```bash
NODE_ENV=development
PORT=8080
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-super-secure-jwt-secret-key
FRONTEND_URL=http://localhost:3000
```

#### **2. Database Initialization**

```bash
# Start infrastructure services
docker-compose -f docker-compose.dev.yml up -d

# Navigate to database setup
cd infrastructure/database

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python migrate.py up

# Load initial schema
psql -h localhost -U postgres -d chatbot -f init.sql

# Verify tables were created
psql -h localhost -U postgres -d chatbot -c "\dt"
```

Expected output should show tables: `users`, `conversations`, `messages`, plus extended schema tables.

#### **3. Dependency Installation**

```bash
# Backend Node.js services
cd backend/gateway && npm install
cd ../auth && npm install
cd ../chat && npm install
cd ../admin && npm install

# Backend Python services
cd ../ai && pip install -r requirements.txt
cd ../data && pip install -r requirements.txt
cd ../personalization && pip install -r requirements.txt
cd ../testing && pip install -r requirements.txt

# Frontend applications
cd ../../frontend/shell && npm install
cd ../chat && npm install
cd ../auth && npm install
cd ../admin && npm install
cd ../profile && npm install

# Shared UI components
cd ../../shared-ui && npm install
```

### Common Development Scenarios

#### **Starting Development (Daily Workflow)**
```bash
# 1. Start infrastructure
docker-compose -f docker-compose.dev.yml up -d

# 2. Verify services are running
docker-compose -f docker-compose.dev.yml ps

# 3. Start backend services in separate terminals
# (Start with gateway first, then others)
cd backend/gateway && npm run dev

# 4. Start frontend applications
cd frontend/shell && npm start

# 5. Run tests to verify everything works
cd backend/testing && pytest

# 6. Check all health endpoints
curl http://localhost:8080/health  # Gateway
curl http://localhost:3001/health  # Auth
curl http://localhost:3002/health  # Chat
```

#### **Running Tests**
```bash
# Backend tests (Python/pytest)
cd backend/testing
pytest                           # All tests
pytest --cov=src --cov-report=html  # With coverage report
pytest -m ai                     # AI service tests only
pytest -m api                    # API tests only

# Frontend tests (Jest)
cd frontend/chat && npm test     # Chat app tests
cd frontend/auth && npm test     # Auth app tests

# Load testing
locust -f tests/performance/test_load.py --host=http://localhost:8080
```

#### **Database Operations**
```bash
# Connect to development database
psql -h localhost -U postgres -d chatbot

# Run specific migration
cd infrastructure/database
python migrate.py up --target 002

# Reset database (development only)
psql -h localhost -U postgres -d chatbot -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
python migrate.py up

# Backup database
pg_dump -h localhost -U postgres chatbot > backup.sql

# Restore database
psql -h localhost -U postgres -d chatbot < backup.sql
```

#### **Working with Redis**
```bash
# Connect to Redis CLI
redis-cli -h localhost -p 6379

# Common Redis commands
127.0.0.1:6379> ping                    # Test connection
127.0.0.1:6379> keys *                  # List all keys
127.0.0.1:6379> get session:user123     # Get specific key
127.0.0.1:6379> del session:user123     # Delete key
127.0.0.1:6379> flushdb                 # Clear all keys (development only)
```

### Troubleshooting Basics

#### **Port Conflicts**
```bash
# Find process using a specific port
lsof -i :8080
lsof -i :3001
lsof -i :3002

# Kill process if needed
kill -9 <PID>
```

#### **Database Connection Issues**
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.dev.yml logs postgres

# Test database connection
psql -h localhost -U postgres -d chatbot -c "SELECT version();"

# Restart PostgreSQL
docker-compose -f docker-compose.dev.yml restart postgres
```

#### **Redis Connection Issues**
```bash
# Check Redis logs
docker-compose -f docker-compose.dev.yml logs redis

# Test Redis connection
redis-cli -h localhost -p 6379 ping

# Restart Redis
docker-compose -f docker-compose.dev.yml restart redis
```

#### **Node.js Dependency Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install

# Use specific Node.js version
nvm use 18
```

#### **Python Dependency Issues**
```bash
# Create fresh virtual environment
python -m venv fresh_venv
source fresh_venv/bin/activate  # On Windows: fresh_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# If using conda environment
conda create -n chatbot_fresh python=3.9
conda activate chatbot_fresh
pip install -r requirements.txt
```

#### **Docker Issues**
```bash
# Restart all services
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

# View service logs
docker-compose -f docker-compose.dev.yml logs

# View specific service logs
docker-compose -f docker-compose.dev.yml logs gateway

# Clean up unused Docker resources
docker system prune -f
```

#### **Performance Issues**
```bash
# Check system resources
top -o %CPU  # CPU usage
top -o %MEM  # Memory usage
df -h        # Disk space

# Check Docker container resources
docker stats

# Monitor service health
curl http://localhost:8080/metrics  # If metrics endpoint is available
```

---

## 💻 Development Guidelines

### Code Organization Principles

#### **Backend Service Architecture**
Each backend service should follow clean architecture principles:

```
service-name/
├── src/
│   ├── routes/          # HTTP request handlers (controllers)
│   ├── services/        # Business logic and algorithms
│   ├── models/          # Data models and database schemas
│   ├── middleware/      # Custom middleware functions
│   ├── utils/           # Utility functions and helpers
│   ├── config/          # Configuration management
│   └── server.ts        # Service entry point and app setup
├── tests/               # Test files
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── fixtures/       # Test data and mocks
├── Dockerfile          # Container configuration
├── package.json        # Node.js dependencies
└── tsconfig.json       # TypeScript configuration
```

#### **Frontend Application Architecture**
Each frontend application should follow component-based architecture:

```
app-name/
├── src/
│   ├── components/     # Reusable React components
│   ├── pages/         # Page-level components
│   ├── hooks/         # Custom React hooks
│   ├── services/      # API service functions
│   ├── utils/         # Utility functions
│   ├── types/         # TypeScript type definitions
│   ├── assets/        # Static assets (images, fonts)
│   └── App.tsx        # Main application component
├── public/            # Static public assets
├── webpack.config.js  # Build configuration
└── package.json       # Dependencies
```

### TypeScript Guidelines

#### **Type Definitions**
```typescript
// Use interfaces for object shapes
interface User {
  readonly id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  preferences: UserPreferences;
  createdAt: Date;
  updatedAt: Date;
}

// Use type aliases for unions and primitives
type MessageType = 'text' | 'image' | 'file';
type ConversationStatus = 'active' | 'closed' | 'archived';

// Use enums for constants
enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin'
}

// Generic interfaces for reusability
interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta: {
    timestamp: string;
    request_id: string;
    pagination?: PaginationInfo;
  };
}
```

#### **Async/Await Patterns**
```typescript
// Good: Use async/await with proper error handling
async function getUser(id: string): Promise<User | null> {
  try {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  } catch (error) {
    if (error.status === 404) {
      return null;
    }
    throw new Error(`Failed to fetch user: ${error.message}`);
  }
}

// Good: Use proper typing for fetch responses
interface LoginResponse {
  user: User;
  token: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
  };
}

async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/auth/login', credentials);
  return response.data;
}
```

#### **Error Handling Patterns**
```typescript
// Custom error classes
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public code: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

// API error interface
interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Error handling wrapper
async function withErrorHandling<T>(
  operation: () => Promise<T>,
  fallback?: T
): Promise<T> {
  try {
    return await operation();
  } catch (error) {
    if (fallback !== undefined) {
      return fallback;
    }
    throw error;
  }
}
```

### Python Guidelines

#### **Type Hints and Pydantic Models**
```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

# Use Pydantic models for request/response validation
class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    name: str
    preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

# Use proper typing for async functions
async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    try:
        async with get_db_session() as session:
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise
```

#### **Async/Await Patterns**
```python
import asyncio
from typing import AsyncGenerator

# Async context managers
async def process_messages(messages: List[Message]) -> List[ProcessedMessage]:
    async with aiohttp.ClientSession() as session:
        tasks = [process_single_message(session, msg) for msg in messages]
        return await asyncio.gather(*tasks)

# Async generators for streaming data
async def message_stream(user_id: str) -> AsyncGenerator[Message, None]:
    """Stream messages for a user in real-time."""
    while True:
        messages = await get_new_messages(user_id)
        for message in messages:
            yield message
        await asyncio.sleep(1)  # Poll every second

# Use async for I/O operations
async def call_external_service(data: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/process",
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
```

### Testing Approaches

#### **Unit Testing**
```typescript
// Jest test example for Node.js service
import { AuthService } from '../src/services/AuthService';

describe('AuthService', () => {
  let authService: AuthService;
  let mockDb: jest.Mocked<Database>;
  
  beforeEach(() => {
    mockDb = createMockDatabase();
    authService = new AuthService(mockDb);
  });
  
  it('should validate correct credentials', async () => {
    const user = { id: 'user-123', email: 'user@example.com', password_hash: 'hashed_password' };
    mockDb.users.findByEmail.mockResolvedValue(user);
    mockDb.users.validatePassword.mockResolvedValue(true);
    
    const result = await authService.validateUser('user@example.com', 'password123');
    
    expect(result).toBeDefined();
    expect(result?.email).toBe('user@example.com');
    expect(mockDb.users.findByEmail).toHaveBeenCalledWith('user@example.com');
  });
  
  it('should reject invalid credentials', async () => {
    mockDb.users.findByEmail.mockResolvedValue(null);
    
    const result = await authService.validateUser('user@example.com', 'wrongpassword');
    
    expect(result).toBeNull();
  });
});
```

#### **Integration Testing**
```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app."""
    return TestClient(app)

@pytest.mark.asyncio
async def test_ai_processing_endpoint(client: TestClient):
    """Test AI processing endpoint with real request/response."""
    response = client.post("/process", json={
        "message": "Hello world",
        "user_id": "test-user",
        "conversation_id": "test-conversation"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
    assert 0 <= data["confidence"] <= 1

@pytest.mark.integration
async def test_database_integration(client: TestClient):
    """Test database integration (requires test database)."""
    # This test requires a test database to be set up
    # Use test containers or in-memory database for CI/CD
    pass
```

#### **API Testing**
```python
# Use httpx for async API testing
import httpx
import pytest

@pytest.mark.asyncio
async def test_full_chat_flow():
    """Test complete chat flow including WebSocket communication."""
    async with httpx.AsyncClient() as client:
        # 1. Authenticate
        login_response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        token = login_response.json()["token"]["access_token"]
        
        # 2. Create conversation
        headers = {"Authorization": f"Bearer {token}"}
        conv_response = await client.post("/api/chat/conversations", 
            json={"title": "Test Chat"},
            headers=headers
        )
        conversation_id = conv_response.json()["data"]["id"]
        
        # 3. Send message
        message_response = await client.post(
            f"/api/chat/conversations/{conversation_id}/messages",
            json={"content": "Hello, AI!"},
            headers=headers
        )
        
        assert message_response.status_code == 201
        message_data = message_response.json()
        assert message_data["data"]["content"] == "Hello, AI!"
```

### Contributing Guidelines

#### **Git Workflow**
```bash
# Feature development workflow
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Make your changes
git add .
git commit -m "feat(service): add new feature description"

# Push and create pull request
git push origin feature/your-feature-name
```

#### **Commit Message Convention**
```
type(scope): description

[optional body]

[optional footer]

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting, etc.)
- refactor: Code refactoring
- test: Adding or updating tests
- chore: Build process or auxiliary tool changes
```

Examples:
```
feat(auth): add OAuth2 integration with Google and GitHub

- Implement Google OAuth2 flow
- Add GitHub OAuth2 provider
- Update JWT token generation
- Add session management

Closes #123
```

```
fix(chat): resolve WebSocket connection timeout issue

- Increase WebSocket ping interval
- Add connection retry logic
- Update error handling for network issues

Fixes #456
```

#### **Code Review Process**
1. **Self Review**: Run tests and check code quality before submitting
2. **PR Description**: Provide clear description of changes
3. **Testing**: Include tests for new functionality
4. **Documentation**: Update relevant documentation
5. **Review**: Address reviewer feedback promptly

#### **Pull Request Template**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

---

## 🚀 Getting Started Checklist

Use this checklist to ensure you have everything set up correctly:

### ✅ Prerequisites
- [ ] Node.js 18+ installed and working
- [ ] Python 3.9+ installed and working  
- [ ] Docker and Docker Compose installed
- [ ] Git installed and configured
- [ ] VS Code or preferred IDE installed

### ✅ Environment Setup
- [ ] Repository cloned and navigated to
- [ ] Environment files created and configured
- [ ] Database and Redis running via Docker
- [ ] Database migrations applied successfully

### ✅ Dependencies Installation
- [ ] All Node.js dependencies installed (gateway, auth, chat, admin)
- [ ] All Python dependencies installed (ai, data, personalization, testing)
- [ ] All frontend dependencies installed (shell, chat, auth, admin, profile)
- [ ] Shared UI components installed

### ✅ Development Environment
- [ ] All 8 services starting successfully without errors
- [ ] Health check endpoints returning success
- [ ] Database connection working (can query tables)
- [ ] Redis connection working (can ping Redis)
- [ ] Frontend applications accessible in browser

### ✅ Testing & Verification
- [ ] Backend tests passing (`pytest`)
- [ ] Frontend tests passing (`npm test`)
- [ ] Can create a test user account
- [ ] Can start a conversation
- [ ] Can send and receive messages
- [ ] WebSocket connection working

### ✅ Documentation Access
- [ ] Can access and understand [COMPREHENSIVE_TECHNICAL_INDEX.md](./COMPREHENSIVE_TECHNICAL_INDEX.md)
- [ ] Can follow [DEVELOPMENT_SETUP_GUIDE.md](./DEVELOPMENT_SETUP_GUIDE.md) instructions
- [ ] Can reference [API_SPECIFICATIONS.md](./API_SPECIFICATIONS.md) for endpoints

---

## 🎯 Next Steps for Junior Developers

### 1. **Explore the Codebase**
Start with these key files:
- `backend/gateway/src/server.ts` - Understanding API routing
- `backend/chat/src/socket/socketHandler.ts` - WebSocket implementation
- `frontend/chat/src/components/ChatInterface.tsx` - Main chat UI
- `backend/ai/src/services/nlp_processor.py` - AI processing logic

### 2. **Run and Test Everything**
- Ensure all services start without errors
- Run the complete test suite
- Try creating a conversation and sending messages
- Test WebSocket functionality

### 3. **Make Your First Contribution**
Look for:
- `TODO` comments in the code
- Failing tests that need fixing
- Documentation that can be improved
- Small features or bug fixes

### 4. **Understand the Architecture**
Study the Mermaid diagrams in the technical documentation:
- System architecture overview
- Data flow patterns
- Service communication diagrams
- Database relationships

### 5. **Join the Development Team**
- Ask questions in team channels
- Attend code reviews
- Participate in architecture discussions
- Contribute to documentation improvements

---

## 📞 Getting Help

### Documentation
- **[📋 Technical Index](./COMPREHENSIVE_TECHNICAL_INDEX.md)** - Complete system documentation
- **[🚀 Setup Guide](./DEVELOPMENT_SETUP_GUIDE.md)** - Step-by-step development setup  
- **[🔌 API Specs](./API_SPECIFICATIONS.md)** - Complete API documentation

### Community
- **Team Channels**: Ask questions in development team Slack/Discord
- **Issues**: Check existing GitHub issues for similar problems
- **Code Reviews**: Learn from pull request reviews and discussions

### Debugging Resources
- **Service Logs**: Check terminal outputs for service-specific errors
- **Browser DevTools**: Use Network and Console tabs for frontend issues
- **Database Tools**: Use pgAdmin for PostgreSQL GUI
- **Redis CLI**: Monitor Redis data and connections

### Performance Monitoring
- **Health Endpoints**: `curl http://localhost:8080/health` for all services
- **Application Logs**: Monitor service outputs for errors
- **Database Performance**: Use PostgreSQL logs and slow query analysis
- **Memory Usage**: Monitor with `top` or Docker stats

---

**Welcome to the Chatbot Application development team! 🎉**

*This README serves as your primary entry point. For detailed technical information, refer to the comprehensive technical documentation included with this project.*