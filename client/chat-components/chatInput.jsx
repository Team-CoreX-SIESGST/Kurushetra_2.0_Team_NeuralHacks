// components/ChatInput.jsx
'use client'
import React, { useRef } from "react";
import { Paperclip, Send, X } from "lucide-react";

export const ChatInput = ({ 
  message, 
  setMessage, 
  files, 
  setFiles, 
  isLoading, 
  handleSubmit, 
  handleKeyDown 
}) => {
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

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

  const canSend = (message.trim() || files.length > 0) && !isLoading;

  return (
    <div className="border-t border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900">
      <div className="max-w-4xl mx-auto p-4">
        {/* File previews */}
        {files.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-2 bg-slate-100 dark:bg-slate-700 rounded-md px-3 py-2 text-sm"
              >
                <Paperclip className="h-3 w-3" />
                <span className="truncate max-w-32 text-slate-900 dark:text-white">{file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="h-5 w-5 p-0 hover:bg-red-500 hover:text-white rounded text-slate-500 dark:text-slate-400 transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input form */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="relative flex items-end gap-2 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-300 dark:border-slate-600 p-3 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-all">
            {/* File upload button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              className="h-8 w-8 p-0 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-md text-slate-500 dark:text-slate-400 transition-colors disabled:opacity-50"
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
              className="flex-1 min-h-8 max-h-48 resize-none border-0 bg-transparent p-0 focus:outline-none placeholder-slate-500 dark:placeholder-slate-400 text-slate-900 dark:text-white"
              rows={1}
            />

            {/* Send button */}
            <button
              type="submit"
              disabled={!canSend}
              className={`h-8 w-8 p-0 rounded-md transition-all ${
                canSend 
                  ? "bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-700 hover:to-cyan-700 text-white shadow-lg" 
                  : "bg-slate-300 dark:bg-slate-600 text-slate-500 dark:text-slate-400 cursor-not-allowed"
              }`}
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </form>

        {/* Disclaimer */}
        <p className="text-xs text-slate-600 dark:text-slate-400 text-center mt-2">
          ChatGPT can make mistakes. Check important info.
        </p>
      </div>
    </div>
  );
};