# Frontend Design Skill - UI/UX Expert

## Purpose
Expert guide for creating distinctive, production-grade frontend interfaces with modern frameworks and best practices.

## Capabilities
- Design responsive layouts
- Implement accessible interfaces
- Create component architectures
- Apply design systems
- Optimize performance
- Handle state management
- Implement animations

## Design Principles

### Visual Hierarchy
1. **Size**: Larger elements draw attention first
2. **Color**: Use contrast strategically
3. **Spacing**: Group related elements
4. **Typography**: Use heading hierarchy
5. **Position**: Top-left is primary focus (LTR languages)

### Layout Guidelines
- Use 8px grid system for spacing
- Maintain consistent margins/padding
- Limit line length to 60-80 characters
- Use whitespace to reduce cognitive load
- Design mobile-first, enhance for desktop

### Color Theory
- **Primary**: Main brand color (buttons, links)
- **Secondary**: Supporting actions
- **Neutral**: Text, backgrounds, borders
- **Semantic**: Success (green), Warning (yellow), Error (red)
- Ensure WCAG AA contrast (4.5:1 for text)

### Typography
- Limit to 2-3 font families
- Use relative units (rem, em)
- Set proper line-height (1.4-1.6 for body)
- Maintain consistent scale (1.25 or 1.333 ratio)

## React Component Patterns

### Functional Component with Hooks

```jsx
import { useState, useEffect, useCallback } from 'react'
import styles from './Component.module.css'

export default function DataList({ endpoint, renderItem }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(endpoint)
        if (!response.ok) throw new Error('Failed to fetch')
        const result = await response.json()
        setData(result)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [endpoint])

  if (loading) return <div className={styles.skeleton}>Loading...</div>
  if (error) return <div className={styles.error}>{error}</div>
  if (!data.length) return <div className={styles.empty}>No data found</div>

  return (
    <ul className={styles.list}>
      {data.map((item, index) => (
        <li key={item.id || index} className={styles.item}>
          {renderItem(item)}
        </li>
      ))}
    </ul>
  )
}
```

### Compound Components Pattern

```jsx
import { createContext, useContext, useState } from 'react'

const AccordionContext = createContext()

export function Accordion({ children, defaultOpen = null }) {
  const [openId, setOpenId] = useState(defaultOpen)

  return (
    <AccordionContext.Provider value={{ openId, setOpenId }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  )
}

Accordion.Item = function AccordionItem({ id, children }) {
  return <div className="accordion-item" data-id={id}>{children}</div>
}

Accordion.Header = function AccordionHeader({ id, children }) {
  const { openId, setOpenId } = useContext(AccordionContext)

  return (
    <button
      className="accordion-header"
      onClick={() => setOpenId(openId === id ? null : id)}
      aria-expanded={openId === id}
    >
      {children}
    </button>
  )
}

Accordion.Panel = function AccordionPanel({ id, children }) {
  const { openId } = useContext(AccordionContext)

  if (openId !== id) return null
  return <div className="accordion-panel">{children}</div>
}
```

## CSS Best Practices

### CSS Modules

```css
/* Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.primary {
  background: var(--color-primary);
  color: white;
}

.primary:hover {
  background: var(--color-primary-dark);
}

.secondary {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.secondary:hover {
  background: var(--color-bg-hover);
}

.large {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
}

.small {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}
```

### CSS Variables (Design Tokens)

```css
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-secondary: #6b7280;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  --color-text: #1f2937;
  --color-text-secondary: #6b7280;
  --color-bg: #ffffff;
  --color-bg-secondary: #f3f4f6;
  --color-border: #e5e7eb;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  /* Typography */
  --font-sans: system-ui, -apple-system, sans-serif;
  --font-mono: ui-monospace, 'Cascadia Code', monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-text: #f9fafb;
    --color-text-secondary: #9ca3af;
    --color-bg: #111827;
    --color-bg-secondary: #1f2937;
    --color-border: #374151;
  }
}
```

## Accessibility Checklist

- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Focus states are visible
- [ ] Color is not the only indicator
- [ ] Text has sufficient contrast
- [ ] Interactive elements are keyboard accessible
- [ ] ARIA labels where needed
- [ ] Skip link for main content
- [ ] Reduced motion respected
- [ ] Screen reader tested

### Accessibility Code Examples

```jsx
// Accessible button
<button
  aria-label="Close dialog"
  aria-pressed={isPressed}
>
  <CloseIcon aria-hidden="true" />
</button>

// Accessible form
<form>
  <label htmlFor="email">Email address</label>
  <input
    id="email"
    type="email"
    aria-describedby="email-hint"
    aria-invalid={hasError}
  />
  <span id="email-hint">We'll never share your email</span>
  {hasError && (
    <span role="alert" className="error">
      Please enter a valid email
    </span>
  )}
</form>

// Skip link
<a href="#main-content" className="skip-link">
  Skip to main content
</a>
```

## Performance Optimization

### Code Splitting

```jsx
import { lazy, Suspense } from 'react'

const HeavyComponent = lazy(() => import('./HeavyComponent'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HeavyComponent />
    </Suspense>
  )
}
```

### Optimized Images

```jsx
import Image from 'next/image'

// Next.js optimized image
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority
  placeholder="blur"
  blurDataURL={shimmer}
/>

// Native lazy loading
<img
  src="image.jpg"
  alt="Description"
  loading="lazy"
  decoding="async"
/>
```

### Memoization

```jsx
import { memo, useMemo, useCallback } from 'react'

// Memoized component
const ExpensiveList = memo(function ExpensiveList({ items, onSelect }) {
  return items.map(item => (
    <Item key={item.id} data={item} onClick={onSelect} />
  ))
})

// Memoized value
const sortedItems = useMemo(() => {
  return items.sort((a, b) => a.name.localeCompare(b.name))
}, [items])

// Memoized callback
const handleClick = useCallback((id) => {
  setSelected(id)
}, [])
```

## Animation Guidelines

```css
/* Smooth transitions */
.card {
  transition: transform var(--transition-normal),
              box-shadow var(--transition-normal);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Loading animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.skeleton {
  animation: pulse 2s ease-in-out infinite;
  background: var(--color-bg-secondary);
}
```

## References
- [React documentation](https://react.dev/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Tailwind CSS](https://tailwindcss.com/docs)
