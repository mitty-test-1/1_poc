import { v4 as uuidv4 } from 'uuid';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:password@localhost:5432/chatbot'
});

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

export class User {
  static async create(userData: Omit<UserData, 'id' | 'createdAt' | 'updatedAt'>): Promise<UserData> {
    const id = uuidv4();
    const createdAt = new Date();
    const updatedAt = new Date();

    const query = `
      INSERT INTO users (id, email, password_hash, name, role, oauth_provider, oauth_id, picture, email_verified, preferences, created_at, updated_at)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      RETURNING *
    `;

    const values = [
      id,
      userData.email,
      userData.passwordHash || null,
      userData.name,
      userData.role,
      userData.oauthProvider || null,
      userData.oauthId || null,
      userData.picture || null,
      userData.emailVerified || false,
      JSON.stringify(userData.preferences || {}),
      createdAt,
      updatedAt
    ];

    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async findById(id: string): Promise<UserData | null> {
    const query = 'SELECT * FROM users WHERE id = $1';
    const result = await pool.query(query, [id]);
    return result.rows[0] || null;
  }

  static async findByEmail(email: string): Promise<UserData | null> {
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await pool.query(query, [email]);
    return result.rows[0] || null;
  }

  static async updateLastLogin(userId: string): Promise<void> {
    const query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1';
    await pool.query(query, [userId]);
  }

  static async updatePreferences(userId: string, preferences: any): Promise<void> {
    const query = 'UPDATE users SET preferences = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2';
    await pool.query(query, [JSON.stringify(preferences), userId]);
  }

  static async createOAuthUser(userData: {
    email: string;
    name: string;
    oauthProvider: string;
    oauthId: string;
    picture?: string;
    role?: string;
  }): Promise<UserData> {
    return this.create({
      email: userData.email,
      name: userData.name,
      role: userData.role || 'user',
      oauthProvider: userData.oauthProvider,
      oauthId: userData.oauthId,
      picture: userData.picture,
      emailVerified: true // OAuth users come pre-verified
    });
  }

  static async updateOAuthInfo(userId: string, provider: string | null, oauthId: string | null, additionalData?: { picture?: string }): Promise<void> {
    const query = `
      UPDATE users
      SET oauth_provider = $1, oauth_id = $2, picture = COALESCE($3, picture), updated_at = CURRENT_TIMESTAMP
      WHERE id = $4
    `;
    await pool.query(query, [provider, oauthId, additionalData?.picture, userId]);
  }

  static async findByOAuthId(provider: string, oauthId: string): Promise<UserData | null> {
    const query = 'SELECT * FROM users WHERE oauth_provider = $1 AND oauth_id = $2';
    const result = await pool.query(query, [provider, oauthId]);
    return result.rows[0] || null;
  }

  static async linkOAuthAccount(userId: string, provider: string, oauthId: string, additionalData?: { picture?: string }): Promise<void> {
    // Check if OAuth account is already linked to another user
    const existingUser = await this.findByOAuthId(provider, oauthId);
    if (existingUser && existingUser.id !== userId) {
      throw new Error('OAuth account already linked to another user');
    }

    await this.updateOAuthInfo(userId, provider, oauthId, additionalData);
  }
}