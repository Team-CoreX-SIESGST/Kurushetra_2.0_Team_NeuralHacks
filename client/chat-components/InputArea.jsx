// InputArea.jsx - Update to handle multiple files
import { useRef, useEffect } from "react";
import { Paperclip, Mic, Send, Loader2 } from "lucide-react";
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
    // Clear the input to allow selecting the same files again
    e.target.value = null;
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
              multiple // Allow multiple file selection
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-shrink-0 p-1 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <button
              onClick={toggleSpeechRecognition}
              className={`flex-shrink-0 p-1 transition-colors ${
                isListening
                  ? "text-red-500 animate-pulse"
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
              }`}
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
              onClick={handleSendMessage}
              disabled={
                (!message.trim() && selectedFiles?.length === 0) || isLoading
              }
              className="flex-shrink-0 w-8 h-8 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-full hover:bg-slate-800 dark:hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center disabled:hover:bg-slate-900 dark:disabled:hover:bg-slate-100"
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
        </p>
      </div>
    </div>
  );
}
