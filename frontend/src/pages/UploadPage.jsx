import { useState, useRef, useEffect } from "react";

const STATS = [
  { target: 15, suffix: "+", label: "Dangerous Permissions Tracked" },
  { target: 5, suffix: "", label: "Malware Families in Database" },
  { target: 4, suffix: "", label: "AI Agents in Pipeline" },
  { target: 98, suffix: "/100", label: "Highest Risk Score Detected" },
];

function StatCounter({ target, suffix, label }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const duration = 1500;
    const steps = 40;
    const increment = target / steps;
    const interval = duration / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, interval);
    return () => clearInterval(timer);
  }, [target]);

  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: "28px", fontWeight: 600, color: "#3b82f6" }}>
        {count}{suffix}
      </div>
      <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginTop: "4px" }}>
        {label}
      </div>
    </div>
  );
}

const FEATURES = [
  {
    icon: "🔍",
    title: "Static Analysis",
    desc: "Extracts permissions, manifest data, certificates and embedded URLs using Androguard",
  },
  {
    icon: "⚖️",
    title: "Heuristic Scoring",
    desc: "Rules engine scores 15+ dangerous permissions and detects known attack combos like OTP-stealers",
  },
  {
    icon: "🤖",
    title: "4-Agent AI Pipeline",
    desc: "Triage → Code Analysis → Risk Synthesis → Report Writing, each powered by Llama 3.1 70B",
  },
  {
    icon: "📄",
    title: "PDF Investigation Report",
    desc: "Bank-grade formal report with IOCs, recommended actions and customer advisory",
  },
];

function UploadPage({ onFileSelect, error: externalError }) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const displayError = error || externalError;
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".apk")) {
      setError("Invalid file type. Please upload a .apk file.");
      return;
    }
    setError("");
    onFileSelect(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="fade-in">
      {/* Stats bar */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          padding: "20px 40px",
          background: "rgba(255,255,255,0.03)",
          borderTop: "0.5px solid rgba(255,255,255,0.08)",
          borderBottom: "0.5px solid rgba(255,255,255,0.08)",
        }}
      >
        {STATS.map((s) => (
          <StatCounter key={s.label} target={s.target} suffix={s.suffix} label={s.label} />
        ))}
      </div>

      <div className="hero-grid">
        <div>
          <h1
            style={{
              fontSize: "32px",
              fontWeight: 500,
              lineHeight: 1.3,
              color: "var(--text-primary)",
            }}
          >
            Detect fraudulent APKs before they reach your customers
          </h1>
          <p style={{ color: "var(--text-secondary)", marginTop: "16px" }}>
            ThreatLens uses a 4-agent AI pipeline to analyze permissions,
            network behavior, and malware signatures, generating bank-grade
            investigation reports for every Android application you upload.
          </p>
        </div>

        <div>
          <div
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            style={{
              border: `1.5px dashed ${dragOver ? "var(--blue)" : "var(--border-accent)"}`,
              borderRadius: "var(--radius-lg)",
              padding: "40px",
              textAlign: "center",
              background: "var(--blue-bg)",
              cursor: "pointer",
            }}
          >
            <div style={{ fontSize: "48px" }}>⬆️</div>
            <div style={{ marginTop: "12px", fontWeight: 500 }}>
              Drop your APK file here
            </div>
            <div
              style={{
                fontSize: "12px",
                color: "var(--text-muted)",
                marginTop: "4px",
              }}
            >
              .apk files only · max 100MB
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                inputRef.current?.click();
              }}
              style={{
                marginTop: "20px",
                padding: "10px 20px",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--blue)",
                background: "var(--blue)",
                color: "#fff",
                fontWeight: 500,
                cursor: "pointer",
              }}
            >
              Choose APK File
            </button>
            <input
              ref={inputRef}
              type="file"
              accept=".apk"
              style={{ display: "none" }}
              onChange={(e) => handleFile(e.target.files[0])}
            />
          </div>
          {displayError && (
            <div style={{ color: "var(--red)", marginTop: "12px", fontSize: "13px" }}>
              {displayError}
            </div>
          )}
        </div>
      </div>

      <div
        className="feature-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "16px",
          padding: "0 40px 60px",
        }}
      >
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="hover-card"
            style={{
              background: "var(--bg-card)",
              border: "0.5px solid var(--border)",
              borderRadius: "var(--radius-md)",
              padding: "20px",
            }}
          >
            <div style={{ fontSize: "24px" }}>{f.icon}</div>
            <div style={{ fontWeight: 500, marginTop: "10px" }}>{f.title}</div>
            <div
              style={{
                fontSize: "13px",
                color: "var(--text-secondary)",
                marginTop: "6px",
                lineHeight: 1.5,
              }}
            >
              {f.desc}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default UploadPage;
