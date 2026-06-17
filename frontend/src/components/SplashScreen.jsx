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

  const institutions = [
    { src: "/logos/bank-of-india.png", alt: "Bank of India", label: "Bank of India" },
    { src: "/logos/iit_hyderabad_logo.jpg", alt: "IIT Hyderabad", label: "IIT Hyderabad" },
    { src: "/logos/dept_of_financial_services.jfif", alt: "Dept. of Financial Services", label: "Dept. of Financial Services" },
  ];

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
        {institutions.map(({ src, alt, label }) => (
          <div key={label} style={{ textAlign: "center" }}>
            <div
              style={{
                background: "#ffffff",
                borderRadius: "12px",
                padding: "12px 20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: "70px",
                width: "160px",
                boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
              }}
            >
              <img
                src={src}
                alt={alt}
                style={{ maxHeight: "50px", maxWidth: "140px", objectFit: "contain" }}
              />
            </div>
            <div style={{ fontSize: "11px", color: "#64748b", textAlign: "center", marginTop: "8px" }}>
              {label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SplashScreen;
