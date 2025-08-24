import { Plus } from "lucide-react";

export default function SidebarHeader({ onClickBack, createNewSection }) {
  return (
    <div className="p-3">
      <button
        onClick={onClickBack}
        className="w-full flex items-center justify-center px-3 py-2.5 text-sm font-medium text-red-700 dark:text-red-300 bg-white dark:bg-red-700 border border-red-200 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-600 transition-colors duration-200 mb-2"
      >
        {"<-  "}Back
      </button>
      <button
        onClick={createNewSection}
        className="w-full flex items-center justify-center px-3 py-2.5 text-sm font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors duration-200"
      >
        <Plus className="w-4 h-4 mr-2" />
        New chat
      </button>
    </div>
  );
}
