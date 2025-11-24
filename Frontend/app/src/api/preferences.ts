import apiClient from './client';
import type { UserPreferences, UserPreferencesUpdate } from '../types';

export const preferencesApi = {
  get: async (): Promise<UserPreferences> => {
    const response = await apiClient.get<UserPreferences>('/users/preferences');
    return response.data;
  },

  create: async (data: UserPreferencesUpdate): Promise<UserPreferences> => {
    const response = await apiClient.post<UserPreferences>('/users/preferences', data);
    return response.data;
  },

  update: async (data: UserPreferencesUpdate): Promise<UserPreferences> => {
    const response = await apiClient.put<UserPreferences>('/users/preferences', data);
    return response.data;
  },

  delete: async (): Promise<void> => {
    await apiClient.delete('/users/preferences');
  },
};

export default preferencesApi;
