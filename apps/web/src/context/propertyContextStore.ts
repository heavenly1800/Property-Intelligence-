import { createContext } from "react";

import type { Property } from "../types/property";

export interface PropertyContextValue {
  property: Property | null;
  loading: boolean;
  refresh: () => Promise<void>;
}

export const PropertyContext = createContext<PropertyContextValue | null>(null);
