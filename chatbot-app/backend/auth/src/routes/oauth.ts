import express from 'express';
import passport from 'passport';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import rateLimit from 'express-rate-limit';
import { User } from '../models/User';

const router = express.Router();

// Rate limiting for OAuth endpoints
const oauthLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // limit each IP to 10 requests per windowMs
  message: 'Too many OAuth requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Store for PKCE challenges (in production, use Redis)
const pkceStore: { [key: string]: { challenge: string; verifier: string; expires: number } } = {};

// Generate PKCE challenge
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto.createHash('sha256').update(verifier).digest('base64url');
  const key = crypto.randomBytes(16).toString('hex');

  pkceStore[key] = {
    challenge,
    verifier,
    expires: Date.now() + 10 * 60 * 1000 // 10 minutes
  };

  // Clean up expired challenges
  Object.keys(pkceStore).forEach(k => {
    if (pkceStore[k].expires < Date.now()) {
      delete pkceStore[k];
    }
  });

  return { key, challenge };
}

// Verify PKCE challenge
function verifyPKCE(key: string, challenge: string): string | null {
  const stored = pkceStore[key];
  if (!stored || stored.expires < Date.now() || stored.challenge !== challenge) {
    return null;
  }
  const verifier = stored.verifier;
  delete pkceStore[key]; // One-time use
  return verifier;
}

// Google OAuth routes
router.get('/google', oauthLimiter, (req, res, next) => {
  const { key, challenge } = generatePKCE();
  const state = JSON.stringify({ provider: 'google', pkceKey: key });

  passport.authenticate('google', {
    scope: ['profile', 'email'],
    state,
    session: false
  })(req, res, next);
});

router.get('/google/callback', oauthLimiter,
  passport.authenticate('google', { session: false, failureRedirect: '/login?error=oauth_failed' }),
  async (req, res) => {
    try {
      const user = req.user as any;
      const token = jwt.sign(
        { userId: user.id, email: user.email, role: user.role },
        process.env.JWT_SECRET || 'fallback-secret',
        { expiresIn: '24h' }
      );

      // Redirect to frontend with token
      const redirectUrl = new URL(process.env.FRONTEND_URL || 'http://localhost:3000');
      redirectUrl.pathname = '/auth/callback';
      redirectUrl.searchParams.set('token', token);
      redirectUrl.searchParams.set('provider', 'google');

      res.redirect(redirectUrl.toString());
    } catch (error) {
      console.error('Google OAuth callback error:', error);
      res.redirect('/login?error=oauth_callback_failed');
    }
  }
);

// GitHub OAuth routes
router.get('/github', oauthLimiter, (req, res, next) => {
  const { key, challenge } = generatePKCE();
  const state = JSON.stringify({ provider: 'github', pkceKey: key });

  passport.authenticate('github', {
    scope: ['user:email'],
    state,
    session: false
  })(req, res, next);
});

router.get('/github/callback', oauthLimiter,
  passport.authenticate('github', { session: false, failureRedirect: '/login?error=oauth_failed' }),
  async (req, res) => {
    try {
      const user = req.user as any;
      const token = jwt.sign(
        { userId: user.id, email: user.email, role: user.role },
        process.env.JWT_SECRET || 'fallback-secret',
        { expiresIn: '24h' }
      );

      // Redirect to frontend with token
      const redirectUrl = new URL(process.env.FRONTEND_URL || 'http://localhost:3000');
      redirectUrl.pathname = '/auth/callback';
      redirectUrl.searchParams.set('token', token);
      redirectUrl.searchParams.set('provider', 'github');

      res.redirect(redirectUrl.toString());
    } catch (error) {
      console.error('GitHub OAuth callback error:', error);
      res.redirect('/login?error=oauth_callback_failed');
    }
  }
);

// Microsoft OAuth routes
router.get('/microsoft', oauthLimiter, (req, res, next) => {
  const { key, challenge } = generatePKCE();
  const state = JSON.stringify({ provider: 'microsoft', pkceKey: key });

  passport.authenticate('microsoft', {
    scope: ['openid', 'profile', 'email'],
    state,
    session: false
  })(req, res, next);
});

router.get('/microsoft/callback', oauthLimiter,
  passport.authenticate('microsoft', { session: false, failureRedirect: '/login?error=oauth_failed' }),
  async (req, res) => {
    try {
      const user = req.user as any;
      const token = jwt.sign(
        { userId: user.id, email: user.email, role: user.role },
        process.env.JWT_SECRET || 'fallback-secret',
        { expiresIn: '24h' }
      );

      // Redirect to frontend with token
      const redirectUrl = new URL(process.env.FRONTEND_URL || 'http://localhost:3000');
      redirectUrl.pathname = '/auth/callback';
      redirectUrl.searchParams.set('token', token);
      redirectUrl.searchParams.set('provider', 'microsoft');

      res.redirect(redirectUrl.toString());
    } catch (error) {
      console.error('Microsoft OAuth callback error:', error);
      res.redirect('/login?error=oauth_callback_failed');
    }
  }
);

// Account linking endpoint
router.post('/link/:provider', oauthLimiter, async (req, res) => {
  try {
    const { provider } = req.params;
    const { userId, oauthId, accessToken } = req.body;

    if (!['google', 'github', 'microsoft'].includes(provider)) {
      return res.status(400).json({ error: 'Invalid OAuth provider' });
    }

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Check if OAuth account is already linked to another user
    const existingUser = await User.findByOAuthId(provider, oauthId);
    if (existingUser && existingUser.id !== userId) {
      return res.status(409).json({ error: 'OAuth account already linked to another user' });
    }

    // Link the account
    await User.linkOAuthAccount(userId, provider, oauthId);

    res.json({ message: 'OAuth account linked successfully' });
  } catch (error) {
    console.error('Account linking error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Unlink OAuth account
router.post('/unlink/:provider', oauthLimiter, async (req, res) => {
  try {
    const { provider } = req.params;
    const { userId } = req.body;

    if (!['google', 'github', 'microsoft'].includes(provider)) {
      return res.status(400).json({ error: 'Invalid OAuth provider' });
    }

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Remove OAuth linking
    await User.updateOAuthInfo(userId, null as any, null as any);

    res.json({ message: 'OAuth account unlinked successfully' });
  } catch (error) {
    console.error('Account unlinking error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export { router as oauthRoutes };