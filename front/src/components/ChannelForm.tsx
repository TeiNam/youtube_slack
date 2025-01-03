// ChannelForm.tsx
import React, { useState } from 'react';
import { createChannel } from '../api/client';
import { AlertCircle } from 'lucide-react';
import type { Webhook } from '../types/api';

interface Props {
  webhooks: Webhook[];
  onSuccess: () => void;
}

export default function ChannelForm({ webhooks, onSuccess }: Props) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    try {
      await createChannel({
        webhook_id: Number(formData.get('webhook_id')),
        yt_handling_id: formData.get('yt_handling_id') as string,
      });
      onSuccess();
      form.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create channel');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="webhook_id" className="block text-sm font-medium text-gray-700">
          Select Webhook
        </label>
        <select
          name="webhook_id"
          id="webhook_id"
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Select a webhook...</option>
          {webhooks.map((webhook) => (
            <option key={webhook.webhook_id} value={webhook.webhook_id}>
              {webhook.workspace_name} - {webhook.webhook_name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="yt_handling_id" className="block text-sm font-medium text-gray-700">
          YouTube Channel ID
        </label>
        <input
          type="text"
          name="yt_handling_id"
          id="yt_handling_id"
          required
          maxLength={30}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      {error && (
        <div className="text-red-600 flex items-center gap-2">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {loading ? 'Adding...' : 'Add Channel'}
      </button>
    </form>
  );
}