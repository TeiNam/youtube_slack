// api/client.ts
import type { Webhook, Channel, SystemStatus } from '../types/api';

const API_HOST = import.meta.env.VITE_API_HOST || 'http://localhost';
const API_PORT = import.meta.env.VITE_API_PORT || '8000';
const API_BASE_URL = `${API_HOST}:${API_PORT}/api/v1`;

// 공통 fetch 함수
async function fetchAPI<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    try {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'API request failed');
    } catch (e) {
      throw new Error(`Request failed with status ${response.status}`);
    }
  }

  return response.json();
}

export async function fetchWebhooks(): Promise<Webhook[]> {
  return fetchAPI<Webhook[]>(`${API_BASE_URL}/webhooks`);
}

export async function createWebhook(data: {
  workspace_name: string;
  webhook_name: string;
  url: string;
}): Promise<Webhook> {
  return fetchAPI<Webhook>(`${API_BASE_URL}/webhooks`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteWebhook(id: number): Promise<void> {
  await fetchAPI(`${API_BASE_URL}/webhooks/${id}`, {
    method: 'DELETE',
  });
}

export async function fetchChannels(): Promise<Channel[]> {
  return fetchAPI<Channel[]>(`${API_BASE_URL}/channels`);
}

export async function createChannel(data: {
  webhook_id: number;
  yt_handling_id: string;
}): Promise<Channel> {
  return fetchAPI<Channel>(`${API_BASE_URL}/channels`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteChannel(id: number): Promise<void> {
  await fetchAPI(`${API_BASE_URL}/channels/${id}`, {
    method: 'DELETE',
  });
}

export async function getSystemStatus(): Promise<SystemStatus> {
  return fetchAPI<SystemStatus>(`${API_BASE_URL}/system/status`);
}