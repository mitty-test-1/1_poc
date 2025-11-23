import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import session from 'express-session';
import passport from 'passport';
import csrf from 'csurf';
import dotenv from 'dotenv';
import { authRoutes } from './routes/auth';
import { oauthRoutes } from './routes/oauth';
import { errorHandler } from './middleware/errorHandler';
import './config/oauth'; // Initialize OAuth strategies

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session middleware for OAuth
app.use(session({
  secret: process.env.SESSION_SECRET || 'oauth-session-secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));

// Passport middleware
app.use(passport.initialize());
app.use(passport.session());

// CSRF protection
const csrfProtection = csrf({
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'strict'
  }
});

// Apply CSRF protection to state-changing routes
app.use('/api/auth', csrfProtection);

// Add CSRF token to requests
app.use('/api/auth', (req, res, next) => {
  res.locals.csrfToken = (req as any).csrfToken();
  next();
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/auth/oauth', oauthRoutes);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK', service: 'auth' });
});

// Error handling
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`Authentication Service running on port ${PORT}`);
});