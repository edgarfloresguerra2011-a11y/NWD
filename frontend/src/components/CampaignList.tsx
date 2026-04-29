import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Send, BarChart3, Play, Pause, Trash2 } from 'lucide-react';
import { campaigns } from '../lib/api';

interface CampaignStep {
  id: number;
  step_order: number;
  subject: string | null;
  delay_hours: number;
}

interface Campaign {
  id: number;
  name: string;
  status: string;
  sent_count: number;
  open_count: number;
  reply_count: number;
  open_rate: number;
  reply_rate: number;
  steps: CampaignStep[];
  created_at: string;
}

export default function CampaignList() {
  const [list, setList] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCampaigns = async () => {
    try {
      const data = await campaigns.list();
      setList(data as Campaign[]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCampaigns(); }, []);

  const handleLaunch = async (id: number) => {
    try {
      await campaigns.launch(id);
      fetchCampaigns();
    } catch (err) {
      console.error(err);
    }
  };

  const handlePause = async (id: number) => {
    try {
      await campaigns.pause(id);
      fetchCampaigns();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this campaign?')) return;
    try {
      await campaigns.delete(id);
      fetchCampaigns();
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400';
      case 'draft': return 'text-slate-400';
      case 'paused': return 'text-yellow-400';
      case 'completed': return 'text-blue-400';
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
          <h1 className="text-2xl font-bold text-white">Campaigns</h1>
          <p className="text-slate-400 text-sm mt-1">Create and manage cold email sequences</p>
        </div>
        <Link
          to="/campaigns/new"
          className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm font-medium"
        >
          <Plus size={16} />
          New Campaign
        </Link>
      </div>

      {list.length === 0 ? (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-12 text-center">
          <Send size={48} className="mx-auto text-slate-600 mb-4" />
          <h3 className="text-lg font-medium text-slate-300 mb-2">No campaigns yet</h3>
          <p className="text-slate-400 text-sm mb-6">Create your first cold email campaign</p>
          <Link
            to="/campaigns/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm font-medium"
          >
            <Plus size={16} />
            New Campaign
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map((campaign) => (
            <div
              key={campaign.id}
              className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <Link to={`/campaigns/${campaign.id}`} className="text-white font-medium hover:text-cyan-400">
                    {campaign.name}
                  </Link>
                  <div className="flex items-center gap-3 mt-1">
                    <span className={`text-xs font-medium ${getStatusColor(campaign.status)}`}>
                      {campaign.status}
                    </span>
                    <span className="text-xs text-slate-500">{campaign.steps.length} steps</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {campaign.status === 'draft' && (
                    <button
                      onClick={() => handleLaunch(campaign.id)}
                      className="p-2 bg-green-600/20 text-green-400 hover:bg-green-600/30 rounded-lg transition-colors"
                      title="Launch"
                    >
                      <Play size={16} />
                    </button>
                  )}
                  {campaign.status === 'running' && (
                    <button
                      onClick={() => handlePause(campaign.id)}
                      className="p-2 bg-yellow-600/20 text-yellow-400 hover:bg-yellow-600/30 rounded-lg transition-colors"
                      title="Pause"
                    >
                      <Pause size={16} />
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(campaign.id)}
                    className="p-2 bg-red-600/20 text-red-400 hover:bg-red-600/30 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-slate-700/50">
                <div>
                  <p className="text-xs text-slate-500">Sent</p>
                  <p className="text-sm font-medium text-white">{campaign.sent_count}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Opens</p>
                  <p className="text-sm font-medium text-white">{campaign.open_count}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Open Rate</p>
                  <p className="text-sm font-medium text-cyan-400">{campaign.open_rate}%</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Reply Rate</p>
                  <p className="text-sm font-medium text-cyan-400">{campaign.reply_rate}%</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
