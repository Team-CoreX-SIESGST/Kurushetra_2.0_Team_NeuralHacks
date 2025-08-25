import ReactMarkdown from "react-markdown";
import { User, Bot, Link as LinkIcon, FileText } from "lucide-react";

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

          {!chat.isUser && Array.isArray(chat.sources) && chat.sources.length > 0 && (
            <div className="mt-3 border-t border-slate-200 dark:border-slate-700 pt-2">
              <div className="text-xs font-semibold opacity-70 mb-1">Sources</div>
              <ul className="space-y-1">
                {chat.sources.slice(0, 5).map((src, idx) => (
                  <li key={idx} className="text-xs flex items-start gap-2 opacity-80">
                    <FileText className="w-3.5 h-3.5 mt-0.5" />
                    <div>
                      <div>
                        {(src.filename || src.file_id || "Source")} {src.page ? `(p. ${src.page})` : ""}
                      </div>
                      {src.url ? (
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          <LinkIcon className="w-3 h-3" /> Open link
                        </a>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

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
