// components/ChatMessage.jsx
'use client'
import React from "react";
import { User, Bot, Copy, ThumbsUp, ThumbsDown, RefreshCw } from "lucide-react";

export const ChatMessage = ({ 
  message, 
  isLoading = false, 
  handleCopy, 
  copiedMessageId 
}) => {
  const isUser = message.role === "user";
  
  return (
    <div className={`group flex gap-4 p-6 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50 ${
      isUser ? "bg-transparent" : "bg-slate-50/50 dark:bg-slate-800/30"
    }`}>
      {/* Avatar */}
      <div className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md ${
        isUser 
          ? "bg-gradient-to-r from-indigo-600 to-cyan-600 text-white" 
          : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
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
              <RefreshCw className="h-4 w-4 animate-spin text-indigo-600" />
              <span className="text-slate-600 dark:text-slate-400">Thinking...</span>
            </div>
          ) : (
            <p className="whitespace-pre-wrap leading-relaxed text-slate-900 dark:text-white">
              {message.content}
            </p>
          )}
        </div>

        {/* Actions - Only show for assistant messages */}
        {!isUser && !isLoading && (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => handleCopy(message.id, message.content)}
              className="h-8 px-2 text-xs text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-md transition-colors flex items-center gap-1"
            >
              <Copy className="h-3 w-3" />
              {copiedMessageId === message.id ? "Copied!" : "Copy"}
            </button>
            
            <button className="h-8 px-2 text-xs text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-md transition-colors flex items-center gap-1">
              <ThumbsUp className="h-3 w-3" />
            </button>
            
            <button className="h-8 px-2 text-xs text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-md transition-colors flex items-center gap-1">
              <ThumbsDown className="h-3 w-3" />
            </button>
            
            <button className="h-8 px-2 text-xs text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-md transition-colors flex items-center gap-1">
              <RefreshCw className="h-3 w-3" />
              Regenerate
            </button>
          </div>
        )}

        {/* Timestamp */}
        <div className="text-xs text-slate-500 dark:text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">
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