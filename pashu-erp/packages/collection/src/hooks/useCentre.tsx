import { createContext, useContext, useState, useCallback, useEffect, useMemo, ReactNode } from "react";
import api from "../api/client";
import { useAuth } from "./useAuth";

interface CentreContextValue {
  centreId: string | null;
  centreName: string | null;
  setCentre: (id: string, name: string) => void;
}

const CentreContext = createContext<CentreContextValue>({
  centreId: null,
  centreName: null,
  setCentre: () => {},
});

export function CentreProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [centreId, setCentreId] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("collection_centre_id") : null
  );
  const [centreName, setCentreName] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("collection_centre_name") : null
  );

  const setCentre = useCallback((id: string, name: string) => {
    setCentreId(id);
    setCentreName(name);
    localStorage.setItem("collection_centre_id", id);
    localStorage.setItem("collection_centre_name", name);
  }, []);

  // Auto-fetch assigned centre when user logs in and no centre is cached
  useEffect(() => {
    if (!user || centreId) return;
    api.get("/milk-center/my-center").then(({ data }) => {
      setCentre(data.id, data.name);
    }).catch(() => {});
  }, [user, centreId, setCentre]);

  const value = useMemo(
    () => ({ centreId, centreName, setCentre }),
    [centreId, centreName, setCentre]
  );

  return (
    <CentreContext.Provider value={value}>
      {children}
    </CentreContext.Provider>
  );
}

export function useCentre() {
  return useContext(CentreContext);
}
