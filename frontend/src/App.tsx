/**
 * Main App Component
 *
 * Root application component with routing setup.
 * This is a placeholder - routing will be configured with TanStack Router.
 */

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { authApi } from '@/api/auth.api';

function App() {
  const { setUser, setLoading } = useAuthStore();

  useEffect(() => {
    // Initialize auth state on app load
    const initAuth = async () => {
      if (authApi.isAuthenticated()) {
        try {
          const user = await authApi.getCurrentUser();
          setUser(user);
        } catch (error) {
          console.error('Failed to load user:', error);
          setUser(null);
        }
      } else {
        setLoading(false);
      }
    };

    initAuth();
  }, [setUser, setLoading]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-primary">
            Service Provider
          </h1>
          <p className="text-secondary-500">
            Frontend setup complete. Routing and pages coming next.
          </p>
          <div className="flex gap-4 justify-center mt-8">
            <button className="btn btn-primary">
              Primary Button
            </button>
            <button className="btn btn-secondary">
              Secondary Button
            </button>
            <button className="btn btn-outline">
              Outline Button
            </button>
          </div>
          <div className="mt-8">
            <span className="badge badge-primary mr-2">Primary Badge</span>
            <span className="badge badge-success mr-2">Success Badge</span>
            <span className="badge badge-warning mr-2">Warning Badge</span>
            <span className="badge badge-danger">Danger Badge</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
