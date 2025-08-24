import { MessageSquare, Edit3, Trash2 } from "lucide-react";

export default function SectionItem({
  section,
  currentSection,
  editingSection,
  editTitle,
  hoveredSection,
  onSelectSection,
  onStartEditing,
  onSaveTitle,
  onDeleteSection,
  setEditTitle,
  setHoveredSection,
  formatTime,
}) {
  return (
    <div
      className={`group relative flex items-center p-2 rounded-lg cursor-pointer transition-all duration-200 ${
        currentSection?._id === section?._id
          ? "bg-slate-200 dark:bg-slate-700"
          : "hover:bg-slate-100 dark:hover:bg-slate-700/50"
      }`}
      onClick={() => onSelectSection(section)}
      onMouseEnter={() => setHoveredSection(section?._id)}
      onMouseLeave={() => setHoveredSection(null)}
    >
      <MessageSquare className="w-4 h-4 mr-3 text-slate-400 shrink-0" />

      {editingSection === section?._id ? (
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          onBlur={onSaveTitle}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onSaveTitle();
            } else if (e.key === "Escape") {
              setEditingSection(null);
              setEditTitle("");
            }
          }}
          className="flex-1 text-sm bg-transparent border-none outline-none text-slate-900 dark:text-slate-100"
          autoFocus
        />
      ) : (
        <div className="flex-1 min-w-0">
          <div className="text-sm text-slate-900 dark:text-slate-100 truncate">
            {section?.title == null ? "New Chat" : section?.title}
          </div>
          {section?.updatedAt && (
            <div className="text-xs text-slate-500 dark:text-slate-400">
              {formatTime(section?.updatedAt)}
            </div>
          )}
        </div>
      )}

      {(hoveredSection === section?._id ||
        currentSection?._id === section?._id) &&
        editingSection !== section?._id && (
          <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={(e) => onStartEditing(section, e)}
              className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors rounded"
            >
              <Edit3 className="w-3 h-3" />
            </button>
            <button
              onClick={(e) => onDeleteSection(section?._id, e)}
              className="p-1 text-slate-400 hover:text-red-500 transition-colors rounded"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        )}
    </div>
  );
}
