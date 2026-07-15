import { useState } from "react";

import { updateFinancials } from "../../services/propertyService";
import type { Property } from "../../types/property";

type Props = { property: Property; onSaved: () => Promise<void> };

const money = (value?: number) => value == null ? "—" : value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const percent = (value?: number) => value == null ? "—" : `${(value * 100).toFixed(2)}%`;

export default function FinancialIntelligenceCard({ property, onSaved }: Props) {
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    listing_url: property.listing_url ?? "", listing_source: property.listing_source ?? "",
    property_subtype: property.property_subtype ?? "", year_built: property.year_built?.toString() ?? "",
    bedrooms: property.bedrooms?.toString() ?? "", bathrooms: property.bathrooms?.toString() ?? "",
    estimated_market_value: property.estimated_market_value?.toString() ?? "",
    asking_price: property.asking_price?.toString() ?? "",
    unit_count: property.unit_count?.toString() ?? "",
    current_monthly_rent: property.current_monthly_rent?.toString() ?? "",
    current_monthly_rent_per_unit: property.current_monthly_rent_per_unit?.toString() ?? "",
    estimated_monthly_rent: property.estimated_monthly_rent?.toString() ?? "",
    estimated_monthly_rent_per_unit: property.estimated_monthly_rent_per_unit?.toString() ?? "",
    expected_operating_expense_percentage: property.expected_operating_expense_percentage?.toString() ?? "",
    occupancy_status: property.occupancy_status ?? "",
    property_condition: property.property_condition ?? "",
    rehab_scope_summary: property.rehab_scope_summary ?? "",
    estimated_rehab_cost_low: property.estimated_rehab_cost_low?.toString() ?? "",
    estimated_rehab_cost_high: property.estimated_rehab_cost_high?.toString() ?? "",
    after_repair_value: property.after_repair_value?.toString() ?? "",
    estimated_post_rehab_monthly_rent: property.estimated_post_rehab_monthly_rent?.toString() ?? "",
    rehab_items: property.rehab_items?.join(", ") ?? "",
    rent_ready: property.rent_ready ?? false, rehab_needed: property.rehab_needed ?? false,
  });

  const set = (key: keyof typeof form, value: string) => setForm({ ...form, [key]: value });
  const number = (value: string) => value.trim() ? Number(value) : undefined;

  async function save() {
    setSaving(true);
    try {
      await updateFinancials(property.property_id, {
        listing_url: form.listing_url || undefined, listing_source: form.listing_source || undefined,
        property_subtype: form.property_subtype || undefined, year_built: number(form.year_built),
        bedrooms: number(form.bedrooms), bathrooms: number(form.bathrooms),
        estimated_market_value: number(form.estimated_market_value),
        asking_price: number(form.asking_price), unit_count: number(form.unit_count),
        current_monthly_rent: number(form.current_monthly_rent), estimated_monthly_rent: number(form.estimated_monthly_rent),
        current_monthly_rent_per_unit: number(form.current_monthly_rent_per_unit), estimated_monthly_rent_per_unit: number(form.estimated_monthly_rent_per_unit),
        expected_operating_expense_percentage: number(form.expected_operating_expense_percentage),
        occupancy_status: form.occupancy_status || undefined, property_condition: form.property_condition || undefined,
        rehab_scope_summary: form.rehab_scope_summary || undefined,
        estimated_rehab_cost_low: number(form.estimated_rehab_cost_low), estimated_rehab_cost_high: number(form.estimated_rehab_cost_high),
        after_repair_value: number(form.after_repair_value), financial_data_source: "Manual entry",
        estimated_post_rehab_monthly_rent: number(form.estimated_post_rehab_monthly_rent),
        rehab_items: form.rehab_items.split(",").map((item) => item.trim()).filter(Boolean),
        rent_ready: form.rent_ready, rehab_needed: form.rehab_needed,
      });
      await onSaved();
    } finally { setSaving(false); }
  }

  return <>
    <section className="command-card overview-section">
      <h2>Financial Intelligence</h2>
      <div className="property-snapshot">
        <Fact label="Asking Price" value={money(property.asking_price)} />
        <Fact label="Tax Assessed Value" value={money(property.assessed_total_value)} />
        <Fact label="Estimated Market Value (Estimate)" value={money(property.estimated_market_value)} />
        <Fact label="Unit Count / Subtype" value={[property.unit_count, property.property_subtype].filter(Boolean).join(" / ") || "—"} />
        <Fact label="Current / Estimated Monthly Rent" value={`${money(property.current_monthly_rent)} / ${money(property.estimated_monthly_rent)}`} />
        <Fact label="Annual Gross Rent" value={money(property.current_annual_rent ?? property.estimated_annual_rent)} />
        <Fact label="Operating Expenses" value={money(property.estimated_operating_expenses_annual)} />
        <Fact label="NOI" value={money(property.estimated_noi_annual)} />
        <Fact label="Cap Rate" value={percent(property.estimated_cap_rate)} />
        <Fact label="GRM" value={property.gross_rent_multiplier?.toFixed(2) ?? "—"} />
        <Fact label="Rent-Ready" value={property.rent_ready == null ? "—" : property.rent_ready ? "Yes" : "No"} />
        <Fact label="Confidence" value={property.financial_analysis_confidence ?? "—"} />
      </div>
      <p className="mt-4 text-sm text-gray-500">Missing Inputs: {property.financial_missing_items?.join(" · ") ?? "—"}</p>
      <p className="font-medium">Next: {property.recommended_financial_action ?? "Enter financial inputs."}</p>
    </section>
    <section className="command-card overview-section">
      <h2>Rehab &amp; Exit Analysis</h2>
      <div className="property-snapshot">
        <Fact label="Rehab Needed" value={property.rehab_needed == null ? "—" : property.rehab_needed ? "Yes" : "No"} />
        <Fact label="Repair Scope" value={property.rehab_scope_summary ?? "—"} />
        <Fact label="Rehab Cost Range" value={`${money(property.estimated_rehab_cost_low)} – ${money(property.estimated_rehab_cost_high)}`} />
        <Fact label="ARV Range (Estimate)" value={`${money(property.estimated_after_repair_value_low)} – ${money(property.estimated_after_repair_value_high)}`} />
        <Fact label="Flip Profit Range" value={`${money(property.estimated_flip_profit_low)} – ${money(property.estimated_flip_profit_high)}`} />
        <Fact label="Post-Rehab Rent" value={money(property.estimated_post_rehab_monthly_rent)} />
      </div>
    </section>
    <section className="command-card overview-section"><h2>Manual Financial Inputs</h2><div className="grid grid-cols-1 gap-2 md:grid-cols-2">
      <Input label="Asking Price" value={form.asking_price} set={(v) => set("asking_price", v)} /><Input label="Unit Count" value={form.unit_count} set={(v) => set("unit_count", v)} />
      <Input label="Listing URL" value={form.listing_url} set={(v) => set("listing_url", v)} /><Input label="Listing Source" value={form.listing_source} set={(v) => set("listing_source", v)} />
      <Input label="Property Subtype" value={form.property_subtype} set={(v) => set("property_subtype", v)} /><Input label="Year Built" value={form.year_built} set={(v) => set("year_built", v)} />
      <Input label="Bedrooms" value={form.bedrooms} set={(v) => set("bedrooms", v)} /><Input label="Bathrooms" value={form.bathrooms} set={(v) => set("bathrooms", v)} />
      <Input label="Estimated Market Value" value={form.estimated_market_value} set={(v) => set("estimated_market_value", v)} />
      <Input label="Current Monthly Rent" value={form.current_monthly_rent} set={(v) => set("current_monthly_rent", v)} /><Input label="Estimated Monthly Rent" value={form.estimated_monthly_rent} set={(v) => set("estimated_monthly_rent", v)} />
      <Input label="Current Rent per Unit" value={form.current_monthly_rent_per_unit} set={(v) => set("current_monthly_rent_per_unit", v)} /><Input label="Estimated Rent per Unit" value={form.estimated_monthly_rent_per_unit} set={(v) => set("estimated_monthly_rent_per_unit", v)} />
      <Input label="Operating Expense %" value={form.expected_operating_expense_percentage} set={(v) => set("expected_operating_expense_percentage", v)} /><Input label="Occupancy Status" value={form.occupancy_status} set={(v) => set("occupancy_status", v)} />
      <Input label="Property Condition" value={form.property_condition} set={(v) => set("property_condition", v)} /><Input label="Rehab Scope" value={form.rehab_scope_summary} set={(v) => set("rehab_scope_summary", v)} />
      <Input label="Rehab Cost Low" value={form.estimated_rehab_cost_low} set={(v) => set("estimated_rehab_cost_low", v)} /><Input label="Rehab Cost High" value={form.estimated_rehab_cost_high} set={(v) => set("estimated_rehab_cost_high", v)} />
      <Input label="Estimated ARV" value={form.after_repair_value} set={(v) => set("after_repair_value", v)} />
      <Input label="Post-Rehab Monthly Rent" value={form.estimated_post_rehab_monthly_rent} set={(v) => set("estimated_post_rehab_monthly_rent", v)} /><Input label="Known Repair Items (comma separated)" value={form.rehab_items} set={(v) => set("rehab_items", v)} />
      <Toggle label="Rent Ready" checked={form.rent_ready} set={(value) => setForm({ ...form, rent_ready: value })} /><Toggle label="Rehab Needed" checked={form.rehab_needed} set={(value) => setForm({ ...form, rehab_needed: value })} />
    </div><button className="workspace-action primary mt-4" onClick={save} disabled={saving}>{saving ? "Saving..." : "Save Financial Inputs"}</button></section>
  </>;
}

function Fact({ label, value }: { label: string; value: string }) { return <div><p className="text-sm text-gray-500">{label}</p><p className="font-medium">{value}</p></div>; }
function Input({ label, value, set }: { label: string; value: string; set: (value: string) => void }) { return <label className="text-sm text-gray-500">{label}<input className="mt-1 w-full rounded border border-gray-300 p-2 text-gray-900" value={value} onChange={(event) => set(event.target.value)} /></label>; }
function Toggle({ label, checked, set }: { label: string; checked: boolean; set: (value: boolean) => void }) { return <label className="flex items-center gap-2 text-sm text-gray-700"><input type="checkbox" checked={checked} onChange={(event) => set(event.target.checked)} />{label}</label>; }
