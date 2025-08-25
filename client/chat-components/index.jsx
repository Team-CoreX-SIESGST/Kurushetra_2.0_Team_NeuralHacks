"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "./Sidebar";
import ChatHeader from "./ChatHeader";
import MessagesArea from "./MessagesArea";
import InputArea from "./InputArea";
import { Menu } from "lucide-react";
import { useToast } from "@/components/ui/ToastProvider";

// FastAPI base URL and helpers
const BASE_URL = "http://localhost:8000";
const DEFAULT_WORKSPACE_ID = "demo";

const getAuthToken = () => {
	// Try common storage keys; adjust if your app stores under a different key
	return (
		(typeof window !== "undefined" &&
			(localStorage.getItem("token") ||
				localStorage.getItem("accessToken") ||
				localStorage.getItem("AUTH_TOKEN"))) || ""
	);
};

const getAuthHeader = () => {
	const token = getAuthToken();
	return token ? { Authorization: `Bearer ${token}` } : {};
};

async function apiUploadFile(file, workspaceId = DEFAULT_WORKSPACE_ID) {
	const form = new FormData();
	form.append("workspace_id", workspaceId);
	form.append("file", file);

	const res = await fetch(`${BASE_URL}/api/v1/upload`, {
		method: "POST",
		headers: {
			...getAuthHeader(),
		},
		body: form,
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(`Upload failed: ${res.status} ${text}`);
	}
	return res.json();
}

async function apiSearch(query, options = {}) {
	const body = {
		workspace_id: options.workspaceId || DEFAULT_WORKSPACE_ID,
		query,
		top_k: options.top_k ?? 10,
		include_web: options.include_web ?? true,
		rerank: options.rerank ?? true,
		summarize: options.summarize ?? true,
	};
	const res = await fetch(`${BASE_URL}/api/v1/search`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			...getAuthHeader(),
		},
		body: JSON.stringify(body),
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(`Search failed: ${res.status} ${text}`);
	}
	return res.json();
}

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
	const { showToast } = useToast();

	const messagesEndRef = useRef(null);
	const recognitionRef = useRef(null);
	const router = useRouter();

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
		// No server-side sections in FastAPI docs; keep local-only
		setIsLoadingSections(true);
		try {
			const saved = [];
			setSections(saved);
		} catch (error) {
			console.error("Error loading sections:", error);
			showToast("Failed to load chats", "error");
		} finally {
			setIsLoadingSections(false);
		}
	};

	const onClickBack = async () => {
		router.push("/");
	};

	const createNewSection = async () => {
		try {
			const newSection = {
				_id: `${Date.now()}`,
				title: "New Chat",
				createdAt: new Date().toISOString(),
			};
			setSections((prev) => [newSection, ...prev]);
			setCurrentSection(newSection);
			setChats([]);
		} catch (error) {
			console.error("Error creating section:", error);
			showToast("Failed to create chat", "error");
		}
	};

	const selectSection = async (section) => {
		try {
			setCurrentSection(section);
			// No server to fetch chat history from in FastAPI docs; keep current chats
		} catch (error) {
			console.error("Error loading section:", error);
			showToast("Failed to open chat", "error");
		}
	};

	const handleSendMessage = async () => {
		if ((!message.trim() && selectedFiles.length === 0) || isLoading) return;

		let sectionToUse = currentSection;
		let uploadedFiles = [];

		// Upload files to FastAPI if any
		if (selectedFiles.length > 0) {
			try {
				uploadedFiles = await Promise.all(
					selectedFiles.map(async (file) => {
						const res = await apiUploadFile(file);
						return res; // contains file_id, filename, status, details
					})
				);
			} catch (error) {
				console.error("Error uploading files:", error);
				showToast("File upload failed. Ensure you're logged in.", "error");
				return;
			}
		}

		// Create new local section if none exists
		if (!currentSection) {
			try {
				const title = message.substring(0, 30) || "Files upload";
				const newSection = { _id: `${Date.now()}`, title: `${title}...` };
				sectionToUse = newSection;
				setCurrentSection(sectionToUse);
				setSections((prev) => [sectionToUse, ...prev]);
			} catch (error) {
				console.error("Error creating section:", error);
				showToast("Failed to create chat", "error");
				return;
			}
		}

		const messageToSend = message;
		const userMessage = {
			_id: Date.now() + "-user",
			message: messageToSend,
			isUser: true,
			createdAt: new Date(),
			files: uploadedFiles,
		};

		setChats((prev) => [...prev, userMessage]);
		setMessage("");
		setSelectedFiles([]);
		setIsLoading(true);

		try {
			const searchRes = await apiSearch(messageToSend, {
				workspaceId: DEFAULT_WORKSPACE_ID,
			});

			const aiMessage = {
				_id: Date.now() + "-ai",
				message: searchRes.answer || "",
				isUser: false,
				createdAt: new Date(),
				sources: searchRes.sources || [],
				confidence: searchRes.confidence,
				metadata: searchRes.metadata,
			};
			setChats((prev) => [...prev, aiMessage]);
		} catch (error) {
			console.error("Error sending message:", error);
			showToast("Search failed. Check your login and API server.", "error");
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
			setSections((prev) =>
				prev.map((s) => (s._id === editingSection ? { ...s, title: editTitle } : s))
			);
			setCurrentSection((prev) => (prev && prev._id === editingSection ? { ...prev, title: editTitle } : prev));
		} catch (error) {
			console.error("Error updating title:", error);
			showToast("Failed to update title", "error");
		}
		setEditingSection(null);
		setEditTitle("");
	};

	const handleDeleteSection = async (sectionId, e) => {
		e.stopPropagation();
		try {
			setSections((prev) => prev.filter((s) => s._id !== sectionId));
			if (currentSection?._id === sectionId) {
				setCurrentSection(null);
				setChats([]);
			}
		} catch (error) {
			console.error("Error deleting section:", error);
			showToast("Failed to delete chat", "error");
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
