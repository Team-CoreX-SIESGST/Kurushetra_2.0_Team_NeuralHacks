"use client"
import { useState } from "react"
import { Check, Apple, ExternalLink } from "lucide-react"
import { Navbar } from "@/components/layout/Navbar"


export default function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState("monthly")

  const getPrice = (monthlyPrice) => {
    if (billingPeriod === "yearly") {
      return Math.round(monthlyPrice * 0.8) // 20% discount
    }
    return monthlyPrice
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 pt-16">
      <Navbar/>  
      <div className="max-w-6xl mx-auto mt-1">
        {/* Billing Toggle */}
        <div className="flex justify-center mb-12">
          <div className="flex bg-slate-800 rounded-lg p-1">
            <button
              onClick={() => setBillingPeriod("monthly")}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                billingPeriod === "monthly" ? "bg-indigo-500 text-white" : "text-slate-400 hover:text-white"
              }`}
            >
              MONTHLY
            </button>
            <button
              onClick={() => setBillingPeriod("yearly")}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                billingPeriod === "yearly" ? "bg-indigo-500 text-white" : "text-slate-400 hover:text-white"
              }`}
            >
              YEARLY (SAVE 20%)
            </button>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold mb-12 text-slate-50">Individual Plans</h1>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Hobby Plan */}
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl">
            <div className="mb-6">
              <h2 className="text-xl font-medium text-slate-400 mb-2">Hobby</h2>
              <div className="text-5xl font-bold mb-1 text-slate-50">Free</div>
            </div>

            <div className="mb-8">
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
          <div className="relative bg-gradient-to-br from-indigo-500 via-indigo-600 to-cyan-500 p-8 rounded-2xl overflow-hidden">
            <div className="relative z-10">
              <div className="mb-6">
                <h2 className="text-xl font-medium text-white mb-2">Pro</h2>
                <div className="flex items-baseline gap-1">
                  <span className="text-5xl font-bold text-white">${getPrice(20)}</span>
                  <span className="text-white/80">/{billingPeriod === "yearly" ? "yr" : "mo"}</span>
                </div>
              </div>

              <div className="mb-8">
                <h3 className="text-white/90 mb-4">Everything in Hobby, plus</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-white flex-shrink-0" />
                    <span className="text-white/90">Extended limits on Agent</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-white flex-shrink-0" />
                    <span className="text-white/90">Unlimited Tab completions</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-white flex-shrink-0" />
                    <span className="text-white/90">Access to Background Agents</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-white flex-shrink-0" />
                    <span className="text-white/90">Access to Bugbot</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-white flex-shrink-0" />
                    <span className="text-white/90">Access to maximum context windows</span>
                  </li>
                </ul>
              </div>

              <div className="flex gap-3">
                <button className="flex-1 bg-white text-slate-900 hover:bg-slate-100 font-medium px-4 py-2 rounded-md transition-colors">
                  Get Pro
                </button>
                <button className="text-white hover:bg-white/10 px-4 py-2 rounded-md flex items-center transition-colors">
                  More info
                  <ExternalLink className="w-4 h-4 ml-2" />
                </button>
              </div>
            </div>
          </div>

          {/* Ultra Plan */}
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl">
            <div className="mb-6">
              <h2 className="text-xl font-medium text-slate-400 mb-2">Ultra</h2>
              <div className="flex items-baseline gap-1">
                <span className="text-5xl font-bold text-slate-50">${getPrice(200)}</span>
                <span className="text-slate-500">/{billingPeriod === "yearly" ? "yr" : "mo"}</span>
              </div>
            </div>

            <div className="mb-8">
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
        </div>
      </div>
    </div>
  )
}