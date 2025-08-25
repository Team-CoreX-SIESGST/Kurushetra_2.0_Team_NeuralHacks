import { useState, useEffect } from 'react';
import { Check, Star, Loader2 } from 'lucide-react';

export default function SubscriptionPlans({ 
  currentPlan, 
  onPlanSelect, 
  className = "" 
}) {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [subscribing, setSubscribing] = useState(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch('/api/subscription/plans', {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setPlans(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId, planName) => {
    if (subscribing || (currentPlan && currentPlan._id === planId)) return;

    setSubscribing(planId);
    try {
      const response = await fetch('/api/subscription/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ 
          planId,
          paymentId: `demo_${Date.now()}` // In production, this would come from payment gateway
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        onPlanSelect?.(data.data.plan);
        alert(`Successfully subscribed to ${planName} plan!`);
      } else {
        alert(`Failed to subscribe: ${data.message}`);
      }
    } catch (error) {
      console.error('Subscription error:', error);
      alert('Failed to subscribe. Please try again.');
    } finally {
      setSubscribing(null);
    }
  };

  const formatTokenLimit = (limit) => {
    if (limit === -1) return 'Unlimited';
    if (limit >= 10000000) return `${(limit / 10000000).toFixed(0)} crore`;
    if (limit >= 100000) return `${(limit / 100000).toFixed(0)} lakh`;
    return limit.toLocaleString();
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <Loader2 className="w-8 h-8 animate-spin text-slate-600" />
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
          Choose Your Plan
        </h2>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Select the perfect plan for your AI research needs
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {plans.map((plan) => {
          const isCurrentPlan = currentPlan && currentPlan._id === plan._id;
          const isSubscribing = subscribing === plan._id;
          
          return (
            <div
              key={plan._id}
              className={`relative rounded-2xl border-2 p-6 transition-all duration-200 hover:shadow-lg ${
                plan.popular
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                  : isCurrentPlan
                  ? 'border-green-500 bg-green-50 dark:bg-green-950/20'
                  : 'border-slate-200 bg-white dark:bg-slate-800 dark:border-slate-700'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <div className="flex items-center gap-1 rounded-full bg-blue-500 px-3 py-1 text-sm font-medium text-white">
                    <Star className="w-4 h-4 fill-current" />
                    Most Popular
                  </div>
                </div>
              )}

              {isCurrentPlan && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <div className="flex items-center gap-1 rounded-full bg-green-500 px-3 py-1 text-sm font-medium text-white">
                    <Check className="w-4 h-4" />
                    Current Plan
                  </div>
                </div>
              )}

              <div className="text-center">
                <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  {plan.name}
                </h3>
                
                <div className="mt-4">
                  <span className="text-4xl font-bold text-slate-900 dark:text-slate-100">
                    ₹{plan.price}
                  </span>
                  <span className="text-slate-600 dark:text-slate-400">/month</span>
                </div>

                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                  {formatTokenLimit(plan.tokenLimit)} tokens per month
                </p>
              </div>

              <ul className="mt-6 space-y-3">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-5 h-5 flex-shrink-0 text-green-500 mt-0.5" />
                    <span className="text-sm text-slate-700 dark:text-slate-300">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscribe(plan._id, plan.name)}
                disabled={isCurrentPlan || isSubscribing}
                className={`mt-8 w-full rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                  isCurrentPlan
                    ? 'bg-green-100 text-green-700 cursor-not-allowed dark:bg-green-900/30 dark:text-green-400'
                    : plan.popular
                    ? 'bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50'
                    : 'bg-slate-900 text-white hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200 disabled:opacity-50'
                } disabled:cursor-not-allowed`}
              >
                {isSubscribing ? (
                  <div className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Subscribing...
                  </div>
                ) : isCurrentPlan ? (
                  'Current Plan'
                ) : plan.price === 0 ? (
                  'Get Started Free'
                ) : (
                  `Subscribe to ${plan.name}`
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
