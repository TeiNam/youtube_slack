import React from 'react';
import { Activity } from 'lucide-react';
import type { SystemStatus } from '../types/api';

interface Props {
  status: SystemStatus;
}

export default function StatusCard({ status }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-800">
        <Activity className="text-blue-600" />
        System Status
      </h2>
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500 mb-1">Service Status</p>
          <p className="font-semibold text-gray-800 flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              status.status === 'running' ? 'bg-green-500' : 'bg-yellow-500'
            }`} />
            {status.status}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500 mb-1">Background Task</p>
          <p className="font-semibold text-gray-800 flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              status.background_task_running ? 'bg-green-500' : 'bg-gray-400'
            }`} />
            {status.background_task_running ? 'Running' : 'Stopped'}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500 mb-1">API Quota Used</p>
          <p className="font-semibold text-gray-800">
            {status.youtube_api_quota_used.toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}