import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Mail, Play, Pause, Trash2, Shield, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { accounts } from '../lib/api';

interface Account {
  id: number;
  email: string;
  provider: string;
  status: string;
  reputation_score: number;
  warmup_progress: number;
  spam_rate: number;
  bounce_rate: number;
  created_at: string;
}

export default function AccountList() {
  const [list, setList] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAccounts = async () => {
    try {
      const data = await accounts.list();
      setList(data as Account[]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAccounts(); }, []);

  const handleStartWarmup = async (id: number) => {
    try {
      await accounts.startWarmup(id);
      fetchAccounts();
    } catch (err) {
      console.error(err);
    }
  };

  const handlePauseWarmup = async (id: number) => {
    try {
      await accounts.pauseWarmup(id);
      fetchAccounts();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this account?')) return;
    try {
      await accounts.delete(id);
      fetchAccounts();
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'stable': return <CheckCircle size={14} className="text-green-400" />;
      case 'warming': return <Play size={14} className="text-yellow-400" />;
      case 'paused': return <Pause size={14} className="text-slate-400" />;
      case 'risk': return <AlertTriangle size={14} className="text-red-400" />;
      case 'error': return <AlertTriangle size={14} className="text-red-500" />;
      default: return <Clock size={14} className="text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'stable': return 'text-green-400';
      case 'warming': return 'text-yellow-400';
      case 'paused': return 'text-slate-400';
      case 'risk': return 'text-red-400';
      case 'error': return 'text-red-500';
      default: return 'text-slate-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Email Accounts</h1>
          <p className="text-slate-400 text-sm mt-1">
            Connect and manage your email accounts
          </p>
        </div>
        <Link
          to="/accounts/connect"
          className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm font-medium"
        >
          <Plus size={16} />
          Connect Account
        </Link>
      </div>

      {list.length === 0 ? (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-12 text-center">
          <Mail size={48} className="mx-auto text-slate-600 mb-4" />
          <h3 className="text-lg font-medium text-slate-300 mb-2">No accounts connected</h3>
          <p className="text-slate-400 text-sm mb-6">
            Connect your first email account to start warming
          </p>
          <Link
            to="/accounts/connect"
            className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm font-medium"
          >
            <Plus size={16} />
            Connect Account
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map((account) => (
            <div
              key={account.id}
              className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-slate-700 rounded-lg">
                    <Mail size={18} className="text-slate-300" />
                  </div>
                  <div>
                    <h3 className="text-white font-medium">{account.email}</h3>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs text-slate-500 uppercase">{account.provider}</span>
                      <span className={`flex items-center gap-1 text-xs ${getStatusColor(account.status)}`}>
                        {getStatusIcon(account.status)}
                        {account.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {account.status === 'connecting' && (
                    <button
                      onClick={() => handleStartWarmup(account.id)}
                      className="p-2 bg-green-600/20 text-green-400 hover:bg-green-600/30 rounded-lg transition-colors"
                      title="Start warmup"
                    >
                      <Play size={16} />
                    </button>
                  )}
                  {(account.status === 'warming' || account.status === 'stable') && (
                    <button
                      onClick={() => handlePauseWarmup(account.id)}
                      className="p-2 bg-yellow-600/20 text-yellow-400 hover:bg-yellow-600/30 rounded-lg transition-colors"
                      title="Pause warmup"
                    >
                      <Pause size={16} />
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(account.id)}
                    className="p-2 bg-red-600/20 text-red-400 hover:bg-red-600/30 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-slate-700/50">
                <div>
                  <p className="text-xs text-slate-500">Reputation</p>
                  <p className="text-sm font-medium text-white">{account.reputation_score}%</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Warmup Progress</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-cyan-500 rounded-full transition-all"
                        style={{ width: `${account.warmup_progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-400">{Math.round(account.warmup_progress)}%</span>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Spam Rate</p>
                  <p className={`text-sm font-medium ${account.spam_rate > 0.003 ? 'text-red-400' : 'text-green-400'}`}>
                    {(account.spam_rate * 100).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Bounce Rate</p>
                  <p className={`text-sm font-medium ${account.bounce_rate > 0.05 ? 'text-red-400' : 'text-green-400'}`}>
                    {(account.bounce_rate * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
