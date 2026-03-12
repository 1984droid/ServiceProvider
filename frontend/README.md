# Service Provider Frontend

Production-ready React frontend application for the Service Provider inspection and asset management system.

## Tech Stack

- **React 19.2.4** - Latest stable React with new features
- **Vite 8.0.0** - Ultra-fast build tool and dev server
- **TypeScript 5.9.3** - Type safety throughout
- **Tailwind CSS v4.2.1** - Utility-first CSS with runtime theming
- **TanStack Query v5.90+** - Server state management
- **TanStack Router v1.166+** - Type-safe routing
- **TanStack Table v8.21+** - Powerful table component
- **TanStack Form v0.2+** - Form state management
- **Axios** - HTTP client with interceptors
- **Zustand** - Client state management
- **Playwright** - End-to-end testing
- **React Hook Form + Zod** - Form validation

## Features

✅ **Theme System** - Runtime CSS variable-based theming (default/dark themes included)
✅ **Authentication** - JWT with automatic token refresh and secure storage
✅ **API Client** - Axios with request/response interceptors
✅ **Type Safety** - Full TypeScript coverage with strict mode
✅ **Component Reusability** - Atomic design pattern (atoms → molecules → organisms → templates → pages)
✅ **E2E Testing** - Playwright tests with page objects and fixtures
✅ **No Hardcoded Data** - All data comes from API or seed command

## Project Structure

```
frontend/
├── src/
│   ├── api/                 # API client layer
│   │   └── auth.api.ts      # Authentication API
│   ├── components/
│   │   ├── ui/              # Base atoms (Button, Input, Card)
│   │   ├── layout/          # Layout components (Header, Sidebar)
│   │   ├── forms/           # Reusable form components
│   │   └── domain/          # Business-specific components
│   ├── features/            # Feature modules
│   │   ├── auth/            # Authentication feature
│   │   ├── inspections/     # Inspections feature
│   │   ├── customers/       # Customers feature
│   │   ├── assets/          # Assets feature
│   │   ├── work-orders/     # Work orders feature
│   │   └── organization/    # Organization feature
│   ├── hooks/               # Custom React hooks
│   │   └── useAuth.ts       # Authentication hook
│   ├── store/               # Zustand stores
│   │   └── authStore.ts     # Auth state
│   ├── lib/                 # Utilities
│   │   ├── axios.ts         # Configured Axios client
│   │   └── queryClient.ts   # TanStack Query config
│   ├── config/              # Configuration
│   │   ├── api.ts           # API endpoints
│   │   └── theme.ts         # Theme configuration
│   └── styles/
│       ├── index.css        # Main styles
│       └── themes/
│           ├── default.css  # Default theme
│           └── dark.css     # Dark theme
├── e2e/                     # Playwright E2E tests
│   ├── fixtures/            # Test fixtures
│   ├── pages/               # Page objects
│   └── *.spec.ts            # Test specs
└── playwright.config.ts     # Playwright config
```

## Getting Started

### Prerequisites

- Node.js 18+ (recommended: 20+)
- npm 9+

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

### Available Scripts

```bash
# Development
npm run dev          # Start dev server with HMR

# Build
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test:e2e     # Run Playwright E2E tests
npm run test:ui      # Run Playwright UI mode

# Linting
npm run lint         # Lint with ESLint
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api
```

### Theme Customization

Themes are defined in `src/styles/themes/`. To switch themes:

1. **At build time**: Change the import in `src/styles/index.css`
2. **At runtime**: Use the `loadTheme()` function from `src/config/theme.ts`

To create a custom theme:

1. Copy `src/styles/themes/default.css` to a new file (e.g., `custom.css`)
2. Modify the CSS variables
3. Import the new theme in your app

**Example CSS variables:**

```css
:root {
  --color-primary: 59 130 246;  /* RGB values only */
  --color-secondary: 100 116 139;
  --color-accent: 168 85 247;
  --radius: 0.5rem;
  --font-size-base: 1rem;
  /* ... */
}
```

## API Integration

### Authentication Flow

1. User logs in via `/api/auth/login/`
2. JWT tokens (access + refresh) are stored in localStorage
3. Access token is injected into all API requests via Axios interceptor
4. When access token expires, refresh token is used to get new tokens automatically
5. On logout, refresh token is blacklisted

### Making API Calls

```typescript
import { authApi } from '@/api/auth.api';

// Using the auth hook
const { login, user, isAuthenticated } = useAuth();

await login({ username: 'admin', password: 'admin' });
console.log(user); // UserProfile object
```

### Adding New API Endpoints

1. Create API client in `src/api/[feature].api.ts`
2. Define TypeScript interfaces
3. Use the configured `apiClient` from `@/lib/axios`

**Example:**

```typescript
// src/api/customers.api.ts
import { apiClient } from '@/lib/axios';
import { API_CONFIG } from '@/config/api';

export interface Customer {
  id: string;
  name: string;
  // ...
}

export const customersApi = {
  async getAll(): Promise<Customer[]> {
    const response = await apiClient.get<Customer[]>(
      API_CONFIG.endpoints.customers.list
    );
    return response.data;
  },
};
```

## Component Development

### Atomic Design Pattern

- **Atoms**: Basic elements (Button, Input, Label, Badge)
- **Molecules**: Simple combinations (FormField = Label + Input)
- **Organisms**: Complex components (LoginForm, CustomerTable)
- **Templates**: Page layouts (DashboardTemplate)
- **Pages**: Complete views (LoginPage, DashboardPage)

### Creating Components

```typescript
// src/components/ui/Button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
}

export function Button({ variant = 'primary', className, ...props }: ButtonProps) {
  return (
    <button className={`btn btn-${variant} ${className}`} {...props} />
  );
}
```

## Testing

### E2E Tests with Playwright

Tests are located in `e2e/` directory using the Page Object Model pattern.

```bash
# Run all E2E tests
npm run test:e2e

# Run in UI mode for debugging
npm run test:ui

# Run specific test file
npx playwright test e2e/auth.spec.ts
```

**Example test:**

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test('should login with valid credentials', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('admin', 'admin');

  await expect(page).toHaveURL('/');
});
```

## Backend Integration

### Django Dev Server

Make sure the Django backend is running:

```bash
cd ..  # Go to project root
python manage.py runserver
```

### Seed Test Data

```bash
cd ..  # Go to project root
python manage.py seed_data
```

This creates:
- 1 Company
- 4 Departments
- 6 Employees
- 6 Users (all with password 'admin')
- 3 Customers
- Multiple Vehicles, Trailers, Equipment

**Test Users:**

| Username    | Password | Role             |
|-------------|----------|------------------|
| admin       | admin    | ADMIN            |
| inspector1  | admin    | INSPECTOR        |
| inspector2  | admin    | INSPECTOR        |
| service1    | admin    | SERVICE_TECH     |
| service2    | admin    | SERVICE_TECH     |
| support1    | admin    | CUSTOMER_SERVICE |

## Production Build

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview

# Output will be in dist/ directory
```

## Troubleshooting

### Port 5173 already in use

```bash
# Change port in vite.config.ts or kill the process
npx kill-port 5173
```

### API connection refused

- Ensure Django backend is running on port 8000
- Check VITE_API_URL in `.env`
- Verify CORS settings in Django `config/settings.py`

### TypeScript errors

```bash
# Clear cache and rebuild
rm -rf node_modules/.vite
npm run build
```

## Next Steps

- [ ] Implement TanStack Router routing
- [ ] Create login page component
- [ ] Build dashboard layout
- [ ] Create inspection list/detail pages
- [ ] Implement customer management UI
- [ ] Add asset management pages
- [ ] Create work order views

## Architecture Decisions

1. **CSS Variables over Tailwind classes** - Easier theme switching at runtime
2. **Type-only imports** - Required by TypeScript's `verbatimModuleSyntax`
3. **Zustand for client state** - Simpler than Redux, better DX
4. **TanStack Query for server state** - Industry standard for data fetching
5. **Axios over fetch** - Better interceptor support for JWT refresh
6. **No mock data** - All data comes from Django via API
7. **Playwright over Jest** - Better E2E testing experience

## Contributing

- Use the existing component patterns
- Follow atomic design principles
- Add TypeScript types for everything
- Write E2E tests for critical flows
- Update this README when adding features
