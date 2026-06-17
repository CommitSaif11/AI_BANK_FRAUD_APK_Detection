import { useState, useEffect } from "react";

function SplashScreen({ onComplete }) {
  const [logoVisible, setLogoVisible] = useState(false);
  const [lineVisible, setLineVisible] = useState(false);
  const [builtForVisible, setBuiltForVisible] = useState(false);
  const [institutionsVisible, setInstitutionsVisible] = useState(false);
  const [fadingOut, setFadingOut] = useState(false);

  useEffect(() => {
    const timers = [
      setTimeout(() => setLogoVisible(true), 100),
      setTimeout(() => setLineVisible(true), 800),
      setTimeout(() => setBuiltForVisible(true), 1100),
      setTimeout(() => setInstitutionsVisible(true), 1400),
      setTimeout(() => setFadingOut(true), 2600),
      setTimeout(() => onComplete(), 3000),
    ];
    return () => timers.forEach(clearTimeout);
  }, [onComplete]);


  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "#0a0e1a",
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity: fadingOut ? 0 : 1,
        transition: "opacity 0.5s ease",
      }}
    >
      {/* ThreatLens logo */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          opacity: logoVisible ? 1 : 0,
          transform: logoVisible ? "translateY(0)" : "translateY(12px)",
          transition: "opacity 0.5s ease, transform 0.5s ease",
        }}
      >
        <svg
          width="40"
          height="40"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#3b82f6"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ marginRight: "12px" }}
        >
          <path d="M12 2 L20 5 V11 C20 16 16.5 19.5 12 22 C7.5 19.5 4 16 4 11 V5 Z" />
        </svg>
        <span style={{ fontSize: "36px", fontWeight: 600, color: "#fff", letterSpacing: "-0.02em" }}>
          ThreatLens
        </span>
      </div>

      {/* Animated line */}
      <div
        style={{
          height: "2px",
          width: lineVisible ? "300px" : "0px",
          background: "#3b82f6",
          borderRadius: "2px",
          marginTop: "20px",
          transition: "width 0.5s ease",
        }}
      />

      {/* Built for */}
      <div
        style={{
          fontSize: "12px",
          color: "#64748b",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginTop: "20px",
          marginBottom: "20px",
          opacity: builtForVisible ? 1 : 0,
          transition: "opacity 0.4s ease",
        }}
      >
        Built for
      </div>

      {/* Logo cards */}
      <div
        style={{
          display: "flex",
          gap: "24px",
          alignItems: "flex-start",
          justifyContent: "center",
          opacity: institutionsVisible ? 1 : 0,
          transform: institutionsVisible ? "translateY(0)" : "translateY(10px)",
          transition: "opacity 0.4s ease, transform 0.4s ease",
        }}
      >
        {/* Bank of India */}
        <div style={{ textAlign: "center" }}>
          <div style={{ background: "#003087", borderRadius: "8px", padding: "12px 20px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: "160px", height: "70px" }}>
            <span style={{ color: "white", fontWeight: "700", fontSize: "15px", letterSpacing: "0.02em" }}>Bank of India</span>
            <span style={{ color: "#87CEEB", fontSize: "9px", marginTop: "3px", fontStyle: "italic" }}>Relationship beyond banking</span>
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "8px" }}>Bank of India</div>
        </div>

        {/* IIT Hyderabad */}
        <div style={{ textAlign: "center" }}>
          <div style={{ background: "white", borderRadius: "8px", padding: "12px 20px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: "160px", height: "70px" }}>
            <span style={{ color: "#FF6B00", fontWeight: "800", fontSize: "18px", letterSpacing: "0.05em" }}>IIT</span>
            <span style={{ color: "#1a1a1a", fontWeight: "600", fontSize: "11px", letterSpacing: "0.08em" }}>HYDERABAD</span>
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "8px" }}>IIT Hyderabad</div>
        </div>

        {/* Dept of Financial Services */}
        <div style={{ textAlign: "center" }}>
          <div style={{ background: "white", borderRadius: "8px", padding: "12px 16px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: "160px", height: "70px" }}>
            <span style={{ fontSize: "18px" }}>🏛️</span>
            <span style={{ color: "#1a1a1a", fontWeight: "700", fontSize: "9px", textAlign: "center", lineHeight: "1.3", marginTop: "3px" }}>DEPT. OF FINANCIAL SERVICES</span>
            <span style={{ color: "#666", fontSize: "8px" }}>Govt. of India</span>
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "8px" }}>Dept. of Financial Services</div>
        </div>
      </div>
    </div>
  );
}

export default SplashScreen;
