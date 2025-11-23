"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const morgan_1 = __importDefault(require("morgan"));
const express_session_1 = __importDefault(require("express-session"));
const passport_1 = __importDefault(require("passport"));
const csurf_1 = __importDefault(require("csurf"));
const dotenv_1 = __importDefault(require("dotenv"));
const auth_1 = require("./routes/auth");
const oauth_1 = require("./routes/oauth");
const errorHandler_1 = require("./middleware/errorHandler");
require("./config/oauth"); // Initialize OAuth strategies
dotenv_1.default.config();
const app = (0, express_1.default)();
const PORT = process.env.PORT || 3001;
// Middleware
app.use((0, helmet_1.default)());
app.use((0, cors_1.default)({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true
}));
app.use((0, morgan_1.default)('combined'));
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
// Session middleware for OAuth
app.use((0, express_session_1.default)({
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
app.use(passport_1.default.initialize());
app.use(passport_1.default.session());
// CSRF protection
const csrfProtection = (0, csurf_1.default)({
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
    res.locals.csrfToken = req.csrfToken();
    next();
});
// Routes
app.use('/api/auth', auth_1.authRoutes);
app.use('/api/auth/oauth', oauth_1.oauthRoutes);
// Health check
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'OK', service: 'auth' });
});
// Error handling
app.use(errorHandler_1.errorHandler);
app.listen(PORT, () => {
    console.log(`Authentication Service running on port ${PORT}`);
});
//# sourceMappingURL=server.js.map