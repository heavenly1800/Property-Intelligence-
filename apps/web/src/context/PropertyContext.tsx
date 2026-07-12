import {
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { getProperty } from "../services/propertyService";
import type { Property } from "../types/property";
import { PropertyContext } from "./propertyContextStore";

interface ProviderProps {
  propertyId: string;
  children: ReactNode;
}

export function PropertyProvider({ propertyId, children }: ProviderProps) {
  const [property, setProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setProperty(await getProperty(propertyId));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [propertyId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <PropertyContext.Provider value={{ property, loading, refresh }}>
      {children}
    </PropertyContext.Provider>
  );
}
