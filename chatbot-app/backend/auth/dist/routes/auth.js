"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.authRoutes = void 0;
const express_1 = __importDefault(require("express"));
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const User_1 = require("../models/User");
const validation_1 = require("../middleware/validation");
const auth_1 = require("../middleware/auth");
const auth_2 = require("../schemas/auth");
const router = express_1.default.Router();
exports.authRoutes = router;
// Register
router.post('/register', (0, validation_1.validateRequest)(auth_2.authSchema), async (req, res) => {
    try {
        const { email, password, name, role = 'user' } = req.body;
        // Check if user already exists
        const existingUser = await User_1.User.findByEmail(email);
        if (existingUser) {
            return res.status(400).json({ error: 'User already exists' });
        }
        // Hash password
        const saltRounds = 12;
        const passwordHash = await bcryptjs_1.default.hash(password, saltRounds);
        // Create user
        const user = await User_1.User.create({
            email,
            passwordHash,
            name,
            role
        });
        // Generate JWT token
        const token = jsonwebtoken_1.default.sign({ userId: user.id, email: user.email, role: user.role }, process.env.JWT_SECRET || 'fallback-secret', { expiresIn: '24h' });
        res.status(201).json({
            message: 'User created successfully',
            token,
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                role: user.role
            }
        });
    }
    catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// Login
router.post('/login', (0, validation_1.validateRequest)(auth_2.loginSchema), async (req, res) => {
    try {
        const { email, password } = req.body;
        // Find user
        const user = await User_1.User.findByEmail(email);
        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        // Check if user has OAuth-only account (no password)
        if (!user.passwordHash) {
            return res.status(401).json({ error: 'This account uses OAuth login. Please use Google, GitHub, or Microsoft to sign in.' });
        }
        // Check password
        const isValidPassword = await bcryptjs_1.default.compare(password, user.passwordHash);
        if (!isValidPassword) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        // Update last login
        await User_1.User.updateLastLogin(user.id);
        // Generate JWT token
        const token = jsonwebtoken_1.default.sign({ userId: user.id, email: user.email, role: user.role }, process.env.JWT_SECRET || 'fallback-secret', { expiresIn: '24h' });
        res.json({
            message: 'Login successful',
            token,
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                role: user.role
            }
        });
    }
    catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// Refresh token
router.post('/refresh', async (req, res) => {
    try {
        const { token } = req.body;
        if (!token) {
            return res.status(401).json({ error: 'Token required' });
        }
        const decoded = jsonwebtoken_1.default.verify(token, process.env.JWT_SECRET || 'fallback-secret');
        const user = await User_1.User.findById(decoded.userId);
        if (!user) {
            return res.status(401).json({ error: 'Invalid token' });
        }
        const newToken = jsonwebtoken_1.default.sign({ userId: user.id, email: user.email, role: user.role }, process.env.JWT_SECRET || 'fallback-secret', { expiresIn: '24h' });
        res.json({ token: newToken });
    }
    catch (error) {
        res.status(401).json({ error: 'Invalid token' });
    }
});
// Get user profile (requires authentication)
router.get('/profile', auth_1.authenticateToken, async (req, res) => {
    try {
        const user = req.user;
        if (!user) {
            return res.status(401).json({ error: 'Authentication required' });
        }
        res.json({
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                role: user.role,
                oauthProvider: user.oauthProvider,
                picture: user.picture,
                emailVerified: user.emailVerified,
                createdAt: user.createdAt,
                lastLogin: user.lastLogin
            }
        });
    }
    catch (error) {
        console.error('Profile fetch error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// Get CSRF token
router.get('/csrf-token', (req, res) => {
    res.json({ csrfToken: req.csrfToken() });
});
// Update user profile
router.put('/profile', auth_1.authenticateToken, async (req, res) => {
    try {
        const user = req.user;
        if (!user) {
            return res.status(401).json({ error: 'Authentication required' });
        }
        const { name, preferences } = req.body;
        // Update user data
        if (name) {
            // Note: In a real implementation, you'd update the user in the database
            // For now, we'll just return success
        }
        if (preferences) {
            await User_1.User.updatePreferences(user.id, preferences);
        }
        res.json({ message: 'Profile updated successfully' });
    }
    catch (error) {
        console.error('Profile update error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});
//# sourceMappingURL=auth.js.map