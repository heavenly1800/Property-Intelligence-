import { useEffect, useState } from "react";

import DashboardLayout from "../components/layout/DashboardLayout";
import PropertyForm from "../components/property/PropertyForm";
import PropertyList from "../components/property/PropertyList";
import PropertySearch from "../components/property/PropertySearch";

import { getProperties } from "../services/propertyService";
import type { Property } from "../types/property";

export default function Properties() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    getProperties().then(setProperties);
  }, []);

  const filteredProperties = properties.filter((property) =>
    `${property.address} ${property.city} ${property.property_type}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div
        style={{
          maxWidth: 1200,
          margin: "auto",
        }}
      >
        <h1>Properties</h1>

        <PropertySearch
          value={search}
          onChange={setSearch}
        />

        <PropertyForm />

        <PropertyList
          properties={filteredProperties}
        />
      </div>
    </DashboardLayout>
  );
}