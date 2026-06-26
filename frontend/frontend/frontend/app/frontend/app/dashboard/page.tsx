const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getOpportunities() {
  try {
    const res = await fetch(`${API}/api/opportunities`, { next: { revalidate: 60 } });
    return res.json();
  } catch { return []; }
}

export default async function Dashboard() {
  const opportunities = await getOpportunities();

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        🔍 TrendScout AI
      </h1>
      <p style={{ color: "#94a3b8", marginBottom: "2rem" }}>
        Top business opportunities from Reddit
      </p>

      {opportunities.length === 0 ? (
        <div style={{ textAlign: "center", padding: "4rem", color: "#94a3b8" }}>
          <p style={{ fontSize: "1.2rem" }}>No opportunities yet</p>
          <p>Trigger an analysis to get started</p>
          <button
            onClick={async () => { await fetch(`${API}/api/run-analysis`, { method: "POST" }); location.reload(); }}
            style={{ marginTop: "1rem", padding: "0.75rem 1.5rem", background: "#3b82f6", color: "white", border: "none", borderRadius: 8, cursor: "pointer" }}
          >
            Run Analysis
          </button>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "1rem" }}>
          {opportunities.map((opp: any, i: number) => (
            <a key={opp.id} href={`/opportunity/${opp.id}`} style={{ textDecoration: "none", color: "inherit" }}>
              <div style={{ background: "#0d1a36", border: "1px solid #132549", borderRadius: 12, padding: "1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                  <span style={{ color: "#3b82f6", fontSize: "0.75rem", fontWeight: 600 }}>#{i + 1}</span>
                  <span style={{ color: opp.growth_rate > 0 ? "#10b981" : "#94a3b8", fontSize: "0.75rem" }}>
                    {opp.growth_rate > 0 ? `+${opp.growth_rate.toFixed(0)}%` : "New"}
                  </span>
                </div>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.5rem" }}>{opp.title}</h3>
                <p style={{ color: "#94a3b8", fontSize: "0.8rem", marginBottom: "0.75rem", lineHeight: 1.5 }}>{opp.summary}</p>
                <div style={{ display: "flex", gap: "0.75rem", fontSize: "0.75rem", color: "#64748b" }}>
                  <span>📊 {opp.mention_count} mentions</span>
                  <span>⭐ Score: {opp.score.toFixed(1)}</span>
                </div>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
