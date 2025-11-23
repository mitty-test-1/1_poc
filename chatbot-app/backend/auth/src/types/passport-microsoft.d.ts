declare module 'passport-microsoft' {
  import { Strategy } from 'passport';

  interface MicrosoftStrategyOptions {
    clientID: string;
    clientSecret: string;
    callbackURL: string;
    tenant?: string;
    scope?: string[];
  }

  class MicrosoftStrategy extends Strategy {
    constructor(options: MicrosoftStrategyOptions, verify: (accessToken: string, refreshToken: string, profile: any, done: (error: any, user?: any) => void) => void);
  }

  export { MicrosoftStrategy as Strategy };
}