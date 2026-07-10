import PropertyCard from "./PropertyCard";
import { Property } from "../../types/property";

type Props = {
  properties: Property[];
};

export default function PropertyList({
  properties,
}: Props) {
  return (
    <>
      {properties.map((property) => (
        <PropertyCard
          key={property.property_id}
          property={property}
        />
      ))}
    </>
  );
}