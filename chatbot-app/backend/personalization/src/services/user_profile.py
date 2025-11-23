import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

class UserProfileService:
    def __init__(self):
        self.connection = self._get_connection()

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host='localhost',
            database='chatbot',
            user='postgres',
            password='password'
        )

    async def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile"""
        try:
            user_id = profile_data['user_id']
            preferences = profile_data.get('preferences', {})
            demographics = profile_data.get('demographics', {})
            settings = profile_data.get('settings', {})

            with self.connection.cursor() as cursor:
                query = """
                INSERT INTO user_profiles
                (user_id, preferences, demographics, settings)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """
                cursor.execute(query, (
                    user_id,
                    json.dumps(preferences),
                    json.dumps(demographics),
                    json.dumps(settings)
                ))

                result = cursor.fetchone()
                self.connection.commit()

                return {
                    'user_id': result[0],
                    'preferences': json.loads(result[1]),
                    'demographics': json.loads(result[2]),
                    'settings': json.loads(result[3]),
                    'created_at': result[4],
                    'updated_at': result[5]
                }

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to create user profile: {str(e)}")

    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user ID"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM user_profiles WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()

                if result:
                    return {
                        'user_id': result['user_id'],
                        'preferences': json.loads(result['preferences']),
                        'demographics': json.loads(result['demographics']),
                        'settings': json.loads(result['settings']),
                        'created_at': result['created_at'],
                        'updated_at': result['updated_at']
                    }
                return None

        except Exception as e:
            raise Exception(f"Failed to get user profile: {str(e)}")

    async def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            preferences = profile_data.get('preferences', {})
            demographics = profile_data.get('demographics', {})
            settings = profile_data.get('settings', {})

            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                UPDATE user_profiles
                SET preferences = %s,
                    demographics = %s,
                    settings = %s
                WHERE user_id = %s
                RETURNING *
                """
                cursor.execute(query, (
                    json.dumps(preferences),
                    json.dumps(demographics),
                    json.dumps(settings),
                    user_id
                ))

                result = cursor.fetchone()
                self.connection.commit()

                if not result:
                    raise Exception("User profile not found")

                return {
                    'user_id': result['user_id'],
                    'preferences': json.loads(result['preferences']),
                    'demographics': json.loads(result['demographics']),
                    'settings': json.loads(result['settings']),
                    'created_at': result['created_at'],
                    'updated_at': result['updated_at']
                }

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to update user profile: {str(e)}")

    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                # Create profile if it doesn't exist
                await self.create_profile({
                    'user_id': user_id,
                    'preferences': preferences,
                    'demographics': {},
                    'settings': {}
                })
                return True

            current_preferences = profile['preferences']
            current_preferences.update(preferences)

            await self.update_profile(user_id, {'preferences': current_preferences})
            return True

        except Exception as e:
            raise Exception(f"Failed to update preferences: {str(e)}")

    async def update_demographics(self, user_id: str, demographics: Dict[str, Any]) -> bool:
        """Update user demographics"""
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                # Create profile if it doesn't exist
                await self.create_profile({
                    'user_id': user_id,
                    'preferences': {},
                    'demographics': demographics,
                    'settings': {}
                })
                return True

            current_demographics = profile['demographics']
            current_demographics.update(demographics)

            await self.update_profile(user_id, {'demographics': current_demographics})
            return True

        except Exception as e:
            raise Exception(f"Failed to update demographics: {str(e)}")

    async def update_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """Update user settings"""
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                # Create profile if it doesn't exist
                await self.create_profile({
                    'user_id': user_id,
                    'preferences': {},
                    'demographics': {},
                    'settings': settings
                })
                return True

            current_settings = profile['settings']
            current_settings.update(settings)

            await self.update_profile(user_id, {'settings': current_settings})
            return True

        except Exception as e:
            raise Exception(f"Failed to update settings: {str(e)}")

    async def delete_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        try:
            with self.connection.cursor() as cursor:
                query = "DELETE FROM user_profiles WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                self.connection.commit()
                return cursor.rowcount > 0

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to delete user profile: {str(e)}")