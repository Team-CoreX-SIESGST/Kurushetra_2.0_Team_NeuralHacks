import { Sparkles, Settings } from "lucide-react";

export default function SidebarFooter() {
  return (
    <div className="p-3 border-t border-slate-200 dark:border-slate-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center text-xs text-slate-500 dark:text-slate-400">
          <Sparkles className="w-3 h-3 mr-1" />
          AI Search Assistant
        </div>
        <button className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
