"use client";

import { useState, useEffect } from "react";
import {
  Loader2,
} from "lucide-react";

import { ChatInterface } from "@/chat-components/index";
import AuthRequired from "@/components/auth/AuthRequired";

// Main Page Component
export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on component mount
  useEffect(() => {
    const checkAuth = () => {
      // Check if we're in a browser environment
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('refresh_token');
        setIsAuthenticated(!!token);
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white dark:bg-slate-900 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600 mb-4" />
          <p className="text-slate-600 dark:text-slate-400">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Show AuthRequired component if not authenticated
  if (!isAuthenticated) {
    return <AuthRequired />;
  }

  // Render the chat interface if authenticated
  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      <ChatInterface
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
      />
    </div>
  );
}