/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { Product } from '@/types';

interface PriceCheckItem {
  productId: number;
  productName: string;
  startedAt: number;
}

interface PriceCheckContextValue {
  checkingProducts: PriceCheckItem[];
  isChecking: (productId: number) => boolean;
  startChecking: (product: Product) => void;
  finishChecking: (productId: number) => void;
}

const PriceCheckContext = createContext<PriceCheckContextValue | undefined>(undefined);

export const PriceCheckProvider = ({ children }: { children: ReactNode }) => {
  const [checkingProducts, setCheckingProducts] = useState<PriceCheckItem[]>([]);

  const isChecking = useCallback(
    (productId: number): boolean => {
      return checkingProducts.some((item) => item.productId === productId);
    },
    [checkingProducts]
  );

  const startChecking = useCallback((product: Product) => {
    setCheckingProducts((prev) => {
      // Avoid duplicates
      if (prev.some((item) => item.productId === product.id)) {
        return prev;
      }
      return [
        ...prev,
        {
          productId: product.id,
          productName: product.name,
          startedAt: Date.now(),
        },
      ];
    });
  }, []);

  const finishChecking = useCallback((productId: number) => {
    setCheckingProducts((prev) => prev.filter((item) => item.productId !== productId));
  }, []);

  return (
    <PriceCheckContext.Provider
      value={{ checkingProducts, isChecking, startChecking, finishChecking }}
    >
      {children}
    </PriceCheckContext.Provider>
  );
};

export const usePriceCheck = () => {
  const context = useContext(PriceCheckContext);
  if (!context) {
    throw new Error('usePriceCheck must be used within a PriceCheckProvider');
  }
  return context;
};
