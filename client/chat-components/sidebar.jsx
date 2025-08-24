import SidebarHeader from "./SidebarHeader";
import SidebarContent from "./SidebarContent";
import SidebarFooter from "./SidebarFooter";

export default function Sidebar({
  isSidebarOpen,
  onClickBack,
  createNewSection,
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
  return (
    <div
      className={`${
        isSidebarOpen ? "w-80" : "w-0"
      } transition-all duration-300 ease-out overflow-hidden md:relative absolute z-20 h-[100vh]`}
    >
      <div className="w-80 bg-slate-50 dark:bg-slate-800 flex flex-col h-full">
        <SidebarHeader
          onClickBack={onClickBack}
          createNewSection={createNewSection}
        />
        <div className="flex-1 overflow-y-auto px-3">
          <SidebarContent
            isLoadingSections={isLoadingSections}
            sections={sections}
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
        </div>
        <SidebarFooter />
      </div>
    </div>
  );
}
