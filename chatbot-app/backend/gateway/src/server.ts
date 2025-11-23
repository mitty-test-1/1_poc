import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { authRoutes } from './routes/auth';
import { chatRoutes } from './routes/chat';
import { adminRoutes } from './routes/admin';
import { personalizationRoutes } from './routes/personalization';
import { dataRoutes } from './routes/data';
import { aiRoutes } from './routes/ai';
import { errorHandler } from './middleware/errorHandler';
import { rateLimiter } from './middleware/rateLimiter';
import { requestLogger } from './middleware/requestLogger';
import { healthCheckRoutes } from './routes/health';
import { metricsMiddleware, metricsEndpoint } from './middleware/metrics';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Custom middleware
app.use(requestLogger);
app.use(rateLimiter);
app.use(metricsMiddleware);

// Routes
app.use('/health', healthCheckRoutes);
app.use('/api/auth', authRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/personalization', personalizationRoutes);
app.use('/api/data', dataRoutes);
app.use('/api/ai', aiRoutes);

// Metrics endpoint
app.get('/metrics', metricsEndpoint);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Chatbot API Gateway',
    version: '1.0.0',
    services: {
      auth: 'http://localhost:3001',
      chat: 'http://localhost:3002',
      admin: 'http://localhost:3003',
      personalization: 'http://localhost:3005',
      data: 'http://localhost:3006',
      ai: 'http://localhost:3007'
    }
  });
});

// Error handling middleware
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    path: req.originalUrl,
    method: req.method
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 API Gateway running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`📈 Metrics endpoint: http://localhost:${PORT}/metrics`);
  console.log(`🔗 Services available:`);
  console.log(`   - Auth: http://localhost:${PORT}/api/auth`);
  console.log(`   - Chat: http://localhost:${PORT}/api/chat`);
  console.log(`   - Admin: http://localhost:${PORT}/api/admin`);
  console.log(`   - Personalization: http://localhost:${PORT}/api/personalization`);
  console.log(`   - Data: http://localhost:${PORT}/api/data`);
  console.log(`   - AI: http://localhost:${PORT}/api/ai`);
});

export default app;