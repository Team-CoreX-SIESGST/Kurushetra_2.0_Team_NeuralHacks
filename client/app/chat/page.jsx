'use client'
import React, { useState, useRef, useEffect } from "react";
import { 
  Menu, 
  MessageSquare, 
  Plus, 
  Search, 
  MoreHorizontal, 
  Edit3, 
  Trash2,
  ArrowDown,
  User,
  Bot,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Send,
  Paperclip,
  X
} from "lucide-react";

const mockConversations = [
  {
    id: "1",
    title: "React Components Help",
    timestamp: "2 hours ago",
    preview: "How do I create a reusable button component in React?"
  },
  {
    id: "2", 
    title: "TypeScript Interfaces",
    timestamp: "1 day ago",
    preview: "What's the difference between interface and type in TypeScript?"
  },
  {
    id: "3",
    title: "API Integration",
    timestamp: "3 days ago", 
    preview: "Best practices for handling API responses in React"
  },
  {
    id: "4",
    title: "Tailwind CSS Grid",
    timestamp: "1 week ago",
    preview: "How to create responsive layouts with CSS Grid in Tailwind"
  }
];

const ChatInterface = () => {
  // Chat state
  const [messages, setMessages] = useState([
    {
      id: "1",
      content: "Hello! I'm ChatGPT, your AI assistant. How can I help you today?",
      role: "assistant",
      timestamp: new Date(Date.now() - 60000)
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Sidebar state
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedChat, setSelectedChat] = useState("1");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(null);
  
  // Chat area state
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  
  // Input state
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  
  // Message actions state
  const [copiedMessageId, setCopiedMessageId] = useState(null);

  const handleSendMessage = async (content, files = []) => {
    try {
      // Add user message
      const userMessage = {
        id: Date.now().toString(),
        content,
        role: "user",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      // Simulate AI response
      setTimeout(() => {
        const aiMessage = {
          id: (Date.now() + 1).toString(),
          content: `I received your message: "${content}"${files?.length ? ` along with ${files.length} file(s)` : ''}. This is a demo response. In a real implementation, this would be connected to an AI service like OpenAI's API.`,
          role: "assistant",
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setIsLoading(false);
      }, 1500);
    } catch (error) {
      console.error("Error sending message:", error);
      setIsLoading(false);
    }
  };

  // Chat area functions
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleScroll = () => {
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 100;
      setShowScrollButton(!isAtBottom && messages.length > 3);
    }
  };

  // Input functions
  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() || files.length > 0) {
      handleSendMessage(message.trim(), files);
      setMessage("");
      setFiles([]);
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileSelect = (e) => {
    try {
      const selectedFiles = Array.from(e.target.files || []);
      setFiles(prev => [...prev, ...selectedFiles]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Error handling file selection:", error);
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleTextareaChange = (e) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
  };

  // Message functions
  const handleCopy = async (messageId, content) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (error) {
      console.error("Failed to copy text:", error);
    }
  };

  // Effects
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener("scroll", handleScroll);
      return () => container.removeEventListener("scroll", handleScroll);
    }
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownOpen && !e.target.closest('.dropdown-container')) {
        setDropdownOpen(null);
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [dropdownOpen]);

  // Computed values
  const canSend = (message.trim() || files.length > 0) && !isLoading;
  const filteredConversations = mockConversations.filter(conv =>
    conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.preview.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Sidebar component
  const Sidebar = () => (
    <div className={`${sidebarCollapsed ? 'w-16' : 'w-80'} bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300`}>
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        {!sidebarCollapsed && (
          <div className="space-y-3">
            <button className="w-full flex items-center justify-start gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              <Plus className="h-4 w-4" />
              New Chat
            </button>
            
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
            </div>
          </div>
        )}
        
        {sidebarCollapsed && (
          <button className="w-full p-2 text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl transition-all duration-200 shadow-lg">
            <Plus className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto">
        {!sidebarCollapsed && (
          <div className="px-4 py-2 text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wider">
            Recent Conversations
          </div>
        )}
        
        <div className="px-2 space-y-1">
          {filteredConversations.map((conversation) => (
            <div key={conversation.id} className="relative group dropdown-container">
              <div
                onClick={() => setSelectedChat(conversation.id)}
                className={`w-full p-3 text-left transition-all hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg cursor-pointer ${
                  selectedChat === conversation.id ? "bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 border-l-4 border-blue-500" : ""
                }`}
              >
                <div className="flex items-start gap-3">
                  <MessageSquare className="h-4 w-4 mt-1 flex-shrink-0 text-blue-600 dark:text-blue-400" />
                  
                  {!sidebarCollapsed && (
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-sm text-gray-900 dark:text-white truncate">
                          {conversation.title}
                        </h4>
                        
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setDropdownOpen(dropdownOpen === conversation.id ? null : conversation.id);
                            }}
                            className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
                          >
                            <MoreHorizontal className="h-3 w-3" />
                          </button>
                          
                          {dropdownOpen === conversation.id && (
                            <div className="absolute right-0 top-8 w-36 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-2xl z-10">
                              <button className="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 flex items-center gap-2 rounded-t-xl">
                                <Edit3 className="h-4 w-4" />
                                Rename
                              </button>
                              <button className="w-full px-3 py-2 text-sm text-left text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2 rounded-b-xl">
                                <Trash2 className="h-4 w-4" />
                                Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-xs text-gray-600 dark:text-gray-300 truncate mt-1">
                        {conversation.preview}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {conversation.timestamp}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Chat message component
  const ChatMessage = ({ message, isLoading = false }) => {
    const isUser = message.role === "user";
    
    return (
      <div className={`group flex gap-4 p-6 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50 ${
        isUser ? "bg-transparent" : "bg-gray-50/50 dark:bg-gray-800/30"
      }`}>
        {/* Avatar */}
        <div className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md ${
          isUser 
            ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white" 
            : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
        }`}>
          {isUser ? (
            <User className="h-4 w-4" />
          ) : (
            <Bot className="h-4 w-4" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-2 overflow-hidden">
          <div className="prose max-w-none">
            {isLoading ? (
              <div className="flex items-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin text-blue-600" />
                <span className="text-gray-600 dark:text-gray-400">Thinking...</span>
              </div>
            ) : (
              <p className="whitespace-pre-wrap leading-relaxed text-gray-900 dark:text-white">
                {message.content}
              </p>
            )}
          </div>

          {/* Actions - Only show for assistant messages */}
          {!isUser && !isLoading && (
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => handleCopy(message.id, message.content)}
                className="h-8 px-2 text-xs text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors flex items-center gap-1"
              >
                <Copy className="h-3 w-3" />
                {copiedMessageId === message.id ? "Copied!" : "Copy"}
              </button>
              
              <button className="h-8 px-2 text-xs text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors flex items-center gap-1">
                <ThumbsUp className="h-3 w-3" />
              </button>
              
              <button className="h-8 px-2 text-xs text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors flex items-center gap-1">
                <ThumbsDown className="h-3 w-3" />
              </button>
              
              <button className="h-8 px-2 text-xs text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors flex items-center gap-1">
                <RefreshCw className="h-3 w-3" />
                Regenerate
              </button>
            </div>
          )}

          {/* Timestamp */}
          <div className="text-xs text-gray-500 dark:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
            {message.timestamp.toLocaleTimeString('en-US', { 
              hour12: true,
              hour: 'numeric',
              minute: '2-digit',
              second: '2-digit'
            })}
          </div>
        </div>
      </div>
    );
  };

  // Chat area component
  const ChatArea = () => {
    if (messages.length === 0) {
      return (
        <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
          <div className="text-center space-y-4 max-w-md">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto shadow-2xl">
              <span className="text-2xl text-white">💬</span>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
              How can I help you today?
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Start a conversation by typing a message below.
            </p>
            
            {/* Suggested prompts */}
            <div className="grid grid-cols-1 gap-2 mt-6">
              {[
                "Explain React hooks",
                "Help me debug TypeScript errors",
                "Write a Python function",
                "Design patterns in JavaScript"
              ].map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setMessage(prompt)}
                  className="text-left h-auto p-3 whitespace-normal bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600 text-gray-900 dark:text-white transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="flex-1 relative">
        <div
          ref={containerRef}
          className="h-full overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
          onScroll={handleScroll}
        >
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            
            {isLoading && (
              <ChatMessage
                message={{
                  id: "loading",
                  content: "",
                  role: "assistant",
                  timestamp: new Date()
                }}
                isLoading={true}
              />
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Scroll to bottom button */}
        {showScrollButton && (
          <button
            onClick={scrollToBottom}
            className="fixed bottom-24 left-1/2 transform -translate-x-1/2 z-10 w-10 h-10 rounded-full shadow-lg transition-all bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
          >
            <ArrowDown className="h-4 w-4 mx-auto" />
          </button>
        )}
      </div>
    );
  };

  // Chat input component
  const ChatInput = () => {
    return (
      <div className="border-t border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800">
        <div className="max-w-4xl mx-auto p-4">
          {/* File previews */}
          {files.length > 0 && (
            <div className="mb-3 flex flex-wrap gap-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-md px-3 py-2 text-sm"
                >
                  <Paperclip className="h-3 w-3" />
                  <span className="truncate max-w-32 text-gray-900 dark:text-white">{file.name}</span>
                  <button
                    onClick={() => removeFile(index)}
                    className="h-5 w-5 p-0 hover:bg-red-500 hover:text-white rounded text-gray-500 dark:text-gray-400 transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Input form */}
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative flex items-end gap-2 bg-gray-50 dark:bg-gray-700 rounded-xl border border-gray-300 dark:border-gray-600 p-3 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
              {/* File upload button */}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
                className="h-8 w-8 p-0 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md text-gray-500 dark:text-gray-400 transition-colors disabled:opacity-50"
              >
                <Paperclip className="h-4 w-4" />
              </button>
              
              <input
                ref={fileInputRef}
                type="file"
                multiple
                className="hidden"
                onChange={handleFileSelect}
                accept="image/*,.pdf,.doc,.docx,.txt"
              />

              {/* Message textarea */}
              <textarea
                ref={textareaRef}
                value={message}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                placeholder="Message ChatGPT..."
                disabled={isLoading}
                className="flex-1 min-h-8 max-h-48 resize-none border-0 bg-transparent p-0 focus:outline-none placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white"
                rows={1}
              />

              {/* Send button */}
              <button
                type="submit"
                disabled={!canSend}
                className={`h-8 w-8 p-0 rounded-md transition-all ${
                  canSend 
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg" 
                    : "bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                }`}
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </form>

          {/* Disclaimer */}
          <p className="text-xs text-gray-600 dark:text-gray-400 text-center mt-2">
            ChatGPT can make mistakes. Check important info.
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen flex w-full bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header with sidebar trigger */}
      <header className="fixed top-0 left-0 right-0 z-50 h-12 flex items-center bg-white/95 dark:bg-gray-800/95 border-b border-gray-200 dark:border-gray-700 backdrop-blur-sm">
        <button 
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="ml-4 p-2 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-xl transition-colors"
        >
          <Menu className="h-4 w-4 text-gray-700 dark:text-gray-300" />
        </button>
        <div className="flex-1 text-center">
          <h1 className="font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">ChatGPT</h1>
        </div>
        <div className="w-12" />
      </header>

      <Sidebar />

      {/* Main chat area */}
      <main className="flex-1 flex flex-col pt-12">
        <ChatArea />   
        <ChatInput />
      </main>
    </div>
  );
};

export default ChatInterface;