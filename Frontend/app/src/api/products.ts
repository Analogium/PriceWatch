import apiClient from './client';
import type {
  Product,
  ProductCreate,
  ProductUpdate,
  PaginatedProducts,
  ProductFilters,
  PriceHistory,
  PriceStats,
} from '../types';

export const productsApi = {
  getAll: async (filters?: ProductFilters): Promise<PaginatedProducts> => {
    const response = await apiClient.get<PaginatedProducts>('/products', {
      params: filters,
    });
    return response.data;
  },

  getById: async (id: number): Promise<Product> => {
    const response = await apiClient.get<Product>(`/products/${id}`);
    return response.data;
  },

  create: async (data: ProductCreate): Promise<Product> => {
    const response = await apiClient.post<Product>('/products', data);
    return response.data;
  },

  update: async (id: number, data: ProductUpdate): Promise<Product> => {
    const response = await apiClient.put<Product>(`/products/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/products/${id}`);
  },

  checkPrice: async (id: number): Promise<Product> => {
    const response = await apiClient.post<Product>(`/products/${id}/check`);
    return response.data;
  },

  getHistory: async (id: number): Promise<PriceHistory[]> => {
    const response = await apiClient.get<PriceHistory[]>(`/products/${id}/history`);
    return response.data;
  },

  getStats: async (id: number): Promise<PriceStats> => {
    const response = await apiClient.get<PriceStats>(`/products/${id}/history/stats`);
    return response.data;
  },
};

export default productsApi;
