"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.canAccessUser = exports.requireAdmin = exports.requireRole = exports.optionalAuth = exports.authenticateToken = void 0;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const User_1 = require("../models/User");
// JWT authentication middleware
const authenticateToken = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
        if (!token) {
            return res.status(401).json({ error: 'Access token required' });
        }
        const decoded = jsonwebtoken_1.default.verify(token, process.env.JWT_SECRET || 'fallback-secret');
        const user = await User_1.User.findById(decoded.userId);
        if (!user) {
            return res.status(401).json({ error: 'Invalid token' });
        }
        req.user = user;
        next();
    }
    catch (error) {
        if (error instanceof jsonwebtoken_1.default.JsonWebTokenError) {
            return res.status(401).json({ error: 'Invalid token' });
        }
        if (error instanceof jsonwebtoken_1.default.TokenExpiredError) {
            return res.status(401).json({ error: 'Token expired' });
        }
        console.error('Authentication error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
};
exports.authenticateToken = authenticateToken;
// Optional authentication middleware (doesn't fail if no token)
const optionalAuth = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        const token = authHeader && authHeader.split(' ')[1];
        if (token) {
            try {
                const decoded = jsonwebtoken_1.default.verify(token, process.env.JWT_SECRET || 'fallback-secret');
                const user = await User_1.User.findById(decoded.userId);
                if (user) {
                    req.user = user;
                }
            }
            catch (error) {
                // Ignore token errors for optional auth
            }
        }
        next();
    }
    catch (error) {
        // Continue without authentication
        next();
    }
};
exports.optionalAuth = optionalAuth;
// Role-based authorization middleware
const requireRole = (roles) => {
    return (req, res, next) => {
        if (!req.user) {
            return res.status(401).json({ error: 'Authentication required' });
        }
        if (!roles.includes(req.user.role)) {
            return res.status(403).json({ error: 'Insufficient permissions' });
        }
        next();
    };
};
exports.requireRole = requireRole;
// Admin-only middleware
exports.requireAdmin = (0, exports.requireRole)(['admin']);
// User profile access middleware (users can access their own data, admins can access all)
const canAccessUser = (req, res, next) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Authentication required' });
    }
    const requestedUserId = req.params.userId || req.params.id;
    const isAdmin = req.user.role === 'admin';
    const isOwner = req.user.id === requestedUserId;
    if (!isAdmin && !isOwner) {
        return res.status(403).json({ error: 'Access denied' });
    }
    next();
};
exports.canAccessUser = canAccessUser;
//# sourceMappingURL=auth.js.map