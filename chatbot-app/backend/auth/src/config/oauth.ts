import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';
import { Strategy as GitHubStrategy } from 'passport-github2';
import { Strategy as MicrosoftStrategy } from 'passport-microsoft';
import { User } from '../models/User';

export interface OAuthProfile {
  provider: 'google' | 'github' | 'microsoft';
  id: string;
  email: string;
  name: string;
  picture?: string;
}

// Serialize user for session
passport.serializeUser((user: any, done) => {
  done(null, user.id);
});

// Deserialize user from session
passport.deserializeUser(async (id: string, done) => {
  try {
    const user = await User.findById(id);
    done(null, user);
  } catch (error) {
    done(error, null);
  }
});

// Google OAuth Strategy
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
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
    let user = await User.findByEmail(email);

    if (user) {
      // Update OAuth info if not already linked
      if (!user.oauthProvider) {
        await User.updateOAuthInfo(user.id!, 'google', profile.id, picture ? { picture } : undefined);
      }
    } else {
      // Create new user
      user = await User.createOAuthUser({
        email,
        name,
        oauthProvider: 'google',
        oauthId: profile.id,
        picture
      });
    }

    return done(null, user);
  } catch (error) {
    return done(error, false);
  }
}));

// GitHub OAuth Strategy
passport.use(new GitHubStrategy({
  clientID: process.env.GITHUB_CLIENT_ID!,
  clientSecret: process.env.GITHUB_CLIENT_SECRET!,
  callbackURL: `${process.env.OAUTH_CALLBACK_BASE_URL}/github/callback`,
  scope: ['user:email']
}, async (accessToken: string, refreshToken: string, profile: any, done: any) => {
  try {
    const email = profile.emails?.[0]?.value;
    const name = profile.displayName || profile.username;
    const picture = profile.photos?.[0]?.value;

    if (!email) {
      return done(new Error('No email provided by GitHub'), null);
    }

    // Check if user exists
    let user = await User.findByEmail(email);

    if (user) {
      // Update OAuth info if not already linked
      if (!user.oauthProvider) {
        await User.updateOAuthInfo(user.id!, 'github', profile.id, picture ? { picture } : undefined);
      }
    } else {
      // Create new user
      user = await User.createOAuthUser({
        email,
        name,
        oauthProvider: 'github',
        oauthId: profile.id,
        picture
      });
    }

    return done(null, user);
  } catch (error) {
    return done(error, false);
  }
}));

// Microsoft OAuth Strategy
passport.use(new MicrosoftStrategy({
  clientID: process.env.MICROSOFT_CLIENT_ID!,
  clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
  callbackURL: `${process.env.OAUTH_CALLBACK_BASE_URL}/microsoft/callback`,
  tenant: process.env.MICROSOFT_TENANT_ID || 'common',
  scope: ['openid', 'profile', 'email']
}, async (accessToken: string, refreshToken: string, profile: any, done: any) => {
  try {
    const email = profile.emails?.[0]?.value;
    const name = profile.displayName;
    const picture = profile.photos?.[0]?.value;

    if (!email) {
      return done(new Error('No email provided by Microsoft'), null);
    }

    // Check if user exists
    let user = await User.findByEmail(email);

    if (user) {
      // Update OAuth info if not already linked
      if (!user.oauthProvider) {
        await User.updateOAuthInfo(user.id!, 'microsoft', profile.id, picture ? { picture } : undefined);
      }
    } else {
      // Create new user
      user = await User.createOAuthUser({
        email,
        name,
        oauthProvider: 'microsoft',
        oauthId: profile.id,
        picture
      });
    }

    return done(null, user);
  } catch (error) {
    return done(error, false);
  }
}));

export default passport;