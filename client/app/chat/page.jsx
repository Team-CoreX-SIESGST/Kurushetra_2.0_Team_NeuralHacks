"use client";

import { useState, useEffect, useRef } from "react";
import {
  Send,
  Plus,
  MessageSquare,
  Edit3,
  Trash2,
  User,
  Bot,
  Loader2,
  Menu,
  X,
  Search,
  FileText,
  Sparkles,
  Settings,
  LogOut,
  MoreHorizontal,
  Archive,
} from "lucide-react";

import { ChatInterface } from "@/chat-components/index";

// Main Page Component
export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      <ChatInterface
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
      />
    </div>
  );
}
