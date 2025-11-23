import express from 'express';
import { ConversationManager } from '../services/ConversationManager';
import { MessageManager } from '../services/MessageManager';
import axios from 'axios';

const router = express.Router();

// Get all conversations for a user
router.get('/conversations/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const conversations = await ConversationManager.findByUserId(userId);
    res.json(conversations);
  } catch (error) {
    console.error('Error fetching conversations:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get conversation details
router.get('/conversations/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const conversation = await ConversationManager.findById(id);
    
    if (!conversation) {
      return res.status(404).json({ error: 'Conversation not found' });
    }

    res.json(conversation);
  } catch (error) {
    console.error('Error fetching conversation details:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new conversation
router.post('/conversations', async (req, res) => {
  try {
    const { userId, title, metadata } = req.body;
    
    const conversation = await ConversationManager.create({
      userId,
      title,
      metadata
    });

    res.status(201).json(conversation);
  } catch (error) {
    console.error('Error creating conversation:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get messages for a conversation
router.get('/messages/:conversationId', async (req, res) => {
  try {
    const { conversationId } = req.params;
    const messages = await MessageManager.findByConversationId(conversationId);
    res.json(messages);
  } catch (error) {
    console.error('Error fetching messages:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create message
router.post('/messages', async (req, res) => {
  try {
    const { conversationId, senderId, content, messageType, attachments } = req.body;
    
    const message = await MessageManager.createMessage({
      conversationId,
      senderId,
      content,
      messageType,
      attachments: attachments || []
    });

    res.status(201).json(message);
  } catch (error) {
    console.error('Error creating message:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update conversation status
router.patch('/conversations/:id/status', async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    
    await ConversationManager.updateStatus(id, status);
    
    res.json({ message: 'Conversation status updated successfully' });
  } catch (error) {
    console.error('Error updating conversation status:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Generate AI response
router.post('/ai/generate-response', async (req, res) => {
  try {
    const { conversationId, message, userId, context = {} } = req.body;
    
    // Call AI service to generate response
    const aiResponse = await axios.post('http://localhost:3007/api/generate-response', {
      conversationId,
      message,
      userId,
      context
    }, {
      timeout: 10000 // 10 second timeout
    });

    // Save AI response to database
    const aiMessage = await MessageManager.createMessage({
      conversationId,
      senderId: 'ai',
      content: aiResponse.data.response,
      messageType: 'ai',
      attachments: aiResponse.data.attachments || []
    });

    res.json({
      response: aiResponse.data.response,
      messageId: aiMessage.id,
      confidence: aiResponse.data.confidence,
      suggestions: aiResponse.data.suggestions || []
    });
  } catch (error) {
    console.error('Error generating AI response:', error);
    
    // Fallback response if AI service is unavailable
    const fallbackResponse = "I apologize, but I'm having trouble responding right now. Please try again later.";
    
    // Save fallback response
    if (req.body.conversationId) {
      await MessageManager.createMessage({
        conversationId: req.body.conversationId,
        senderId: 'ai',
        content: fallbackResponse,
        messageType: 'ai',
        attachments: []
      });
    }
    
    res.status(500).json({
      response: fallbackResponse,
      error: 'AI service unavailable',
      fallback: true
    });
  }
});

// Get AI conversation suggestions
router.post('/ai/suggestions', async (req, res) => {
  try {
    const { conversationId, userId, context = {} } = req.body;
    
    const response = await axios.post('http://localhost:3007/api/suggestions', {
      conversationId,
      userId,
      context
    }, {
      timeout: 5000 // 5 second timeout
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error getting AI suggestions:', error);
    res.json({ suggestions: [] });
  }
});

// Analyze conversation sentiment
router.post('/ai/analyze-sentiment', async (req, res) => {
  try {
    const { conversationId } = req.body;
    
    const response = await axios.post('http://localhost:3007/api/analyze-sentiment', {
      conversationId
    }, {
      timeout: 5000 // 5 second timeout
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    res.json({ sentiment: 'neutral', confidence: 0 });
  }
});

// Get conversation summary
router.post('/ai/summary', async (req, res) => {
  try {
    const { conversationId } = req.body;
    
    const response = await axios.post('http://localhost:3007/api/summary', {
      conversationId
    }, {
      timeout: 10000 // 10 second timeout
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error generating summary:', error);
    res.json({ summary: 'Unable to generate summary at this time.' });
  }
});

export { router as chatRoutes };