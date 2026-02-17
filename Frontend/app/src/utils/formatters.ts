import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import { enUS } from 'date-fns/locale';
import i18n from '../i18n';

const getDateLocale = () => (i18n.language === 'en' ? enUS : fr);
const getIntlLocale = () => (i18n.language === 'en' ? 'en-US' : 'fr-FR');

export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat(getIntlLocale(), {
    style: 'currency',
    currency: 'EUR',
  }).format(price);
};

export const formatDate = (dateString: string): string => {
  const date = parseISO(dateString);
  return format(date, 'dd/MM/yyyy', { locale: getDateLocale() });
};

export const formatDateTime = (dateString: string): string => {
  const date = parseISO(dateString);
  return format(date, 'dd/MM/yyyy HH:mm', { locale: getDateLocale() });
};

export const formatRelativeTime = (dateString: string): string => {
  const date = parseISO(dateString);
  return formatDistanceToNow(date, { addSuffix: true, locale: getDateLocale() });
};

export const formatPercentage = (value: number | null): string => {
  if (value === null) return '-';
  const percentage = value * 100;
  const sign = percentage > 0 ? '+' : '';
  return `${sign}${percentage.toFixed(2)}%`;
};
