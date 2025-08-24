import { Menu, MoreHorizontal, Bot } from "lucide-react";

export default function ChatHeader({
  currentSection,
  isSidebarOpen,
  setIsSidebarOpen,
}) {
  if (!currentSection) return null;

  return (
    <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
      <div className="flex items-center space-x-3">
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors md:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-medium text-slate-900 dark:text-slate-100">
              {currentSection.title}
            </h1>
          </div>
        </div>
      </div>
      <button className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
        <MoreHorizontal className="w-5 h-5" />
      </button>
    </div>
  );
}
