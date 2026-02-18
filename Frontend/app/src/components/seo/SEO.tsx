import { Helmet } from 'react-helmet-async';
import { useTranslation } from 'react-i18next';

interface SEOProps {
  title?: string;
  description?: string;
  canonical?: string;
  ogImage?: string;
  noindex?: boolean;
  lang?: string;
}

export default function SEO({
  title,
  description,
  canonical,
  ogImage = '/og-image.png',
  noindex = false,
  lang,
}: SEOProps) {
  const { i18n } = useTranslation();
  const currentLang = lang || i18n.language;

  const siteUrl = import.meta.env.VITE_SITE_URL || 'https://pricewatch.fr';
  const fullTitle = title ? `${title} | PriceWatch` : 'PriceWatch - Surveillance de prix automatique';
  const defaultDescription =
    'Suivez automatiquement les prix de vos produits préférés sur Amazon, Fnac, Darty, Cdiscount et plus. Recevez des alertes email dès que le prix baisse.';
  const metaDescription = description || defaultDescription;
  const canonicalUrl = canonical ? `${siteUrl}${canonical}` : siteUrl;


  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <html lang={currentLang} />
      <title>{fullTitle}</title>
      <meta name="description" content={metaDescription} />
      {canonical && <link rel="canonical" href={canonicalUrl} />}
      {noindex && <meta name="robots" content="noindex,nofollow" />}

      {/* Open Graph Tags */}
      <meta property="og:type" content="website" />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={metaDescription} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:image" content={`${siteUrl}${ogImage}`} />
      <meta property="og:locale" content={currentLang === 'fr' ? 'fr_FR' : 'en_US'} />
      <meta property="og:site_name" content="PriceWatch" />

      {/* Twitter Card Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={metaDescription} />
      <meta name="twitter:image" content={`${siteUrl}${ogImage}`} />

      {/* Hreflang Tags */}
      <link rel="alternate" hrefLang="fr" href={`${siteUrl}/fr${canonical || '/'}`} />
      <link rel="alternate" hrefLang="en" href={`${siteUrl}/en${canonical || '/'}`} />
      <link rel="alternate" hrefLang="x-default" href={`${siteUrl}${canonical || '/'}`} />
    </Helmet>
  );
}
