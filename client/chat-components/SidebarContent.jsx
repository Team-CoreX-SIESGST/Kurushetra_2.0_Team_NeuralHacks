import { Loader2, MessageSquare } from "lucide-react";
import SectionItem from "./SectionItem";

export default function SidebarContent({
  isLoadingSections,
  sections,
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
  if (isLoadingSections) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
      </div>
    );
  }

  if (sections.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 dark:text-slate-400">
        <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No conversations yet</p>
        <p className="text-xs mt-1 opacity-70">Start a new chat to begin</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {sections.map((section) => (
        <SectionItem
          key={section?._id}
          section={section}
          currentSection={currentSection}
          editingSection={editingSection}
          editTitle={editTitle}
          hoveredSection={hoveredSection}
          onSelectSection={onSelectSection}
          onStartEditing={onStartEditing}
          onSaveTitle={onSaveTitle}
          onDeleteSection={onDeleteSection}
          setEditTitle={setEditTitle}
          setHoveredSection={setHoveredSection}
          formatTime={formatTime}
        />
      ))}
    </div>
  );
}
