import { useCallback, useEffect, useState } from "react";
import { getPropertyConditionSummary } from "../../services/propertyMediaService";
import type { PropertyConditionSummary, RepairItem } from "../../types/propertyMedia";

const money = (value = 0) => value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const percent = (value = 0) => `${Math.round(value * 100)}%`;

export default function AIConditionAnalysisCard({ propertyId }: { propertyId: string }) {
  const [summary, setSummary] = useState<PropertyConditionSummary | null>(null);
  const [error, setError] = useState("");
  const refresh = useCallback(() => { void getPropertyConditionSummary(propertyId).then((value) => { setSummary(value); setError(""); }).catch((err) => setError(err instanceof Error ? err.message : "Unable to load condition analysis.")); }, [propertyId]);
  useEffect(() => { refresh(); window.addEventListener("condition-analysis-updated", refresh); return () => window.removeEventListener("condition-analysis-updated", refresh); }, [refresh]);
  return <section className="command-card overview-section"><h2>AI Condition Analysis</h2>
    {error && <p className="media-error">{error}</p>}
    {!summary ? <p>Analyze a property photo to create an evidence-based visible-condition summary.</p> : <>
      <div className="property-snapshot"><Fact label="Visible Condition" value={summary.overall_visible_condition} /><Fact label="Rent-Ready Guidance" value={summary.overall_rent_ready_status.replaceAll("_", " ")} /><Fact label="Regional Profile" value={summary.regional_profile_name || "National fallback"} /><Fact label="Profile Match" value={`${percent(summary.profile_match_confidence)} · ${summary.profile_match_reason || "fallback"}`} /><Fact label="Total Visible Estimate" value={`${money(summary.estimated_visible_repair_cost_low)}–${money(summary.estimated_visible_repair_cost_high)}`} /><Fact label="Photos Analyzed" value={String(summary.analyzed_photo_count)} /></div>
      <p><strong>Visible scope:</strong> {summary.visible_repair_scope_summary || "No visible repair scope identified."}</p>
      {summary.visible_repair_items?.length ? <div className="repair-cost-table-wrap"><table className="repair-cost-table"><thead><tr><th>Visible repair</th><th>Quantity</th><th>Unit cost</th><th>Extended</th></tr></thead><tbody>{summary.visible_repair_items.map((item, index) => <RepairRow key={`${item.category}-${item.area}-${index}`} item={item} />)}</tbody></table></div> : <p>No visible repair items were priced.</p>}
      <div className="repair-totals"><Fact label="Visible Repair Subtotal" value={`${money(summary.visible_repair_subtotal_low)}–${money(summary.visible_repair_subtotal_high)}`} /><Fact label="Contingency" value={`${money(summary.contingency_low)}–${money(summary.contingency_high)}`} /><Fact label="Total" value={`${money(summary.estimated_visible_repair_cost_low)}–${money(summary.estimated_visible_repair_cost_high)}`} /></div>
      <p><strong>Major observed issues:</strong> {summary.major_observed_issues.map((item) => item.description).join(" · ") || "None identified."}</p><p><strong>Inspection required:</strong> {summary.required_inspection_items.map((item) => item.description).join(" · ") || "No specific items identified."}</p>
      <h3>Cost limitations</h3><ul>{summary.cost_limitations?.map((item) => <li key={item}>{item}</li>)}</ul>
      <p className="underwriting-disclaimer">Underwriting assumptions only—not contractor bids. AI/regional estimates remain separate from manually entered rehab costs.</p><small>Effective {summary.cost_assumption_effective_date || "date unavailable"} · {summary.cost_assumption_version} · {summary.review_status}</small>
    </>}
  </section>;
}

function RepairRow({ item }: { item: RepairItem }) { const quantity = item.estimated_quantity_low == null || item.estimated_quantity_high == null ? `Unknown · minimum allowance (${item.quantity_unit})` : `${item.estimated_quantity_low}–${item.estimated_quantity_high} ${item.quantity_unit} (${percent(item.quantity_confidence)})`; return <tr><td><strong>{item.category}</strong><br /><small>{item.area} · {item.description}</small></td><td>{quantity}</td><td>{money(item.unit_cost_low)}–{money(item.unit_cost_high)}</td><td>{money(item.extended_cost_low)}–{money(item.extended_cost_high)}</td></tr>; }
function Fact({ label, value }: { label: string; value: string }) { return <div><p className="text-sm text-gray-500">{label}</p><p className="font-medium">{value}</p></div>; }
