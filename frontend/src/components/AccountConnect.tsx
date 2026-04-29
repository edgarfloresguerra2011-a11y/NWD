import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Server, Key } from 'lucide-react';
import { accounts } from '../lib/api';

export default function AccountConnect() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: '',
    provider: 'smtp',
    smtp_host: '',
    smtp_port: '587',
    imap_host: '',
    imap_port: '993',
    smtp_username: '',
    smtp_password: '',
    warmup_max_per_day: '50',
    warmup_reply_rate: '0.05',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await accounts.create({
        email: form.email,
        provider: form.provider,
        smtp_host: form.smtp_host || undefined,
        smtp_port: form.smtp_port ? parseInt(form.smtp_port) : undefined,
        imap_host: form.imap_host || undefined,
        imap_port: form.imap_port ? parseInt(form.imap_port) : undefined,
        smtp_username: form.smtp_username || undefined,
        smtp_password: form.smtp_password || undefined,
        warmup_max_per_day: parseInt(form.warmup_max_per_day),
        warmup_reply_rate: parseFloat(form.warmup_reply_rate),
      });
      navigate('/accounts');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/accounts')}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">Connect Account</h1>
          <p className="text-slate-400 text-sm mt-1">
            Add an email account for warmup and campaigns
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Provider Selection */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Email Provider</label>
          <div className="grid grid-cols-3 gap-3">
            {['smtp', 'gmail', 'outlook'].map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setForm({ ...form, provider: p })}
                className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                  form.provider === p
                    ? 'border-cyan-500 bg-cyan-500/10 text-cyan-400'
                    : 'border-slate-700 bg-slate-800 text-slate-400 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <Server size={16} />
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Email Address</label>
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            placeholder="sender@yourdomain.com"
            required
          />
        </div>

        {/* SMTP Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">SMTP Host</label>
            <input
              type="text"
              value={form.smtp_host}
              onChange={(e) => setForm({ ...form, smtp_host: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              placeholder="smtp.yourdomain.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">SMTP Port</label>
            <input
              type="number"
              value={form.smtp_port}
              onChange={(e) => setForm({ ...form, smtp_port: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">IMAP Host</label>
            <input
              type="text"
              value={form.imap_host}
              onChange={(e) => setForm({ ...form, imap_host: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              placeholder="imap.yourdomain.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">IMAP Port</label>
            <input
              type="number"
              value={form.imap_port}
              onChange={(e) => setForm({ ...form, imap_port: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">SMTP Username</label>
            <input
              type="text"
              value={form.smtp_username}
              onChange={(e) => setForm({ ...form, smtp_username: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              placeholder="sender@yourdomain.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">SMTP Password</label>
            <input
              type="password"
              value={form.smtp_password}
              onChange={(e) => setForm({ ...form, smtp_password: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              placeholder="App password"
            />
          </div>
        </div>

        {/* Warmup config */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Max Emails/Day</label>
            <input
              type="number"
              value={form.warmup_max_per_day}
              onChange={(e) => setForm({ ...form, warmup_max_per_day: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
              max="500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Target Reply Rate</label>
            <input
              type="number"
              step="0.01"
              value={form.warmup_reply_rate}
              onChange={(e) => setForm({ ...form, warmup_reply_rate: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors"
        >
          {loading ? 'Connecting...' : 'Connect Account'}
        </button>
      </form>
    </div>
  );
}
