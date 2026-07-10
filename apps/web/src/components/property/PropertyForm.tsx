import { useState } from "react";
import { createProperty } from "../../services/propertyService";

export default function PropertyForm() {
  const [form, setForm] = useState({
    property_id: "",
    address: "",
    city: "",
    county: "",
    state: "",
    zip_code: "",
    property_type: "",
  });

  async function submit() {
    await createProperty(form as any);

    window.location.reload();
  }

  return (
    <div style={{ marginBottom: 30 }}>
      <input
        placeholder="Property ID"
        value={form.property_id}
        onChange={(e) =>
          setForm({ ...form, property_id: e.target.value })
        }
      />

      <input
        placeholder="Address"
        value={form.address}
        onChange={(e) =>
          setForm({ ...form, address: e.target.value })
        }
      />

      <input
        placeholder="City"
        value={form.city}
        onChange={(e) =>
          setForm({ ...form, city: e.target.value })
        }
      />

      <input
        placeholder="County"
        value={form.county}
        onChange={(e) =>
          setForm({ ...form, county: e.target.value })
        }
      />

      <input
        placeholder="State"
        value={form.state}
        onChange={(e) =>
          setForm({ ...form, state: e.target.value })
        }
      />

      <input
        placeholder="Zip Code"
        value={form.zip_code}
        onChange={(e) =>
          setForm({ ...form, zip_code: e.target.value })
        }
      />

      <input
        placeholder="Property Type"
        value={form.property_type}
        onChange={(e) =>
          setForm({ ...form, property_type: e.target.value })
        }
      />

      <button onClick={submit}>
        Save Property
      </button>
    </div>
  );
}