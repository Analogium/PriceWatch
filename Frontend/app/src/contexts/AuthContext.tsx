/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useEffect, useCallback, useMemo, type ReactNode } from 'react';
import i18n from '../i18n';
import { authApi } from '../api';
import { preferencesApi } from '../api/preferences';
import { queryClient } from '../lib/queryClient';
import type { User, LoginCredentials, RegisterData } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  loginWithGoogle: (credential: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const syncLanguageFromPreferences = async () => {
  try {
    const prefs = await preferencesApi.get();
    if (prefs.language && prefs.language !== i18n.language) {
      i18n.changeLanguage(prefs.language);
    }
  } catch {
    // Preferences not found or error - keep current language
  }
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const userData = await authApi.me();
      setUser(userData);
      await syncLanguageFromPreferences();
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const tokenData = await authApi.login(credentials);
    localStorage.setItem('access_token', tokenData.access_token);
    if (tokenData.refresh_token) {
      localStorage.setItem('refresh_token', tokenData.refresh_token);
    }
    const userData = await authApi.me();
    setUser(userData);
    await syncLanguageFromPreferences();
  }, []);

  const loginWithGoogle = useCallback(async (credential: string) => {
    const tokenData = await authApi.googleLogin(credential);
    localStorage.setItem('access_token', tokenData.access_token);
    if (tokenData.refresh_token) {
      localStorage.setItem('refresh_token', tokenData.refresh_token);
    }
    const userData = await authApi.me();
    setUser(userData);
    await syncLanguageFromPreferences();
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    // Backend doesn't need confirmPassword, only email and password
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { confirmPassword, ...registerData } = data;
    await authApi.register(registerData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    // Clear all React Query cache to prevent showing previous user's data
    queryClient.clear();
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      login,
      loginWithGoogle,
      register,
      logout,
      checkAuth,
    }),
    [user, isAuthenticated, isLoading, login, loginWithGoogle, register, logout, checkAuth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
