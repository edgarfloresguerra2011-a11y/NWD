import React, { useEffect, useState } from 'react';
import { Globe, Plus, Trash2, Shield, RefreshCw, CheckCircle, XCircle } from 'lucide-react';
import { domains } from '../lib/api';

interface Domain {
  id: number;
  domain_name: string;
  spf_status: string;
  dkim_status: string;
  dmarc_status: string;
  overall_ok: boolean;
  created_at: string;
}

export default function DNSChecker() {
  const [list, setList] = useState<Domain[]>([]);
  const [newDomain, setNewDomain] = useState('');
  const [loading, setLoading] = useState(true);
  const [checkingId, setCheckingId] = useState<number | null>(null);
  const [addLoading, setAddLoading] = useState(false);

  const fetchDomains = async () => {
    try {
      const data = await domains.list();
      setList(data as Domain[]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDomains(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDomain) return;
    setAddLoading(true);
    try {
      await domains.create(newDomain);
      setNewDomain('');
      fetchDomains();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setAddLoading(false);
    }
  };

  const handleCheckDns = async (id: number) => {
    setCheckingId(id);
    try {
      await domains.checkDns(id);
      fetchDomains();
    } catch (err) {
      console.error(err);
    } finally {
      setCheckingId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this domain?')) return;
    try {
      await domains.delete(id);
      fetchDomains();
    } catch (err) {
      console.error(err);
    }
  };

  const StatusBadge = ({ status }: { status: string }) => (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
      status === 'ok' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
    }`}>
      {status === 'ok' ? <CheckCircle size={10} /> : <XCircle size={10} />}
      {status === 'ok' ? 'Valid' : 'Missing'}
    </span>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">DNS Manager</h1>
        <p className="text-slate-400 text-sm mt-1">Verify SPF, DKIM, and DMARC records for your domains</p>
      </div>

      {/* Add domain */}
      <form onSubmit={handleAdd} className="flex gap-3">
        <input
          type="text"
          value={newDomain}
          onChange={(e) => setNewDomain(e.target.value)}
          placeholder="yourdomain.com"
          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
        <button
          type="submit"
          disabled={addLoading}
          className="flex items-center gap-2 px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-lg transition-colors text-sm font-medium"
        >
          <Plus size={16} />
          Add Domain
        </button>
      </form>

      {list.length === 0 ? (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-12 text-center">
          <Globe size={48} className="mx-auto text-slate-600 mb-4" />
          <h3 className="text-lg font-medium text-slate-300 mb-2">No domains added</h3>
          <p className="text-slate-400 text-sm">Add your sending domains to verify DNS records</p>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map((domain) => (
            <div
              key={domain.id}
              className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${domain.overall_ok ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                    {domain.overall_ok ? (
                      <CheckCircle size={18} className="text-green-400" />
                    ) : (
                      <XCircle size={18} className="text-red-400" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-white font-medium">{domain.domain_name}</h3>
                    <p className="text-xs text-slate-500">
                      {domain.overall_ok ? 'All DNS records valid' : 'DNS records need attention'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCheckDns(domain.id)}
                    disabled={checkingId === domain.id}
                    className="flex items-center gap-1 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-slate-300 rounded-lg transition-colors text-xs"
                  >
                    <RefreshCw size={12} className={checkingId === domain.id ? 'animate-spin' : ''} />
                    Check DNS
                  </button>
                  <button
                    onClick={() => handleDelete(domain.id)}
                    className="p-1.5 bg-red-600/20 text-red-400 hover:bg-red-600/30 rounded-lg transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-700/50">
                <div className="flex items-center gap-2">
                  <Shield size={12} className="text-slate-500" />
                  <span className="text-xs text-slate-400">SPF</span>
                  <StatusBadge status={domain.spf_status} />
                </div>
                <div className="flex items-center gap-2">
                  <Shield size={12} className="text-slate-500" />
                  <span className="text-xs text-slate-400">DKIM</span>
                  <StatusBadge status={domain.dkim_status} />
                </div>
                <div className="flex items-center gap-2">
                  <Shield size={12} className="text-slate-500" />
                  <span className="text-xs text-slate-400">DMARC</span>
                  <StatusBadge status={domain.dmarc_status} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
