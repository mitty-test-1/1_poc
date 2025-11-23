import passport from 'passport';
export interface OAuthProfile {
    provider: 'google' | 'github' | 'microsoft';
    id: string;
    email: string;
    name: string;
    picture?: string;
}
export default passport;
//# sourceMappingURL=oauth.d.ts.map