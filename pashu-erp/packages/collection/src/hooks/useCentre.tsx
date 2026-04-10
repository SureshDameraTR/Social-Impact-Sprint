import { createContext, useContext, useState, ReactNode } from "react";

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

  const setCentre = (id: string, name: string) => {
    setCentreId(id);
    setCentreName(name);
    localStorage.setItem("collection_centre_id", id);
    localStorage.setItem("collection_centre_name", name);
  };

  return (
    <CentreContext.Provider value={{ centreId, centreName, setCentre }}>
      {children}
    </CentreContext.Provider>
  );
}

export function useCentre() {
  return useContext(CentreContext);
}
