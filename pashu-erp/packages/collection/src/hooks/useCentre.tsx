import { createContext, useContext, useState, useCallback, useMemo, ReactNode } from "react";

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
  const [centreId, setCentreId] = useState<string | null>(
    localStorage.getItem("collection_centre_id")
  );
  const [centreName, setCentreName] = useState<string | null>(
    localStorage.getItem("collection_centre_name")
  );

  const setCentre = useCallback((id: string, name: string) => {
    setCentreId(id);
    setCentreName(name);
    localStorage.setItem("collection_centre_id", id);
    localStorage.setItem("collection_centre_name", name);
  }, []);

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
