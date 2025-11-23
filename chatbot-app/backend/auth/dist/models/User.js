"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.User = void 0;
const uuid_1 = require("uuid");
const pg_1 = require("pg");
const pool = new pg_1.Pool({
    connectionString: process.env.DATABASE_URL || 'postgresql://postgres:password@localhost:5432/chatbot'
});
class User {
    static async create(userData) {
        const id = (0, uuid_1.v4)();
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
    static async findById(id) {
        const query = 'SELECT * FROM users WHERE id = $1';
        const result = await pool.query(query, [id]);
        return result.rows[0] || null;
    }
    static async findByEmail(email) {
        const query = 'SELECT * FROM users WHERE email = $1';
        const result = await pool.query(query, [email]);
        return result.rows[0] || null;
    }
    static async updateLastLogin(userId) {
        const query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1';
        await pool.query(query, [userId]);
    }
    static async updatePreferences(userId, preferences) {
        const query = 'UPDATE users SET preferences = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2';
        await pool.query(query, [JSON.stringify(preferences), userId]);
    }
    static async createOAuthUser(userData) {
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
    static async updateOAuthInfo(userId, provider, oauthId, additionalData) {
        const query = `
      UPDATE users
      SET oauth_provider = $1, oauth_id = $2, picture = COALESCE($3, picture), updated_at = CURRENT_TIMESTAMP
      WHERE id = $4
    `;
        await pool.query(query, [provider, oauthId, additionalData?.picture, userId]);
    }
    static async findByOAuthId(provider, oauthId) {
        const query = 'SELECT * FROM users WHERE oauth_provider = $1 AND oauth_id = $2';
        const result = await pool.query(query, [provider, oauthId]);
        return result.rows[0] || null;
    }
    static async linkOAuthAccount(userId, provider, oauthId, additionalData) {
        // Check if OAuth account is already linked to another user
        const existingUser = await this.findByOAuthId(provider, oauthId);
        if (existingUser && existingUser.id !== userId) {
            throw new Error('OAuth account already linked to another user');
        }
        await this.updateOAuthInfo(userId, provider, oauthId, additionalData);
    }
}
exports.User = User;
//# sourceMappingURL=User.js.map