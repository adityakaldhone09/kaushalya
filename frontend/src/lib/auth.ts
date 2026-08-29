/**
 * KAUSHALYA Auth helpers
 * Manages JWT token storage and user session in localStorage.
 */

const TOKEN_KEY = 'kaushalya_token';
const USER_KEY = 'kaushalya_user';

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: string;
  organization?: string | null;
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredUser(user: AuthUser): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

/** Returns the dashboard path for a given role */
export function roleDashboard(role: string): string {
  switch (role) {
    case 'GOVERNMENT_ADMIN':
    case 'SUPER_ADMIN':
      return '/admin/dashboard';
    case 'EMPLOYER':
      return '/employer/dashboard';
    case 'TRAINING_INSTITUTE':
      return '/institute/dashboard';
    case 'TRAINEE':
    default:
      return '/trainee/dashboard';
  }
}
