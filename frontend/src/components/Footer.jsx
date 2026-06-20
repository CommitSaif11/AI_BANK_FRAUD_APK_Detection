const Footer = () => (
  <footer
    style={{
      position: "fixed",
      bottom: 0,
      left: 0,
      right: 0,
      background: "linear-gradient(180deg, rgba(10,10,20,0.95) 0%, rgba(5,5,15,1) 100%)",
      borderTop: "1px solid rgba(255,255,255,0.08)",
      padding: "12px 24px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      flexWrap: "wrap",
      gap: "8px",
      zIndex: 1000,
      backdropFilter: "blur(12px)",
    }}
  >
    <div style={{ color: "rgba(255,255,255,0.5)", fontSize: "12px" }}>
      Built for{" "}
      <span style={{ color: "rgba(255,255,255,0.85)", fontWeight: 600 }}>
        Bank of India
      </span>
    </div>

    <div
      style={{
        color: "rgba(255,255,255,0.4)",
        fontSize: "11px",
        textAlign: "center",
      }}
    >
      In collaboration with Department of Financial Services & IIT Hyderabad
      &nbsp;·&nbsp; Powered by 4-Agent AI Pipeline
    </div>

    <div style={{ color: "rgba(255,255,255,0.35)", fontSize: "11px" }}>
      © 2026 APK Fraud Analysis System. All rights reserved.
    </div>
  </footer>
);

export default Footer;
