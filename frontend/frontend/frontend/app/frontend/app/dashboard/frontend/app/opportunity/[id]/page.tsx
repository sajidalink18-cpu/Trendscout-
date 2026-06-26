const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getOpportunity(id: string) {
  try {
    const res = await fetch(`${API}/api/opportunity/${id}`, { next: { revalidate: 60 } });
    return res.json();
  } catch { return null; }
}

export default async function OpportunityPage({ params }: { params: { id: string } }) {
  const opp = await getOpportunity(params.id);

  if (!opp) return <div style={{ padding: "2rem", color: "#94a3b8" }}>Not found</div>;

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2rem 1rem" }}>
      <a href="/dashboard" style={{ color: "#3b82f6", textDecoration: "none", fontSize: "0.875rem" }}>← Back</a>

      <h1 style={{ fontSize: "1.75rem", fontWeight: 700, margin: "1rem 0 0.5rem" }}>{opp.title}</h1>
      <p style={{ color: "#94a3b8", marginBottom: "2rem" }}>{opp.summary}</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        {opp.who_has_problem && (
          <div style={{ background: "#0d1a36", border: "1px solid #132549", borderRadius: 10, padding: "1rem" }}>
            <div style={{ color: "#64748b", fontSize: "0.7rem", marginBottom: "0.5rem" }}>WHO HAS THIS PROBLEM</div>
            <p style={{ fontSize: "0.875rem" }}>{opp.who_has_problem}</p>
          </div>
        )}
        {opp.why_it_matters && (
          <div style={{ background: "#0d1a36", border: "1px solid #132549", borderRadius: 10, padding: "1rem" }}>
            <div style={{ color: "#64748b", fontSize: "0.7rem", marginBottom: "0.5rem" }}>WHY IT MATTERS</div>
            <p style={{ fontSize: "0.875rem" }}>{opp.why_it_matters}</p>
          </div>
        )}
        {opp.saas_idea && (
          <div style={{ background: "#0d1836", border: "1px solid #1e3a5f", borderRadius: 10, padding: "1rem" }}>
            <div style={{ color: "#3b82f6", fontSize: "0.7rem", marginBottom: "0.5rem" }}>💡 SAAS IDEA</div>
            <p style={{ fontSize: "0.875rem", color: "#93c5fd" }}>{opp.saas_idea}</p>
          </div>
        )}
      </div>

      <h2 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "1rem" }}>
        Source Posts ({opp.posts?.length || 0})
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {opp.posts?.map((post: any) => (
          <div key={post.id} style={{ background: "#0d1a36", border: "1px solid #132549", borderRadius: 10, padding: "1rem" }}>
            <a href={post.url} target="_blank" rel="noopener noreferrer"
              style={{ color: "#e2e8f0", textDecoration: "none", fontSize: "0.875rem", fontWeight: 500 }}>
              {post.title}
            </a>
            <div style={{ marginTop: "0.5rem", display: "flex", gap: "1rem", fontSize: "0.75rem", color: "#64748b" }}>
              <span>r/{post.subreddit}</span>
              <span>▲ {post.upvotes}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
