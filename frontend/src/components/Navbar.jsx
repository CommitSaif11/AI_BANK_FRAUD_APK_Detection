function Navbar() {
  return (
    <nav
      style={{
        background: "rgba(10,14,26,0.95)",
        backdropFilter: "blur(12px)",
        borderBottom: "0.5px solid var(--border)",
        padding: "14px 40px",
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="var(--blue)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 2 L20 5 V11 C20 16 16.5 19.5 12 22 C7.5 19.5 4 16 4 11 V5 Z" />
        </svg>
        <div>
          <div style={{ color: "#fff", fontWeight: 500 }}>ThreatLens</div>
          <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>
            APK Fraud Analysis
          </div>
        </div>
      </div>

      <div className="badge badge-blue">Powered by 4-Agent AI Pipeline</div>
    </nav>
  );
}

export default Navbar;
