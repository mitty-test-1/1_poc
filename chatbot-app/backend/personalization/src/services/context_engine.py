import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

class ContextEngine:
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

    async def add_behavior_data(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add behavior data for a user"""
        try:
            data_id = str(uuid.uuid4())
            user_id = behavior_data['user_id']
            behavior_type = behavior_data.get('behavior_type', 'general')
            data_value = behavior_data.get('data_value', {})

            with self.connection.cursor() as cursor:
                query = """
                INSERT INTO personalization_data
                (id, user_id, behavior_type, data_value)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """
                cursor.execute(query, (
                    data_id,
                    user_id,
                    behavior_type,
                    json.dumps(data_value)
                ))

                result = cursor.fetchone()
                self.connection.commit()

                return {
                    'id': result[0],
                    'user_id': result[1],
                    'behavior_type': result[2],
                    'data_value': json.loads(result[3]),
                    'timestamp': result[4]
                }

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to add behavior data: {str(e)}")

    async def get_behavior_data(self, user_id: str, behavior_type: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get user behavior data"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if behavior_type:
                    query = """
                    SELECT * FROM personalization_data
                    WHERE user_id = %s AND behavior_type = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                    """
                    cursor.execute(query, (user_id, behavior_type, limit))
                else:
                    query = """
                    SELECT * FROM personalization_data
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                    """
                    cursor.execute(query, (user_id, limit))

                results = cursor.fetchall()

                behavior_data = []
                for result in results:
                    behavior_data.append({
                        'id': result['id'],
                        'user_id': result['user_id'],
                        'behavior_type': result['behavior_type'],
                        'data_value': json.loads(result['data_value']),
                        'timestamp': result['timestamp']
                    })

                return {
                    'user_id': user_id,
                    'behavior_data': behavior_data,
                    'total_entries': len(behavior_data)
                }

        except Exception as e:
            raise Exception(f"Failed to get user behavior data: {str(e)}")

    async def get_user_behavior_patterns(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get behavior patterns by type
                query = """
                SELECT
                    behavior_type,
                    COUNT(*) as event_count,
                    MIN(timestamp) as first_occurrence,
                    MAX(timestamp) as last_occurrence
                FROM personalization_data
                WHERE user_id = %s AND timestamp >= %s
                GROUP BY behavior_type
                ORDER BY event_count DESC
                """
                cursor.execute(query, (user_id, cutoff_date))
                behavior_patterns = cursor.fetchall()

                # Get recent activity timeline
                query = """
                SELECT
                    DATE_TRUNC('day', timestamp) as date,
                    behavior_type,
                    COUNT(*) as daily_count
                FROM personalization_data
                WHERE user_id = %s AND timestamp >= %s
                GROUP BY DATE_TRUNC('day', timestamp), behavior_type
                ORDER BY date DESC
                """
                cursor.execute(query, (user_id, cutoff_date))
                daily_activity = cursor.fetchall()

                return {
                    'user_id': user_id,
                    'time_period_days': days,
                    'behavior_patterns': [
                        {
                            'behavior_type': pattern['behavior_type'],
                            'event_count': pattern['event_count'],
                            'first_occurrence': pattern['first_occurrence'].isoformat(),
                            'last_occurrence': pattern['last_occurrence'].isoformat()
                        }
                        for pattern in behavior_patterns
                    ],
                    'daily_activity': [
                        {
                            'date': activity['date'].isoformat(),
                            'behavior_type': activity['behavior_type'],
                            'count': activity['daily_count']
                        }
                        for activity in daily_activity
                    ],
                    'total_events': sum(pattern['event_count'] for pattern in behavior_patterns)
                }

        except Exception as e:
            raise Exception(f"Failed to analyze user behavior: {str(e)}")

    async def get_similar_users(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find users with similar behavior patterns"""
        try:
            # Get current user's behavior
            user_behavior = await self.get_user_behavior_patterns(user_id, 30)

            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get all other users with recent activity
                query = """
                SELECT DISTINCT user_id FROM personalization_data
                WHERE user_id != %s AND timestamp >= NOW() - INTERVAL '30 days'
                """
                cursor.execute(query, (user_id,))
                other_users = cursor.fetchall()

                similar_users = []
                for other_user in other_users[:limit]:  # Limit to avoid too many calculations
                    other_behavior = await self.get_user_behavior_patterns(other_user['user_id'], 30)
                    similarity_score = self._calculate_similarity(user_behavior, other_behavior)

                    if similarity_score > 0.3:  # Lower threshold for broader matching
                        similar_users.append({
                            'user_id': other_user['user_id'],
                            'similarity_score': similarity_score,
                            'total_events': other_behavior['total_events']
                        })

                # Sort by similarity score
                similar_users.sort(key=lambda x: x['similarity_score'], reverse=True)

                return similar_users[:limit]

        except Exception as e:
            raise Exception(f"Failed to find similar users: {str(e)}")

    async def add_conversation_context(self, user_id: str, conversation_id: str, message_content: str) -> Dict[str, Any]:
        """Add conversation context data (backward compatibility)"""
        return await self.add_behavior_data({
            'user_id': user_id,
            'behavior_type': 'conversation',
            'data_value': {
                'conversation_id': conversation_id,
                'message_content': message_content,
                'message_length': len(message_content)
            }
        })

    async def get_conversation_context(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get conversation context data (backward compatibility)"""
        return await self.get_behavior_data(user_id, 'conversation', limit)

    def _calculate_similarity(self, behavior1: Dict[str, Any], behavior2: Dict[str, Any]) -> float:
        """Calculate similarity between two behavior patterns"""
        # Compare behavior type distributions
        types1 = {p['behavior_type']: p['event_count'] for p in behavior1.get('behavior_patterns', [])}
        types2 = {p['behavior_type']: p['event_count'] for p in behavior2.get('behavior_patterns', [])}

        all_types = set(types1.keys()) | set(types2.keys())

        if not all_types:
            return 0.0

        # Cosine similarity of behavior type vectors
        dot_product = sum(types1.get(t, 0) * types2.get(t, 0) for t in all_types)
        magnitude1 = sum(count ** 2 for count in types1.values()) ** 0.5
        magnitude2 = sum(count ** 2 for count in types2.values()) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)