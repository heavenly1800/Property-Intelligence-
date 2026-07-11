import {
    createContext,
    useContext,
    useEffect,
    useState,
    ReactNode,
    useCallback,
} from "react";

import { getProperty } from "../services/propertyService";
import type { Property } from "../types/property";

interface PropertyContextValue {
    property: Property | null;
    loading: boolean;
    refresh: () => Promise<void>;
}

const PropertyContext =
    createContext<PropertyContextValue | null>(null);

interface ProviderProps {
    propertyId: string;
    children: ReactNode;
}

export function PropertyProvider({
    propertyId,
    children,
}: ProviderProps) {
    const [property, setProperty] =
        useState<Property | null>(null);

    const [loading, setLoading] =
        useState(true);

    const refresh = useCallback(async () => {
        setLoading(true);

        try {
            const result =
                await getProperty(propertyId);

            setProperty(result);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [propertyId]);

    useEffect(() => {
        refresh();
    }, [refresh]);

    return (
        <PropertyContext.Provider
            value={{
                property,
                loading,
                refresh,
            }}
        >
            {children}
        </PropertyContext.Provider>
    );
}

export function useProperty() {
    const context =
        useContext(PropertyContext);

    if (!context) {
        throw new Error(
            "useProperty must be used within PropertyProvider."
        );
    }

    return context;
}