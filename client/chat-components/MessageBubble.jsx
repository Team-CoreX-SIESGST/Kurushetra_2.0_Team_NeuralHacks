import ReactMarkdown from "react-markdown";
import { User, Bot, BookOpen, Code, FileText } from "lucide-react";

export default function MessageBubble({ chat, formatTime }) {
  // Function to detect content type and format accordingly
  const renderBotMessage = (message) => {
    // Check if message contains structured academic content
    if (
      message.includes("Unit") ||
      message.includes("NLP") ||
      message.includes("**")
    ) {
      return (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-4 h-4 text-indigo-500" />
            <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">
              Course Content Summary
            </span>
          </div>
          <div
            className="prose prose-sm dark:prose-invert max-w-none
                       prose-headings:text-slate-800 dark:prose-headings:text-slate-200
                       prose-p:text-slate-700 dark:prose-p:text-slate-300
                       prose-strong:text-slate-900 dark:prose-strong:text-slate-100
                       prose-ul:text-slate-700 dark:prose-ul:text-slate-300
                       prose-li:mb-1"
          >
            <ReactMarkdown
              components={{
                h3: ({ children }) => (
                  <h3 className="text-lg font-semibold text-indigo-700 dark:text-indigo-300 mt-4 mb-2 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></div>
                    {children}
                  </h3>
                ),
                h4: ({ children }) => (
                  <h4 className="text-md font-medium text-slate-800 dark:text-slate-200 mt-3 mb-2">
                    {children}
                  </h4>
                ),
                ul: ({ children }) => (
                  <ul className="space-y-1 ml-4">{children}</ul>
                ),
                li: ({ children }) => (
                  <li className="flex items-start gap-2">
                    <div className="w-1 h-1 bg-slate-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span>{children}</span>
                  </li>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold bg-slate-100 dark:bg-slate-700 px-1 rounded text-slate-900 dark:text-slate-100">
                    {children}
                  </strong>
                ),
                code: ({ children }) => (
                  <code className="bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded text-sm font-mono text-indigo-600 dark:text-indigo-400">
                    {children}
                  </code>
                ),
              }}
            >
              {message}
            </ReactMarkdown>
          </div>
        </div>
      );
    }

    // For code content
    if (
      message.includes("```") ||
      message.includes("import") ||
      message.includes("def ")
    ) {
      return (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <Code className="w-4 h-4 text-green-500" />
            <span className="text-sm font-medium text-green-600 dark:text-green-400">
              Code Example
            </span>
          </div>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown
              components={{
                pre: ({ children }) => (
                  <pre className="bg-slate-900 dark:bg-slate-800 text-slate-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {children}
                  </pre>
                ),
                code: ({ className, children }) => {
                  const isInline = !className;
                  if (isInline) {
                    return (
                      <code className="bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded text-sm font-mono text-indigo-600 dark:text-indigo-400">
                        {children}
                      </code>
                    );
                  }
                  return <code className="font-mono">{children}</code>;
                },
              }}
            >
              {message}
            </ReactMarkdown>
          </div>
        </div>
      );
    }

    // Default rendering for regular text
    return (
      <div
        className="prose prose-sm dark:prose-invert max-w-none
                   prose-p:text-slate-700 dark:prose-p:text-slate-300
                   prose-strong:text-slate-900 dark:prose-strong:text-slate-100"
      >
        <ReactMarkdown>{message}</ReactMarkdown>
      </div>
    );
  };

  return (
    <div
      className={`flex ${chat.isUser ? "justify-end" : "justify-start"} mb-6`}
    >
      <div
        className={`flex max-w-[85%] ${
          chat.isUser ? "flex-row-reverse" : "flex-row"
        }`}
      >
        {/* Avatar */}
        <div className={`flex-shrink-0 ${chat.isUser ? "ml-3" : "mr-3"}`}>
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
              chat.isUser
                ? "bg-gradient-to-r from-slate-800 to-slate-900 dark:from-slate-100 dark:to-slate-200"
                : "bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500"
            }`}
          >
            {chat.isUser ? (
              <User className="w-5 h-5 text-white dark:text-slate-900" />
            ) : (
              <Bot className="w-5 h-5 text-white" />
            )}
          </div>
        </div>

        <div
          className={`px-5 py-4 rounded-2xl shadow-sm border ${
            chat.isUser
              ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 border-slate-800 dark:border-slate-200"
              : "bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border-slate-200 dark:border-slate-700"
          }`}
        >
          {/* Message Body */}
          <div className="text-sm leading-relaxed">
            {chat.isUser ? (
              <p className="whitespace-pre-wrap">{chat.message}</p>
            ) : (
              renderBotMessage(chat.message)
            )}
          </div>

          {/* Timestamp and Actions */}
          <div
            className={`flex items-center justify-between mt-3 pt-2 border-t ${
              chat.isUser
                ? "border-slate-700 dark:border-slate-300"
                : "border-slate-100 dark:border-slate-700"
            }`}
          >
            <span
              className={`text-xs ${
                chat.isUser
                  ? "text-slate-400 dark:text-slate-600"
                  : "text-slate-500 dark:text-slate-400"
              }`}
            >
              {formatTime(chat.createdAt)}
            </span>

            {!chat.isUser && (
              <div className="flex items-center gap-2">
                <FileText className="w-3 h-3 text-slate-400 dark:text-slate-500" />
                <span className="text-xs text-slate-400 dark:text-slate-500">
                  AI Response
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
