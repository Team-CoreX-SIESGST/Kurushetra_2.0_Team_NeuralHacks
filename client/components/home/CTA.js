"use client";

import Link from "next/link";
import {
  ArrowRight,
  Brain,
  FileText,
  Image,
  Video,
  Database,
  Search,
  Cloud,
} from "lucide-react";

export function CTA() {
  return (
    // THEME CHANGE: Light background by default, dark background in dark mode
    <section className="relative overflow-hidden bg-slate-50 dark:bg-slate-950 py-20 sm:py-24">
      {/* Background Decoration */}
      <div
        // THEME CHANGE: Adapted radial gradient for dark mode
        className="absolute inset-0 -z-10 bg-[radial-gradient(45rem_45rem_at_50%_50%,_theme(colors.indigo.100/50%),_transparent)] dark:bg-[radial-gradient(45rem_45rem_at_50%_50%,_theme(colors.indigo.950/40%),_theme(colors.slate.950))]"
        aria-hidden="true"
      />

      {/* Floating Icons Animation */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        {/* THEME CHANGE: Made icons visible in both themes */}
        <FileText className="absolute top-20 left-10 w-8 h-8 text-slate-300 dark:text-slate-800 animate-float" />
        <Image className="absolute top-40 right-20 w-6 h-6 text-slate-300 dark:text-slate-800 animate-float animation-delay-1000" />
        <Video className="absolute bottom-40 left-20 w-7 h-7 text-slate-300 dark:text-slate-800 animate-float animation-delay-2000" />
        <Database className="absolute top-60 right-40 w-5 h-5 text-slate-300 dark:text-slate-800 animate-float animation-delay-3000" />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          {/* THEME CHANGE: Adapted badge for light/dark modes */}
          <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-slate-200/50 dark:bg-slate-100/5 ring-1 ring-inset ring-slate-900/10 dark:ring-slate-100/10 mb-8 backdrop-blur-lg">
            <Brain className="w-4 h-4 text-indigo-500 dark:text-indigo-400 mr-2" />
            {/* THEME CHANGE: Adapted text for light/dark modes */}
            <span className="text-sm font-medium text-slate-800 dark:text-slate-300">
              AI-Powered Multi-Modal Intelligence
            </span>
          </div>

          {/* Main Content */}
          {/* THEME CHANGE: Adapted heading for light/dark modes */}
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 dark:text-white mb-6">
            Unlock Insights, Instantly
            <br />
            {/* Gradient remains the same, as it looks good on both */}
            <span className="bg-gradient-to-r from-indigo-500 to-cyan-500 dark:from-indigo-400 dark:to-cyan-400 bg-clip-text text-transparent">
              Across All Your Data
            </span>
          </h2>

          {/* THEME CHANGE: Adapted paragraph for light/dark modes */}
          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-400 mb-10 max-w-3xl mx-auto">
            Our AI agent searches across{" "}
            <strong className="text-slate-900 dark:text-slate-200">
              text, images, videos, and tables
            </strong>{" "}
            simultaneously. Connect your Drive to let AI analyze, summarize, and
            generate reports from your entire knowledge base.
          </p>

          {/* Use Cases */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              {
                icon: "⚖️",
                title: "Legal Research",
                content:
                  "Search case laws across documents, images, and video depositions simultaneously.",
              },
              {
                icon: "🔬",
                title: "Medical Research",
                content:
                  "Analyze papers with text, medical images, and video consultations.",
              },
              {
                icon: "📚",
                title: "Academic Study",
                content:
                  "Search through textbooks, lecture slides, and videos in one query.",
              },
            ].map((useCase) => (
              <div
                key={useCase.title}
                // THEME CHANGE: Adapted card for light/dark modes
                className="bg-white/50 dark:bg-slate-100/5 rounded-2xl p-6 ring-1 ring-inset ring-slate-900/10 dark:ring-slate-100/10 hover:ring-slate-900/20 dark:hover:ring-slate-100/20 transition-all duration-300 group text-left"
              >
                <div className="text-3xl mb-4 group-hover:scale-110 transition-transform duration-300 w-fit">
                  {useCase.icon}
                </div>
                {/* THEME CHANGE: Adapted card text for light/dark modes */}
                <h3 className="font-semibold text-slate-900 dark:text-white text-lg mb-2">
                  {useCase.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">
                  {useCase.content}
                </p>
              </div>
            ))}
          </div>

          {/* Bottom Text */}
          <div className="mt-16">
            {/* THEME CHANGE: Adapted bottom text for light/dark modes */}
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              🔒 Privacy-first &nbsp;&bull;&nbsp; 🚀 Lightning fast
              &nbsp;&bull;&nbsp; 🤖 AI-powered insights
            </p>
          </div>
        </div>
      </div>

      {/* Custom Styles for animation (no changes needed here) */}
      <style jsx>{`
        @keyframes float {
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-15px);
          }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animation-delay-1000 {
          animation-delay: 1s;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-3000 {
          animation-delay: 3s;
        }
      `}</style>
    </section>
  );
}
