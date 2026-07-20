import { useCallback, useEffect, useState } from "react";
import { createStrategyAnalysis, getStrategyAnalysis, recalculateStrategyAnalysis } from "../../services/strategyAnalysisService";
import type { StrategyAnalysis, StrategyResult } from "../../types/strategyAnalysis";

const money = (value?: number) => value == null ? "—" : value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const percent = (value?: number) => value == null ? "—" : `${(value * 100).toFixed(1)}%`;
const label = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export default function DealStrategySection({ propertyId }: { propertyId: string }) {
  const [analysis, setAnalysis] = useState<StrategyAnalysis | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const load = useCallback(async () => { setLoading(true); try { setAnalysis(await getStrategyAnalysis(propertyId)); setError(""); } catch { setAnalysis(null); } finally { setLoading(false); } }, [propertyId]);
  useEffect(() => { void load(); }, [load]);
  async function calculate(recalculate: boolean) { setLoading(true); setError(""); try { setAnalysis(recalculate ? await recalculateStrategyAnalysis(propertyId) : await createStrategyAnalysis(propertyId)); } catch (err) { setError(err instanceof Error ? err.message : "Strategy analysis failed."); } finally { setLoading(false); } }
  return <section className="command-card overview-section strategy-section">
    <div className="section-heading"><div><h2>Deal Strategy</h2><p>Deterministic comparison kept separate from the Opportunity Score.</p></div><button className="workspace-action primary" disabled={loading} onClick={() => void calculate(Boolean(analysis))}>{loading ? "Calculating…" : analysis ? "Recalculate" : "Calculate Strategies"}</button></div>
    {error && <p className="media-error">{error}</p>}{!analysis && !loading ? <p>No saved strategy analysis. Calculation runs only when explicitly requested.</p> : analysis && <>
      <div className="strategy-recommendation"><div><span>Recommended strategy</span><strong>{analysis.recommended_strategy ? label(analysis.recommended_strategy) : "No viable strategy"}</strong></div><div><span>Confidence</span><strong>{percent(analysis.recommendation_confidence)}</strong></div><div><span>Status</span><strong>{label(analysis.analysis_status)}</strong></div></div>
      <div className="strategy-cards">{[...analysis.results].sort((a,b) => (a.rank ?? 99)-(b.rank ?? 99)).map((item) => <StrategyCard key={item.strategy} item={item} />)}</div>
      <h3>Side-by-side comparison</h3><div className="repair-cost-table-wrap"><table className="repair-cost-table"><thead><tr><th>Strategy</th><th>Viable / score</th><th>Value basis</th><th>Acquisition</th><th>Profit / cash flow</th><th>Return / cap rate</th></tr></thead><tbody>{analysis.results.map((item) => <tr key={item.strategy}><td>{label(item.strategy)}</td><td>{item.viable ? `Yes · #${item.rank}` : "No"} · {item.score.toFixed(0)}</td><td>{item.value_basis ?? "—"}<br /><small>{money(item.value_low)}–{money(item.value_high)}</small></td><td>{money(item.acquisition_price_used)}</td><td>{item.strategy === "rental_hold" ? `${money(item.monthly_cash_flow)}/mo unlevered` : `${money(item.projected_profit_low)}–${money(item.projected_profit_high)}`}</td><td>{item.cap_rate != null ? `${percent(item.cap_rate)} cap` : `${percent(item.projected_return_percentage_low)}–${percent(item.projected_return_percentage_high)}`}</td></tr>)}</tbody></table></div>
      <p><strong>Next:</strong> {analysis.recommended_next_action}</p><p><strong>Analysis limitations:</strong> {analysis.limitations.join(" · ")}</p><small>Saved {new Date(analysis.analyzed_at).toLocaleString()} · {analysis.assumptions_version}</small>
    </>}
  </section>;
}

function StrategyCard({ item }: { item: StrategyResult }) { return <article className={`strategy-card ${item.viable ? "viable" : "nonviable"}`}><div className="strategy-card-heading"><h3>{item.rank ? `#${item.rank} ` : ""}{label(item.strategy)}</h3><span>{item.viable ? "Viable" : "Not viable"}</span></div><div className="property-snapshot"><Fact label="Score / confidence" value={`${item.score.toFixed(0)} / ${percent(item.confidence)}`} /><Fact label="Acquisition used" value={money(item.acquisition_price_used)} /><Fact label="Value basis" value={item.value_basis ?? "—"} /><Fact label="Profit range" value={`${money(item.projected_profit_low)}–${money(item.projected_profit_high)}`} /><Fact label="Return" value={`${percent(item.projected_return_percentage_low)}–${percent(item.projected_return_percentage_high)}`} /><Fact label="Cap rate" value={percent(item.cap_rate)} /></div><List label="Strengths" values={item.strengths} /><List label="Major risks" values={item.major_risks} /><List label="Missing inputs" values={item.missing_inputs} /><List label="Formula" values={item.formula_notes} /></article>; }
function Fact({ label: title, value }: { label: string; value: string }) { return <div><p className="text-sm text-gray-500">{title}</p><p className="font-medium">{value}</p></div>; }
function List({ label: title, values }: { label: string; values: string[] }) { return values.length ? <div><strong>{title}:</strong><ul>{values.map((value) => <li key={value}>{value}</li>)}</ul></div> : null; }
