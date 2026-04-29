import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Mail, Activity, TrendingUp, AlertTriangle, Play, Plus,
  BarChart3, Thermometer, Flame, Snowflake, Sun, Search,
  RefreshCw, Shield, CheckCircle, XCircle, MessageSquare,
} from 'lucide-react';
import { analytics, warmup } from '../lib/api';

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

interface WarmupScore {
  account_id: number;
  email: string;
  provider: string;
  status: string;
  warmup_score: number;
  warmup_label: string;
  reputation_score: number;
  open_rate: number;
  reply_rate: number;
  bounce_rate: number;
  spam_rate: number;
  days_warming: number;
  warmup_progress: number;
  inbox_placement_est: number;
}

interface SeedTestResult {
  account_id: number;
  email: string;
  inbox_placement_percent: number;
  spf_pass: boolean;
  dkim_pass: boolean;
  dmarc_pass: boolean;
  spam_score: number;
  recommendations: string[];
}

function WarmupBadge({ score }: { score: number }) {
  let color: string, icon: React.ReactNode, label: string;
  if (score >= 85) {
    color = 'bg-red-500/20 text-red-400 border-red-500/30';
    icon = <Flame size={14} />;
    label = 'Hot';
  } else if (score >= 60) {
    color = 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    icon = <Sun size={14} />;
    label = 'Warm';
  } else if (score >= 25) {
    color = 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
    icon = <Thermometer size={14} />;
    label = 'Warming';
  } else {
    color = 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    icon = <Snowflake size={14} />;
    label = 'Cold';
  }
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${color}`}>
      {icon} {label} ({score})
    </span>
  );
}

function ProgressBar({ value, color = 'bg-cyan-500' }: { value: number; color?: string }) {
  const safe = Math.min(Math.max(value, 0), 100);
  let barColor = color;
  if (value >= 85) barColor = 'bg-red-500';
  else if (value >= 60) barColor = 'bg-orange-500';
  else if (value >= 25) barColor = 'bg-cyan-500';
  else barColor = 'bg-blue-500';
  return (
    <div className="w-full bg-slate-700 rounded-full h-2">
      <div className={`${barColor} h-2 rounded-full transition-all duration-500`} style={{ width: `${safe}%` }} />
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [warmupStatus, setWarmupStatus] = useState<any>(null);
  const [warmupScores, setWarmupScores] = useState<WarmupScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [seedTesting, setSeedTesting] = useState<number | null>(null);
  const [seedResults, setSeedResults] = useState<Record<number, SeedTestResult>>({});

  const loadData = async () => {
    try {
      const [a, wu, ws] = await Promise.all([
        analytics.overview(),
        warmup.status(),
        analytics.warmupScores(),
      ]);
      setData(a as AnalyticsData);
      setWarmupStatus(wu);
      setWarmupScores(ws as WarmupScore[]);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const runSeedTest = async (accountId: number) => {
    setSeedTesting(accountId);
    try {
      const result = await analytics.seedTest(accountId, 'seed@mail-tester.com');
      setSeedResults(prev => ({ ...prev, [accountId]: result as SeedTestResult }));
    } catch (err) {
      console.error('Seed test error:', err);
    } finally {
      setSeedTesting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500" />
      </div>
    );
  }

  const overview = data?.overview;

  const stats = [
    { label: 'Email Accounts', value: overview?.total_accounts || 0, icon: Mail, color: 'text-blue-400 bg-blue-500/10' },
    { label: 'Active Warmups', value: overview?.active_warmups || 0, icon: Activity, color: 'text-green-400 bg-green-500/10' },
    { label: 'Avg Reputation', value: `${overview?.avg_reputation || 0}%`, icon: TrendingUp, color: 'text-cyan-400 bg-cyan-500/10' },
    { label: 'At Risk', value: overview?.accounts_at_risk || 0, icon: AlertTriangle, color: 'text-red-400 bg-red-500/10' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">🔥 Nexus Warmup Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Monitor and measure your email account temperature in real-time</p>
        </div>
        <div className="flex gap-3">
          <button onClick={loadData} className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors text-sm">
            <RefreshCw size={14} />
            Refresh
          </button>
          <Link to="/accounts/connect" className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm font-medium">
            <Plus size={16} />
            Add Account
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 hover:border-slate-600 transition-colors">
              <div className={`p-2 rounded-lg ${stat.color} inline-flex`}><Icon size={20} /></div>
              <p className="text-2xl font-bold text-white mt-3">{stat.value}</p>
              <p className="text-sm text-slate-400 mt-1">{stat.label}</p>
            </div>
          );
        })}
      </div>

      {/* Today's Metrics */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Today's Activity</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-slate-400 text-sm">Sent</p>
            <p className="text-2xl font-bold text-white">{overview?.total_sent_today || 0}</p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">Opens</p>
            <p className="text-2xl font-bold text-white">{overview?.total_opens_today || 0}</p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">Replies</p>
            <p className="text-2xl font-bold text-white">{overview?.total_replies_today || 0}</p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">Open Rate</p>
            <p className="text-2xl font-bold text-cyan-400">{overview?.avg_open_rate || 0}%</p>
          </div>
        </div>
      </div>

      {/* Warmup Scores - Account Temperature */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Thermometer size={20} className="text-cyan-400" />
            Account Temperature
          </h2>
          {warmupStatus && (
            <div className="flex gap-4 text-xs">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Stable: {warmupStatus.stable}</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500" /> Warming: {warmupStatus.warming}</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Risk: {warmupStatus.risk}</span>
            </div>
          )}
        </div>

        {warmupScores.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <Mail size={40} className="mx-auto mb-3 opacity-50" />
            <p>No accounts yet. Connect your first email account to start warming up.</p>
            <Link to="/accounts/connect" className="inline-block mt-3 px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm hover:bg-cyan-500 transition-colors">
              Connect Account
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {warmupScores.map((acct) => {
              const seed = seedResults[acct.account_id];
              return (
                <div key={acct.account_id} className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-5 hover:border-slate-600 transition-all">
                  {/* Row 1: Account info + score */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${
                        acct.warmup_score >= 85 ? 'bg-red-500/10' :
                        acct.warmup_score >= 60 ? 'bg-orange-500/10' :
                        acct.warmup_score >= 25 ? 'bg-cyan-500/10' : 'bg-blue-500/10'
                      }`}>
                        {acct.warmup_score >= 85 ? <Flame size={18} className="text-red-400" /> :
                         acct.warmup_score >= 60 ? <Sun size={18} className="text-orange-400" /> :
                         acct.warmup_score >= 25 ? <Thermometer size={18} className="text-cyan-400" /> :
                         <Snowflake size={18} className="text-blue-400" />}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-white font-medium">{acct.email}</p>
                          <WarmupBadge score={acct.warmup_score} />
                        </div>
                        <p className="text-xs text-slate-500">
                          {acct.provider} · {acct.days_warming} days warming · {acct.status}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => runSeedTest(acct.account_id)}
                      disabled={seedTesting === acct.account_id}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition-colors disabled:opacity-50"
                    >
                      {seedTesting === acct.account_id ? (
                        <RefreshCw size={12} className="animate-spin" />
                      ) : (
                        <Search size={12} />
                      )}
                      Seed Test
                    </button>
                  </div>

                  {/* Row 2: Progress bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Warmup Progress</span>
                      <span>{acct.warmup_score}/100</span>
                    </div>
                    <ProgressBar value={acct.warmup_score} />
                  </div>

                  {/* Row 3: Metrics grid */}
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
                    <div className="bg-slate-800/50 rounded-lg p-2">
                      <p className="text-xs text-slate-500">Reputation</p>
                      <p className="text-sm font-semibold text-white">{acct.reputation_score}%</p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-2">
                      <p className="text-xs text-slate-500">Open Rate</p>
                      <p className="text-sm font-semibold text-cyan-400">{acct.open_rate}%</p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-2">
                      <p className="text-xs text-slate-500">Reply Rate</p>
                      <p className="text-sm font-semibold text-green-400">{acct.reply_rate}%</p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-2">
                      <p className="text-xs text-slate-500">Bounce</p>
                      <p className={`text-sm font-semibold ${acct.bounce_rate > 0.05 ? 'text-red-400' : 'text-slate-300'}`}>
                        {acct.bounce_rate}%
                      </p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-2">
                      <p className="text-xs text-slate-500">Inbox Est.</p>
                      <p className="text-sm font-semibold text-cyan-300">{acct.inbox_placement_est}%</p>
                    </div>
                  </div>

                  {/* Row 4: Seed test results (collapsible) */}
                  {seed && (
                    <div className="mt-4 bg-slate-900/80 border border-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-medium text-white flex items-center gap-2">
                          <Shield size={14} className="text-cyan-400" />
                          Seed Test Results
                        </h4>
                        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                          seed.inbox_placement_percent >= 80 ? 'bg-green-500/20 text-green-400' :
                          seed.inbox_placement_percent >= 50 ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {seed.inbox_placement_percent}% Inbox
                        </span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                        <div className="flex items-center gap-2 text-xs">
                          {seed.spf_pass ? <CheckCircle size={14} className="text-green-400" /> : <XCircle size={14} className="text-red-400" />}
                          <span className="text-slate-400">SPF: {seed.spf_pass ? 'Pass' : 'Fail'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          {seed.dkim_pass ? <CheckCircle size={14} className="text-green-400" /> : <XCircle size={14} className="text-red-400" />}
                          <span className="text-slate-400">DKIM: {seed.dkim_pass ? 'Pass' : 'Fail'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          {seed.dmarc_pass ? <CheckCircle size={14} className="text-green-400" /> : <XCircle size={14} className="text-red-400" />}
                          <span className="text-slate-400">DMARC: {seed.dmarc_pass ? 'Pass' : 'Fail'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          <MessageSquare size={14} className="text-slate-400" />
                          <span className="text-slate-400">Spam Score: {seed.spam_score}/3</span>
                        </div>
                      </div>
                      {seed.recommendations.length > 0 && (
                        <div>
                          <p className="text-xs text-slate-500 mb-1">Recommendations:</p>
                          <ul className="space-y-1">
                            {seed.recommendations.map((rec, i) => (
                              <li key={i} className="text-xs text-yellow-400 flex items-start gap-1.5">
                                <span>•</span>
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Provider breakdown */}
      {data?.provider_breakdown && data.provider_breakdown.length > 0 && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Provider Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.provider_breakdown.map((p) => (
              <div key={p.provider} className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
                <p className="text-sm font-medium text-white capitalize mb-1">{p.provider}</p>
                <p className="text-2xl font-bold text-cyan-400">{p.count}</p>
                <p className="text-xs text-slate-500">accounts · {p.avg_reputation}% avg rep</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
