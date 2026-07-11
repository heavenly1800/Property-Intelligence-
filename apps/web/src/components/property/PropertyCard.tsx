import { Link } from "react-router-dom";
import type { Property } from "../../types/property";

type Props = {
  property: Property;
};

export default function PropertyCard({
  property,
}: Props) {
  return (
    <Link
      to={`/properties/${property.property_id}`}
      style={{
        textDecoration: "none",
        color: "inherit",
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 12,
          padding: 20,
          marginBottom: 20,
          boxShadow: "0 2px 8px rgba(0,0,0,.08)",
        }}
      >
        <h2>{property.address}</h2>

        <p>
          {property.city}
        </p>

        <strong>
          {property.property_type}
        </strong>

        <hr />

        <h3>
          Opportunity Score
        </h3>

        <h1>
          {property.opportunity_score ?? "--"}
        </h1>

        <p>
          Strategy:
          {" "}
          {property.strategy ?? "Pending"}
        </p>

        <p>
          Confidence:
          {" "}
          {property.confidence ?? "--"}%
        </p>

        <p>
          Next Action:
          {" "}
          {property.next_action ?? "Analyze"}
        </p>
      </div>
    </Link>
  );
}