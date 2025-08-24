// "use client";

// import { useState, useEffect, useRef } from "react";
// import {
//   Send,
//   Plus,
//   MessageSquare,
//   Edit3,
//   Trash2,
//   User,
//   Bot,
//   Loader2,
//   Menu,
//   X,
//   Search,
//   FileText,
//   Sparkles,
//   Settings,
//   LogOut,
//   MoreHorizontal,
//   Archive,
//   Mic,
//   Paperclip,
// } from "lucide-react";
// import {
//   getSection,
//   deleteSection,
//   createSection,
//   updateSectionTitle,
//   getSections,
//   sendMessage,
// } from "@/services/chat/chatServices";
// import ReactMarkdown from "react-markdown";
// import { Router, useRouter } from "next/navigation";

// export function ChatInterface({ isSidebarOpen, setIsSidebarOpen }) {
//   const [sections, setSections] = useState([]);
//   const [currentSection, setCurrentSection] = useState(null);
//   const [chats, setChats] = useState([]);
//   const [message, setMessage] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const [editingSection, setEditingSection] = useState(null);
//   const [editTitle, setEditTitle] = useState("");
//   const [isLoadingSections, setIsLoadingSections] = useState(true);
//   const [hoveredSection, setHoveredSection] = useState(null);
//   const [isListening, setIsListening] = useState(false);
//   const [selectedFile, setSelectedFile] = useState(null);

//   const messagesEndRef = useRef(null);
//   const textareaRef = useRef(null);
//   const fileInputRef = useRef(null);
//   const recognitionRef = useRef(null);
//   const router = useRouter();

//   useEffect(() => {
//     loadSections();

//     // Initialize speech recognition if available
//     if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
//       const SpeechRecognition =
//         window.SpeechRecognition || window.webkitSpeechRecognition;
//       recognitionRef.current = new SpeechRecognition();
//       recognitionRef.current.continuous = true;
//       recognitionRef.current.interimResults = true;
//       recognitionRef.current.lang = "en-US";

//       recognitionRef.current.onresult = (event) => {
//         const transcript = Array.from(event.results)
//           .map((result) => result[0])
//           .map((result) => result.transcript)
//           .join("");
//         setMessage(transcript);
//       };

//       recognitionRef.current.onend = () => {
//         if (isListening) {
//           recognitionRef.current.start();
//         }
//       };
//     }

//     return () => {
//       if (recognitionRef.current) {
//         recognitionRef.current.stop();
//       }
//     };
//   }, []);

//   useEffect(() => {
//     scrollToBottom();
//   }, [chats]);

//   useEffect(() => {
//     if (textareaRef.current) {
//       textareaRef.current.style.height = "auto";
//       textareaRef.current.style.height =
//         Math.min(textareaRef.current.scrollHeight, 200) + "px";
//     }
//   }, [message]);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   const loadSections = async () => {
//     try {
//       setIsLoadingSections(true);
//       const response = await getSections();
//       setSections(response.data.data);
//     } catch (error) {
//       console.error("Error loading sections:", error);
//     } finally {
//       setIsLoadingSections(false);
//     }
//   };

//   const onClickBack = async () => {
//     router.push("/");
//   };

//   const createNewSection = async () => {
//     try {
//       const payload = {
//         title: "New Chat",
//       };
//       const response = await createSection(payload);
//       const newSection = response.data;
//       // console.log(response.data,"Fewofhweoi")
//       // console.log(sections)
//       setSections((prev) => [newSection, ...prev]);
//       setCurrentSection(newSection);
//       setChats([]);
//     } catch (error) {
//       console.error("Error creating section:", error);
//     }
//   };

//   const selectSection = async (section) => {
//     try {
//       setCurrentSection(section);
//       const response = await getSection(section._id);
//       setChats(response.data.data.chats);
//     } catch (error) {
//       console.error("Error loading section:", error);
//     }
//   };

//   const handleSendMessage = async () => {
//     if (!message.trim() || isLoading) return;

//     let sectionToUse = currentSection;

//     // Create new section if none exists
//     if (!currentSection) {
//       try {
//         const payload = {
//           title: message.substring(0, 30) + "...",
//         };
//         const response = await createSection(payload);
//         sectionToUse = response.data.data;
//         setCurrentSection(sectionToUse);
//         setSections((prev) => [sectionToUse, ...prev]);
//       } catch (error) {
//         console.error("Error creating section:", error);
//         return;
//       }
//     }

//     const userMessage = {
//       _id: Date.now() + "-user",
//       message: message,
//       isUser: true,
//       createdAt: new Date(),
//     };

//     setChats((prev) => [...prev, userMessage]);
//     setMessage("");
//     setIsLoading(true);

//     try {
//       const response = await sendMessage(sectionToUse._id, {
//         message: message,
//       });
//       setChats((prev) => [...prev, response.data.data.aiMessage]);
//     } catch (error) {
//       console.error("Error sending message:", error);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleKeyDown = (e) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       handleSendMessage();
//     }
//   };

//   const startEditing = (section, e) => {
//     e.stopPropagation();
//     setEditingSection(section._id);
//     setEditTitle(section.title);
//   };

//   const saveTitle = async () => {
//     if (!editTitle.trim()) return;

//     try {
//       const response = await updateSectionTitle(editingSection, {
//         title: editTitle,
//       });
//       setSections((prev) =>
//         prev.map((s) => (s._id === editingSection ? response.data.data : s))
//       );
//       setCurrentSection(response.data.data);
//     } catch (error) {
//       console.error("Error updating title:", error);
//     }

//     setEditingSection(null);
//     setEditTitle("");
//   };

//   const handleDeleteSection = async (sectionId, e) => {
//     e.stopPropagation();
//     try {
//       await deleteSection(sectionId);
//       setSections((prev) => prev.filter((s) => s._id !== sectionId));
//       if (currentSection?._id === sectionId) {
//         setCurrentSection(null);
//         setChats([]);
//       }
//     } catch (error) {
//       console.error("Error deleting section:", error);
//     }
//   };

//   const toggleSpeechRecognition = () => {
//     if (!recognitionRef.current) {
//       alert("Speech recognition is not supported in your browser");
//       return;
//     }

//     if (isListening) {
//       recognitionRef.current.stop();
//       setIsListening(false);
//     } else {
//       recognitionRef.current.start();
//       setIsListening(true);
//     }
//   };

//   const handleFileUpload = (e) => {
//     const file = e.target.files[0];
//     if (file) {
//       setSelectedFile(file);
//       // For now, we'll just append the file name to the message
//       setMessage((prev) => prev + ` [File: ${file.name}]`);
//     }
//   };

//   const formatTime = (date = new Date()) => {
//     const now = new Date();
//     const messageDate = new Date(date);
//     const diffInMinutes = Math.floor((now - messageDate) / (1000 * 60));

//     if (diffInMinutes < 60) {
//       return `${diffInMinutes}m ago`;
//     } else if (diffInMinutes < 1440) {
//       return `${Math.floor(diffInMinutes / 60)}h ago`;
//     } else {
//       return messageDate.toLocaleDateString();
//     }
//   };

//   const suggestedPrompts = [
//     {
//       icon: FileText,
//       title: "Analyze my documents",
//       subtitle: "Get insights from your files and PDFs",
//       query: "Help me analyze the documents in my Google Drive",
//     },
//     {
//       icon: Search,
//       title: "Search through images",
//       subtitle: "Find and describe images by content",
//       query: "Help me search through my images and photos",
//     },
//     {
//       icon: Sparkles,
//       title: "Summarize presentations",
//       subtitle: "Create summaries from your slides",
//       query: "Can you summarize my recent presentations?",
//     },
//     {
//       icon: Archive,
//       title: "Research assistance",
//       subtitle: "Help with data analysis and research",
//       query: "Help me research and analyze data from my files",
//     },
//   ];

//   return (
//     <div className="flex h-screen bg-white dark:bg-slate-900">
//       {/* Sidebar */}
//       <div
//         className={`${
//           isSidebarOpen ? "w-80" : "w-0"
//         } transition-all duration-300 ease-out overflow-hidden md:relative absolute z-20 h-full`}
//       >
//         <div className="w-80 bg-slate-50 dark:bg-slate-800 flex flex-col h-full">
//           {/* Sidebar Header */}
//           <div className="p-3">
//             <button
//               onClick={onClickBack}
//               className="w-full flex items-center justify-center px-3 py-2.5 text-sm font-medium text-red-700 dark:text-red-300 bg-white dark:bg-red-700 border border-red-200 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-600 transition-colors duration-200 mb-2"
//             >
//               {"<-  "}Back
//             </button>
//             <button
//               onClick={createNewSection}
//               className="w-full flex items-center justify-center px-3 py-2.5 text-sm font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors duration-200"
//             >
//               <Plus className="w-4 h-4 mr-2" />
//               New chat
//             </button>
//           </div>

//           {/* Sections List */}
//           <div className="flex-1 overflow-y-auto px-3">
//             {isLoadingSections ? (
//               <div className="flex items-center justify-center py-8">
//                 <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
//               </div>
//             ) : sections.length === 0 ? (
//               <div className="text-center py-8 text-slate-500 dark:text-slate-400">
//                 <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
//                 <p className="text-sm">No conversations yet</p>
//                 <p className="text-xs mt-1 opacity-70">
//                   Start a new chat to begin
//                 </p>
//               </div>
//             ) : (
//               <div className="space-y-1">
//                 {sections.map((section) => (
//                   <div
//                     key={section?._id}
//                     className={`group relative flex items-center p-2 rounded-lg cursor-pointer transition-all duration-200 ${
//                       currentSection?._id === section?._id
//                         ? "bg-slate-200 dark:bg-slate-700"
//                         : "hover:bg-slate-100 dark:hover:bg-slate-700/50"
//                     }`}
//                     onClick={() => selectSection(section)}
//                     onMouseEnter={() => setHoveredSection(section?._id)}
//                     onMouseLeave={() => setHoveredSection(null)}
//                   >
//                     <MessageSquare className="w-4 h-4 mr-3 text-slate-400 shrink-0" />

//                     {editingSection === section?._id ? (
//                       <input
//                         type="text"
//                         value={editTitle}
//                         onChange={(e) => setEditTitle(e.target.value)}
//                         onBlur={saveTitle}
//                         onKeyDown={(e) => {
//                           if (e.key === "Enter") {
//                             saveTitle();
//                           } else if (e.key === "Escape") {
//                             setEditingSection(null);
//                             setEditTitle("");
//                           }
//                         }}
//                         className="flex-1 text-sm bg-transparent border-none outline-none text-slate-900 dark:text-slate-100"
//                         autoFocus
//                       />
//                     ) : (
//                       <div className="flex-1 min-w-0">
//                         <div className="text-sm text-slate-900 dark:text-slate-100 truncate">
//                           {section?.title == null ? "New Chat" : section?.title}
//                         </div>
//                         {section?.updatedAt && (
//                           <div className="text-xs text-slate-500 dark:text-slate-400">
//                             {formatTime(section?.updatedAt)}
//                           </div>
//                         )}
//                       </div>
//                     )}

//                     {(hoveredSection === section?._id ||
//                       currentSection?._id === section?._id) &&
//                       editingSection !== section?._id && (
//                         <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
//                           <button
//                             onClick={(e) => startEditing(section, e)}
//                             className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors rounded"
//                           >
//                             <Edit3 className="w-3 h-3" />
//                           </button>
//                           <button
//                             onClick={(e) =>
//                               handleDeleteSection(section?._id, e)
//                             }
//                             className="p-1 text-slate-400 hover:text-red-500 transition-colors rounded"
//                           >
//                             <Trash2 className="w-3 h-3" />
//                           </button>
//                         </div>
//                       )}
//                   </div>
//                 ))}
//               </div>
//             )}
//           </div>

//           {/* Footer */}
//           <div className="p-3 border-t border-slate-200 dark:border-slate-700">
//             <div className="flex items-center justify-between">
//               <div className="flex items-center text-xs text-slate-500 dark:text-slate-400">
//                 <Sparkles className="w-3 h-3 mr-1" />
//                 AI Search Assistant
//               </div>
//               <button className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
//                 <Settings className="w-4 h-4" />
//               </button>
//             </div>
//           </div>
//         </div>
//       </div>

//       {/* Backdrop for mobile */}
//       {isSidebarOpen && (
//         <div
//           className="fixed inset-0 bg-black bg-opacity-50 z-10 md:hidden"
//           onClick={() => setIsSidebarOpen(false)}
//         />
//       )}

//       {/* Main Chat Area */}
//       <div className="flex-1 flex flex-col min-w-0">
//         {/* Chat Header - Only show when there's an active chat */}
//         {currentSection && (
//           <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
//             <div className="flex items-center space-x-3">
//               <button
//                 onClick={() => setIsSidebarOpen(!isSidebarOpen)}
//                 className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors md:hidden"
//               >
//                 <Menu className="w-5 h-5" />
//               </button>
//               <div className="flex items-center space-x-2">
//                 <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 flex items-center justify-center">
//                   <Bot className="w-4 h-4 text-white" />
//                 </div>
//                 <div>
//                   <h1 className="text-sm font-medium text-slate-900 dark:text-slate-100">
//                     {currentSection.title}
//                   </h1>
//                 </div>
//               </div>
//             </div>
//             <button className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
//               <MoreHorizontal className="w-5 h-5" />
//             </button>
//           </div>
//         )}

//         {/* Toggle sidebar button for desktop when sidebar is closed */}
//         {!isSidebarOpen && (
//           <div className="absolute top-4 left-4 z-10">
//             <button
//               onClick={() => setIsSidebarOpen(true)}
//               className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700"
//             >
//               <Menu className="w-5 h-5" />
//             </button>
//           </div>
//         )}

//         {/* Messages Area */}
//         <div className="flex-1 overflow-y-auto">
//           {chats.length === 0 ? (
//             <div className="flex items-center justify-center h-full p-8">
//               <div className="text-center max-w-2xl">
//                 <div className="w-20 h-20 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-8">
//                   <Sparkles className="w-10 h-10 text-white" />
//                 </div>
//                 <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-100 mb-4">
//                   How can I help you today?
//                 </h1>
//                 <p className="text-lg text-slate-600 dark:text-slate-400 mb-12">
//                   Search across all your files, analyze documents, and get
//                   intelligent insights from your data.
//                 </p>

//                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
//                   {suggestedPrompts.map((prompt, i) => {
//                     const Icon = prompt.icon;
//                     return (
//                       <button
//                         key={i}
//                         onClick={() => setMessage(prompt.query)}
//                         className="group p-4 bg-slate-50 dark:bg-slate-800 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-all duration-200 text-left border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
//                       >
//                         <div className="flex items-start space-x-3">
//                           <div className="w-8 h-8 bg-white dark:bg-slate-700 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
//                             <Icon className="w-4 h-4 text-slate-600 dark:text-slate-300" />
//                           </div>
//                           <div>
//                             <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-1">
//                               {prompt.title}
//                             </h3>
//                             <p className="text-xs text-slate-500 dark:text-slate-400">
//                               {prompt.subtitle}
//                             </p>
//                           </div>
//                         </div>
//                       </button>
//                     );
//                   })}
//                 </div>
//               </div>
//             </div>
//           ) : (
//             <div className="max-w-4xl mx-auto">
//               <div className="space-y-6 p-4">
//                 {chats.map((chat, index) => (
//                   <div
//                     key={chat._id}
//                     className={`flex ${
//                       chat.isUser ? "justify-end" : "justify-start"
//                     }`}
//                   >
//                     <div
//                       className={`flex max-w-[80%] ${
//                         chat.isUser ? "flex-row-reverse" : "flex-row"
//                       }`}
//                     >
//                       <div
//                         className={`flex-shrink-0 ${
//                           chat.isUser ? "ml-3" : "mr-3"
//                         }`}
//                       >
//                         <div
//                           className={`w-8 h-8 rounded-full flex items-center justify-center ${
//                             chat.isUser
//                               ? "bg-slate-900 dark:bg-slate-100"
//                               : "bg-gradient-to-r from-indigo-500 to-cyan-500"
//                           }`}
//                         >
//                           {chat.isUser ? (
//                             <User className="w-4 h-4 text-white dark:text-slate-900" />
//                           ) : (
//                             <Bot className="w-4 h-4 text-white" />
//                           )}
//                         </div>
//                       </div>
//                       <div
//                         className={`px-4 py-3 rounded-3xl ${
//                           chat.isUser
//                             ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
//                             : "bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
//                         }`}
//                       >
//                         <p className="text-sm whitespace-pre-wrap leading-relaxed">
//                           <ReactMarkdown>{chat.message}</ReactMarkdown>
//                         </p>
//                         <div className="flex items-center justify-between mt-2">
//                           <span className="text-xs opacity-60">
//                             {formatTime(chat.createdAt)}
//                           </span>
//                         </div>
//                       </div>
//                     </div>
//                   </div>
//                 ))}

//                 {isLoading && (
//                   <div className="flex justify-start">
//                     <div className="flex max-w-[80%]">
//                       <div className="mr-3">
//                         <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 flex items-center justify-center">
//                           <Bot className="w-4 h-4 text-white" />
//                         </div>
//                       </div>
//                       <div className="px-4 py-3 rounded-3xl bg-slate-50 dark:bg-slate-800">
//                         <div className="flex items-center space-x-2">
//                           <div className="flex space-x-1">
//                             <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"></div>
//                             <div
//                               className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"
//                               style={{ animationDelay: "0.1s" }}
//                             ></div>
//                             <div
//                               className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"
//                               style={{ animationDelay: "0.2s" }}
//                             ></div>
//                           </div>
//                           <span className="text-sm text-slate-500 dark:text-slate-400">
//                             Thinking...
//                           </span>
//                         </div>
//                       </div>
//                     </div>
//                   </div>
//                 )}

//                 <div ref={messagesEndRef} />
//               </div>
//             </div>
//           )}
//         </div>

//         {/* Input Area */}
//         <div className="p-4 bg-white dark:bg-slate-900">
//           <div className="max-w-4xl mx-auto">
//             <div className="relative">
//               {selectedFile && (
//                 <div className="mb-2 flex items-center justify-between bg-slate-100 dark:bg-slate-800 p-2 rounded-lg">
//                   <div className="flex items-center">
//                     <FileText className="w-4 h-4 mr-2" />
//                     <span className="text-sm truncate max-w-xs">
//                       {selectedFile.name}
//                     </span>
//                   </div>
//                   <button
//                     onClick={() => setSelectedFile(null)}
//                     className="text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
//                   >
//                     <X className="w-4 h-4" />
//                   </button>
//                 </div>
//               )}
//               <div className="flex items-end space-x-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 focus-within:border-slate-300 dark:focus-within:border-slate-600 transition-colors">
//                 <input
//                   type="file"
//                   ref={fileInputRef}
//                   onChange={handleFileUpload}
//                   className="hidden"
//                 />
//                 <button
//                   onClick={() => fileInputRef.current?.click()}
//                   className="flex-shrink-0 p-1 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
//                 >
//                   <Paperclip className="w-5 h-5" />
//                 </button>
//                 <button
//                   onClick={toggleSpeechRecognition}
//                   className={`flex-shrink-0 p-1 transition-colors ${
//                     isListening
//                       ? "text-red-500 animate-pulse"
//                       : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
//                   }`}
//                 >
//                   <Mic className="w-5 h-5" />
//                 </button>
//                 <div className="flex-1">
//                   <textarea
//                     ref={textareaRef}
//                     value={message}
//                     onChange={(e) => setMessage(e.target.value)}
//                     onKeyDown={handleKeyDown}
//                     placeholder="Message AI Search Assistant"
//                     className="w-full bg-transparent border-0 resize-none focus:outline-none text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 text-sm leading-6"
//                     rows={1}
//                     disabled={isLoading}
//                     style={{ minHeight: "24px", maxHeight: "200px" }}
//                   />
//                 </div>
//                 <button
//                   onClick={handleSendMessage}
//                   disabled={!message.trim() || isLoading}
//                   className="flex-shrink-0 w-8 h-8 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-full hover:bg-slate-800 dark:hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center disabled:hover:bg-slate-900 dark:disabled:hover:bg-slate-100"
//                 >
//                   {isLoading ? (
//                     <Loader2 className="w-4 h-4 animate-spin" />
//                   ) : (
//                     <Send className="w-4 h-4" />
//                   )}
//                 </button>
//               </div>
//             </div>
//             <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 text-center">
//               AI can search across text, images, PDFs, and more from your
//               connected drives
//             </p>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
