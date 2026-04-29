import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Plus, Send, Trash2, GripVertical } from 'lucide-react';
import { campaigns } from '../lib/api';

interface Step {
  step_order: number;
  action: string;
  subject: string;
  body_text: string;
  delay_hours: number;
}

export default function CampaignEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = id === 'new';

  const [name, setName] = useState('');
  const [steps, setSteps] = useState<Step[]>([
    { step_order: 1, action: 'send_email', subject: '', body_text: '', delay_hours: 0 },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isNew && id) {
      campaigns.get(parseInt(id)).then((data: any) => {
        setName(data.name);
        if (data.steps && data.steps.length > 0) {
          setSteps(data.steps.map((s: any) => ({
            step_order: s.step_order,
            action: s.action,
            subject: s.subject || '',
            body_text: s.body_text || '',
            delay_hours: s.delay_hours,
          })));
        }
      }).catch(console.error);
    }
  }, [id]);

  const addStep = () => {
    const newOrder = steps.length + 1;
    setSteps([...steps, { step_order: newOrder, action: 'send_email', subject: '', body_text: '', delay_hours: 24 }]);
  };

  const removeStep = (index: number) => {
    if (steps.length <= 1) return;
    const newSteps = steps.filter((_, i) => i !== index).map((s, i) => ({ ...s, step_order: i + 1 }));
    setSteps(newSteps);
  };

  const updateStep = (index: number, field: keyof Step, value: any) => {
    const newSteps = [...steps];
    (newSteps[index] as any)[field] = value;
    setSteps(newSteps);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (isNew) {
        await campaigns.create({ name, steps });
      } else {
        await campaigns.update(parseInt(id!), { name, steps });
      }
      navigate('/campaigns');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/campaigns')}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">{isNew ? 'New Campaign' : 'Edit Campaign'}</h1>
          <p className="text-slate-400 text-sm mt-1">Configure your cold email sequence</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
          <label className="block text-sm font-medium text-slate-300 mb-1">Campaign Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            placeholder="Q1 Outreach - Tech Leads"
            required
          />
        </div>

        {/* Steps */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Email Steps</h2>
            <button
              type="button"
              onClick={addStep}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors text-sm"
            >
              <Plus size={14} />
              Add Step
            </button>
          </div>

          {steps.map((step, index) => (
            <div key={index} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <GripVertical size={16} className="text-slate-600" />
                  <span className="text-sm font-medium text-cyan-400">Step {step.step_order}</span>
                </div>
                {steps.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeStep(index)}
                    className="p-1 text-slate-500 hover:text-red-400 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Subject Line</label>
                  <input
                    type="text"
                    value={step.subject}
                    onChange={(e) => updateStep(index, 'subject', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="Hi {{first_name}}, quick question..."
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Email Body</label>
                  <textarea
                    value={step.body_text}
                    onChange={(e) => updateStep(index, 'body_text', e.target.value)}
                    rows={5}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 resize-y font-mono"
                    placeholder="Hi {{first_name}},&#10;&#10;I noticed you're doing amazing work at {{company}}..."
                  />
                </div>

                <div className="flex items-center gap-4">
                  <div className="w-32">
                    <label className="block text-xs font-medium text-slate-400 mb-1">Delay (hours)</label>
                    <input
                      type="number"
                      value={step.delay_hours}
                      onChange={(e) => updateStep(index, 'delay_hours', parseInt(e.target.value) || 0)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="0"
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {loading ? 'Saving...' : isNew ? 'Create Campaign' : 'Save Changes'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/campaigns')}
            className="px-6 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-2.5 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
