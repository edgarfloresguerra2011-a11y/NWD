import React, { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, TrendingDown, Mail, Send, Reply, AlertTriangle } from 'lucide-react';
import { analytics } from '../lib/api';

interface AnalyticsData {
  overview: {
    total_accounts: number;
    active_warmups: number;
    avg_reputation: number;
    running_campaigns: number;
    total_sent_today: number;
    total_opens_today: number;
    total_replies_today: number;
    avg_open_rate: number;
    avg_reply_rate: number;
    accounts_at_risk: number;
  };
  reputation_trends: { date: string; score: number }[];
  provider_breakdown: { provider: string; count: number; avg_reputation: number }[];
}

export default function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analytics.overview().then((d) => {
      setData(d as AnalyticsData);
    }).catch(console.error)
    .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500" />
      </div>
    );
  }

  const o = data?.overview;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-slate-400 text-sm mt-1">Email infrastructure performance metrics</p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-1">
            <Send size={14} />
            Sent Today
          </div>
          <p className="text-2xl font-bold text-white">{o?.total_sent_today || 0}</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-1">
            <Mail size={14} />
            Open Rate
          </div>
          <p className="text-2xl font-bold text-cyan-400">{o?.avg_open_rate || 0}%</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-1">
            <Reply size={14} />
            Reply Rate
          </div>
          <p className="text-2xl font-bold text-cyan-400">{o?.avg_reply_rate || 0}%</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-1">
            <AlertTriangle size={14} />
            Accounts at Risk
          </div>
          <p className={`text-2xl font-bold ${(o?.accounts_at_risk || 0) > 0 ? 'text-red-400' : 'text-green-400'}`}>
            {o?.accounts_at_risk || 0}
          </p>
        </div>
      </div>

      {/* Reputation trend */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Reputation Trend (30 days)</h2>
        <div className="flex items-end gap-1 h-40">
          {data?.reputation_trends?.map((point, i) => {
            const height = Math.max(8, (point.score / 100) * 140);
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className="w-full bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t"
                  style={{ height: `${height}px` }}
                  title={`${point.date}: ${point.score}%`}
                />
                {i % 7 === 0 && (
                  <span className="text-[10px] text-slate-500">{point.date.slice(5)}</span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Provider breakdown */}
      {data?.provider_breakdown && data.provider_breakdown.length > 0 && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Provider Performance</h2>
          <div className="space-y-4">
            {data.provider_breakdown.map((p) => (
              <div key={p.provider} className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium capitalize">{p.provider}</p>
                  <p className="text-sm text-slate-400">{p.count} accounts</p>
                </div>
                <div className="text-right">
                  <p className="text-cyan-400 font-bold">{p.avg_reputation}%</p>
                  <p className="text-xs text-slate-500">avg reputation</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
