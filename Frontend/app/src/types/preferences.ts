export type WebhookType = 'slack' | 'discord' | 'custom';
export type Language = 'fr' | 'en';

export interface UserPreferences {
  id: number;
  user_id: number;
  email_notifications: boolean;
  webhook_notifications: boolean;
  webhook_url: string | null;
  webhook_type: WebhookType | null;
  price_drop_alerts: boolean;
  weekly_summary: boolean;
  language: Language;
}

export interface UserPreferencesUpdate {
  email_notifications?: boolean;
  webhook_notifications?: boolean;
  webhook_url?: string | null;
  webhook_type?: WebhookType | null;
  price_drop_alerts?: boolean;
  weekly_summary?: boolean;
  language?: Language;
}
