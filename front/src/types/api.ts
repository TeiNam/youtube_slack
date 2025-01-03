// types/api.ts
export interface Webhook {
  webhook_id: number;
  workspace_name: string;
  webhook_name: string;
  url: string;
  create_at: string;
  update_at: string;
}

export interface Channel {
  id: number;
  webhook_id: number;
  yt_channel_id: string;
  yt_handling_id: string;
  yt_ch_name: string;
  create_at: string;
  update_at: string;
}

export interface SystemStatus {
  status: string;
  background_task_running: boolean;
  youtube_api_quota_used: number;
}