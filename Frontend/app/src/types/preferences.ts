export type WebhookType = 'slack' | 'discord' | 'custom';
export type NotificationFrequency = 'instant' | 'daily' | 'weekly';

export interface UserPreferences {
  id: number;
  user_id: number;
  email_notifications: boolean;
  webhook_notifications: boolean;
  webhook_url: string | null;
  webhook_type: WebhookType | null;
  notification_frequency: NotificationFrequency;
  price_drop_alerts: boolean;
  weekly_summary: boolean;
  availability_alerts: boolean;
}

export interface UserPreferencesUpdate {
  email_notifications?: boolean;
  webhook_notifications?: boolean;
  webhook_url?: string | null;
  webhook_type?: WebhookType | null;
  notification_frequency?: NotificationFrequency;
  price_drop_alerts?: boolean;
  weekly_summary?: boolean;
  availability_alerts?: boolean;
}
