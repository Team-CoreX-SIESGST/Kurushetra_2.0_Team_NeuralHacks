// components/ChatInterface.jsx
'use client'
import React, { useState, useRef, useEffect } from "react";
import { Menu } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { ChatArea } from "./ChatArea";
import { ChatInput } from "./ChatInput";

export const ChatInterface = () => {
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
  
  // Chat area state
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  
  // Input state
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState([]);
  
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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() || files.length > 0) {
      handleSendMessage(message.trim(), files);
      setMessage("");
      setFiles([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

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

  return (
    <div className="min-h-screen flex w-full bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Header with sidebar trigger */}
      <header className="fixed top-0 left-0 right-0 z-50 h-12 flex items-center bg-white/95 dark:bg-slate-900/95 border-b border-slate-200 dark:border-slate-700 backdrop-blur-sm">
        <button 
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="ml-4 p-2 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-xl transition-colors"
        >
          <Menu className="h-4 w-4 text-slate-700 dark:text-slate-300" />
        </button>
        <div className="flex-1 text-center">
          <h1 className="font-semibold bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-transparent">ChatGPT</h1>
        </div>
        <div className="w-12" />
      </header>

      <Sidebar 
        sidebarCollapsed={sidebarCollapsed}
        setSidebarCollapsed={setSidebarCollapsed}
        selectedChat={selectedChat}
        setSelectedChat={setSelectedChat}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
      />

      {/* Main chat area */}
      <main className="flex-1 flex flex-col pt-12">
        <ChatArea 
          messages={messages}
          isLoading={isLoading}
          handleCopy={handleCopy}
          copiedMessageId={copiedMessageId}
          setMessage={setMessage}
          containerRef={containerRef}
          messagesEndRef={messagesEndRef}
          showScrollButton={showScrollButton}
          scrollToBottom={scrollToBottom}
          handleScroll={handleScroll}
        />   
        <ChatInput 
          message={message}
          setMessage={setMessage}
          files={files}
          setFiles={setFiles}
          isLoading={isLoading}
          handleSubmit={handleSubmit}
          handleKeyDown={handleKeyDown}
        />
      </main>
    </div>
  );
};
