"use client";

import { useState } from "react";
import { useTheme } from "./ThemeProvider"; // or 'next-themes'
import { Sun, Moon, Monitor } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const themes = [
    { name: "light", icon: Sun, label: "Light" },
    { name: "dark", icon: Moon, label: "Dark" },
    { name: "system", icon: Monitor, label: "System" },
  ];

  const currentTheme = themes.find((t) => t.name === theme) || themes[0];

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      {/* Toggle button with dark border in both light and dark modes */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex items-center justify-center w-10 h-10 rounded-lg 
                   bg-gray-100 dark:bg-gray-800 
                   hover:bg-gray-200 dark:hover:bg-gray-700 
                   text-gray-700 dark:text-gray-200 
                   border border-gray-900 dark:border-gray-700 
                   transition-colors"
        aria-label="Toggle theme menu"
      >
        <currentTheme.icon className="w-5 h-5" />
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
          {themes.map((themeOption) => {
            const Icon = themeOption.icon;
            const isActive = theme === themeOption.name;

            return (
              <button
                key={themeOption.name}
                onClick={() => handleThemeChange(themeOption.name)}
                className={`w-full flex items-center px-4 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <Icon className="w-4 h-4 mr-3" />
                {themeOption.label}
              </button>
            );
          })}
        </div>
      )}

      {/* Backdrop to close menu */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
}
