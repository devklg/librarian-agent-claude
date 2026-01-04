# Brand Guidelines - Anthropic Brand Identity

## Purpose
Official Anthropic brand colors, typography, and visual identity guidelines for consistent branding.

## Brand Colors

### Primary Palette

| Color Name | Hex | RGB | Usage |
|------------|-----|-----|-------|
| Anthropic Coral | #D4A574 | 212, 165, 116 | Primary brand color |
| Anthropic Dark | #1A1A2E | 26, 26, 46 | Dark backgrounds |
| Anthropic Light | #F5F5F5 | 245, 245, 245 | Light backgrounds |

### Extended Palette

```css
:root {
  /* Primary */
  --anthropic-coral: #D4A574;
  --anthropic-coral-light: #E8CDB3;
  --anthropic-coral-dark: #B8865A;

  /* Neutrals */
  --anthropic-dark: #1A1A2E;
  --anthropic-gray-900: #2D2D44;
  --anthropic-gray-800: #404058;
  --anthropic-gray-700: #53536C;
  --anthropic-gray-600: #666680;
  --anthropic-gray-500: #808094;
  --anthropic-gray-400: #9999A8;
  --anthropic-gray-300: #B3B3BC;
  --anthropic-gray-200: #CCCCD0;
  --anthropic-gray-100: #E6E6E8;
  --anthropic-light: #F5F5F5;
  --anthropic-white: #FFFFFF;

  /* Accent Colors */
  --anthropic-blue: #4A90D9;
  --anthropic-green: #5CB85C;
  --anthropic-purple: #8B5CF6;
}
```

### Color Usage Guidelines

| Context | Color | Notes |
|---------|-------|-------|
| Primary buttons | Coral | Main CTAs |
| Secondary buttons | Gray-700 | Secondary actions |
| Links | Blue | Interactive text |
| Success states | Green | Confirmations |
| Text on light | Dark | Body copy |
| Text on dark | Light/White | Inverted sections |

## Typography

### Font Families

```css
:root {
  /* Primary - Headers and UI */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, sans-serif;

  /* Secondary - Long-form content */
  --font-secondary: 'Source Serif Pro', Georgia, serif;

  /* Monospace - Code */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

### Type Scale

```css
:root {
  /* Display */
  --text-display-lg: 3.5rem;    /* 56px */
  --text-display: 3rem;         /* 48px */
  --text-display-sm: 2.5rem;    /* 40px */

  /* Headings */
  --text-h1: 2rem;              /* 32px */
  --text-h2: 1.5rem;            /* 24px */
  --text-h3: 1.25rem;           /* 20px */
  --text-h4: 1.125rem;          /* 18px */

  /* Body */
  --text-body-lg: 1.125rem;     /* 18px */
  --text-body: 1rem;            /* 16px */
  --text-body-sm: 0.875rem;     /* 14px */

  /* Small */
  --text-caption: 0.75rem;      /* 12px */
  --text-overline: 0.625rem;    /* 10px */
}
```

### Font Weights

```css
:root {
  --font-light: 300;
  --font-regular: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

## Logo Usage

### Clear Space
- Minimum clear space: Height of the "A" in Anthropic
- Never place elements within the clear space zone

### Minimum Sizes
- Digital: 80px width minimum
- Print: 0.75 inches width minimum

### Logo Variations
1. **Full color** - Use on light backgrounds
2. **Reversed** - White logo on dark backgrounds
3. **Monochrome** - Single color when required

### Don'ts
- Don't stretch or distort
- Don't change colors arbitrarily
- Don't add effects (shadows, gradients)
- Don't place on busy backgrounds
- Don't rotate or flip

## UI Components

### Buttons

```css
.btn-primary {
  background: var(--anthropic-coral);
  color: var(--anthropic-dark);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: var(--anthropic-coral-dark);
}

.btn-secondary {
  background: transparent;
  color: var(--anthropic-gray-700);
  border: 1px solid var(--anthropic-gray-300);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

.btn-secondary:hover {
  background: var(--anthropic-gray-100);
}
```

### Cards

```css
.card {
  background: var(--anthropic-white);
  border: 1px solid var(--anthropic-gray-200);
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-dark {
  background: var(--anthropic-gray-900);
  border: 1px solid var(--anthropic-gray-700);
  color: var(--anthropic-light);
}
```

### Forms

```css
.input {
  border: 1px solid var(--anthropic-gray-300);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: var(--text-body);
  transition: border-color 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--anthropic-coral);
  box-shadow: 0 0 0 3px rgba(212, 165, 116, 0.2);
}
```

## Iconography

### Style Guidelines
- Line weight: 1.5px stroke
- Corner radius: Slightly rounded (2px)
- Size: 24x24px standard, 16x16px small, 32x32px large
- Color: Inherit from text color

### Icon Grid
- Design on 24x24px grid
- 2px padding/safe zone
- Optical alignment over mathematical

## Photography

### Style
- Natural, authentic moments
- Clean, uncluttered compositions
- Warm, approachable lighting
- Diverse representation

### Treatment
- No heavy filters
- Subtle warmth adjustment acceptable
- Maintain natural skin tones
- High quality, sharp focus

## Voice & Tone

### Brand Voice
- **Clear**: Simple, accessible language
- **Thoughtful**: Considered, nuanced perspectives
- **Optimistic**: Positive about AI's potential
- **Responsible**: Acknowledging challenges honestly

### Writing Guidelines
- Use active voice
- Keep sentences concise
- Avoid jargon when possible
- Be inclusive in language

## Application Examples

### Website Header

```html
<header class="site-header">
  <div class="logo">
    <img src="anthropic-logo.svg" alt="Anthropic" />
  </div>
  <nav class="nav">
    <a href="/research">Research</a>
    <a href="/products">Products</a>
    <a href="/company">Company</a>
    <a href="/careers">Careers</a>
  </nav>
  <a href="/claude" class="btn-primary">Try Claude</a>
</header>
```

### Footer

```html
<footer class="site-footer">
  <div class="footer-brand">
    <img src="anthropic-logo-white.svg" alt="Anthropic" />
    <p>Building reliable, interpretable, and steerable AI systems.</p>
  </div>
  <div class="footer-links">
    <!-- Link groups -->
  </div>
  <div class="footer-legal">
    <p>&copy; 2025 Anthropic. All rights reserved.</p>
  </div>
</footer>
```

## Resources

### Downloads
- Logo files (SVG, PNG)
- Color palette (ASE, CSS)
- Font files (if licensed)
- Icon set (SVG)

### References
- [Anthropic Website](https://www.anthropic.com)
- [Claude Documentation](https://docs.anthropic.com)
