export interface User {
  id: number;
  email: string;
  created_at: string;
  auth_provider: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  confirmPassword: string;
  acceptTerms: true;
}

export interface Token {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
