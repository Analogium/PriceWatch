export const APP_NAME = 'PriceWatch';

export const CHECK_FREQUENCIES = [
  { value: 6, label: 'Toutes les 6 heures' },
  { value: 12, label: 'Toutes les 12 heures' },
  { value: 24, label: 'Toutes les 24 heures' },
] as const;

export const WEBHOOK_TYPES = [
  { value: 'slack', label: 'Slack' },
  { value: 'discord', label: 'Discord' },
  { value: 'custom', label: 'Custom' },
] as const;

export const SORT_OPTIONS = [
  { value: 'name', label: 'Nom' },
  { value: 'current_price', label: 'Prix actuel' },
  { value: 'target_price', label: 'Prix cible' },
  { value: 'created_at', label: 'Date de création' },
  { value: 'last_checked', label: 'Dernière vérification' },
] as const;

export const PAGE_SIZES = [10, 20, 50, 100] as const;

export const DEFAULT_PAGE_SIZE = 20;
