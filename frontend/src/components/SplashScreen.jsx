import { useState, useEffect } from "react";

function SplashScreen({ onComplete }) {
  const [logoVisible, setLogoVisible] = useState(false);
  const [builtForVisible, setBuiltForVisible] = useState(false);
  const [inst1Visible, setInst1Visible] = useState(false);
  const [sep1Visible, setSep1Visible] = useState(false);
  const [inst2Visible, setInst2Visible] = useState(false);
  const [sep2Visible, setSep2Visible] = useState(false);
  const [inst3Visible, setInst3Visible] = useState(false);
  const [fadingOut, setFadingOut] = useState(false);

  useEffect(() => {
    const timers = [
      setTimeout(() => setLogoVisible(true), 100),
      setTimeout(() => setBuiltForVisible(true), 800),
      setTimeout(() => setInst1Visible(true), 1100),
      setTimeout(() => setSep1Visible(true), 1500),
      setTimeout(() => setInst2Visible(true), 1500),
      setTimeout(() => setSep2Visible(true), 1900),
      setTimeout(() => setInst3Visible(true), 1900),
      setTimeout(() => setFadingOut(true), 2500),
      setTimeout(() => onComplete(), 3000),
    ];
    return () => timers.forEach(clearTimeout);
  }, [onComplete]);

  const instStyle = (visible) => ({
    fontSize: "16px",
    fontWeight: 500,
    color: "#e2e8f0",
    opacity: visible ? 1 : 0,
    transform: visible ? "translateY(0)" : "translateY(10px)",
    transition: "opacity 0.4s ease, transform 0.4s ease",
  });

  const dotStyle = (visible) => ({
    width: "4px",
    height: "4px",
    borderRadius: "50%",
    background: "#3b82f6",
    opacity: visible ? 1 : 0,
    transition: "opacity 0.3s ease",
    flexShrink: 0,
  });

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
      {/* Logo row */}
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
        <span
          style={{
            fontSize: "36px",
            fontWeight: 600,
            color: "#fff",
            letterSpacing: "-0.02em",
          }}
        >
          ThreatLens
        </span>
      </div>

      {/* Built for */}
      <div
        style={{
          fontSize: "12px",
          color: "#64748b",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginTop: "24px",
          marginBottom: "16px",
          opacity: builtForVisible ? 1 : 0,
          transition: "opacity 0.4s ease",
        }}
      >
        Built for
      </div>

      {/* Institution names */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "16px",
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        <span style={instStyle(inst1Visible)}>Bank of India</span>
        <div style={dotStyle(sep1Visible)} />
        <span style={instStyle(inst2Visible)}>IIT Hyderabad</span>
        <div style={dotStyle(sep2Visible)} />
        <span style={instStyle(inst3Visible)}>Dept. of Financial Services, Govt. of India</span>
      </div>
    </div>
  );
}

export default SplashScreen;
