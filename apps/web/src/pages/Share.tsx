import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import DashboardLayout from "../components/layout/DashboardLayout";
import Card from "../components/ui/Card";
import PageHeader from "../components/ui/PageHeader";
import { uploadPropertyMedia } from "../services/propertyMediaService";
import { createShareIntake, processShareIntake } from "../services/shareIntakeService";
import type { ShareIntake } from "../types/shareIntake";

const restrictedSource = (value: string) =>
  /(?:^|\.)(?:zillow\.com|redfin\.com|realtor\.com)$/i.test((() => {
    try { return new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`).hostname; }
    catch { return ""; }
  })()) || /(?:^|\.)(?:mls|matrix|paragon|flexmls)\b/i.test(value);

export default function Share() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [sourceUrl, setSourceUrl] = useState(params.get("url") ?? "");
  const [sharedText, setSharedText] = useState(params.get("text") ?? "");
  const [title, setTitle] = useState(params.get("title") ?? "");
  const [notes, setNotes] = useState("");
  const [photos, setPhotos] = useState<File[]>([]);
  const [result, setResult] = useState<ShareIntake | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const propertyId = result?.matched_property_id ?? result?.created_property_id;
  const showRestrictedNotice = useMemo(() => restrictedSource(sourceUrl), [sourceUrl]);

  async function processShare() {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const share = await createShareIntake({
        source_url: sourceUrl.trim() || undefined,
        shared_text: sharedText.trim() || undefined,
        title: title.trim() || undefined,
        notes: notes.trim() || undefined,
      });
      const processed = await processShareIntake(share.share_id);
      const resolvedPropertyId = processed.matched_property_id ?? processed.created_property_id;
      if (resolvedPropertyId) {
        await Promise.all(photos.map((photo) => uploadPropertyMedia(resolvedPropertyId, photo)));
      }
      setResult(processed);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to process this share.");
    } finally {
      setBusy(false);
    }
  }

  const fieldStyle = { width: "100%", boxSizing: "border-box" as const, padding: 12, borderRadius: 8, border: "1px solid #ccc" };

  return (
    <DashboardLayout>
      <PageHeader title="Share a Listing" subtitle="Save a listing link and analyze only the content you choose to share." />
      <Card>
        <div style={{ display: "grid", gap: 16, textAlign: "left" }}>
          <label>Listing URL<input style={fieldStyle} value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} placeholder="https://..." /></label>
          {showRestrictedNotice && <div role="status" style={{ padding: 12, borderRadius: 8, background: "var(--accent-bg)" }}>This URL will be saved for reference. Property Intelligence does not open or scrape this source; it analyzes only text and photos you explicitly share.</div>}
          <label>Listing text<textarea style={{ ...fieldStyle, minHeight: 180 }} value={sharedText} onChange={(event) => setSharedText(event.target.value)} placeholder="Paste the address, description, price, beds, baths, and other listing details." /></label>
          <label>Title (optional)<input style={fieldStyle} value={title} onChange={(event) => setTitle(event.target.value)} /></label>
          <label>Notes (optional)<textarea style={{ ...fieldStyle, minHeight: 90 }} value={notes} onChange={(event) => setNotes(event.target.value)} /></label>
          <label>Photos (optional)<input style={fieldStyle} type="file" accept="image/*" multiple onChange={(event) => setPhotos(Array.from(event.target.files ?? []))} /></label>
          <small>Photos upload after a property is matched or a draft is created.</small>
          <button onClick={processShare} disabled={busy} style={{ padding: "12px 18px", border: 0, borderRadius: 8, cursor: busy ? "wait" : "pointer", fontWeight: 600 }}>{busy ? "Processing…" : "Process Share"}</button>
          {error && <div role="alert" style={{ color: "#b42318" }}>{error}</div>}
          {result && propertyId && (
            <div role="status" style={{ padding: 16, borderRadius: 8, background: "#f5f5f5" }}>
              <h3 style={{ marginTop: 0 }}>{result.matched_property_id ? "Existing property matched" : "Draft property created"}</h3>
              <p>{result.detected_address}</p>
              <p style={{ marginTop: 8 }}>Property ID: {propertyId}</p>
              <button onClick={() => navigate(`/properties/${propertyId}`)} style={{ marginTop: 16, padding: "10px 18px", border: 0, borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>Open Property</button>
            </div>
          )}
        </div>
      </Card>
    </DashboardLayout>
  );
}
