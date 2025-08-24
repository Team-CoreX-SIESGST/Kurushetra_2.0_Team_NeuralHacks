"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/components/auth/AuthProvider";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { Menu, X, User, LogOut, Sparkles } from "lucide-react";

export function Navbar() {
  const { user, user_info, logout, loading } = useAuth(); // Added user_info to destructuring
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Debug: Log the auth state
  useEffect(() => {
    console.log("Auth Debug:", { user, user_info, loading });
  }, [user, user_info, loading]);

  // Handle scroll effect for navbar background
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    if (isMobileMenuOpen) {
      setIsMobileMenuOpen(false);
    }
  }, [pathname, isMobileMenuOpen]);

  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/features", label: "Features" },
    { href: "/about", label: "About" },
    { href: "/contact", label: "Contact" },
  ];

  const mobileMenuVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.2 } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
  };

  // Use user_info if user is not available, or vice versa
  const currentUser = user || user_info;

  // Helper for creating desktop navigation links
  const createDesktopNavLinks = () =>
    navLinks.map((link) =>
      React.createElement(
        Link,
        {
          key: link.href,
          href: link.href,
          className: `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            pathname === link.href
              ? "bg-slate-900/10 dark:bg-slate-100/10 text-slate-900 dark:text-slate-100"
              : "text-slate-600 dark:text-slate-300 hover:bg-slate-900/5 dark:hover:bg-slate-100/5 hover:text-slate-900 dark:hover:text-slate-100"
          }`,
        },
        link.label
      )
    );

  // Helper for creating mobile navigation links
  const createMobileNavLinks = () =>
    navLinks.map((link) =>
      React.createElement(
        Link,
        {
          key: link.href,
          href: link.href,
          className: `block px-3 py-2 rounded-md text-base font-medium transition-colors ${
            pathname === link.href
              ? "bg-slate-900/10 dark:bg-slate-100/10 text-slate-900 dark:text-slate-100"
              : "text-slate-600 dark:text-slate-300 hover:bg-slate-900/5 dark:hover:bg-slate-100/5"
          }`,
        },
        link.label
      )
    );

  // Main render return
  return React.createElement(
    "nav",
    {
      className: `fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled || isMobileMenuOpen
          ? "bg-slate-50/80 dark:bg-slate-950/80 backdrop-blur-lg border-b border-slate-200/50 dark:border-slate-800/50 shadow-sm"
          : "bg-transparent"
      }`,
    },
    React.createElement(
      "div",
      { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" },
      React.createElement(
        "div",
        { className: "flex justify-between h-16" },
        // Logo
        React.createElement(
          "div",
          { className: "flex items-center" },
          React.createElement(
            Link,
            { href: "/", className: "flex items-center space-x-2.5 group" },
            React.createElement(
              "div",
              {
                className:
                  "w-9 h-9 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-lg flex items-center justify-center shadow-md group-hover:scale-105 transition-transform duration-300",
              },
              React.createElement(Sparkles, { className: "w-5 h-5 text-white" })
            ),
            React.createElement(
              "span",
              {
                className:
                  "text-xl font-semibold tracking-tight text-slate-900 dark:text-white",
              },
              "OmniSearch"
            )
          )
        ),
        // Desktop Navigation
        React.createElement(
          "div",
          { className: "hidden md:flex items-center space-x-2" },
          ...createDesktopNavLinks()
        ),
        // Right side - Auth & Theme
        React.createElement(
          "div",
          { className: "flex items-center space-x-3" },
          React.createElement(ThemeToggle),
          React.createElement(
            "div",
            { className: "hidden md:flex items-center space-x-3" },
            // Only render buttons after loading is complete
            !loading &&
              (currentUser
                ? // Logged In state
                  React.createElement(
                    React.Fragment,
                    null,
                    React.createElement(
                      "span",
                      {
                        className: "text-sm text-slate-600 dark:text-slate-400",
                      },
                      `Welcome, ${
                        currentUser.name || currentUser.username || "User"
                      }`
                    ),
                    React.createElement(
                      "button",
                      {
                        onClick: logout,
                        className:
                          "px-3 py-2 rounded-md text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-red-500/10 hover:text-red-600 dark:hover:text-red-500 transition-colors",
                      },
                      React.createElement(LogOut, { className: "w-4 h-4" })
                    )
                  )
                : // Logged Out state
                  React.createElement(
                    React.Fragment,
                    null,
                    React.createElement(
                      Link,
                      {
                        href: "/login",
                        className:
                          "px-3 py-2 rounded-md text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-900/5 dark:hover:bg-slate-100/5 hover:text-slate-900 dark:hover:text-slate-100 transition-colors",
                      },
                      "Login"
                    ),
                    React.createElement(
                      Link,
                      {
                        href: "/register",
                        className:
                          "px-4 py-2 rounded-md text-sm font-semibold text-white bg-slate-900 hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200 transition-colors",
                      },
                      "Get Started"
                    )
                  ))
          ),
          // Mobile menu button
          React.createElement(
            "button",
            {
              onClick: () => setIsMobileMenuOpen(!isMobileMenuOpen),
              className:
                "md:hidden p-2 rounded-md text-slate-600 dark:text-slate-300 hover:bg-slate-900/5 dark:hover:bg-slate-100/5 transition-colors",
              "aria-label": "Toggle mobile menu",
            },
            isMobileMenuOpen
              ? React.createElement(X, { className: "w-6 h-6" })
              : React.createElement(Menu, { className: "w-6 h-6" })
          )
        )
      ),
      // Mobile Navigation
      React.createElement(
        AnimatePresence,
        null,
        isMobileMenuOpen &&
          React.createElement(
            motion.div,
            {
              variants: mobileMenuVariants,
              initial: "hidden",
              animate: "visible",
              exit: "exit",
              className:
                "md:hidden absolute top-full left-0 w-full bg-slate-50 dark:bg-slate-950 border-t border-slate-200/80 dark:border-slate-800/80",
            },
            React.createElement(
              "div",
              { className: "px-4 pt-4 pb-6 space-y-2" },
              ...createMobileNavLinks(),
              React.createElement(
                "div",
                {
                  className:
                    "pt-4 border-t border-slate-200 dark:border-slate-800 space-y-2",
                },
                // Only render buttons after loading is complete
                !loading &&
                  (currentUser
                    ? // Logged In Mobile
                      React.createElement(
                        React.Fragment,
                        null,
                        React.createElement(
                          "div",
                          {
                            className: "flex items-center px-3 py-2 space-x-3",
                          },
                          React.createElement(
                            "div",
                            {
                              className:
                                "w-8 h-8 flex items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500",
                            },
                            React.createElement(User, {
                              className: "w-4 h-4 text-white",
                            })
                          ),
                          React.createElement(
                            "span",
                            {
                              className:
                                "font-medium text-slate-700 dark:text-slate-200",
                            },
                            `Welcome, ${
                              currentUser.name || currentUser.username || "User"
                            }`
                          )
                        ),
                        React.createElement(
                          "button",
                          {
                            onClick: () => {
                              logout();
                              setIsMobileMenuOpen(false);
                            },
                            className:
                              "w-full flex items-center px-3 py-2 rounded-md text-base font-medium text-red-600 dark:text-red-500 hover:bg-red-500/10 transition-colors",
                          },
                          React.createElement(LogOut, {
                            className: "w-5 h-5 mr-2",
                          }),
                          "Logout"
                        )
                      )
                    : // Logged Out Mobile
                      React.createElement(
                        React.Fragment,
                        null,
                        React.createElement(
                          Link,
                          {
                            href: "/login",
                            className:
                              "block px-3 py-2 rounded-md text-base font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-900/5 dark:hover:bg-slate-100/5",
                          },
                          "Login"
                        ),
                        React.createElement(
                          Link,
                          {
                            href: "/register",
                            className:
                              "block w-full text-center px-3 py-3 rounded-md text-base font-semibold text-white bg-slate-900 hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200",
                          },
                          "Get Started"
                        )
                      ))
              )
            )
          )
      )
    )
  );
}
