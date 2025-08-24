import { Bot } from "lucide-react";

export default function LoadingMessage() {
  return (
    <div className="flex justify-start">
      <div className="flex max-w-[80%]">
        <div className="mr-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
        </div>
        <div className="px-4 py-3 rounded-3xl bg-slate-50 dark:bg-slate-800">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"></div>
              <div
                className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"
                style={{ animationDelay: "0.1s" }}
              ></div>
              <div
                className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"
                style={{ animationDelay: "0.2s" }}
              ></div>
            </div>
            <span className="text-sm text-slate-500 dark:text-slate-400">
              Thinking...
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
