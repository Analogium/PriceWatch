import apiClient from './client';

export const usersApi = {
  exportData: async (): Promise<Blob> => {
    const response = await apiClient.get('/users/me/export', {
      responseType: 'blob',
    });
    return response.data;
  },

  deleteAccount: async (password?: string): Promise<void> => {
    await apiClient.delete('/users/me', {
      data: { password: password ?? null },
    });
  },
};

export default usersApi;
