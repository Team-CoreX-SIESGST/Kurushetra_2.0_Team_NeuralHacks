"use client";

import React from "react";
import Link from "next/link";
import { Sparkles } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";

export default function AuthRequired({
  title = "Authentication Required",
  message = "You need to be logged in to access this page.",
  loginPath = "/login",
  buttonText = "Go to Login",
}) {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">
      <Navbar />

      {/* Main content area */}
      <main className="flex-1 flex items-center justify-center px-4">
        <div className="text-center max-w-md w-full">
          {/* Icon container with gradient */}
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Sparkles className="w-8 h-8 text-white" />
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            {title}
          </h1>

          {/* Message */}
          <p className="text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
            {message}
          </p>
        </div>
      </main>
    </div>
  );
}
