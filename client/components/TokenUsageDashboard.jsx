import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp, Calendar, AlertCircle, Loader2 } from 'lucide-react';

export default function TokenUsageDashboard({ className = "" }) {
  const [subscription, setSubscription] = useState(null);
  const [usageStats, setUsageStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('30');

  useEffect(() => {
    fetchData();
  }, [period]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch current subscription
      const subscriptionResponse = await fetch('/api/subscription/current', {
        credentials: 'include'
      });
      const subscriptionData = await subscriptionResponse.json();
      
      // Fetch usage statistics
      const usageResponse = await fetch(`/api/subscription/usage-stats?period=${period}`, {
        credentials: 'include'
      });
      const usageData = await usageResponse.json();

      if (subscriptionData.success) {
        setSubscription(subscriptionData.data);
      }
      
      if (usageData.success) {
        setUsageStats(usageData.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTokens = (tokens) => {
    if (tokens >= 10000000) return `${(tokens / 10000000).toFixed(1)}Cr`;
    if (tokens >= 100000) return `${(tokens / 100000).toFixed(1)}L`;
    if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}K`;
    return tokens.toString();
  };

  const getUsagePercentage = () => {
    if (!subscription || subscription.plan.tokenLimit === -1) return 0;
    return (subscription.tokensUsed / subscription.plan.tokenLimit) * 100;
  };

  const getUsageColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'text-red-500 bg-red-100 dark:bg-red-900/30';
    if (percentage >= 70) return 'text-orange-500 bg-orange-100 dark:bg-orange-900/30';
    return 'text-green-500 bg-green-100 dark:bg-green-900/30';
  };

  const getProgressBarColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-orange-500';
    return 'bg-green-500';
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Usage Dashboard
          </h2>
          <p className="text-slate-600 dark:text-slate-400">
            Monitor your token usage and subscription details
          </p>
        </div>
        
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </select>
      </div>

      {/* Current Plan & Usage */}
      {subscription && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Current Plan */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                Current Plan
              </h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Plan:</span>
                <span className="font-medium text-slate-900 dark:text-slate-100">
                  {subscription.plan.name}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Monthly Limit:</span>
                <span className="font-medium text-slate-900 dark:text-slate-100">
                  {subscription.plan.tokenLimit === -1 ? 'Unlimited' : formatTokens(subscription.plan.tokenLimit)}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Status:</span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  subscription.subscriptionStatus === 'active'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                }`}>
                  {subscription.subscriptionStatus}
                </span>
              </div>
            </div>
          </div>

          {/* Usage Overview */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className={`p-2 rounded-lg ${getUsageColor()}`}>
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                Token Usage
              </h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Used:</span>
                <span className="font-medium text-slate-900 dark:text-slate-100">
                  {formatTokens(subscription.tokensUsed)}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Remaining:</span>
                <span className="font-medium text-slate-900 dark:text-slate-100">
                  {subscription.tokensRemaining === -1 ? 'Unlimited' : formatTokens(subscription.tokensRemaining)}
                </span>
              </div>
              
              {subscription.plan.tokenLimit !== -1 && (
                <>
                  <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${getProgressBarColor()}`}
                      style={{ width: `${Math.min(getUsagePercentage(), 100)}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-600 dark:text-slate-400">
                      {getUsagePercentage().toFixed(1)}% used
                    </span>
                    {getUsagePercentage() >= 90 && (
                      <div className="flex items-center gap-1 text-red-500">
                        <AlertCircle className="w-4 h-4" />
                        <span>Low tokens</span>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Usage Chart */}
      {usageStats && usageStats.dailyUsage.length > 0 && (
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
              <Calendar className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                Daily Usage ({period} days)
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Total tokens used: {formatTokens(usageStats.totalTokensInPeriod)}
              </p>
            </div>
          </div>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={usageStats.dailyUsage}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis 
                  dataKey="_id" 
                  tick={{ fontSize: 12 }}
                  axisLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  axisLine={false}
                  tickFormatter={(value) => formatTokens(value)}
                />
                <Tooltip 
                  formatter={(value) => [formatTokens(value), 'Tokens']}
                  labelFormatter={(label) => `Date: ${label}`}
                  contentStyle={{
                    backgroundColor: 'var(--tooltip-bg)',
                    border: '1px solid var(--tooltip-border)',
                    borderRadius: '8px'
                  }}
                />
                <Bar 
                  dataKey="totalTokens" 
                  fill="#3b82f6" 
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-4">
        <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
          Upgrade Plan
        </button>
        <button className="px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
          View Billing History
        </button>
        <button 
          onClick={fetchData}
          className="px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
        >
          Refresh Data
        </button>
      </div>
    </div>
  );
}
