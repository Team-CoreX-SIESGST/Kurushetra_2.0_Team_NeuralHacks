// InputArea.jsx - Updated with Google Drive integration
import { useRef, useEffect, useState } from "react";
import { Paperclip, Mic, Send, Loader2, Cloud, LogOut } from "lucide-react";
import FileUpload from "./FileUpload";

export default function InputArea({
  message,
  setMessage,
  isLoading,
  handleSendMessage,
  handleKeyDown,
  isListening,
  toggleSpeechRecognition,
  selectedFiles,
  setSelectedFiles,
}) {
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const [isGoogleAuthenticated, setIsGoogleAuthenticated] = useState(false);
  const [isLoadingGoogle, setIsLoadingGoogle] = useState(false);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [message]);

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      setSelectedFiles((prevFiles) => [...prevFiles, ...files]);
    }
    e.target.value = null;
  };

  const handleGoogleDriveAuth = async () => {
    if (isGoogleAuthenticated) {
      // Logout logic
      setIsGoogleAuthenticated(false);
      localStorage.removeItem("google_access_token");
      return;
    }

    setIsLoadingGoogle(true);
    try {
      // Initiate Google OAuth flow
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
      const scope = encodeURIComponent(
        "https://www.googleapis.com/auth/drive.readonly"
      );
      const redirectUri = "http://localhost:3000/oauth-callback";
      const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=token&scope=${scope}`;

      // Open Google OAuth in a popup
      const popup = window.open(authUrl, "GoogleAuth", "width=500,height=600");

      // Listen for message from popup with access token
      const messageHandler = (event) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === "GOOGLE_OAUTH_SUCCESS") {
          const accessToken = event.data.accessToken;
          localStorage.setItem("google_access_token", accessToken);
          setIsGoogleAuthenticated(true);
          setIsLoadingGoogle(false);
          window.removeEventListener("message", messageHandler);
          popup.close();
        } else if (event.data.type === "GOOGLE_OAUTH_ERROR") {
          console.error("Google OAuth error:", event.data.error);
          setIsLoadingGoogle(false);
          window.removeEventListener("message", messageHandler);
          popup.close();
        }
      };

      window.addEventListener("message", messageHandler);
    } catch (error) {
      console.error("Google auth error:", error);
      setIsLoadingGoogle(false);
    }
  };

  const handleGoogleDriveFileSelect = async () => {
    if (!isGoogleAuthenticated) return;

    const accessToken = localStorage.getItem("google_access_token");
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    const developerKey = process.env.NEXT_PUBLIC_GOOGLE_API_KEY;

    // Load Google Picker script
    if (!window.gapi) {
      await new Promise((resolve) => {
        const script = document.createElement("script");
        script.src = "https://apis.google.com/js/api.js";
        script.onload = resolve;
        document.body.appendChild(script);
      });
    }

    window.gapi.load("picker", { callback: createPicker });

    function createPicker() {
      if (accessToken) {
        const picker = new window.google.picker.PickerBuilder()
          .addView(window.google.picker.ViewId.DOCS)
          .setOAuthToken(accessToken)
          .setDeveloperKey(developerKey)
          .setCallback(pickerCallback)
          .build();
        picker.setVisible(true);
      }
    }

    async function pickerCallback(data) {
      if (data.action === window.google.picker.Action.PICKED) {
        const fileId = data.docs[0].id;

        const response = await fetch(
          `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
          {
            headers: { Authorization: `Bearer ${accessToken}` },
          }
        );

        const blob = await response.blob();
        const driveFile = new File([blob], data.docs[0].name, {
          type: data.docs[0].mimeType,
        });

        setSelectedFiles((prevFiles) => [...prevFiles, driveFile]);
      }
    }
  };

  // Check if user is already authenticated on component mount
  useEffect(() => {
    const token = localStorage.getItem("google_access_token");
    if (token) {
      setIsGoogleAuthenticated(true);
    }
  }, []);

  const [isCorrectingPrompt, setIsCorrectingPrompt] = useState(false);

  const handleAutoCorrect = async () => {
    if (!message.trim() || isCorrectingPrompt) return;

    setIsCorrectingPrompt(true);
    try {
      const response = await fetch('/api/ai/improve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ prompt: message }),
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        setMessage(data.data.improvedPrompt);
      } else {
        // Handle error cases
        console.error('Failed to improve prompt:', data.message);
        if (response.status === 429) {
          alert(`Token limit exceeded: ${data.message}\n\nPlease upgrade your plan to continue.`);
        } else {
          alert(data.message || 'Failed to improve prompt. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error improving prompt:', error);
      alert('Network error. Please check your connection and try again.');
    } finally {
      setIsCorrectingPrompt(false);
    }
  };

  return (
    <div className="p-4 bg-white dark:bg-slate-900">
      <div className="max-w-4xl mx-auto">
        <div className="relative">
          <FileUpload
            selectedFiles={selectedFiles}
            setSelectedFiles={setSelectedFiles}
          />
          <div className="flex items-end space-x-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 focus-within:border-slate-300 dark:focus-within:border-slate-600 transition-colors">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              multiple
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-shrink-0 p-1 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
              title="Upload files"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            {/* Google Drive Button */}
            <button
              onClick={
                isGoogleAuthenticated
                  ? handleGoogleDriveFileSelect
                  : handleGoogleDriveAuth
              }
              disabled={isLoadingGoogle}
              className={`flex-shrink-0 p-1 transition-colors ${
                isGoogleAuthenticated
                  ? "text-blue-500 hover:text-blue-700 dark:hover:text-blue-300"
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
              } ${isLoadingGoogle ? "opacity-50 cursor-not-allowed" : ""}`}
              title={
                isGoogleAuthenticated
                  ? "Select from Google Drive"
                  : "Connect Google Drive"
              }
            >
              {isLoadingGoogle ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : isGoogleAuthenticated ? (
                <Cloud className="w-5 h-5" fill="currentColor" />
              ) : (
                <Cloud className="w-5 h-5" />
              )}
            </button>

            {/* Logout button when authenticated */}
            {isGoogleAuthenticated && (
              <button
                onClick={handleGoogleDriveAuth}
                className="flex-shrink-0 p-1 text-red-500 hover:text-red-700 dark:hover:text-red-300 transition-colors"
                title="Disconnect Google Drive"
              >
                <LogOut className="w-5 h-5" />
              </button>
            )}

            <button
              onClick={toggleSpeechRecognition}
              className={`flex-shrink-0 p-1 transition-colors ${
                isListening
                  ? "text-red-500 animate-pulse"
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
              }`}
              title="Voice input"
            >
              <Mic className="w-5 h-5" />
            </button>
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message AI Search Assistant"
                className="w-full bg-transparent border-0 resize-none focus:outline-none text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 text-sm leading-6"
                rows={1}
                disabled={isLoading}
                style={{ minHeight: "24px", maxHeight: "200px" }}
              />
            </div>
            <button
              onClick={handleAutoCorrect}
              disabled={!message.trim() || isCorrectingPrompt || isLoading}
              className="flex-shrink-0 w-8 h-8 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-full hover:bg-slate-800 dark:hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center disabled:hover:bg-slate-900 dark:disabled:hover:bg-slate-100"
              title="Improve prompt with AI"
            >
              {isCorrectingPrompt ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                "A"
              )}
            </button>
            <button
              onClick={handleSendMessage}
              disabled={
                (!message.trim() && selectedFiles?.length === 0) || isLoading
              }
              className="flex-shrink-0 w-8 h-8 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-full hover:bg-slate-800 dark:hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center disabled:hover:bg-slate-900 dark:disabled:hover:bg-slate-100"
              title="Send message"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 text-center">
          AI can search across text, images, PDFs, and more from your connected
          drives
          {isGoogleAuthenticated && (
            <span className="text-blue-500 ml-1">• Google Drive connected</span>
          )}
        </p>
      </div>
    </div>
  );
}
