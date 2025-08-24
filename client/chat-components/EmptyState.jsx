import { FileText, Search, Sparkles, Archive } from "lucide-react";

export default function EmptyState({ setMessage }) {
  const suggestedPrompts = [
    {
      icon: FileText,
      title: "Analyze my documents",
      subtitle: "Get insights from your files and PDFs",
      query: "Help me analyze the documents in my Google Drive",
    },
    {
      icon: Search,
      title: "Search through images",
      subtitle: "Find and describe images by content",
      query: "Help me search through my images and photos",
    },
    {
      icon: Sparkles,
      title: "Summarize presentations",
      subtitle: "Create summaries from your slides",
      query: "Can you summarize my recent presentations?",
    },
    {
      icon: Archive,
      title: "Research assistance",
      subtitle: "Help with data analysis and research",
      query: "Help me research and analyze data from my files",
    },
  ];

  return (
    <div className="flex items-center justify-center h-full p-8">
      <div className="text-center max-w-2xl">
        <div className="w-20 h-20 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-8">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-100 mb-4">
          How can I help you today?
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-400 mb-12">
          Search across all your files, analyze documents, and get intelligent
          insights from your data.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          {suggestedPrompts.map((prompt, i) => {
            const Icon = prompt.icon;
            return (
              <button
                key={i}
                onClick={() => setMessage(prompt.query)}
                className="group p-4 bg-slate-50 dark:bg-slate-800 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-all duration-200 text-left border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
              >
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-white dark:bg-slate-700 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Icon className="w-4 h-4 text-slate-600 dark:text-slate-300" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-1">
                      {prompt.title}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {prompt.subtitle}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
