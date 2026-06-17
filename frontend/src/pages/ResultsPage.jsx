import { useState } from "react";
import axios from "axios";

const RISK_COLORS = {
  CRITICAL: { bg: "var(--red-bg)", border: "var(--red)", text: "var(--red-light)" },
  HIGH: { bg: "var(--amber-bg)", border: "var(--amber)", text: "var(--amber-light)" },
  MEDIUM: { bg: "var(--blue-bg)", border: "var(--blue)", text: "var(--blue-light)" },
  LOW: { bg: "var(--green-bg)", border: "var(--green)", text: "var(--green-light)" },
};

function badgeClassForLevel(level) {
  switch (level) {
    case "CRITICAL":
      return "badge-red";
    case "HIGH":
      return "badge-amber";
    case "MEDIUM":
      return "badge-blue";
    case "LOW":
      return "badge-green";
    default:
      return "badge-blue";
  }
}

function scoreColor(score) {
  if (score > 60) return "var(--red)";
  if (score >= 30) return "var(--amber)";
  return "var(--green)";
}

function ScoreCard({ icon, title, score }) {
  const color = scoreColor(score);
  return (
    <div
      className="hover-card"
      style={{
        background: "var(--bg-card)",
        border: "0.5px solid var(--border)",
        borderRadius: "var(--radius-md)",
        padding: "20px",
      }}
    >
      <div style={{ fontSize: "20px" }}>{icon}</div>
      <div style={{ fontWeight: 500, marginTop: "8px" }}>{title}</div>
      <div style={{ fontSize: "24px", fontWeight: 500, marginTop: "4px" }}>
        {score}
        <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>/100</span>
      </div>
      <div
        style={{
          height: "6px",
          borderRadius: "4px",
          background: "var(--bg-secondary)",
          marginTop: "10px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${Math.min(100, Math.max(0, score))}%`,
            background: color,
            borderRadius: "4px",
          }}
        />
      </div>
    </div>
  );
}

function ResultsPage({ data, filename, onReset }) {
  if (!data) return <div style={{ color: "white", padding: "40px" }}>No analysis data available.</div>;

  const [tab, setTab] = useState("threat");
  const [downloading, setDownloading] = useState(false);

  const risk = data?.risk || {};
  const impersonation = data?.impersonation || {};
  const networkRisk = data?.network_risk || {};
  const analysis = data?.analysis || {};
  const report = data?.report || {};
  const triage = data?.triage || {};
  const riskAssessment = data?.risk_assessment || {};
  const fingerprintMatch = data?.fingerprint_match || {};

  const riskLevel = data?.risk_level || riskAssessment?.risk_level || "MEDIUM";
  const riskColors = RISK_COLORS[riskLevel] || RISK_COLORS.MEDIUM;

  const flaggedPermissions = risk?.flagged_permissions || [];
  const triggeredCombos = risk?.triggered_combos || [];
  const flaggedUrls = networkRisk?.flagged_urls || [];
  const reasons = impersonation?.reasons || [];
  const matchedPermissions = fingerprintMatch?.matched_permission_overlap || [];
  const recommendedActions = riskAssessment?.recommended_actions || [];

  const handleDownloadPdf = async () => {
    setDownloading(true);
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/report/${encodeURIComponent(filename)}`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${filename}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error("Failed to download report", e);
    } finally {
      setDownloading(false);
    }
  };

  const confidence = fingerprintMatch?.confidence ?? 0;
  const circumference = 2 * Math.PI * 40;
  const dashOffset = circumference * (1 - confidence / 100);

  return (
    <div className="fade-in" style={{ padding: "0 40px 60px" }}>
      {/* SECTION 1 — Top bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "20px 0",
        }}
      >
        <div className="mono text-muted">{filename}</div>
        <div style={{ display: "flex", gap: "12px" }}>
          <button
            onClick={handleDownloadPdf}
            disabled={downloading}
            style={{
              padding: "10px 18px",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--blue)",
              background: "var(--blue)",
              color: "#fff",
              fontWeight: 500,
              cursor: downloading ? "default" : "pointer",
              opacity: downloading ? 0.8 : 1,
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            {downloading && <span className="spinner-sm" />}
            {downloading ? "Generating..." : "Download PDF Report"}
          </button>
          <button
            onClick={onReset}
            style={{
              padding: "10px 18px",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--border)",
              background: "transparent",
              color: "var(--text-primary)",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            Analyze Another APK
          </button>
        </div>
      </div>

      {/* SECTION 2 — Score + Info row */}
      <div style={{ display: "grid", gridTemplateColumns: "180px auto", gap: "24px" }}>
        <div
          className={riskLevel === "CRITICAL" ? "pulse-critical" : ""}
          style={{
            background: riskColors.bg,
            border: `1px solid ${riskColors.border}`,
            borderRadius: "var(--radius-lg)",
            padding: "20px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "56px", fontWeight: 600, lineHeight: 1 }}>
            {riskAssessment?.final_risk_score ?? data?.final_risk_score ?? "--"}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Risk Score
          </div>
          <div className={`badge ${badgeClassForLevel(riskLevel)}`} style={{ marginTop: "12px" }}>
            {riskLevel}
          </div>
        </div>

        <div
          className="hover-card"
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "16px",
            background: "var(--bg-card)",
            border: "0.5px solid var(--border)",
            borderRadius: "var(--radius-lg)",
            padding: "20px",
          }}
        >
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Package Name</div>
            <div className="mono" style={{ marginTop: "4px" }}>
              {data?.package_name || "—"}
            </div>
          </div>
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>App Name</div>
            <div style={{ marginTop: "4px" }}>{data?.app_name || "—"}</div>
          </div>
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Threat Category</div>
            <div style={{ marginTop: "4px" }}>
              <span className="badge badge-red">{triage?.threat_category || "Unknown"}</span>
            </div>
          </div>
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Malware Family Match</div>
            <div style={{ marginTop: "4px" }}>{fingerprintMatch?.matched_family || "None detected"}</div>
          </div>
        </div>
      </div>

      {/* SECTION 3 — Agent Pipeline Strip */}
      <div
        className="pipeline-strip"
        style={{
          display: "flex",
          marginTop: "24px",
          background: "var(--bg-card)",
          border: "0.5px solid var(--border)",
          borderRadius: "var(--radius-lg)",
          overflow: "hidden",
        }}
      >
        {[
          { label: "01 Triage", value: triage?.threat_category || "Triage complete" },
          { label: "02 Code Analyst", value: analysis?.technical_indicators?.[0] || "Analysis complete" },
          { label: "03 Risk Synthesis", value: `Score: ${riskAssessment?.final_risk_score ?? data?.final_risk_score ?? "—"}` },
          { label: "04 Report Writer", value: report?.report_title?.substring(0, 50) || "Report complete" },
        ].map((item, i) => (
          <div
            key={item.label}
            style={{
              flex: 1,
              padding: "16px 20px",
              borderLeft: i === 0 ? "none" : "0.5px solid var(--border)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  background: "var(--green)",
                }}
              />
              <div style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)" }}>
                {item.label}
              </div>
            </div>
            <div
              style={{
                fontSize: "13px",
                marginTop: "8px",
                color: "var(--text-primary)",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {item.value}
            </div>
          </div>
        ))}
      </div>

      {/* SECTION 4 — Three score cards */}
      <div className="results-three-col" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginTop: "24px" }}>
        <ScoreCard icon="🔐" title="Permission Risk" score={risk?.permission_risk_score || 0} />
        <ScoreCard icon="🎭" title="Impersonation Risk" score={impersonation?.impersonation_risk_score || 0} />
        <ScoreCard icon="🌐" title="Network Risk" score={networkRisk?.network_risk_score || 0} />
      </div>

      {/* SECTION 5 — Two column layout */}
      <div className="results-two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "24px" }}>
        {/* Left column — Flagged Permissions */}
        <div
          className="hover-card"
          style={{
            background: "var(--bg-card)",
            border: "0.5px solid var(--border)",
            borderRadius: "var(--radius-md)",
            padding: "20px",
          }}
        >
          <div style={{ fontWeight: 500, marginBottom: "12px" }}>Flagged Permissions</div>
          {flaggedPermissions.length === 0 && (
            <div style={{ color: "var(--text-muted)", fontSize: "13px" }}>None flagged</div>
          )}
          {flaggedPermissions.map((p, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 0",
                borderBottom: i < flaggedPermissions.length - 1 ? "0.5px solid var(--border)" : "none",
              }}
            >
              <div>
                <div className="mono" style={{ color: "var(--red-light)", fontSize: "13px" }}>
                  {p?.permission || "Unknown"}
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
                  {p?.reason || "Unknown"}
                </div>
              </div>
              <div className="badge badge-red">+{p?.points || 0}</div>
            </div>
          ))}

          {triggeredCombos.length > 0 && (
            <div style={{ marginTop: "16px" }}>
              {triggeredCombos.map((combo, i) => (
                <div
                  key={i}
                  style={{
                    background: "var(--amber-bg)",
                    border: "1px solid var(--amber)",
                    borderRadius: "var(--radius-sm)",
                    padding: "10px 14px",
                    color: "var(--amber-light)",
                    fontSize: "13px",
                    marginTop: "8px",
                  }}
                >
                  ⚠ {typeof combo === "string" ? combo : `${combo.name}${combo.reason ? ` — ${combo.reason}` : ""}${combo.bonus ? ` (+${combo.bonus})` : ""}`}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right column — AI Analysis tabs */}
        <div
          className="hover-card"
          style={{
            background: "var(--bg-card)",
            border: "0.5px solid var(--border)",
            borderRadius: "var(--radius-md)",
            padding: "20px",
          }}
        >
          <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
            {[
              { key: "threat", label: "Threat Analysis" },
              { key: "network", label: "Network" },
              { key: "impersonation", label: "Impersonation" },
            ].map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                style={{
                  padding: "8px 14px",
                  borderRadius: "var(--radius-sm)",
                  border: tab === t.key ? "1px solid var(--blue)" : "1px solid var(--border)",
                  background: tab === t.key ? "var(--blue-bg)" : "transparent",
                  color: tab === t.key ? "var(--blue-light)" : "var(--text-secondary)",
                  fontSize: "13px",
                  cursor: "pointer",
                }}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === "threat" && (
            <div style={{ fontSize: "13px", lineHeight: 1.6, color: "var(--text-secondary)" }}>
              <div style={{ marginBottom: "12px" }}>
                <div style={{ fontWeight: 500, color: "var(--text-primary)", marginBottom: "4px" }}>
                  Behavioral Pattern
                </div>
                {analysis?.behavioral_pattern || "—"}
              </div>
              <div>
                <div style={{ fontWeight: 500, color: "var(--text-primary)", marginBottom: "4px" }}>
                  Banking Impact
                </div>
                {analysis?.banking_impact || "—"}
              </div>
            </div>
          )}

          {tab === "network" && (
            <div style={{ fontSize: "13px", lineHeight: 1.6, color: "var(--text-secondary)" }}>
              <div style={{ fontWeight: 500, color: "var(--text-primary)", marginBottom: "4px" }}>
                Flagged URLs
              </div>
              {flaggedUrls.length === 0 && <div>None detected</div>}
              {flaggedUrls.map((u, i) => (
                <div key={i} style={{ marginBottom: "8px" }}>
                  <div className="mono" style={{ color: "var(--red-light)" }}>
                    {u?.url}
                  </div>
                  {(u?.reasons || []).map((r, j) => (
                    <div key={j} style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                      • {r}
                    </div>
                  ))}
                </div>
              ))}
              <div style={{ fontWeight: 500, color: "var(--text-primary)", marginTop: "12px", marginBottom: "4px" }}>
                Network Analysis
              </div>
              {analysis?.network_analysis || "—"}
            </div>
          )}

          {tab === "impersonation" && (
            <div style={{ fontSize: "13px", lineHeight: 1.6, color: "var(--text-secondary)" }}>
              <div style={{ fontWeight: 500, color: "var(--text-primary)", marginBottom: "4px" }}>
                Reasons
              </div>
              {reasons.length === 0 && <div>None detected</div>}
              <ul style={{ paddingLeft: "18px" }}>
                {reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
              <div style={{ fontWeight: 500, color: "var(--text-primary)", marginTop: "12px", marginBottom: "4px" }}>
                Impersonation Analysis
              </div>
              {analysis?.impersonation_analysis || "—"}
            </div>
          )}
        </div>
      </div>

      {/* SECTION 6 — Fingerprint Match */}
      <div
        className="fingerprint-card hover-card"
        style={{
          display: "grid",
          gridTemplateColumns: "1fr auto",
          gap: "24px",
          alignItems: "center",
          background: "var(--bg-card)",
          border: "0.5px solid var(--border)",
          borderRadius: "var(--radius-lg)",
          padding: "24px",
          marginTop: "24px",
        }}
      >
        <div>
          <div style={{ fontSize: "20px", fontWeight: 500 }}>
            {fingerprintMatch?.matched_family || "No Fingerprint Match"}
          </div>
          <div style={{ color: "var(--text-secondary)", fontSize: "13px", marginTop: "6px" }}>
            {fingerprintMatch?.description || "No known malware family signature matched this APK."}
          </div>
          <div style={{ display: "flex", gap: "8px", marginTop: "12px", flexWrap: "wrap" }}>
            {matchedPermissions.map((p, i) => (
              <span key={i} className="badge badge-blue mono">
                {p}
              </span>
            ))}
          </div>
        </div>

        <div style={{ textAlign: "center" }}>
          <svg width="100" height="100" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--bg-secondary)" strokeWidth="8" />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="var(--amber)"
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              transform="rotate(-90 50 50)"
            />
            <text x="50" y="55" textAnchor="middle" fontSize="20" fill="var(--amber-light)" fontWeight="600">
              {confidence}%
            </text>
          </svg>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            Family similarity
          </div>
        </div>
      </div>

      {/* SECTION 7 — AI Report Preview */}
      <div className="results-two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "24px" }}>
        <div
          className="hover-card"
          style={{
            background: "var(--bg-card)",
            border: "0.5px solid var(--border)",
            borderRadius: "var(--radius-md)",
            padding: "20px",
          }}
        >
          <div style={{ fontWeight: 500, marginBottom: "8px" }}>Executive Summary</div>
          <div style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
            {report?.executive_summary || "—"}
          </div>
          <div style={{ fontWeight: 500, marginTop: "16px", marginBottom: "8px" }}>Verdict</div>
          <div style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
            {riskAssessment?.verdict || "—"}
          </div>
        </div>

        <div
          className="hover-card"
          style={{
            background: "var(--bg-card)",
            border: "0.5px solid var(--border)",
            borderRadius: "var(--radius-md)",
            padding: "20px",
          }}
        >
          <div style={{ fontWeight: 500, marginBottom: "8px" }}>Recommended Actions</div>
          <ol style={{ paddingLeft: "18px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.8 }}>
            {recommendedActions.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ol>

          {riskAssessment?.customer_advisory && (
            <div
              style={{
                background: "var(--blue-bg)",
                border: "1px solid var(--blue)",
                borderRadius: "var(--radius-sm)",
                padding: "14px",
                marginTop: "16px",
                fontSize: "13px",
                color: "var(--blue-light)",
                lineHeight: 1.6,
              }}
            >
              {riskAssessment.customer_advisory}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
