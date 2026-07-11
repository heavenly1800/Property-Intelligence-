import { useParams } from "react-router-dom";

import { PropertyProvider } from "../context/PropertyContext";

import PropertyDetailPage from "../components/property-detail/PropertyDetailPage";

export default function PropertyDetail() {
    const { id } = useParams();

    if (!id) {
        return <div>Property not found.</div>;
    }

    return (
        <PropertyProvider propertyId={id}>
            <PropertyDetailPage />
        </PropertyProvider>
    );
}