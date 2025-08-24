import ReactMarkdown from "react-markdown";
import { User, Bot } from "lucide-react";

export default function MessageBubble({ chat, formatTime }) {
  return (
    <div className={`flex ${chat.isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`flex max-w-[80%] ${
          chat.isUser ? "flex-row-reverse" : "flex-row"
        }`}
      >
        <div className={`flex-shrink-0 ${chat.isUser ? "ml-3" : "mr-3"}`}>
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center ${
              chat.isUser
                ? "bg-slate-900 dark:bg-slate-100"
                : "bg-gradient-to-r from-indigo-500 to-cyan-500"
            }`}
          >
            {chat.isUser ? (
              <User className="w-4 h-4 text-white dark:text-slate-900" />
            ) : (
              <Bot className="w-4 h-4 text-white" />
            )}
          </div>
        </div>
        <div
          className={`px-4 py-3 rounded-3xl ${
            chat.isUser
              ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
              : "bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          }`}
        >
          <p className="text-sm whitespace-pre-wrap leading-relaxed">
            <ReactMarkdown>{chat.message}</ReactMarkdown>
          </p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs opacity-60">
              {formatTime(chat.createdAt)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
