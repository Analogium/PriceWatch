import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Lazy load pages for code splitting
import { lazy, Suspense } from 'react';

// Auth pages
const Login = lazy(() => import('./pages/auth/Login'));
const Register = lazy(() => import('./pages/auth/Register'));
const ForgotPassword = lazy(() => import('./pages/auth/ForgotPassword'));
const ResetPassword = lazy(() => import('./pages/auth/ResetPassword'));
const VerifyEmail = lazy(() => import('./pages/auth/VerifyEmail'));

// App pages
const Dashboard = lazy(() => import('./pages/dashboard/Dashboard'));
const ProductDetail = lazy(() => import('./pages/products/ProductDetail'));
const ProductAdd = lazy(() => import('./pages/products/ProductAdd'));
const ProductEdit = lazy(() => import('./pages/products/ProductEdit'));
const Settings = lazy(() => import('./pages/settings/Settings'));

// Loading component
function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  );
}

// Protected route wrapper
function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <PageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Suspense fallback={<PageLoader />}>
      <Outlet />
    </Suspense>
  );
}

// Public route wrapper (redirects to dashboard if already authenticated)
function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <PageLoader />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Suspense fallback={<PageLoader />}>
      <Outlet />
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  // Public routes (auth pages)
  {
    element: <PublicRoute />,
    children: [
      {
        path: '/login',
        element: <Login />,
      },
      {
        path: '/register',
        element: <Register />,
      },
      {
        path: '/forgot-password',
        element: <ForgotPassword />,
      },
      {
        path: '/reset-password',
        element: <ResetPassword />,
      },
      {
        path: '/verify-email',
        element: <VerifyEmail />,
      },
    ],
  },
  // Protected routes (app pages)
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: '/dashboard',
        element: <Dashboard />,
      },
      {
        path: '/products/add',
        element: <ProductAdd />,
      },
      {
        path: '/products/:id',
        element: <ProductDetail />,
      },
      {
        path: '/products/:id/edit',
        element: <ProductEdit />,
      },
      {
        path: '/settings',
        element: <Settings />,
      },
    ],
  },
  // 404
  {
    path: '*',
    element: (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900">404</h1>
          <p className="mt-2 text-gray-600">Page non trouvée</p>
        </div>
      </div>
    ),
  },
]);

export default router;
