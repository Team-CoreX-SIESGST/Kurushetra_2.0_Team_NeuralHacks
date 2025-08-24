"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Check, Apple, ExternalLink, Sparkles } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

// Animation variants from the reference page
const FADE_IN_STAGGER_VARIANTS = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const FADE_IN_UP_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
};

export default function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState("monthly");

  const getPrice = (monthlyPrice) => {
    // Apply a 20% discount for yearly billing
    return billingPeriod === "yearly" ? monthlyPrice * 12 * 0.8 : monthlyPrice;
  };

  return (
    <div className="bg-slate-950 text-white">
      <Navbar />
      <main className="relative overflow-hidden py-16 sm:py-20">
        <div
          className="absolute inset-0 -z-10 bg-[radial-gradient(45rem_45rem_at_50%_50%,_theme(colors.indigo.950/40%),_theme(colors.slate.950))]"
          aria-hidden="true"
        />
        <motion.div
          initial="hidden"
          animate="show"
          variants={FADE_IN_STAGGER_VARIANTS}
          className="max-w-7xl mx-auto px-6 lg:px-8 space-y-16 sm:space-y-20"
        >
          {/* Hero Section */}
          <motion.div variants={FADE_IN_UP_VARIANTS} className="text-center">
            <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-slate-100/5 ring-1 ring-inset ring-slate-100/10 mb-8 backdrop-blur-lg">
              <Sparkles className="w-4 h-4 text-indigo-400 mr-2" />
              <span className="text-sm font-medium text-slate-300">
                Simple & Transparent Pricing
              </span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent mb-6">
              Find the Right Plan for You
            </h1>
            <p className="text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto">
              Start for free, then upgrade to unlock powerful features. Save 20%
              with our annual plans.
            </p>
          </motion.div>

          {/* Billing Toggle */}
          <motion.div
            variants={FADE_IN_UP_VARIANTS}
            className="flex justify-center"
          >
            <div className="flex bg-slate-900/80 ring-1 ring-slate-100/10 backdrop-blur-lg rounded-lg p-1">
              <button
                onClick={() => setBillingPeriod("monthly")}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors relative ${
                  billingPeriod === "monthly"
                    ? "text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {billingPeriod === "monthly" && (
                  <motion.div
                    layoutId="billing-pill"
                    className="absolute inset-0 bg-indigo-500 rounded-md"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <span className="relative z-10">MONTHLY</span>
              </button>
              <button
                onClick={() => setBillingPeriod("yearly")}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors relative ${
                  billingPeriod === "yearly"
                    ? "text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {billingPeriod === "yearly" && (
                  <motion.div
                    layoutId="billing-pill"
                    className="absolute inset-0 bg-indigo-500 rounded-md"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <span className="relative z-10">YEARLY (SAVE 20%)</span>
              </button>
            </div>
          </motion.div>

          {/* Pricing Cards */}
          <motion.div
            variants={FADE_IN_UP_VARIANTS}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {/* Hobby Plan */}
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl flex flex-col">
              <div className="mb-6">
                <h2 className="text-xl font-medium text-slate-400 mb-2">Hobby</h2>
                <div className="text-5xl font-bold mb-1 text-slate-50">Free</div>
              </div>
              <div className="mb-8 flex-grow">
                <h3 className="text-slate-400 mb-4">Includes</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                    <span className="text-slate-400">Pro two-week trial</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                    <span className="text-slate-400">Limited Agent requests</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                    <span className="text-slate-400">Limited Tab completions</span>
                  </li>
                </ul>
              </div>
              <div className="flex gap-3">
                <button className="flex-1 bg-white text-slate-900 hover:bg-slate-100 font-medium px-4 py-2 rounded-md flex items-center justify-center transition-colors">
                  <Apple className="w-4 h-4 mr-2" />
                  Download
                </button>
                <button className="bg-transparent border border-slate-700 text-slate-400 hover:bg-slate-800 hover:text-white px-4 py-2 rounded-md transition-colors">
                  Others
                </button>
              </div>
            </div>

            {/* Pro Plan */}
            <div className="relative bg-slate-900 border-2 border-indigo-500 p-8 rounded-2xl flex flex-col shadow-2xl shadow-indigo-500/10">
              <div className="absolute top-0 -translate-y-1/2 w-full left-0 flex justify-center">
                  <div className="bg-indigo-500 text-white text-xs font-semibold px-4 py-1 rounded-full">MOST POPULAR</div>
              </div>
              <div className="mb-6">
                <h2 className="text-xl font-medium text-indigo-400 mb-2">Pro</h2>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-white">${getPrice(20)}</span>
                  <span className="text-slate-400">/{billingPeriod === "yearly" ? "year" : "month"}</span>
                </div>
              </div>
              <div className="mb-8 flex-grow">
                <h3 className="text-slate-300 mb-4">Everything in Hobby, plus</h3>
                <ul className="space-y-3">
                    {[
                        "Extended limits on Agent",
                        "Unlimited Tab completions",
                        "Access to Background Agents",
                        "Access to Bugbot",
                        "Access to maximum context windows"
                    ].map(feature => (
                        <li className="flex items-center gap-3" key={feature}>
                            <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                            <span className="text-slate-300">{feature}</span>
                        </li>
                    ))}
                </ul>
              </div>
              <div className="flex gap-3">
                <button className="flex-1 bg-indigo-500 text-white hover:bg-indigo-600 font-medium px-4 py-2 rounded-md transition-colors">
                  Get Pro
                </button>
                <button className="text-slate-300 hover:bg-slate-800 px-4 py-2 rounded-md flex items-center transition-colors">
                  More info
                  <ExternalLink className="w-4 h-4 ml-2" />
                </button>
              </div>
            </div>

            {/* Ultra Plan */}
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl flex flex-col">
              <div className="mb-6">
                <h2 className="text-xl font-medium text-slate-400 mb-2">Ultra</h2>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-slate-50">${getPrice(200)}</span>
                  <span className="text-slate-500">/{billingPeriod === "yearly" ? "year" : "month"}</span>
                </div>
              </div>
              <div className="mb-8 flex-grow">
                <h3 className="text-slate-400 mb-4">Everything in Pro, plus</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                    <span className="text-slate-400">20x usage on all OpenAI, Claude, Gemini models</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                    <span className="text-slate-400">Priority access to new features</span>
                  </li>
                </ul>
              </div>
              <div className="flex gap-3">
                <button className="flex-1 bg-white text-slate-900 hover:bg-slate-100 font-medium px-4 py-2 rounded-md transition-colors">
                  Get Ultra
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}