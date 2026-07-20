import { useCallback, useEffect, useState } from "react";
import {
  analyzeAllPropertyMedia, analyzePropertyMedia, deletePropertyMedia, getPropertyMediaAnalysis,
  listPropertyMedia, setPrimaryPropertyMedia, updatePropertyMedia, uploadPropertyMedia,
} from "../../services/propertyMediaService";
import type { PropertyMedia, PropertyMediaAnalysis } from "../../types/propertyMedia";

const money = (value: number) => value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export default function PropertyMediaGallery({ propertyId }: { propertyId: string }) {
  const [media, setMedia] = useState<PropertyMedia[]>([]);
  const [selected, setSelected] = useState<PropertyMedia | null>(null);
  const [analysis, setAnalysis] = useState<PropertyMediaAnalysis | null>(null);
  const [modal, setModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [batchProgress, setBatchProgress] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const items = await listPropertyMedia(propertyId);
      setMedia(items);
      setSelected((current) => items.find((item) => item.media_id === current?.media_id) ?? items.find((item) => item.is_primary) ?? items[0] ?? null);
      setError("");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load photos."); }
    finally { setLoading(false); }
  }, [propertyId]);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    setAnalysis(null);
    if (selected?.analysis_status === "completed") {
      void getPropertyMediaAnalysis(propertyId, selected.media_id).then(setAnalysis).catch(() => setAnalysis(null));
    }
  }, [propertyId, selected?.media_id, selected?.analysis_status]);

  const mutate = async (action: () => Promise<unknown>) => {
    try { await action(); await refresh(); }
    catch (err) { setError(err instanceof Error ? err.message : "Photo update failed."); }
  };

  async function analyzeSelected(reanalyze: boolean) {
    if (!selected) return;
    setAnalyzing(true); setError("");
    try {
      const result = await analyzePropertyMedia(propertyId, selected.media_id, reanalyze);
      setAnalysis(result); await refresh(); window.dispatchEvent(new Event("condition-analysis-updated"));
    } catch (err) { setError(err instanceof Error ? err.message : "Photo analysis failed."); }
    finally { setAnalyzing(false); }
  }

  async function analyzeAll() {
    setAnalyzing(true); setError(""); setBatchProgress(`Analyzing up to ${media.length} photos…`);
    try {
      const result = await analyzeAllPropertyMedia(propertyId);
      setBatchProgress(`${result.completed} completed${result.failed ? `, ${result.failed} failed` : ""}.`);
      await refresh(); window.dispatchEvent(new Event("condition-analysis-updated"));
    } catch (err) { setError(err instanceof Error ? err.message : "Batch analysis failed."); setBatchProgress(""); }
    finally { setAnalyzing(false); }
  }

  if (loading) return <section className="command-card overview-section"><h2>Property Photos</h2><p>Loading photos…</p></section>;
  return <section className="command-card overview-section media-gallery">
    <div className="media-actions"><h2>Property Photos</h2>{media.length > 0 && <button onClick={() => void analyzeAll()} disabled={analyzing}>Analyze All Photos</button>}</div>
    <input aria-label="Upload property photo" type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(event) => { const file = event.target.files?.[0]; if (file) void mutate(() => uploadPropertyMedia(propertyId, file)); event.currentTarget.value = ""; }} />
    {batchProgress && <p role="status">{batchProgress}</p>}{error && <p className="media-error" role="alert">{error}</p>}
    {selected ? <>
      <button className="media-primary" onClick={() => setModal(true)}><img src={selected.public_url} alt={selected.caption || selected.original_filename} /></button>
      <div className="media-actions">
        <button onClick={() => void analyzeSelected(Boolean(analysis))} disabled={analyzing}>{analyzing ? "Analyzing…" : analysis ? "Reanalyze" : "Analyze Photo"}</button>
        <button onClick={() => void mutate(() => setPrimaryPropertyMedia(propertyId, selected.media_id))}>Set primary</button>
        <button onClick={() => { if (confirm("Delete this photo?")) void mutate(() => deletePropertyMedia(propertyId, selected.media_id)); }}>Delete</button>
      </div>
      <label>Caption<input value={selected.caption ?? ""} onChange={(event) => setSelected({ ...selected, caption: event.target.value })} onBlur={() => void mutate(() => updatePropertyMedia(propertyId, selected.media_id, { caption: selected.caption }))} /></label>
      <label>Room category<input value={selected.room_category ?? ""} onChange={(event) => setSelected({ ...selected, room_category: event.target.value })} onBlur={() => void mutate(() => updatePropertyMedia(propertyId, selected.media_id, { room_category: selected.room_category }))} /></label>
      {analysis && <PhotoAnalysis analysis={analysis} />}
      <div className="media-thumbnails">{media.map((item) => <button key={item.media_id} className={item.media_id === selected.media_id ? "active" : ""} onClick={() => setSelected(item)}><img src={item.public_url} alt={item.caption || item.original_filename} /></button>)}</div>
      {modal && <div className="media-modal" role="dialog" aria-modal="true" onClick={() => setModal(false)}><img src={selected.public_url} alt={selected.caption || selected.original_filename} /></div>}
    </> : <p className="media-empty">No property photos yet. Upload an exterior, interior, or condition photo to begin.</p>}
  </section>;
}

function PhotoAnalysis({ analysis }: { analysis: PropertyMediaAnalysis }) {
  return <div className="media-analysis" style={{ textAlign: "left", marginTop: 16 }}>
    <h3>AI Visible Condition: {analysis.condition_rating}</h3><p>{analysis.visible_condition_summary}</p>
    <p><strong>Rent ready:</strong> {analysis.rent_ready_status.replaceAll("_", " ")}</p>
    <p><strong>Visible repair estimate:</strong> {money(analysis.estimated_repair_cost_low)}–{money(analysis.estimated_repair_cost_high)}</p>
    <h4>Observed issues</h4>{analysis.observed_issues.length ? <ul>{analysis.observed_issues.map((issue, index) => <li key={`${issue.category}-${index}`}><strong>{issue.severity}: {issue.description}</strong> — {issue.visible_evidence} ({Math.round(issue.confidence * 100)}% confidence). {issue.recommended_action}</li>)}</ul> : <p>None identified.</p>}
    <h4>Inferred — unconfirmed</h4>{analysis.inferred_issues.length ? <ul>{analysis.inferred_issues.map((issue, index) => <li key={`${issue.category}-${index}`}>{issue.description}. Inspection: {issue.recommended_inspection}</li>)}</ul> : <p>None.</p>}
    <h4>Physical inspection required</h4>{analysis.unknown_inspection_items.length ? <ul>{analysis.unknown_inspection_items.map((item, index) => <li key={`${item.category}-${index}`}>{item.description}: {item.reason}</li>)}</ul> : <p>None specifically identified.</p>}
    {analysis.safety_concerns.length > 0 && <><h4>Safety concerns</h4><ul>{analysis.safety_concerns.map((item) => <li key={item}>{item}</li>)}</ul></>}
    <h4>Limitations</h4><ul>{analysis.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
    <small>{Math.round(analysis.analysis_confidence * 100)}% confidence · {new Date(analysis.analyzed_at).toLocaleString()} · review pending</small>
  </div>;
}
