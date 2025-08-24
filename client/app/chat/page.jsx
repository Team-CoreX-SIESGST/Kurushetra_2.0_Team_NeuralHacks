"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send } from "lucide-react";

import { ChatInterface } from "@/chat-components/index";
import AuthRequired from "@/components/auth/AuthRequired";

// Animation variants
const FADE_IN_VARIANTS = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

// Skeleton Loader Component with Correct Colors
const ChatSkeleton = () => {
  return (
    <div className="flex h-screen bg-white dark:bg-slate-900">
      {/* Sidebar Skeleton */}
      <div className="w-80 bg-slate-50 dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="h-7 w-36 bg-slate-200 dark:bg-slate-700 rounded-md animate-pulse"></div>
          <div className="h-9 w-9 bg-slate-200 dark:bg-slate-700 rounded-full animate-pulse"></div>
        </div>
        
        {/* Search Bar */}
        <div className="mb-6">
          <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded-lg animate-pulse"></div>
        </div>
        
        {/* New Chat Button */}
        <div className="mb-6">
          <div className="h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg animate-pulse"></div>
        </div>
        
        {/* Conversation List */}
        <div className="mb-4">
          <div className="h-5 w-20 bg-slate-300 dark:bg-slate-600 rounded mb-4 animate-pulse"></div>
          {[1, 2, 3].map((item) => (
            <div key={item} className="flex items-center p-2 mb-2 rounded-lg">
              <div className="h-8 w-8 bg-slate-200 dark:bg-slate-700 rounded-full mr-3 animate-pulse"></div>
              <div className="flex-1">
                <div className="h-4 w-32 bg-slate-200 dark:bg-slate-700 rounded mb-1.5 animate-pulse"></div>
                <div className="h-3 w-40 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Main Chat Area Skeleton */}
      <div className="flex-1 flex flex-col">
        {/* Header Skeleton */}
        <div className="h-16 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6 bg-white dark:bg-slate-900">
          <div className="flex items-center">
            <div className="h-9 w-9 bg-slate-200 dark:bg-slate-700 rounded-full mr-3 animate-pulse"></div>
            <div className="h-5 w-28 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
          </div>
          <div className="flex space-x-2">
            <div className="h-9 w-9 bg-slate-200 dark:bg-slate-700 rounded-full animate-pulse"></div>
            <div className="h-9 w-9 bg-slate-200 dark:bg-slate-700 rounded-full animate-pulse"></div>
          </div>
        </div>
        
        {/* Messages Skeleton */}
        <div className="flex-1 p-6 overflow-y-auto bg-slate-50 dark:bg-slate-800/30">
          <div className="max-w-3xl mx-auto space-y-4">
            {/* AI Message */}
            <div className="flex justify-start">
              <div className="flex items-start space-x-3 max-w-md">
                <div className="h-8 w-8 bg-slate-300 dark:bg-slate-600 rounded-full animate-pulse flex-shrink-0"></div>
                <div className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-sm">
                  <div className="space-y-2">
                    <div className="h-4 w-64 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                    <div className="h-4 w-56 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                    <div className="h-4 w-60 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* User Message */}
            <div className="flex justify-end">
              <div className="flex items-start space-x-3 max-w-md">
                <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-2xl p-4 shadow-sm">
                  <div className="space-y-2">
                    <div className="h-4 w-52 bg-indigo-200 dark:bg-indigo-700/50 rounded animate-pulse"></div>
                    <div className="h-4 w-48 bg-indigo-200 dark:bg-indigo-700/50 rounded animate-pulse"></div>
                  </div>
                </div>
                <div className="h-8 w-8 bg-slate-300 dark:bg-slate-600 rounded-full animate-pulse flex-shrink-0"></div>
              </div>
            </div>
            
            {/* AI Message */}
            <div className="flex justify-start">
              <div className="flex items-start space-x-3 max-w-md">
                <div className="h-8 w-8 bg-slate-300 dark:bg-slate-600 rounded-full animate-pulse flex-shrink-0"></div>
                <div className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-sm">
                  <div className="space-y-2">
                    <div className="h-4 w-72 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                    <div className="h-4 w-60 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Input Area Skeleton */}
        <div className="border-t border-slate-200 dark:border-slate-700 p-4 bg-white dark:bg-slate-900">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center space-x-2 mb-2">
              <div className="h-9 w-9 bg-slate-200 dark:bg-slate-700 rounded-full animate-pulse"></div>
              <div className="h-9 w-9 bg-slate-200 dark:bg-slate-700 rounded-full animate-pulse"></div>
              <div className="h-9 w-9 bg-slate-200 dark:bg-slate-700 rounded-full animate-pulse"></div>
            </div>
            <div className="flex items-end space-x-3">
              <div className="flex-1 h-12 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse"></div>
              <div className="h-12 w-12 bg-indigo-200 dark:bg-indigo-700 rounded-xl animate-pulse flex items-center justify-center">
                <Send className="h-5 w-5 text-indigo-600 dark:text-indigo-300 opacity-50" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = () => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("refresh_token");
        setIsAuthenticated(!!token);
      }
      setIsLoading(false);
    };

    // Simulate a slight delay for better UX
    const timer = setTimeout(checkAuth, 1200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      <AnimatePresence mode="wait">
        {/* 1. Skeleton loader while checking authentication */}
        {isLoading && (
          <motion.div
            key="skeleton"
            variants={FADE_IN_VARIANTS}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <ChatSkeleton />
          </motion.div>
        )}

        {/* 2. Show AuthRequired if not authenticated */}
        {!isLoading && !isAuthenticated && (
          <motion.div
            key="auth-required"
            variants={FADE_IN_VARIANTS}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <AuthRequired />
          </motion.div>
        )}

        {/* 3. Render chat interface if authenticated */}
        {!isLoading && isAuthenticated && (
          <motion.div
            key="chat-interface"
            variants={FADE_IN_VARIANTS}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <ChatInterface
              isSidebarOpen={isSidebarOpen}
              setIsSidebarOpen={setIsSidebarOpen}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}