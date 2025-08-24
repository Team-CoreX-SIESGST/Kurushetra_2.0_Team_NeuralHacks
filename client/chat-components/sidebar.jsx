// components/Sidebar.jsx
'use client'
import React, { useState } from "react";
import { 
  Menu, 
  MessageSquare, 
  Plus, 
  Search, 
  MoreHorizontal, 
  Edit3, 
  Trash2
} from "lucide-react";

const mockConversations = [
  {
    id: "1",
    title: "React Components Help",
    timestamp: "2 hours ago",
    preview: "How do I create a reusable button component in React?"
  },
  // ... other conversations
];

export const Sidebar = ({ 
  sidebarCollapsed, 
  setSidebarCollapsed, 
  selectedChat, 
  setSelectedChat,
  searchTerm,
  setSearchTerm 
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(null);

  const filteredConversations = mockConversations.filter(conv =>
    conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.preview.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className={`${sidebarCollapsed ? 'w-16' : 'w-80'} bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transition-all duration-300`}>
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        {!sidebarCollapsed && (
          <div className="space-y-3">
            <button className="w-full flex items-center justify-start gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-700 hover:to-cyan-700 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              <Plus className="h-4 w-4" />
              New Chat
            </button>
            
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
              />
            </div>
          </div>
        )}
        
        {sidebarCollapsed && (
          <button className="w-full p-2 text-white bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-700 hover:to-cyan-700 rounded-xl transition-all duration-200 shadow-lg">
            <Plus className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto">
        {!sidebarCollapsed && (
          <div className="px-4 py-2 text-xs font-medium text-slate-600 dark:text-slate-400 uppercase tracking-wider">
            Recent Conversations
          </div>
        )}
        
        <div className="px-2 space-y-1">
          {filteredConversations.map((conversation) => (
            <div key={conversation.id} className="relative group dropdown-container">
              <div
                onClick={() => setSelectedChat(conversation.id)}
                className={`w-full p-3 text-left transition-all hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg cursor-pointer ${
                  selectedChat === conversation.id ? "bg-gradient-to-r from-indigo-100 to-cyan-100 dark:from-indigo-900/30 dark:to-cyan-900/30 border-l-4 border-indigo-500" : ""
                }`}
              >
                <div className="flex items-start gap-3">
                  <MessageSquare className="h-4 w-4 mt-1 flex-shrink-0 text-indigo-600 dark:text-indigo-400" />
                  
                  {!sidebarCollapsed && (
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-sm text-slate-900 dark:text-white truncate">
                          {conversation.title}
                        </h4>
                        
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setDropdownOpen(dropdownOpen === conversation.id ? null : conversation.id);
                            }}
                            className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
                          >
                            <MoreHorizontal className="h-3 w-3" />
                          </button>
                          
                          {dropdownOpen === conversation.id && (
                            <div className="absolute right-0 top-8 w-36 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-2xl z-10">
                              <button className="w-full px-3 py-2 text-sm text-left text-slate-700 dark:text-slate-300 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 flex items-center gap-2 rounded-t-xl">
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
                      
                      <p className="text-xs text-slate-600 dark:text-slate-300 truncate mt-1">
                        {conversation.preview}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
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
};