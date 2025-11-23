import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum

class ConversationState(Enum):
    NEW = "new"
    ACTIVE = "active"
    WAITING = "waiting"
    COMPLETED = "completed"
    STALLED = "stalled"

@dataclass
class ConversationContext:
    conversation_id: str
    user_id: str
    state: ConversationState
    current_topic: Optional[str] = None
    previous_intents: List[str] = None
    previous_sentiments: List[str] = None
    entities_mentioned: Dict[str, Any] = None
    last_activity: datetime = None
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.previous_intents is None:
            self.previous_intents = []
        if self.previous_sentiments is None:
            self.previous_sentiments = []
        if self.entities_mentioned is None:
            self.entities_mentioned = {}
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

class ConversationStateManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conversations: Dict[str, ConversationContext] = {}
        self.user_conversations: Dict[str, List[str]] = defaultdict(list)
        self.max_conversation_age = timedelta(hours=24)  # Conversations expire after 24 hours
        self.max_conversations_per_user = 10
        self.cleanup_interval = 3600  # Cleanup every hour
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background cleanup task"""
        asyncio.create_task(self._cleanup_expired_conversations())

    async def _cleanup_expired_conversations(self):
        """Clean up expired conversations"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                current_time = datetime.utcnow()
                expired_conversations = []

                for conv_id, context in self.conversations.items():
                    if current_time - context.last_activity > self.max_conversation_age:
                        expired_conversations.append(conv_id)

                for conv_id in expired_conversations:
                    await self._remove_conversation(conv_id)

                if expired_conversations:
                    self.logger.info(f"Cleaned up {len(expired_conversations)} expired conversations")

            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")

    async def create_conversation(self, conversation_id: str, user_id: str,
                                initial_context: Optional[Dict[str, Any]] = None) -> ConversationContext:
        """Create a new conversation context"""
        try:
            # Check if conversation already exists
            if conversation_id in self.conversations:
                return self.conversations[conversation_id]

            # Create new conversation context
            context = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                state=ConversationState.NEW,
                current_topic=initial_context.get("topic") if initial_context else None,
                metadata=initial_context or {}
            )

            self.conversations[conversation_id] = context
            self.user_conversations[user_id].append(conversation_id)

            # Limit conversations per user
            if len(self.user_conversations[user_id]) > self.max_conversations_per_user:
                oldest_conv_id = self.user_conversations[user_id].pop(0)
                await self._remove_conversation(oldest_conv_id)

            self.logger.info(f"Created new conversation {conversation_id} for user {user_id}")
            return context

        except Exception as e:
            self.logger.error(f"Error creating conversation {conversation_id}: {e}")
            raise

    async def update_conversation(self, conversation_id: str, intent: str,
                                sentiment: str, entities: List[Dict[str, Any]],
                                additional_context: Optional[Dict[str, Any]] = None) -> ConversationContext:
        """Update conversation context with new message data"""
        try:
            if conversation_id not in self.conversations:
                raise ValueError(f"Conversation {conversation_id} not found")

            context = self.conversations[conversation_id]

            # Update state to active if it was new
            if context.state == ConversationState.NEW:
                context.state = ConversationState.ACTIVE

            # Add intent and sentiment to history
            context.previous_intents.append(intent)
            context.previous_sentiments.append(sentiment)

            # Keep only last 10 intents/sentiments
            context.previous_intents = context.previous_intents[-10:]
            context.previous_sentiments = context.previous_sentiments[-10:]

            # Update entities mentioned
            for entity in entities:
                entity_type = entity.get("type", "unknown")
                entity_value = entity.get("value", entity.get("text", ""))
                if entity_type not in context.entities_mentioned:
                    context.entities_mentioned[entity_type] = []
                if entity_value not in context.entities_mentioned[entity_type]:
                    context.entities_mentioned[entity_type].append(entity_value)

            # Update topic based on intent patterns
            context.current_topic = self._infer_topic_from_intent(intent, context.previous_intents)

            # Update metadata
            if additional_context:
                context.metadata.update(additional_context)

            # Update timestamps
            context.last_activity = datetime.utcnow()
            context.updated_at = datetime.utcnow()

            self.logger.debug(f"Updated conversation {conversation_id} with intent: {intent}")
            return context

        except Exception as e:
            self.logger.error(f"Error updating conversation {conversation_id}: {e}")
            raise

    def _infer_topic_from_intent(self, current_intent: str, previous_intents: List[str]) -> str:
        """Infer conversation topic from intent patterns"""
        try:
            # Topic mapping based on intents
            topic_mapping = {
                "booking": ["booking", "reservation", "schedule", "appointment"],
                "complaint": ["complaint", "problem", "issue", "error", "bug"],
                "information": ["information", "help", "what", "how", "when", "where", "why"],
                "pricing": ["pricing", "price", "cost", "payment", "billing"],
                "shipping": ["shipping", "delivery", "tracking", "order"],
                "account": ["account", "login", "register", "profile", "settings"],
                "technical": ["technical", "support", "installation", "setup", "configuration"],
                "general": ["general", "greeting", "goodbye", "thanks"]
            }

            # Check current intent
            for topic, intents in topic_mapping.items():
                if current_intent in intents:
                    return topic

            # Check previous intents for dominant topic
            intent_counts = defaultdict(int)
            for intent in previous_intents[-5:]:  # Last 5 intents
                for topic, intents in topic_mapping.items():
                    if intent in intents:
                        intent_counts[topic] += 1

            if intent_counts:
                return max(intent_counts, key=intent_counts.get)

            return "general"

        except Exception as e:
            self.logger.error(f"Error inferring topic: {e}")
            return "general"

    async def get_conversation_context(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get conversation context"""
        try:
            return self.conversations.get(conversation_id)
        except Exception as e:
            self.logger.error(f"Error getting conversation context {conversation_id}: {e}")
            return None

    async def get_user_conversations(self, user_id: str) -> List[ConversationContext]:
        """Get all conversations for a user"""
        try:
            conversation_ids = self.user_conversations.get(user_id, [])
            return [self.conversations[conv_id] for conv_id in conversation_ids if conv_id in self.conversations]
        except Exception as e:
            self.logger.error(f"Error getting user conversations for {user_id}: {e}")
            return []

    async def get_conversation_state(self, conversation_id: str) -> ConversationState:
        """Get conversation state"""
        try:
            context = self.conversations.get(conversation_id)
            return context.state if context else ConversationState.NEW
        except Exception as e:
            self.logger.error(f"Error getting conversation state {conversation_id}: {e}")
            return ConversationState.NEW

    async def set_conversation_state(self, conversation_id: str, state: ConversationState) -> bool:
        """Set conversation state"""
        try:
            if conversation_id in self.conversations:
                self.conversations[conversation_id].state = state
                self.conversations[conversation_id].updated_at = datetime.utcnow()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error setting conversation state {conversation_id}: {e}")
            return False

    async def get_context_aware_features(self, conversation_id: str) -> Dict[str, Any]:
        """Get context-aware features for AI processing"""
        try:
            context = self.conversations.get(conversation_id)
            if not context:
                return {}

            # Calculate conversation features
            features = {
                "conversation_length": len(context.previous_intents),
                "dominant_intent": self._get_dominant_intent(context.previous_intents),
                "sentiment_trend": self._calculate_sentiment_trend(context.previous_sentiments),
                "topic_consistency": self._calculate_topic_consistency(context.previous_intents),
                "entity_richness": len(context.entities_mentioned),
                "conversation_age_hours": (datetime.utcnow() - context.created_at).total_seconds() / 3600,
                "last_activity_hours": (datetime.utcnow() - context.last_activity).total_seconds() / 3600,
                "current_topic": context.current_topic,
                "state": context.state.value
            }

            return features

        except Exception as e:
            self.logger.error(f"Error getting context features for {conversation_id}: {e}")
            return {}

    def _get_dominant_intent(self, intents: List[str]) -> str:
        """Get the most common intent in conversation"""
        try:
            if not intents:
                return "unknown"

            intent_counts = defaultdict(int)
            for intent in intents:
                intent_counts[intent] += 1

            return max(intent_counts, key=intent_counts.get)
        except Exception:
            return "unknown"

    def _calculate_sentiment_trend(self, sentiments: List[str]) -> str:
        """Calculate sentiment trend"""
        try:
            if len(sentiments) < 2:
                return "stable"

            # Simple trend calculation
            positive_count = sentiments.count("positive")
            negative_count = sentiments.count("negative")
            neutral_count = sentiments.count("neutral")

            total = len(sentiments)
            positive_ratio = positive_count / total
            negative_ratio = negative_count / total

            if positive_ratio > 0.6:
                return "positive"
            elif negative_ratio > 0.6:
                return "negative"
            else:
                return "mixed"

        except Exception:
            return "stable"

    def _calculate_topic_consistency(self, intents: List[str]) -> float:
        """Calculate topic consistency (0.0 to 1.0)"""
        try:
            if len(intents) < 2:
                return 1.0

            # Group intents by topic
            topic_groups = defaultdict(list)
            for intent in intents:
                topic = self._infer_topic_from_intent(intent, [])
                topic_groups[topic].append(intent)

            # Calculate consistency as the ratio of the largest topic group
            if topic_groups:
                max_group_size = max(len(group) for group in topic_groups.values())
                return max_group_size / len(intents)
            else:
                return 0.0

        except Exception:
            return 0.0

    async def _remove_conversation(self, conversation_id: str):
        """Remove a conversation"""
        try:
            if conversation_id in self.conversations:
                context = self.conversations[conversation_id]
                user_id = context.user_id

                # Remove from conversations
                del self.conversations[conversation_id]

                # Remove from user conversations
                if user_id in self.user_conversations and conversation_id in self.user_conversations[user_id]:
                    self.user_conversations[user_id].remove(conversation_id)

                self.logger.debug(f"Removed conversation {conversation_id}")

        except Exception as e:
            self.logger.error(f"Error removing conversation {conversation_id}: {e}")

    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        try:
            context = self.conversations.get(conversation_id)
            if not context:
                return {"error": "Conversation not found"}

            summary = {
                "conversation_id": conversation_id,
                "user_id": context.user_id,
                "state": context.state.value,
                "current_topic": context.current_topic,
                "message_count": len(context.previous_intents),
                "dominant_intent": self._get_dominant_intent(context.previous_intents),
                "sentiment_trend": self._calculate_sentiment_trend(context.previous_sentiments),
                "entities_mentioned": len(context.entities_mentioned),
                "created_at": context.created_at.isoformat(),
                "last_activity": context.last_activity.isoformat(),
                "duration_hours": (context.last_activity - context.created_at).total_seconds() / 3600
            }

            return summary

        except Exception as e:
            self.logger.error(f"Error getting conversation summary {conversation_id}: {e}")
            return {"error": str(e)}

    async def export_conversations(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Export conversation data"""
        try:
            if user_id:
                conversations = await self.get_user_conversations(user_id)
            else:
                conversations = list(self.conversations.values())

            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_conversations": len(conversations),
                "conversations": [asdict(conv) for conv in conversations]
            }

            return export_data

        except Exception as e:
            self.logger.error(f"Error exporting conversations: {e}")
            return {"error": str(e)}