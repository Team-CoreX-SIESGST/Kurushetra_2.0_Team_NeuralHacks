import { apiClient } from "@/helper/commonHelper";
import { uploadFile } from "@/services/files/fileServices";
import { performAISearch, performSimpleSearch } from "@/services/ai/searchServices";
import { processSingleDocument, generateBasicSummary } from "@/services/ai/documentServices";

// ========================================================================================
// CHAT SESSION MANAGEMENT
// ========================================================================================

/**
 * Create a new chat session/conversation
 * @param {Object} sessionData
 * @param {string} sessionData.title - Session title
 * @param {string} [sessionData.workspace_id] - Optional workspace ID
 */
export const createChatSession = async (sessionData) => {
  // Since your backend doesn't have sessions yet, we'll simulate with localStorage
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const session = {
    _id: sessionId,
    title: sessionData.title,
    workspace_id: sessionData.workspace_id || 'default',
    created_at: new Date().toISOString(),
    messages: []
  };
  
  // Store in localStorage for now
  const existingSessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  existingSessions.unshift(session);
  localStorage.setItem('chat_sessions', JSON.stringify(existingSessions));
  
  return { data: session };
};

/**
 * Get all chat sessions for the user
 */
export const getChatSessions = () => {
  const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  return { data: { data: sessions } };
};

/**
 * Get a specific chat session with its messages
 * @param {string} sessionId - Session identifier
 */
export const getChatSession = (sessionId) => {
  const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  const session = sessions.find(s => s._id === sessionId);
  return { data: { data: { chats: session?.messages || [] } } };
};

/**
 * Update session title
 * @param {string} sessionId - Session identifier
 * @param {Object} payload
 * @param {string} payload.title - New title
 */
export const updateSessionTitle = (sessionId, payload) => {
  const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  const sessionIndex = sessions.findIndex(s => s._id === sessionId);
  
  if (sessionIndex !== -1) {
    sessions[sessionIndex].title = payload.title;
    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    return { data: { data: sessions[sessionIndex] } };
  }
  
  throw new Error('Session not found');
};

/**
 * Delete a chat session
 * @param {string} sessionId - Session identifier
 */
export const deleteChatSession = (sessionId) => {
  const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  const filteredSessions = sessions.filter(s => s._id !== sessionId);
  localStorage.setItem('chat_sessions', JSON.stringify(filteredSessions));
  return { data: { success: true } };
};

// ========================================================================================
// MESSAGE HANDLING WITH AI INTEGRATION
// ========================================================================================

/**
 * Send a message and get AI response
 * @param {string} sessionId - Session identifier
 * @param {Object} messageData
 * @param {string} messageData.message - User message
 * @param {File[]} [messageData.files] - Optional attached files
 * @param {string} [messageData.workspace_id] - Workspace identifier
 */
export const sendMessage = async (sessionId, messageData) => {
  try {
    const { message, files, workspace_id = 'default' } = messageData;
    
    // Get current session
    const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
    const sessionIndex = sessions.findIndex(s => s._id === sessionId);
    
    if (sessionIndex === -1) {
      throw new Error('Session not found');
    }
    
    // Create user message
    const userMessage = {
      _id: `msg_${Date.now()}_user`,
      message,
      isUser: true,
      createdAt: new Date().toISOString(),
      files: files ? files.map(f => ({ name: f.name, size: f.size, type: f.type })) : []
    };
    
    // Add user message to session
    sessions[sessionIndex].messages.push(userMessage);
    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    
    // Process files if any
    let fileProcessingResults = [];
    if (files && files.length > 0) {
      for (const file of files) {
        try {
          // Upload file first
          const uploadResult = await uploadFile(file, workspace_id);
          
          // Process document for AI analysis
          const processResult = await generateBasicSummary(file);
          
          fileProcessingResults.push({
            file: file.name,
            upload: uploadResult.data,
            analysis: processResult.data
          });
        } catch (error) {
          console.error(`Error processing file ${file.name}:`, error);
          fileProcessingResults.push({
            file: file.name,
            error: error.message
          });
        }
      }
    }
    
    // Generate AI response
    let aiResponse;
    try {
      // Determine if this is a search query or general chat
      const isSearchQuery = message.toLowerCase().includes('search') || 
                           message.toLowerCase().includes('find') ||
                           message.toLowerCase().includes('what') ||
                           message.toLowerCase().includes('how') ||
                           files && files.length > 0;
      
      if (isSearchQuery) {
        // Use AI search for queries
        const searchResult = await performAISearch({
          workspace_id,
          query: message,
          top_k: 5,
          include_web: true,
          summarize: true
        });
        
        aiResponse = searchResult.data.answer;
      } else {
        // Use simple search for general chat
        const simpleResult = await performSimpleSearch(workspace_id, message);
        aiResponse = simpleResult.data.answer;
      }
    } catch (error) {
      console.error('AI response error:', error);
      aiResponse = "I'm sorry, I encountered an issue processing your request. Please try again.";
    }
    
    // Enhance AI response with file processing results
    if (fileProcessingResults.length > 0) {
      aiResponse += "\n\n📁 **File Analysis:**\n";
      fileProcessingResults.forEach(result => {
        if (result.error) {
          aiResponse += `- ${result.file}: Error - ${result.error}\n`;
        } else if (result.analysis && result.analysis.data) {
          const summary = result.analysis.data.summary || 'File processed successfully';
          aiResponse += `- ${result.file}: ${summary}\n`;
        }
      });
    }
    
    // Create AI message
    const aiMessage = {
      _id: `msg_${Date.now()}_ai`,
      message: aiResponse,
      isUser: false,
      createdAt: new Date().toISOString(),
      metadata: {
        filesProcessed: fileProcessingResults.length,
        processingResults: fileProcessingResults
      }
    };
    
    // Add AI message to session
    sessions[sessionIndex].messages.push(aiMessage);
    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    
    return {
      data: {
        data: {
          aiMessage,
          userMessage,
          fileResults: fileProcessingResults
        }
      }
    };
    
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

// ========================================================================================
// BACKWARD COMPATIBILITY ALIASES
// ========================================================================================

// For backward compatibility with existing components
export const createSection = createChatSession;
export const getSections = getChatSessions;
export const getSection = getChatSession;
export const updateSectionTitle = updateSessionTitle;
export const deleteSection = deleteChatSession;

// ========================================================================================
// UTILITY FUNCTIONS
// ========================================================================================

/**
 * Get chat statistics
 * @param {string} workspaceId - Workspace identifier
 */
export const getChatStats = (workspaceId = 'default') => {
  const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  const workspaceSessions = sessions.filter(s => s.workspace_id === workspaceId);
  
  const totalMessages = workspaceSessions.reduce((sum, session) => sum + session.messages.length, 0);
  const userMessages = workspaceSessions.reduce((sum, session) => 
    sum + session.messages.filter(m => m.isUser).length, 0
  );
  
  return {
    data: {
      totalSessions: workspaceSessions.length,
      totalMessages,
      userMessages,
      aiMessages: totalMessages - userMessages,
      workspace_id: workspaceId
    }
  };
};

/**
 * Search through chat history
 * @param {string} query - Search query
 * @param {string} [workspaceId] - Optional workspace filter
 */
export const searchChatHistory = (query, workspaceId = null) => {
  const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
  const filteredSessions = workspaceId ? 
    sessions.filter(s => s.workspace_id === workspaceId) : sessions;
  
  const results = [];
  const searchTerm = query.toLowerCase();
  
  filteredSessions.forEach(session => {
    session.messages.forEach(message => {
      if (message.message.toLowerCase().includes(searchTerm)) {
        results.push({
          sessionId: session._id,
          sessionTitle: session.title,
          message,
          relevance: message.message.toLowerCase().split(searchTerm).length - 1
        });
      }
    });
  });
  
  // Sort by relevance
  results.sort((a, b) => b.relevance - a.relevance);
  
  return { data: results };
};
