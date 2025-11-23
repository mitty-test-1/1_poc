import re
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import random
import os
from pathlib import Path

class ResponseGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.response_templates = self._load_response_templates()
        self.context_memory = {}
        self.user_profiles = {}
    
    def _load_response_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load response templates from configuration"""
        return {
            "greeting": {
                "templates": [
                    "Hello! How can I help you today?",
                    "Hi there! What can I do for you?",
                    "Greetings! How may I assist you?",
                    "Welcome! How can I be of service?",
                    "Hey! What's on your mind?"
                ],
                "fallback": "Hello! How can I help you?",
                "context_aware": True
            },
            "goodbye": {
                "templates": [
                    "Goodbye! Have a great day!",
                    "See you later! Take care!",
                    "Farewell! Have a wonderful day!",
                    "Bye! Feel free to come back anytime!",
                    "Take care! Talk to you soon!"
                ],
                "fallback": "Goodbye! Have a great day!",
                "context_aware": False
            },
            "thanks": {
                "templates": [
                    "You're welcome! Is there anything else I can help with?",
                    "My pleasure! How else can I assist you?",
                    "Happy to help! What else can I do for you?",
                    "No problem! Let me know if you need anything else.",
                    "You're very welcome! I'm here to help."
                ],
                "fallback": "You're welcome! Is there anything else I can help with?",
                "context_aware": True
            },
            "help": {
                "templates": [
                    "I'm here to help! What specific assistance do you need?",
                    "I'd be happy to help! What can I assist you with?",
                    "How can I help you today? Please let me know what you need.",
                    "I'm at your service! What would you like help with?",
                    "What can I help you with? I'm here to assist."
                ],
                "fallback": "I'm here to help! What specific assistance do you need?",
                "context_aware": True
            },
            "information": {
                "templates": [
                    "Let me provide you with that information.",
                    "I'd be happy to share that information with you.",
                    "Here's what I can tell you about that.",
                    "Let me get that information for you.",
                    "I can help with that information."
                ],
                "fallback": "Let me provide you with that information.",
                "context_aware": True
            },
            "booking": {
                "templates": [
                    "I'd be happy to help you book that. What dates work for you?",
                    "Let me assist you with booking. When would you like to schedule?",
                    "I can help you make a reservation. What time works best?",
                    "Booking is available! Let me get that set up for you.",
                    "I'll help you book that. What are your preferred dates?"
                ],
                "fallback": "I'd be happy to help you book that. What dates work for you?",
                "context_aware": True
            },
            "complaint": {
                "templates": [
                    "I'm sorry to hear about your issue. Let me help resolve this.",
                    "I understand your frustration. I'm here to help fix this problem.",
                    "I apologize for the inconvenience. How can I make this right?",
                    "I'm sorry you're experiencing this. Let me work on a solution.",
                    "I understand your concern. I'll help get this resolved for you."
                ],
                "fallback": "I'm sorry to hear about your issue. Let me help resolve this.",
                "context_aware": True
            },
            "feedback": {
                "templates": [
                    "Thank you for your feedback! I appreciate your input.",
                    "I value your feedback! How can I improve your experience?",
                    "Thanks for sharing your thoughts! Your feedback is important.",
                    "I appreciate you taking the time to provide feedback.",
                    "Thank you for your valuable feedback! How else can I help?"
                ],
                "fallback": "Thank you for your feedback! I appreciate your input.",
                "context_aware": True
            },
            "pricing": {
                "templates": [
                    "Let me help you with pricing information.",
                    "I can provide you with pricing details.",
                    "Here's the pricing information you requested.",
                    "Let me get that pricing information for you.",
                    "I'd be happy to share pricing details with you."
                ],
                "fallback": "Let me help you with pricing information.",
                "context_aware": True
            },
            "availability": {
                "templates": [
                    "Let me check the availability for you.",
                    "I'll look up the availability information.",
                    "Here's what I found regarding availability.",
                    "Let me get that availability information for you.",
                    "I can help you check availability."
                ],
                "fallback": "Let me check the availability for you.",
                "context_aware": True
            },
            "location": {
                "templates": [
                    "I can help you with location information.",
                    "Let me provide you with location details.",
                    "Here's the location information you need.",
                    "I'd be happy to share location details with you.",
                    "Let me get that location information for you."
                ],
                "fallback": "I can help you with location information.",
                "context_aware": True
            },
            "contact": {
                "templates": [
                    "Here's how you can reach us:",
                    "You can contact us through these channels:",
                    "Here are our contact details:",
                    "Feel free to reach out to us:",
                    "You can get in touch with us via:"
                ],
                "fallback": "Here's how you can reach us:",
                "context_aware": True
            },
            "account": {
                "templates": [
                    "I can help you with your account.",
                    "Let me assist you with account-related matters.",
                    "Here's what I can help you with regarding your account:",
                    "I'm here to help with your account needs.",
                    "Let me get that information for your account."
                ],
                "fallback": "I can help you with your account.",
                "context_aware": True
            },
            "payment": {
                "templates": [
                    "I can help you with payment information.",
                    "Let me provide you with payment details.",
                    "Here's what you need to know about payments:",
                    "I'd be happy to help with payment-related questions.",
                    "Let me get that payment information for you."
                ],
                "fallback": "I can help you with payment information.",
                "context_aware": True
            },
            "shipping": {
                "templates": [
                    "I can help you with shipping information.",
                    "Let me provide you with shipping details.",
                    "Here's what you need to know about shipping:",
                    "I'd be happy to help with shipping-related questions.",
                    "Let me get that shipping information for you."
                ],
                "fallback": "I can help you with shipping information.",
                "context_aware": True
            },
            "return": {
                "templates": [
                    "I can help you with return information.",
                    "Let me provide you with return details.",
                    "Here's what you need to know about returns:",
                    "I'd be happy to help with return-related questions.",
                    "Let me get that return information for you."
                ],
                "fallback": "I can help you with return information.",
                "context_aware": True
            },
            "warranty": {
                "templates": [
                    "I can help you with warranty information.",
                    "Let me provide you with warranty details.",
                    "Here's what you need to know about warranty:",
                    "I'd be happy to help with warranty-related questions.",
                    "Let me get that warranty information for you."
                ],
                "fallback": "I can help you with warranty information.",
                "context_aware": True
            },
            "technical": {
                "templates": [
                    "I can help you with technical support.",
                    "Let me provide you with technical assistance.",
                    "Here's what I can do to help with technical issues:",
                    "I'm here to help with your technical needs.",
                    "Let me get that technical information for you."
                ],
                "fallback": "I can help you with technical support.",
                "context_aware": True
            },
            "general": {
                "templates": [
                    "I'm here to help! What would you like to discuss?",
                    "How can I assist you today?",
                    "I'm ready to help with whatever you need.",
                    "What's on your mind? I'm here to listen.",
                    "I'm at your service! How can I help?"
                ],
                "fallback": "I'm here to help! What would you like to discuss?",
                "context_aware": True
            },
            "unknown": {
                "templates": [
                    "I'm not sure I understand. Could you please clarify?",
                    "I didn't quite catch that. Could you rephrase?",
                    "I'm having trouble understanding. Could you explain differently?",
                    "I'm not sure what you mean. Could you provide more details?",
                    "I didn't understand that. Could you please elaborate?"
                ],
                "fallback": "I'm not sure I understand. Could you please clarify?",
                "context_aware": True
            }
        }
    
    async def generate(self, message: str, intent: str, entities: List[Dict[str, Any]], 
                      sentiment: str, user_id: Optional[str] = None, 
                      conversation_id: Optional[str] = None, 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate AI response based on input"""
        try:
            # Update user context
            if user_id:
                self._update_user_context(user_id, message, intent, sentiment, entities, context)
            
            # Generate response based on intent
            response = await self._generate_intent_response(intent, entities, sentiment, user_id, context)
            
            # Enhance response with context
            enhanced_response = self._enhance_response_with_context(response, context)
            
            # Calculate confidence
            confidence = self._calculate_response_confidence(intent, sentiment, entities, context)
            
            # Log the response
            self.logger.info(f"Generated response for intent '{intent}' with confidence {confidence}")
            
            return {
                "response": enhanced_response,
                "confidence": confidence,
                "type": self._determine_response_type(intent),
                "metadata": {
                    "intent": intent,
                    "sentiment": sentiment,
                    "entities_count": len(entities),
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "context_used": bool(context)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I'm having trouble generating a response right now. Could you please try again?",
                "confidence": 0.0,
                "type": "error",
                "metadata": {
                    "error": str(e),
                    "intent": intent,
                    "user_id": user_id,
                    "conversation_id": conversation_id
                }
            }
    
    def _update_user_context(self, user_id: str, message: str, intent: str, 
                           sentiment: str, entities: List[Dict[str, Any]], 
                           context: Optional[Dict[str, Any]]):
        """Update user context for personalization"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "conversation_history": [],
                "preferences": {},
                "common_intents": {},
                "sentiment_patterns": {},
                "entity_preferences": {}
            }
        
        user_profile = self.user_profiles[user_id]
        
        # Update conversation history
        user_profile["conversation_history"].append({
            "message": message,
            "intent": intent,
            "sentiment": sentiment,
            "entities": entities,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 10 conversations
        if len(user_profile["conversation_history"]) > 10:
            user_profile["conversation_history"] = user_profile["conversation_history"][-10:]
        
        # Update common intents
        user_profile["common_intents"][intent] = user_profile["common_intents"].get(intent, 0) + 1
        
        # Update sentiment patterns
        user_profile["sentiment_patterns"][sentiment] = user_profile["sentiment_patterns"].get(sentiment, 0) + 1
        
        # Update entity preferences
        for entity in entities:
            entity_type = entity.get("type", "unknown")
            user_profile["entity_preferences"][entity_type] = user_profile["entity_preferences"].get(entity_type, 0) + 1
    
    async def _generate_intent_response(self, intent: str, entities: List[Dict[str, Any]], 
                                      sentiment: str, user_id: Optional[str], 
                                      context: Optional[Dict[str, Any]]) -> str:
        """Generate response based on intent"""
        try:
            # Get intent-specific response
            if intent in self.response_templates:
                template_info = self.response_templates[intent]
                
                # Select template based on context and user preferences
                if template_info["context_aware"] and user_id:
                    response = self._select_contextual_template(
                        template_info, user_id, entities, sentiment, context
                    )
                else:
                    response = random.choice(template_info["templates"])
                
                # Customize response with entities
                response = self._customize_with_entities(response, entities)
                
                # Adjust tone based on sentiment
                response = self._adjust_tone(response, sentiment)
                
                return response
            else:
                # Fallback to unknown intent response
                return random.choice(self.response_templates["unknown"]["templates"])
                
        except Exception as e:
            self.logger.error(f"Error generating intent response: {e}")
            return self.response_templates["unknown"]["fallback"]
    
    def _select_contextual_template(self, template_info: Dict[str, Any], user_id: str, 
                                  entities: List[Dict[str, Any]], sentiment: str, 
                                  context: Optional[Dict[str, Any]]) -> str:
        """Select template based on context and user preferences"""
        try:
            user_profile = self.user_profiles[user_id]
            
            # Get user's preferred response style
            preferred_style = user_profile.get("preferences", {}).get("response_style", "neutral")
            
            # Filter templates based on style
            if preferred_style == "friendly":
                friendly_templates = [t for t in template_info["templates"] if 
                                    any(word in t.lower() for word in ["happy", "great", "wonderful", "pleased"])]
                if friendly_templates:
                    return random.choice(friendly_templates)
            
            elif preferred_style == "professional":
                professional_templates = [t for t in template_info["templates"] if 
                                        any(word in t.lower() for word in ["assist", "provide", "service", "help"])]
                if professional_templates:
                    return random.choice(professional_templates)
            
            # Default to random selection
            return random.choice(template_info["templates"])
            
        except Exception as e:
            self.logger.error(f"Error selecting contextual template: {e}")
            return template_info["fallback"]
    
    def _customize_with_entities(self, response: str, entities: List[Dict[str, Any]]) -> str:
        """Customize response with extracted entities"""
        try:
            for entity in entities:
                entity_type = entity.get("type", "")
                entity_value = entity.get("value", "")
                entity_text = entity.get("text", "")
                
                # Replace entity placeholders in response
                if entity_type == "date":
                    response = response.replace("[DATE]", entity_text)
                elif entity_type == "time":
                    response = response.replace("[TIME]", entity_text)
                elif entity_type == "number":
                    response = response.replace("[NUMBER]", str(entity_value))
                elif entity_type == "email":
                    response = response.replace("[EMAIL]", entity_text)
                elif entity_type == "phone":
                    response = response.replace("[PHONE]", entity_text)
                elif entity_type == "location":
                    response = response.replace("[LOCATION]", entity_text)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error customizing response with entities: {e}")
            return response
    
    def _adjust_tone(self, response: str, sentiment: str) -> str:
        """Adjust response tone based on sentiment"""
        try:
            if sentiment == "positive":
                # Add enthusiastic elements
                if not any(word in response.lower() for word in ["great", "wonderful", "amazing", "excellent"]):
                    response = response.replace("I'm here to help", "I'd be delighted to help")
                    response = response.replace("I can help", "I'd love to help")
            
            elif sentiment == "negative":
                # Add empathetic elements
                if not any(word in response.lower() for word in ["sorry", "apologize", "understand"]):
                    response = response.replace("I can help", "I understand this is frustrating, but I can help")
                    response = response.replace("Let me help", "I'm sorry to hear that. Let me help")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error adjusting tone: {e}")
            return response
    
    def _enhance_response_with_context(self, response: str, context: Optional[Dict[str, Any]]) -> str:
        """Enhance response with conversation context"""
        try:
            if not context:
                return response
            
            # Add previous context if available
            if "previous_messages" in context and len(context["previous_messages"]) > 0:
                # Reference previous conversation
                last_message = context["previous_messages"][-1].get("content", "")
                if len(last_message) > 0:
                    response = f"Regarding our previous conversation about {last_message[:50]}..., {response.lower()}"
            
            # Add user preferences if available
            if "user_preferences" in context:
                preferences = context["user_preferences"]
                if "name" in preferences:
                    response = response.replace("I'm here to help", f"Hi {preferences['name']}, I'm here to help")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error enhancing response with context: {e}")
            return response
    
    def _calculate_response_confidence(self, intent: str, sentiment: str, 
                                     entities: List[Dict[str, Any]], 
                                     context: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence score for the response"""
        try:
            confidence = 0.5  # Base confidence
            
            # Boost confidence for known intents
            if intent in self.response_templates:
                confidence += 0.3
            
            # Boost confidence for strong sentiment
            if sentiment in ["positive", "negative"]:
                confidence += 0.1
            
            # Boost confidence for entities
            if len(entities) > 0:
                confidence += 0.1
            
            # Boost confidence with context
            if context and "previous_messages" in context:
                confidence += 0.05
            
            # Cap at 1.0
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _determine_response_type(self, intent: str) -> str:
        """Determine the type of response"""
        response_types = {
            "greeting": "greeting",
            "goodbye": "farewell",
            "thanks": "acknowledgment",
            "help": "assistance",
            "information": "informative",
            "booking": "action",
            "complaint": "empathetic",
            "feedback": "appreciation",
            "pricing": "informative",
            "availability": "informative",
            "location": "informative",
            "contact": "informative",
            "account": "informative",
            "payment": "informative",
            "shipping": "informative",
            "return": "informative",
            "warranty": "informative",
            "technical": "assistance",
            "general": "conversational",
            "unknown": "clarification"
        }
        
        return response_types.get(intent, "conversational")
    
    async def generate_follow_up(self, user_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate follow-up question or suggestion"""
        try:
            if user_id not in self.user_profiles:
                return {
                    "follow_up": "Is there anything else I can help you with?",
                    "confidence": 0.5,
                    "type": "general"
                }
            
            user_profile = self.user_profiles[user_id]
            conversation_history = user_profile["conversation_history"]
            
            if not conversation_history:
                return {
                    "follow_up": "Is there anything else I can help you with?",
                    "confidence": 0.5,
                    "type": "general"
                }
            
            # Analyze conversation patterns
            last_intent = conversation_history[-1]["intent"]
            last_sentiment = conversation_history[-1]["sentiment"]
            
            # Generate context-aware follow-up
            follow_ups = {
                "complaint": [
                    "Would you like me to escalate this issue to a supervisor?",
                    "Is there anything else I can help you with regarding this problem?",
                    "Would you like me to provide additional information about our resolution process?"
                ],
                "booking": [
                    "Would you like me to send you a confirmation of your booking?",
                    "Is there anything else you'd like to know about your reservation?",
                    "Would you like me to help you with anything else related to your booking?"
                ],
                "information": [
                    "Does that information answer your question?",
                    "Would you like me to provide more details on any specific aspect?",
                    "Is there anything else you'd like to know about this topic?"
                ],
                "general": [
                    "Is there anything else I can help you with today?",
                    "Would you like assistance with anything else?",
                    "How else can I be of service to you?"
                ]
            }
            
            # Select appropriate follow-up
            if last_intent in follow_ups:
                follow_up = random.choice(follow_ups[last_intent])
            else:
                follow_up = random.choice(follow_ups["general"])
            
            return {
                "follow_up": follow_up,
                "confidence": 0.7,
                "type": "follow_up",
                "context": {
                    "last_intent": last_intent,
                    "last_sentiment": last_sentiment
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating follow-up: {e}")
            return {
                "follow_up": "Is there anything else I can help you with?",
                "confidence": 0.5,
                "type": "general"
            }
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get user insights based on conversation history"""
        try:
            if user_id not in self.user_profiles:
                return {"error": "User not found"}
            
            user_profile = self.user_profiles[user_id]
            conversation_history = user_profile["conversation_history"]
            
            if not conversation_history:
                return {"error": "No conversation history available"}
            
            # Analyze patterns
            intents = [conv["intent"] for conv in conversation_history]
            sentiments = [conv["sentiment"] for conv in conversation_history]
            
            # Calculate statistics
            intent_frequency = {}
            for intent in intents:
                intent_frequency[intent] = intent_frequency.get(intent, 0) + 1
            
            sentiment_frequency = {}
            for sentiment in sentiments:
                sentiment_frequency[sentiment] = sentiment_frequency.get(sentiment, 0) + 1
            
            # Get most common intent and sentiment
            most_common_intent = max(intent_frequency, key=intent_frequency.get)
            most_common_sentiment = max(sentiment_frequency, key=sentiment_frequency.get)
            
            return {
                "user_id": user_id,
                "total_conversations": len(conversation_history),
                "most_common_intent": most_common_intent,
                "intent_frequency": intent_frequency,
                "most_common_sentiment": most_common_sentiment,
                "sentiment_frequency": sentiment_frequency,
                "preferences": user_profile.get("preferences", {}),
                "last_conversation": conversation_history[-1] if conversation_history else None,
                "insights": {
                    "engagement_level": "high" if len(conversation_history) > 5 else "medium" if len(conversation_history) > 2 else "low",
                    "satisfaction_trend": "improving" if sentiment_frequency.get("positive", 0) > sentiment_frequency.get("negative", 0) else "declining",
                    "primary_needs": [most_common_intent]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user insights: {e}")
            return {"error": str(e)}
    
    async def get_conversation_history(self, conversation_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conversation history for analysis"""
        try:
            # In a real implementation, this would fetch from a database
            # For now, return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def generate_suggestions(self, user_id: str, conversation_id: str,
                                 conversation_history: List[Dict[str, Any]],
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate conversation suggestions"""
        try:
            suggestions = []
            
            # Analyze conversation context
            if conversation_history:
                last_intent = conversation_history[-1].get("intent", "general")
                last_sentiment = conversation_history[-1].get("sentiment", "neutral")
                
                # Generate context-aware suggestions
                if last_intent == "complaint":
                    suggestions = [
                        "Would you like me to escalate this issue?",
                        "Can I provide more information about our resolution process?",
                        "Would you like to speak with a supervisor?"
                    ]
                elif last_intent == "information":
                    suggestions = [
                        "Would you like more details on this topic?",
                        "Is there anything specific you'd like to know?",
                        "Can I help you with related information?"
                    ]
                elif last_intent == "booking":
                    suggestions = [
                        "Would you like a confirmation of your booking?",
                        "Can I help you modify your reservation?",
                        "Would you like information about nearby services?"
                    ]
                else:
                    suggestions = [
                        "Is there anything else I can help you with?",
                        "Would you like assistance with something else?",
                        "Can I provide information about other services?"
                    ]
            else:
                # Default suggestions for new conversations
                suggestions = [
                    "How can I help you today?",
                    "What would you like to discuss?",
                    "Is there something specific you need assistance with?"
                ]
            
            # Filter and prioritize suggestions based on user preferences
            if user_id and user_id in self.user_profiles:
                user_preferences = self.user_profiles[user_id].get("preferences", {})
                if user_preferences.get("suggestion_style") == "concise":
                    suggestions = suggestions[:2]  # Limit to 2 suggestions
            
            return {
                "suggestions": suggestions[:3],  # Return top 3 suggestions
                "confidence": 0.8,
                "context": {
                    "last_intent": last_intent if conversation_history else None,
                    "conversation_length": len(conversation_history),
                    "user_id": user_id
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}")
            return {
                "suggestions": ["Is there anything else I can help you with?"],
                "confidence": 0.5,
                "context": {}
            }
    
    async def analyze_conversation(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of entire conversation"""
        try:
            if not conversation_history:
                return {
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "scores": {"positive": 0.0, "negative": 0.0, "neutral": 1.0},
                    "emotions": {},
                    "trend": "stable"
                }
            
            # Calculate overall sentiment scores
            positive_count = sum(1 for conv in conversation_history if conv.get("sentiment") == "positive")
            negative_count = sum(1 for conv in conversation_history if conv.get("sentiment") == "negative")
            neutral_count = sum(1 for conv in conversation_history if conv.get("sentiment") == "neutral")
            
            total_messages = len(conversation_history)
            positive_score = positive_count / total_messages
            negative_score = negative_count / total_messages
            neutral_score = neutral_count / total_messages
            
            # Determine overall sentiment
            if positive_score > negative_score and positive_score > neutral_score:
                overall_sentiment = "positive"
            elif negative_score > positive_score and negative_score > neutral_score:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            # Calculate trend
            if total_messages >= 3:
                recent_half = conversation_history[total_messages//2:]
                recent_positive = sum(1 for conv in recent_half if conv.get("sentiment") == "positive")
                recent_negative = sum(1 for conv in recent_half if conv.get("sentiment") == "negative")
                
                if recent_positive > recent_negative:
                    trend = "improving"
                elif recent_negative > recent_positive:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Extract emotions (simplified)
            emotions = {}
            for conv in conversation_history:
                sentiment = conv.get("sentiment", "neutral")
                if sentiment == "positive":
                    emotions["happy"] = emotions.get("happy", 0) + 1
                    emotions["satisfied"] = emotions.get("satisfied", 0) + 1
                elif sentiment == "negative":
                    emotions["frustrated"] = emotions.get("frustrated", 0) + 1
                    emotions["disappointed"] = emotions.get("disappointed", 0) + 1
                else:
                    emotions["neutral"] = emotions.get("neutral", 0) + 1
            
            # Normalize emotion scores
            total_emotions = sum(emotions.values())
            if total_emotions > 0:
                emotions = {k: v/total_emotions for k, v in emotions.items()}
            
            # Calculate confidence based on conversation length and sentiment consistency
            confidence = min(0.9, total_messages * 0.1)  # More messages = higher confidence
            
            return {
                "sentiment": overall_sentiment,
                "confidence": confidence,
                "scores": {
                    "positive": positive_score,
                    "negative": negative_score,
                    "neutral": neutral_score
                },
                "emotions": emotions,
                "trend": trend,
                "metadata": {
                    "total_messages": total_messages,
                    "positive_messages": positive_count,
                    "negative_messages": negative_count,
                    "neutral_messages": neutral_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing conversation: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "scores": {"positive": 0.0, "negative": 0.0, "neutral": 1.0},
                "emotions": {},
                "trend": "stable"
            }
    
    async def generate_summary(self, conversation_history: List[Dict[str, Any]],
                             conversation_id: str) -> Dict[str, Any]:
        """Generate conversation summary"""
        try:
            if not conversation_history:
                return {
                    "summary": "No conversation data available.",
                    "key_points": [],
                    "topics": [],
                    "sentiment_trend": "neutral",
                    "duration": 0,
                    "message_count": 0,
                    "metadata": {}
                }
            
            # Extract key topics from intents
            intents = [conv.get("intent", "general") for conv in conversation_history]
            unique_intents = list(set(intents))
            
            # Generate summary based on conversation content
            if "complaint" in unique_intents:
                summary_type = "issue_resolution"
                summary = "This conversation focused on resolving a customer issue."
            elif "booking" in unique_intents:
                summary_type = "reservation"
                summary = "This conversation involved making a reservation."
            elif "information" in unique_intents:
                summary_type = "information_request"
                summary = "This conversation provided information to the customer."
            else:
                summary_type = "general"
                summary = "This was a general customer service conversation."
            
            # Extract key points
            key_points = []
            for conv in conversation_history[:5]:  # Consider first 5 messages
                intent = conv.get("intent", "general")
                if intent in ["complaint", "booking", "information"]:
                    key_points.append(f"Discussed {intent} related topic")
            
            # Calculate sentiment trend
            sentiment_analysis = await self.analyze_conversation(conversation_history)
            sentiment_trend = sentiment_analysis.get("trend", "neutral")
            
            # Calculate duration (simplified - using message count as proxy)
            duration = len(conversation_history) * 30  # Assume 30 seconds per message
            
            return {
                "summary": summary,
                "key_points": key_points[:3],  # Limit to 3 key points
                "topics": unique_intents[:5],  # Limit to 5 topics
                "sentiment_trend": sentiment_trend,
                "duration": duration,
                "message_count": len(conversation_history),
                "metadata": {
                    "summary_type": summary_type,
                    "conversation_id": conversation_id,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return {
                "summary": "Unable to generate summary at this time.",
                "key_points": [],
                "topics": [],
                "sentiment_trend": "neutral",
                "duration": 0,
                "message_count": len(conversation_history),
                "metadata": {"error": str(e)}
            }