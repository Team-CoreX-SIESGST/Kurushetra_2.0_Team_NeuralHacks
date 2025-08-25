"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Check, Apple, ExternalLink, Sparkles } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import {
  getPlans,
  createSubscriptionOrder,
  verifySubscriptionPayment,
  subscribeToPlan,
} from "@/services/subscription/subscription";

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
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingPlan, setProcessingPlan] = useState(null);

  const formatPrice = (price) => {
    if (price === 0) return "Free";
    return `₹${price.toLocaleString("en-IN")}`;
  };

  const formatTokenLimit = (tokenLimit) => {
    if (tokenLimit === -1) return "Unlimited tokens";
    if (tokenLimit >= 1000000) {
      return `${tokenLimit / 1000000} million tokens per month`;
    }
    return `${tokenLimit.toLocaleString()} tokens per month`;
  };

  const loadRazorpay = () => {
    return new Promise((resolve) => {
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handleSubscription = async (plan) => {
    try {
      setProcessingPlan(plan._id);

      // For free plan, subscribe directly
      if (plan.price === 0) {
        const response = await subscribeToPlan(plan._id);
        if (response.data) {
          alert("Successfully subscribed to free plan!");
        } else {
          alert("Failed to subscribe: " + response.message);
        }
        setProcessingPlan(null);
        return;
      }

      // For paid plans, create Razorpay order
      const orderResponse = await createSubscriptionOrder(plan._id);

      if (!orderResponse.status) {
        alert("Failed to create order: " + orderResponse.message);
        setProcessingPlan(null);
        return;
      }

      const razorpayOrder = orderResponse.data;

      // Load Razorpay script
      const isLoaded = await loadRazorpay();
      if (!isLoaded) {
        alert("Razorpay SDK failed to load");
        setProcessingPlan(null);
        return;
      }

      // Initialize Razorpay payment
      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
        amount: razorpayOrder.amount,
        currency: razorpayOrder.currency,
        order_id: razorpayOrder.id,
        name: "AI Assistant Pro",
        description: `Subscription for ${plan.name} Plan`,
        handler: async function (response) {
          try {
            // Verify payment
            const verificationResponse = await verifySubscriptionPayment({
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verificationResponse.status) {
              alert("Payment successful! Your subscription is now active.");
            } else {
              alert(
                "Payment verification failed: " + verificationResponse.message
              );
            }
          } catch (error) {
            console.error("Payment verification error:", error);
            alert("Payment verification failed");
          } finally {
            setProcessingPlan(null);
          }
        },
        prefill: {
          name: "Customer Name", // You might want to get this from user profile
          email: "customer@example.com", // You might want to get this from user profile
          contact: "9999999999",
        },
        theme: {
          color: "#3399cc",
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (error) {
      console.error("Subscription error:", error);
      alert(
        "Subscription failed: " +
          (error.response?.data?.message || error.message)
      );
      setProcessingPlan(null);
    }
  };

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const responseData = await getPlans();
        // if (responseData.status && responseData.data) {
          const sortedPlans = responseData.data.sort(
            (a, b) => a.price - b.price
          );
          setPlans(sortedPlans);
        // }
      } catch (err) {
        console.log("Error fetching plans:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  if (loading) {
    return (
      <div className="bg-slate-950 text-white min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

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
            <p className="text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto ">
              Start for free, then upgrade to unlock powerful features. Save 20%
              with our annual plans.
            </p>
          </motion.div>

          {/* Pricing Cards */}
          <motion.div
            variants={FADE_IN_UP_VARIANTS}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {plans.map((plan, index) => {
              const isPopular = plan.popular || plan.name === "Pro";
              const isFree = plan.price === 0;

              return (
                <div
                  key={plan._id}
                  className={`relative bg-slate-900 p-8 rounded-2xl flex flex-col ${
                    isPopular
                      ? "border-2 border-indigo-500 shadow-2xl shadow-indigo-500/10"
                      : "border border-slate-800"
                  }`}
                >
                  {isPopular && (
                    <div className="absolute top-0 -translate-y-1/2 w-full left-0 flex justify-center">
                      <div className="bg-indigo-500 text-white text-xs font-semibold px-4 py-1 rounded-full">
                        MOST POPULAR
                      </div>
                    </div>
                  )}

                  <div className="mb-6">
                    <h2
                      className={`text-xl font-medium mb-2 ${
                        isPopular ? "text-indigo-400" : "text-slate-400"
                      }`}
                    >
                      {plan.name}
                    </h2>
                    <div className="flex items-baseline gap-2">
                      <span
                        className={`text-5xl font-bold ${
                          isPopular ? "text-white" : "text-slate-50"
                        }`}
                      >
                        {formatPrice(plan.price)}
                      </span>
                      {!isFree && (
                        <span className="text-slate-400">/month</span>
                      )}
                    </div>
                  </div>

                  <div className="mb-8 flex-grow">
                    <h3
                      className={`mb-4 ${
                        isPopular ? "text-slate-300" : "text-slate-400"
                      }`}
                    >
                      {index === 0
                        ? "Includes"
                        : `Everything in ${plans[index - 1]?.name}, plus`}
                    </h3>
                    <ul className="space-y-3">
                      {/* Add token limit as first feature */}
                      <li className="flex items-center gap-3">
                        <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                        <span
                          className={
                            isPopular ? "text-slate-300" : "text-slate-400"
                          }
                        >
                          {formatTokenLimit(plan.tokenLimit)}
                        </span>
                      </li>

                      {plan.features.map((feature, featureIndex) => (
                        <li
                          className="flex items-center gap-3"
                          key={featureIndex}
                        >
                          <Check className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                          <span
                            className={
                              isPopular ? "text-slate-300" : "text-slate-400"
                            }
                          >
                            {feature}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex gap-3">
                    {isFree ? (
                      <>
                        <button
                          onClick={() => handleSubscription(plan)}
                          disabled={processingPlan === plan._id}
                          className="flex-1 bg-white text-slate-900 hover:bg-slate-100 font-medium px-4 py-2 rounded-md flex items-center justify-center transition-colors disabled:opacity-50"
                        >
                          {processingPlan === plan._id ? (
                            "Processing..."
                          ) : (
                            <>
                              <Apple className="w-4 h-4 mr-2" />
                              Get Started
                            </>
                          )}
                        </button>
                        <button className="bg-transparent border border-slate-700 text-slate-400 hover:bg-slate-800 hover:text-white px-4 py-2 rounded-md transition-colors">
                          Others
                        </button>
                      </>
                    ) : isPopular ? (
                      <>
                        <button
                          onClick={() => handleSubscription(plan)}
                          disabled={processingPlan === plan._id}
                          className="flex-1 bg-indigo-500 text-white hover:bg-indigo-600 font-medium px-4 py-2 rounded-md transition-colors disabled:opacity-50"
                        >
                          {processingPlan === plan._id
                            ? "Processing..."
                            : `Get ${plan.name}`}
                        </button>
                        <button className="text-slate-300 hover:bg-slate-800 px-4 py-2 rounded-md flex items-center transition-colors">
                          More info
                          <ExternalLink className="w-4 h-4 ml-2" />
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => handleSubscription(plan)}
                        disabled={processingPlan === plan._id}
                        className="flex-1 bg-white text-slate-900 hover:bg-slate-100 font-medium px-4 py-2 rounded-md transition-colors disabled:opacity-50"
                      >
                        {processingPlan === plan._id
                          ? "Processing..."
                          : `Get ${plan.name}`}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </motion.div>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}
