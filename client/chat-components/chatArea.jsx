// components/ChatArea.jsx
'use client'
import React, { useRef } from "react";
import { ArrowDown } from "lucide-react";
import { ChatMessage } from "./ChatMessage";

export const ChatArea = ({ 
  messages, 
  isLoading, 
  handleCopy, 
  copiedMessageId, 
  setMessage,
  containerRef,
  messagesEndRef,
  showScrollButton,
  scrollToBottom,
  handleScroll
}) => {
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
        <div className="text-center space-y-4 max-w-md">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-cyan-600 rounded-full flex items-center justify-center mx-auto shadow-2xl">
            <span className="text-2xl text-white">💬</span>
          </div>
          <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">
            How can I help you today?
          </h2>
          <p className="text-slate-600 dark:text-slate-300">
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
                className="text-left h-auto p-3 whitespace-normal bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:border-indigo-300 dark:hover:border-indigo-600 text-slate-900 dark:text-white transition-all duration-200 shadow-sm hover:shadow-md"
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
        className="h-full overflow-y-auto bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900"
        onScroll={handleScroll}
      >
        <div className="max-w-4xl mx-auto">
          {messages.map((message) => (
            <ChatMessage 
              key={message.id} 
              message={message} 
              handleCopy={handleCopy}
              copiedMessageId={copiedMessageId}
            />
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
          className="fixed bottom-24 left-1/2 transform -translate-x-1/2 z-10 w-10 h-10 rounded-full shadow-lg transition-all bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300"
        >
          <ArrowDown className="h-4 w-4 mx-auto" />
        </button>
      )}
    </div>
  );
};