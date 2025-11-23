"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const passport_1 = __importDefault(require("passport"));
const passport_google_oauth20_1 = require("passport-google-oauth20");
const passport_github2_1 = require("passport-github2");
const passport_microsoft_1 = require("passport-microsoft");
const User_1 = require("../models/User");
// Serialize user for session
passport_1.default.serializeUser((user, done) => {
    done(null, user.id);
});
// Deserialize user from session
passport_1.default.deserializeUser(async (id, done) => {
    try {
        const user = await User_1.User.findById(id);
        done(null, user);
    }
    catch (error) {
        done(error, null);
    }
});
// Google OAuth Strategy
passport_1.default.use(new passport_google_oauth20_1.Strategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: `${process.env.OAUTH_CALLBACK_BASE_URL}/google/callback`
}, async (accessToken, refreshToken, profile, done) => {
    try {
        const email = profile.emails?.[0]?.value;
        const name = profile.displayName;
        const picture = profile.photos?.[0]?.value;
        if (!email) {
            return done(new Error('No email provided by Google'), false);
        }
        // Check if user exists
        let user = await User_1.User.findByEmail(email);
        if (user) {
            // Update OAuth info if not already linked
            if (!user.oauthProvider) {
                await User_1.User.updateOAuthInfo(user.id, 'google', profile.id, picture ? { picture } : undefined);
            }
        }
        else {
            // Create new user
            user = await User_1.User.createOAuthUser({
                email,
                name,
                oauthProvider: 'google',
                oauthId: profile.id,
                picture
            });
        }
        return done(null, user);
    }
    catch (error) {
        return done(error, false);
    }
}));
// GitHub OAuth Strategy
passport_1.default.use(new passport_github2_1.Strategy({
    clientID: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    callbackURL: `${process.env.OAUTH_CALLBACK_BASE_URL}/github/callback`,
    scope: ['user:email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        const email = profile.emails?.[0]?.value;
        const name = profile.displayName || profile.username;
        const picture = profile.photos?.[0]?.value;
        if (!email) {
            return done(new Error('No email provided by GitHub'), null);
        }
        // Check if user exists
        let user = await User_1.User.findByEmail(email);
        if (user) {
            // Update OAuth info if not already linked
            if (!user.oauthProvider) {
                await User_1.User.updateOAuthInfo(user.id, 'github', profile.id, picture ? { picture } : undefined);
            }
        }
        else {
            // Create new user
            user = await User_1.User.createOAuthUser({
                email,
                name,
                oauthProvider: 'github',
                oauthId: profile.id,
                picture
            });
        }
        return done(null, user);
    }
    catch (error) {
        return done(error, false);
    }
}));
// Microsoft OAuth Strategy
passport_1.default.use(new passport_microsoft_1.Strategy({
    clientID: process.env.MICROSOFT_CLIENT_ID,
    clientSecret: process.env.MICROSOFT_CLIENT_SECRET,
    callbackURL: `${process.env.OAUTH_CALLBACK_BASE_URL}/microsoft/callback`,
    tenant: process.env.MICROSOFT_TENANT_ID || 'common',
    scope: ['openid', 'profile', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        const email = profile.emails?.[0]?.value;
        const name = profile.displayName;
        const picture = profile.photos?.[0]?.value;
        if (!email) {
            return done(new Error('No email provided by Microsoft'), null);
        }
        // Check if user exists
        let user = await User_1.User.findByEmail(email);
        if (user) {
            // Update OAuth info if not already linked
            if (!user.oauthProvider) {
                await User_1.User.updateOAuthInfo(user.id, 'microsoft', profile.id, picture ? { picture } : undefined);
            }
        }
        else {
            // Create new user
            user = await User_1.User.createOAuthUser({
                email,
                name,
                oauthProvider: 'microsoft',
                oauthId: profile.id,
                picture
            });
        }
        return done(null, user);
    }
    catch (error) {
        return done(error, false);
    }
}));
exports.default = passport_1.default;
//# sourceMappingURL=oauth.js.map