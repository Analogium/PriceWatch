import { createBrowserRouter } from 'react-router-dom';
import { lazy } from 'react';

// Route components
import ProtectedRoute from './components/routes/ProtectedRoute';
import PublicRoute from './components/routes/PublicRoute';

// Landing page
const LandingPage = lazy(() => import('./pages/landing/LandingPage'));

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

// Legal & info pages
const PrivacyPolicy = lazy(() => import('./pages/legal/PrivacyPolicy'));
const TermsOfService = lazy(() => import('./pages/legal/TermsOfService'));
const LegalNotices = lazy(() => import('./pages/legal/LegalNotices'));
const About = lazy(() => import('./pages/about/About'));

// Error pages
const NotFound = lazy(() => import('./pages/errors/NotFound'));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
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
  // Legal & info pages (public, no auth required)
  {
    path: '/privacy',
    element: <PrivacyPolicy />,
  },
  {
    path: '/terms',
    element: <TermsOfService />,
  },
  {
    path: '/legal',
    element: <LegalNotices />,
  },
  {
    path: '/about',
    element: <About />,
  },
  // 404
  {
    path: '*',
    element: <NotFound />,
  },
]);

export default router;
