import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { setAuthTokenGetter } from '@workspace/api-client-react';
import { getToken, setToken, clearToken, getStoredUser, setStoredUser, type AuthUser } from '@/lib/auth';

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
  isAuthenticated: false,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());

  // Wire token into the generated api-client-react customFetch
  useEffect(() => {
    setAuthTokenGetter(() => getToken());
  }, []);

  function login(newToken: string, newUser: AuthUser) {
    setToken(newToken);
    setStoredUser(newUser);
    setTokenState(newToken);
    setUser(newUser);
  }

  function logout() {
    clearToken();
    setTokenState(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
