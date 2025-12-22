import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productsApi } from '@/api/products';
import type { ProductFilters, ProductCreate, ProductUpdate } from '@/types';

// Query keys
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (filters?: ProductFilters) => [...productKeys.lists(), filters] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (id: number) => [...productKeys.details(), id] as const,
  history: (id: number) => [...productKeys.detail(id), 'history'] as const,
  stats: (id: number) => [...productKeys.detail(id), 'stats'] as const,
};

// Get all products with filters
export function useProducts(filters?: ProductFilters) {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () => productsApi.getAll(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Get single product by ID
export function useProduct(id: number) {
  return useQuery({
    queryKey: productKeys.detail(id),
    queryFn: () => productsApi.getById(id),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Get product price history
export function useProductHistory(id: number) {
  return useQuery({
    queryKey: productKeys.history(id),
    queryFn: () => productsApi.getHistory(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get product price stats
export function useProductStats(id: number) {
  return useQuery({
    queryKey: productKeys.stats(id),
    queryFn: () => productsApi.getStats(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Create product mutation
export function useCreateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ProductCreate) => productsApi.create(data),
    onSuccess: () => {
      // Invalidate and refetch all product lists
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
    },
  });
}

// Update product mutation
export function useUpdateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductUpdate }) => productsApi.update(id, data),
    onSuccess: (_, variables) => {
      // Invalidate specific product and all lists
      queryClient.invalidateQueries({ queryKey: productKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
    },
  });
}

// Delete product mutation
export function useDeleteProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => productsApi.delete(id),
    onSuccess: () => {
      // Invalidate all product lists
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
    },
  });
}

// Check price mutation
export function useCheckPrice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => productsApi.checkPrice(id),
    onSuccess: (updatedProduct) => {
      // Update the specific product in cache
      queryClient.setQueryData(productKeys.detail(updatedProduct.id), updatedProduct);

      // Invalidate lists to reflect the updated product
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });

      // Invalidate history and stats as they may have changed
      queryClient.invalidateQueries({ queryKey: productKeys.history(updatedProduct.id) });
      queryClient.invalidateQueries({ queryKey: productKeys.stats(updatedProduct.id) });
    },
  });
}
