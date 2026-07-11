import { useMemo } from "react";

import { useProperty } from "../../context/PropertyContext";
import { buildWorkspace } from "./buildWorkspace";

export function useWorkspace() {
    const {
        property,
        loading,
        refresh,
    } = useProperty();

    const workspace = useMemo(() => {
        if (!property) return null;

        return buildWorkspace(property);
    }, [property]);

    return {
        property,
        workspace,
        loading,
        refresh,
    };
}