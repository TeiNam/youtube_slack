import React, { useState, useEffect } from 'react';
import { fetchWebhooks, fetchChannels, deleteWebhook, deleteChannel, getSystemStatus } from '../api/client';
import { Webhook, Channel, SystemStatus } from '../types/api';
import { Trash2, Youtube, Bell, Activity, AlertCircle } from 'lucide-react';
import WebhookForm from './WebhookForm';
import ChannelForm from './ChannelForm';
import StatusCard from './StatusCard';

export default function Dashboard() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      const [webhooksData, channelsData, statusData] = await Promise.all([
        fetchWebhooks(),
        fetchChannels(),
        getSystemStatus(),
      ]);
      setWebhooks(webhooksData);
      setChannels(channelsData);
      setSystemStatus(statusData);
      setError('');
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDeleteWebhook = async (id: number) => {
    if (!confirm('Are you sure you want to delete this webhook?')) return;
    try {
      await deleteWebhook(id);
      await loadData();
    } catch (err) {
      setError('Failed to delete webhook');
    }
  };

  const handleDeleteChannel = async (id: number) => {
    if (!confirm('Are you sure you want to delete this channel?')) return;
    try {
      await deleteChannel(id);
      await loadData();
    } catch (err) {
      setError('Failed to delete channel');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-pulse text-lg text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">
            YouTube Monitor Dashboard
          </h1>
          
          {systemStatus && <StatusCard status={systemStatus} />}

          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg mb-4 flex items-center gap-2">
              <AlertCircle className="text-red-500" size={20} />
              <span className="text-red-700">{error}</span>
            </div>
          )}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-gray-800">
                  <Bell className="text-blue-600" />
                  Add New Webhook
                </h2>
              </div>
              <div className="p-6">
                <WebhookForm onSuccess={loadData} />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Webhooks</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {webhooks.map((webhook) => (
                    <div
                      key={webhook.webhook_id}
                      className="group border border-gray-200 p-4 rounded-lg hover:bg-blue-50 transition-colors duration-200"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-gray-800">{webhook.workspace_name}</h3>
                          <p className="text-sm text-gray-600">{webhook.webhook_name}</p>
                          <p className="text-sm text-gray-500 truncate max-w-xs">{webhook.url}</p>
                        </div>
                        <button
                          onClick={() => handleDeleteWebhook(webhook.webhook_id)}
                          className="text-gray-400 hover:text-red-600 transition-colors duration-200 opacity-0 group-hover:opacity-100"
                        >
                          <Trash2 size={20} />
                        </button>
                      </div>
                    </div>
                  ))}
                  {webhooks.length === 0 && (
                    <p className="text-center text-gray-500 py-4">No webhooks added yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-gray-800">
                  <Youtube className="text-blue-600" />
                  Add New Channel
                </h2>
              </div>
              <div className="p-6">
                <ChannelForm webhooks={webhooks} onSuccess={loadData} />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Monitored Channels</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {channels.map((channel) => (
                    <div
                      key={channel.id}
                      className="group border border-gray-200 p-4 rounded-lg hover:bg-blue-50 transition-colors duration-200"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-gray-800">{channel.yt_ch_name}</h3>
                          <p className="text-sm text-gray-600">
                            Channel ID: {channel.yt_channel_id}
                          </p>
                          <p className="text-sm text-gray-500">
                            Webhook: {
                              webhooks.find(w => w.webhook_id === channel.webhook_id)?.webhook_name
                            }
                          </p>
                        </div>
                        <button
                          onClick={() => handleDeleteChannel(channel.id)}
                          className="text-gray-400 hover:text-red-600 transition-colors duration-200 opacity-0 group-hover:opacity-100"
                        >
                          <Trash2 size={20} />
                        </button>
                      </div>
                    </div>
                  ))}
                  {channels.length === 0 && (
                    <p className="text-center text-gray-500 py-4">No channels monitored yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}