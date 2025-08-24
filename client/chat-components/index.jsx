"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  getSection,
  deleteSection,
  createSection,
  updateSectionTitle,
  getSections,
  sendMessage,
} from "@/services/chat/chatServices";
import Sidebar from "./Sidebar";
import ChatHeader from "./ChatHeader";
import MessagesArea from "./MessagesArea";
import InputArea from "./InputArea";

export function ChatInterface({ isSidebarOpen, setIsSidebarOpen }) {
  const [sections, setSections] = useState([]);
  const [currentSection, setCurrentSection] = useState(null);
  const [chats, setChats] = useState([]);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [isLoadingSections, setIsLoadingSections] = useState(true);
  const [hoveredSection, setHoveredSection] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const router = useRouter()

  useEffect(() => {
    loadSections();

    // Initialize speech recognition if available
    if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = "en-US";

      recognitionRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0])
          .map((result) => result.transcript)
          .join("");
        setMessage(transcript);
      };

      recognitionRef.current.onend = () => {
        if (isListening) {
          recognitionRef.current.start();
        }
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chats]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadSections = async () => {
    try {
      setIsLoadingSections(true);
      const response = await getSections();
      setSections(response.data.data);
    } catch (error) {
      console.error("Error loading sections:", error);
    } finally {
      setIsLoadingSections(false);
    }
  };

  const onClickBack = async () => {
    router.push("/");
  };

  const createNewSection = async () => {
    try {
      const payload = {
        title: "New Chat",
      };
      const response = await createSection(payload);
      const newSection = response.data.data;
      setSections((prev) => [newSection, ...prev]);
      setCurrentSection(newSection);
      setChats([]);
    } catch (error) {
      console.error("Error creating section:", error);
    }
  };

  const selectSection = async (section) => {
    try {
      setCurrentSection(section);
      const response = await getSection(section._id);
      setChats(response.data.data.chats);
    } catch (error) {
      console.error("Error loading section:", error);
    }
  };

  const handleSendMessage = async () => {
    if ((!message.trim() && selectedFiles.length === 0) || isLoading) return;

    let sectionToUse = currentSection;

    // Create new section if none exists
    if (!currentSection) {
      try {
        const title = message.substring(0, 30) || "Files upload";
        const payload = {
          title: title + "...",
        };
        const response = await createSection(payload);
        sectionToUse = response.data.data;
        setCurrentSection(sectionToUse);
        setSections((prev) => [sectionToUse, ...prev]);
      } catch (error) {
        console.error("Error creating section:", error);
        return;
      }
    }

    const userMessage = {
      _id: Date.now() + "-user",
      message: message,
      isUser: true,
      createdAt: new Date(),
      files: selectedFiles.length > 0 ? [...selectedFiles] : undefined, // Include files in message
    };

    setChats((prev) => [...prev, userMessage]);
    setMessage("");
    setSelectedFiles([]); // Clear selected files after sending
    setIsLoading(true);

    try {
      // You'll need to update your sendMessage service to handle file uploads
      const response = await sendMessage(sectionToUse._id, {
        message: message,
        files: selectedFiles, // Send files to the API
      });
      setChats((prev) => [...prev, response.data.data.aiMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startEditing = (section, e) => {
    e.stopPropagation();
    setEditingSection(section._id);
    setEditTitle(section.title);
  };

  const saveTitle = async () => {
    if (!editTitle.trim()) return;

    try {
      const response = await updateSectionTitle(editingSection, {
        title: editTitle,
      });
      setSections((prev) =>
        prev.map((s) => (s._id === editingSection ? response.data.data : s))
      );
      setCurrentSection(response.data.data);
    } catch (error) {
      console.error("Error updating title:", error);
    }

    setEditingSection(null);
    setEditTitle("");
  };

  const handleDeleteSection = async (sectionId, e) => {
    e.stopPropagation();
    try {
      await deleteSection(sectionId);
      setSections((prev) => prev.filter((s) => s._id !== sectionId));
      if (currentSection?._id === sectionId) {
        setCurrentSection(null);
        setChats([]);
      }
    } catch (error) {
      console.error("Error deleting section:", error);
    }
  };

  const toggleSpeechRecognition = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in your browser");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const formatTime = (date = new Date()) => {
    const now = new Date();
    const messageDate = new Date(date);
    const diffInMinutes = Math.floor((now - messageDate) / (1000 * 60));

    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)}h ago`;
    } else {
      return messageDate.toLocaleDateString();
    }
  };

  return (
    <div className="flex h-screen bg-white dark:bg-slate-900">
      {/* Sidebar */}
      <Sidebar
        isSidebarOpen={isSidebarOpen}
        onClickBack={onClickBack}
        createNewSection={createNewSection}
        isLoadingSections={isLoadingSections}
        sections={sections}
        currentSection={currentSection}
        editingSection={editingSection}
        editTitle={editTitle}
        hoveredSection={hoveredSection}
        onSelectSection={selectSection}
        onStartEditing={startEditing}
        onSaveTitle={saveTitle}
        onDeleteSection={handleDeleteSection}
        setEditTitle={setEditTitle}
        setHoveredSection={setHoveredSection}
        formatTime={formatTime}
      />

      {/* Backdrop for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-10 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Header */}
        <ChatHeader
          currentSection={currentSection}
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
        />

        {/* Toggle sidebar button for desktop when sidebar is closed */}
        {!isSidebarOpen && (
          <div className="absolute top-4 left-4 z-10">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          <MessagesArea
            chats={chats}
            isLoading={isLoading}
            formatTime={formatTime}
            setMessage={setMessage}
          />
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <InputArea
          message={message}
          setMessage={setMessage}
          isLoading={isLoading}
          handleSendMessage={handleSendMessage}
          handleKeyDown={handleKeyDown}
          isListening={isListening}
          toggleSpeechRecognition={toggleSpeechRecognition}
          selectedFiles={selectedFiles}
          setSelectedFiles={setSelectedFiles}
        />
      </div>
    </div>
  );
}
