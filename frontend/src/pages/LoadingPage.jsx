const SUBTEXTS = [
  "Extracting APK contents and parsing manifest...",
  "Running heuristic scoring engine...",
  "Agent 1: Triage classification...",
  "Agent 2: Code analysis and behavioral mapping...",
  "Agent 3: Risk synthesis...",
  "Agent 4: Generating investigation report...",
];

const AGENTS = [
  "Triage",
  "Code Analysis",
  "Risk Synthesis",
  "Report Writer",
];

function LoadingPage({ filename, currentStep = 0 }) {
  return (
    <div style={{ textAlign: "center", padding: "80px 40px" }}>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes pulseStep {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
        @keyframes progressFill {
          from { width: 0%; }
          to { width: 95%; }
        }
      `}</style>

      <div className="mono text-muted" style={{ marginBottom: "32px" }}>
        {filename}
      </div>

      <div
        style={{
          width: "64px",
          height: "64px",
          margin: "0 auto",
          borderRadius: "50%",
          border: "4px solid var(--border)",
          borderTopColor: "var(--blue)",
          animation: "spin 1s linear infinite",
        }}
      />

      <div style={{ fontSize: "20px", fontWeight: 500, marginTop: "24px" }}>
        Analyzing APK...
      </div>

      <div style={{ color: "var(--text-secondary)", marginTop: "8px" }}>
        {SUBTEXTS[currentStep] ?? SUBTEXTS[SUBTEXTS.length - 1]}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "16px",
          maxWidth: "700px",
          margin: "48px auto 0",
        }}
      >
        {AGENTS.map((name, i) => {
          const agentStep = i + 2; // steps 2-5 map to agents 0-3
          let status = "pending";
          if (agentStep < currentStep) status = "done";
          else if (agentStep === currentStep) status = "active";

          const colors = {
            pending: { border: "var(--border)", color: "var(--text-muted)", dot: "var(--text-muted)" },
            active: { border: "var(--blue)", color: "var(--blue-light)", dot: "var(--blue)" },
            done: { border: "var(--green)", color: "var(--green-light)", dot: "var(--green)" },
          }[status];

          return (
            <div
              key={name}
              style={{
                background: "var(--bg-card)",
                border: `0.5px solid ${colors.border}`,
                borderRadius: "var(--radius-md)",
                padding: "16px",
                animation: status === "active" ? "pulseStep 1.5s ease-in-out infinite" : "none",
              }}
            >
              <div
                style={{
                  width: "10px",
                  height: "10px",
                  borderRadius: "50%",
                  background: colors.dot,
                  margin: "0 auto 8px",
                }}
              />
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                Agent {i + 1}
              </div>
              <div style={{ fontSize: "13px", fontWeight: 500, color: colors.color, marginTop: "4px" }}>
                {name}
              </div>
            </div>
          );
        })}
      </div>

      <div
        style={{
          maxWidth: "700px",
          margin: "32px auto 0",
          height: "6px",
          borderRadius: "4px",
          background: "var(--bg-card)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            background: "var(--blue)",
            borderRadius: "4px",
            width: "0%",
            animation: "progressFill 25s ease-out forwards",
          }}
        />
      </div>
    </div>
  );
}

export default LoadingPage;
