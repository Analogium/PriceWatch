import { type ReactNode } from 'react';
import { Header } from './Header';
import { Footer } from './Footer';
import { ToastContainer } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';

interface LayoutProps {
  children: ReactNode;
  showFooter?: boolean;
}

export function Layout({ children, showFooter = true }: LayoutProps) {
  const { toasts } = useToast();

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-6 md:py-8">{children}</main>
      {showFooter && <Footer />}
      <ToastContainer toasts={toasts} />
    </div>
  );
}

export default Layout;
