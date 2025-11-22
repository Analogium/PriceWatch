# Design System - PriceWatch Frontend

Ce document définit les paramètres de style extraits des maquettes Figma pour assurer la cohérence du frontend.

---

## Couleurs

### Couleurs Principales

| Nom | Valeur HEX | Usage |
|-----|------------|-------|
| `primary` | `#2563EB` | Boutons principaux, liens, focus, badges actifs |
| `background-light` | `#F8FAFC` | Fond de page mode clair |
| `background-dark` | `#101722` | Fond de page mode sombre |

> **Note** : Certaines maquettes utilisent `#206cee` ou `#3B82F6` comme primary. La valeur standardisée est `#2563EB` (blue-600 Tailwind).

### Couleurs Sémantiques

| Nom | Valeur HEX | Usage |
|-----|------------|-------|
| `success` | `#16A34A` | Prix cible atteint, validations, variations positives |
| `danger` / `error` | `#DC3545` / `#EF4444` | Suppressions, erreurs, alertes |
| `warning` | `#F59E0B` | Avertissements (à définir) |

### Couleurs de Texte

| Mode | Couleur Principale | Couleur Secondaire |
|------|-------------------|-------------------|
| Light | `#1E293B` (gray-800) | `#64748B` / `#94A3B8` (gray-500/400) |
| Dark | `#E2E8F0` / `#F1F5F9` | `#94A3B8` / `#64748B` |

### Couleurs de Bordure

| Mode | Valeur |
|------|--------|
| Light | `#E5E7EB` / `#CBD5E1` (gray-200/300) |
| Dark | `#374151` / `#334155` (gray-700/800) |

### Couleurs d'Input/Background

| Mode | Background Input | Placeholder |
|------|-----------------|-------------|
| Light | `#F9FAFB` / `#F3F4F6` (gray-50/100) | `#94A3B8` |
| Dark | `#374151` / `#1F2937` (gray-700/800) | `#64748B` |

---

## Typographie

### Police

```css
font-family: "Inter", sans-serif;
```

**Weights utilisés** :
- `400` - Regular (texte courant)
- `500` - Medium (labels, liens)
- `600` - Semibold (sous-titres)
- `700` - Bold (titres, boutons)
- `900` - Black (titres principaux hero)

### Tailles de Texte

| Usage | Taille | Classes Tailwind |
|-------|--------|-----------------|
| Hero title | 48px - 60px | `text-4xl md:text-6xl` |
| Page title | 30px - 36px | `text-3xl md:text-4xl` |
| Section title | 24px - 30px | `text-2xl md:text-3xl` |
| Card title | 16px - 18px | `text-base md:text-lg` |
| Body text | 14px - 16px | `text-sm md:text-base` |
| Small/Caption | 12px | `text-xs` |

### Line Height & Tracking

- Titres : `leading-tight` avec `tracking-tight` ou `tracking-[-0.033em]`
- Body : `leading-normal`

---

## Espacements

### Padding/Margin Standards

| Élément | Valeur |
|---------|--------|
| Container padding | `px-4 sm:px-6 lg:px-8` |
| Card padding | `p-4` ou `p-6` |
| Section gap | `gap-6` ou `gap-8` |
| Form field gap | `gap-2` (label-input), `gap-4` ou `gap-6` (entre champs) |
| Button padding | `px-4 py-2` ou `px-6 py-3` |

### Grid Gaps

- Cards grid : `gap-4` ou `gap-6`
- Dashboard grid : `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`

---

## Border Radius

| Token | Valeur | Usage |
|-------|--------|-------|
| `DEFAULT` | `0.375rem` (6px) | Inputs, petits éléments |
| `lg` | `0.5rem` (8px) | Boutons, cards compactes |
| `xl` | `0.75rem` (12px) | Cards, modales |
| `full` | `9999px` | Avatars, badges pills |

---

## Ombres

| Usage | Classe |
|-------|--------|
| Cards repos | `shadow-sm` |
| Cards hover | `shadow-lg` |
| Modales | `shadow-2xl` |
| Header sticky | Pas d'ombre (border-b uniquement) |

---

## Composants Standards

### Boutons

#### Primary Button
```css
bg-primary text-white font-semibold rounded-lg px-4 py-2
hover:bg-primary/90
focus:ring-2 focus:ring-primary focus:ring-offset-2
```

#### Secondary Button
```css
bg-white dark:bg-gray-800
border border-gray-300 dark:border-gray-700
text-gray-800 dark:text-gray-200
rounded-lg px-4 py-2
hover:bg-gray-100 dark:hover:bg-gray-700
```

#### Danger Button
```css
bg-danger text-white font-semibold rounded-lg px-4 py-2
hover:bg-danger/90
```

#### Hauteurs
- Standard : `h-10` ou `h-11`
- Large : `h-12`

### Inputs

```css
/* Structure de base */
form-input w-full rounded-lg
border border-gray-300 dark:border-gray-700
bg-gray-50 dark:bg-gray-800
text-gray-900 dark:text-gray-100
placeholder:text-gray-400 dark:placeholder:text-gray-500
focus:border-primary focus:ring-2 focus:ring-primary/20
h-11 px-4 py-2

/* Avec icône gauche */
pl-10 /* + icône en absolute left-3 */
```

### Cards

```css
/* Card de base */
rounded-xl
border border-gray-200 dark:border-gray-800
bg-white dark:bg-gray-900
p-4 ou p-6
shadow-sm

/* Card hover effect */
hover:shadow-lg hover:border-primary/50
transition-all duration-300
```

### Badges/Tags

```css
/* Badge standard */
inline-flex items-center gap-1.5
rounded-full px-2.5 py-0.5
text-xs font-medium

/* Variantes */
/* Success */ bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300
/* Primary */ bg-blue-100 dark:bg-blue-900/50 text-primary dark:text-blue-300
/* Neutral */ bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300
```

### Header/Navbar

```css
sticky top-0 z-10
border-b border-gray-200 dark:border-gray-800
bg-background-light/80 dark:bg-background-dark/80
backdrop-blur-sm
px-4 sm:px-6 lg:px-8 py-3
```

---

## Icônes

### Bibliothèque
**Material Symbols Outlined** (Google Fonts)

```html
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
```

### Configuration par défaut
```css
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
```

### Tailles courantes
- Small : `!text-sm` (14px)
- Default : `text-xl` (20px)
- Medium : `!text-2xl` (24px)
- Large : `!text-3xl` (30px)
- XL : `!text-4xl` (36px)

### Icônes fréquentes utilisées
- Navigation : `menu`, `notifications`, `help`, `chevron_left`, `chevron_right`
- Actions : `add`, `delete`, `edit`, `sync`, `search`, `more_vert`
- Produits : `update`, `military_tech`, `link`, `euro`
- Auth : `mail`, `lock`, `visibility`, `visibility_off`
- Feedback : `check_circle`, `radio_button_unchecked`, `expand_more`

---

## États & Transitions

### Transitions
```css
transition-colors /* pour hover couleurs */
transition-all duration-300 /* pour hover complet (shadow, border) */
```

### Focus
```css
focus:outline-none
focus:ring-2 focus:ring-primary
focus:ring-offset-2 focus:ring-offset-background-light dark:focus:ring-offset-background-dark
```

### Disabled
```css
disabled:opacity-50 disabled:cursor-not-allowed
```

---

## Responsive Breakpoints

Utiliser les breakpoints Tailwind standards :
- `sm` : 640px
- `md` : 768px
- `lg` : 1024px
- `xl` : 1280px

### Patterns courants
```css
/* Mobile-first stacking to row */
flex-col sm:flex-row

/* Grid responsive */
grid-cols-1 md:grid-cols-2 lg:grid-cols-3

/* Container widths */
max-w-md    /* Forms, auth pages */
max-w-2xl   /* Modales */
max-w-5xl   /* Landing page */
max-w-7xl   /* Dashboard */
```

---

## Dark Mode

Le dark mode est activé via la classe `dark` sur `<html>`.

### Pattern de couleurs
```css
/* Texte */
text-gray-900 dark:text-gray-100

/* Background */
bg-white dark:bg-gray-900
bg-gray-50 dark:bg-gray-800

/* Borders */
border-gray-200 dark:border-gray-800

/* Placeholder */
placeholder:text-gray-400 dark:placeholder:text-gray-500
```

---

## Configuration Tailwind

Voici la configuration Tailwind à utiliser :

```javascript
// tailwind.config.js
module.exports = {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563EB",
        "background-light": "#F8FAFC",
        "background-dark": "#101722",
        success: "#16A34A",
        danger: "#DC3545",
        error: "#EF4444",
      },
      fontFamily: {
        display: ["Inter", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "0.375rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
}
```

---

## Google Fonts à inclure

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
```

---

**Dernière mise à jour** : 2025-11-22

> **Note** : L'implémentation de ce design system est détaillée dans [RoadMap.md](RoadMap.md) aux sections 1.1, 1.2 et 4.4.
