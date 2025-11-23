export interface UserData {
    id?: string;
    email: string;
    passwordHash?: string;
    name: string;
    role: string;
    oauthProvider?: string;
    oauthId?: string;
    picture?: string;
    emailVerified?: boolean;
    preferences?: any;
    createdAt?: Date;
    updatedAt?: Date;
    lastLogin?: Date;
}
export declare class User {
    static create(userData: Omit<UserData, 'id' | 'createdAt' | 'updatedAt'>): Promise<UserData>;
    static findById(id: string): Promise<UserData | null>;
    static findByEmail(email: string): Promise<UserData | null>;
    static updateLastLogin(userId: string): Promise<void>;
    static updatePreferences(userId: string, preferences: any): Promise<void>;
    static createOAuthUser(userData: {
        email: string;
        name: string;
        oauthProvider: string;
        oauthId: string;
        picture?: string;
        role?: string;
    }): Promise<UserData>;
    static updateOAuthInfo(userId: string, provider: string | null, oauthId: string | null, additionalData?: {
        picture?: string;
    }): Promise<void>;
    static findByOAuthId(provider: string, oauthId: string): Promise<UserData | null>;
    static linkOAuthAccount(userId: string, provider: string, oauthId: string, additionalData?: {
        picture?: string;
    }): Promise<void>;
}
//# sourceMappingURL=User.d.ts.map