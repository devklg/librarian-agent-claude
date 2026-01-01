# Theme Factory - Styling & Theming Toolkit

## Purpose
Toolkit for creating consistent, beautiful themes and styling for web applications and documents.

## Capabilities
- Generate color palettes
- Create typography scales
- Define spacing systems
- Build dark/light modes
- Export to CSS/SCSS/Tailwind

## Color Palettes

### Primary Palette Generation

Start with a brand color and generate a full palette:

```javascript
// Generate shades from a base color
function generatePalette(baseColor) {
  return {
    50:  adjustLightness(baseColor, 95),
    100: adjustLightness(baseColor, 90),
    200: adjustLightness(baseColor, 80),
    300: adjustLightness(baseColor, 70),
    400: adjustLightness(baseColor, 60),
    500: baseColor,  // Base color
    600: adjustLightness(baseColor, 40),
    700: adjustLightness(baseColor, 30),
    800: adjustLightness(baseColor, 20),
    900: adjustLightness(baseColor, 10),
    950: adjustLightness(baseColor, 5),
  }
}
```

### Semantic Colors

```css
:root {
  /* Primary - Brand color */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-active: #1d4ed8;

  /* Secondary - Supporting actions */
  --color-secondary: #6b7280;
  --color-secondary-hover: #4b5563;

  /* Success */
  --color-success: #10b981;
  --color-success-bg: #d1fae5;
  --color-success-text: #065f46;

  /* Warning */
  --color-warning: #f59e0b;
  --color-warning-bg: #fef3c7;
  --color-warning-text: #92400e;

  /* Error */
  --color-error: #ef4444;
  --color-error-bg: #fee2e2;
  --color-error-text: #991b1b;

  /* Info */
  --color-info: #3b82f6;
  --color-info-bg: #dbeafe;
  --color-info-text: #1e40af;
}
```

### Color Accessibility

Ensure WCAG AA compliance (4.5:1 for text, 3:1 for large text):

| Background | Text Color | Contrast Ratio |
|------------|------------|----------------|
| #ffffff | #1f2937 | 14.7:1 ✓ |
| #f3f4f6 | #374151 | 8.2:1 ✓ |
| #3b82f6 | #ffffff | 4.5:1 ✓ |
| #1f2937 | #f9fafb | 14.1:1 ✓ |

## Typography

### Type Scale

Using a 1.25 ratio (Major Third):

```css
:root {
  --text-xs:   0.64rem;   /* 10.24px */
  --text-sm:   0.8rem;    /* 12.8px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.25rem;   /* 20px */
  --text-xl:   1.563rem;  /* 25px */
  --text-2xl:  1.953rem;  /* 31.25px */
  --text-3xl:  2.441rem;  /* 39px */
  --text-4xl:  3.052rem;  /* 48.83px */
}
```

### Font Stacks

```css
:root {
  /* System fonts - Fast loading */
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

  /* Monospace - Code blocks */
  --font-mono: ui-monospace, SFMono-Regular, 'SF Mono',
    Menlo, Monaco, Consolas, monospace;

  /* Serif - Long-form content */
  --font-serif: Georgia, Cambria, 'Times New Roman',
    Times, serif;
}
```

### Line Heights

```css
:root {
  --leading-none:   1;
  --leading-tight:  1.25;
  --leading-snug:   1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose:  2;
}
```

## Spacing System

### 8px Grid

```css
:root {
  --space-0:  0;
  --space-1:  0.25rem;  /* 4px */
  --space-2:  0.5rem;   /* 8px */
  --space-3:  0.75rem;  /* 12px */
  --space-4:  1rem;     /* 16px */
  --space-5:  1.25rem;  /* 20px */
  --space-6:  1.5rem;   /* 24px */
  --space-8:  2rem;     /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

## Dark Mode

### CSS Variables Approach

```css
:root {
  /* Light mode (default) */
  --bg-primary: #ffffff;
  --bg-secondary: #f3f4f6;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
}

[data-theme="dark"] {
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --border-color: #374151;
}

/* System preference */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg-primary: #111827;
    --bg-secondary: #1f2937;
    --text-primary: #f9fafb;
    --text-secondary: #9ca3af;
    --border-color: #374151;
  }
}
```

### JavaScript Theme Toggle

```javascript
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme')
  const next = current === 'dark' ? 'light' : 'dark'
  document.documentElement.setAttribute('data-theme', next)
  localStorage.setItem('theme', next)
}

// Initialize from stored preference
const stored = localStorage.getItem('theme')
if (stored) {
  document.documentElement.setAttribute('data-theme', stored)
}
```

## Pre-built Themes

### Corporate Blue

```css
:root {
  --primary: #1e40af;
  --secondary: #64748b;
  --accent: #0ea5e9;
  --bg: #ffffff;
  --text: #0f172a;
}
```

### Forest Green

```css
:root {
  --primary: #166534;
  --secondary: #4b5563;
  --accent: #22c55e;
  --bg: #f0fdf4;
  --text: #14532d;
}
```

### Sunset Orange

```css
:root {
  --primary: #ea580c;
  --secondary: #78716c;
  --accent: #f97316;
  --bg: #fffbeb;
  --text: #431407;
}
```

### Midnight Purple

```css
:root {
  --primary: #7c3aed;
  --secondary: #6b7280;
  --accent: #a855f7;
  --bg: #faf5ff;
  --text: #3b0764;
}
```

## Shadows

```css
:root {
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1),
               0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1),
               0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1),
               0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1),
               0 8px 10px -6px rgb(0 0 0 / 0.1);
}
```

## Border Radius

```css
:root {
  --radius-none: 0;
  --radius-sm: 0.125rem;  /* 2px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-full: 9999px;
}
```

## Export Formats

### Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
}
```

### SCSS Variables

```scss
// _variables.scss
$primary: #3b82f6;
$secondary: #6b7280;
$success: #10b981;
$warning: #f59e0b;
$error: #ef4444;

$font-sans: 'Inter', system-ui, sans-serif;
$font-mono: 'JetBrains Mono', monospace;

$space-unit: 0.25rem;
@function space($n) {
  @return $space-unit * $n;
}
```

## References
- [Tailwind CSS Colors](https://tailwindcss.com/docs/customizing-colors)
- [Type Scale Calculator](https://type-scale.com/)
- [Contrast Checker](https://webaim.org/resources/contrastchecker/)
