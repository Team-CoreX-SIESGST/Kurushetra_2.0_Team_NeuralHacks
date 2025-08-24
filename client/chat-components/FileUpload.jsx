// FileUpload.jsx - Updated to handle multiple files
import { FileText, X } from "lucide-react";

export default function FileUpload({ selectedFiles, setSelectedFiles }) {
  if (!selectedFiles || selectedFiles.length === 0) return null;

  const removeFile = (indexToRemove) => {
    setSelectedFiles((prevFiles) =>
      prevFiles.filter((_, index) => index !== indexToRemove)
    );
  };

  return (
    <div className="mb-2 space-y-2">
      {selectedFiles.map((file, index) => (
        <div
          key={index}
          className="flex items-center justify-between bg-slate-100 dark:bg-slate-800 p-2 rounded-lg"
        >
          <div className="flex items-center">
            <FileText className="w-4 h-4 mr-2" />
            <span className="text-sm truncate max-w-xs">{file.name}</span>
          </div>
          <button
            onClick={() => removeFile(index)}
            className="text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
