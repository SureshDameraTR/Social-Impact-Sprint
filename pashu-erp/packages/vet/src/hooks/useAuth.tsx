import { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from "react";
import { getMe, logout as apiLogout } from "../api/auth";

interface AuthUser {
  userId: string;
  role: string;
  name: string;
  district: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  refresh: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const { data } = await getMe();
      setUser({
        userId: data.user_id,
        role: data.role,
        name: data.name,
        district: data.location_district,
      });
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleLogout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const value = useMemo(
    () => ({ user, loading, refresh, logout: handleLogout }),
    [user, loading, refresh, handleLogout]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
