import React, { useState } from 'react';
import { createWebhook } from '../api/client';
import { AlertCircle } from 'lucide-react';

export default function WebhookForm({ onSuccess }: { onSuccess: () => void }) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    try {
      await createWebhook({
        workspace_name: formData.get('workspace_name') as string,
        webhook_name: formData.get('webhook_name') as string,
        url: formData.get('url') as string,
      });
      onSuccess();
      e.currentTarget.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create webhook');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="workspace_name" className="block text-sm font-medium text-gray-700">
          Workspace Name
        </label>
        <input
          type="text"
          name="workspace_name"
          id="workspace_name"
          required
          maxLength={30}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="webhook_name" className="block text-sm font-medium text-gray-700">
          Webhook Name
        </label>
        <input
          type="text"
          name="webhook_name"
          id="webhook_name"
          required
          maxLength={20}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="url" className="block text-sm font-medium text-gray-700">
          Webhook URL
        </label>
        <input
          type="url"
          name="url"
          id="url"
          required
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
        {loading ? 'Creating...' : 'Create Webhook'}
      </button>
    </form>
  );
}