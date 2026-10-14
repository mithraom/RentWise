export const scoreColor = (s) => (s >= 85 ? "#16a34a" : s >= 70 ? "#2563eb" : s >= 50 ? "#d97706" : "#dc2626");
export const scoreLabel = (s) => (s >= 85 ? "Excellent Match" : s >= 70 ? "Good Match" : s >= 50 ? "Fair Match" : "Low Match");

export default function ScoreBadge({ score }) {
  const c = scoreColor(score);
  return (
    <div className="score-badge">
      <div className="ring" style={{ background: `conic-gradient(${c} ${score * 3.6}deg, #e2e8f0 0deg)` }}>
        <div className="ring-inner"><b>{score}</b><small>/100</small></div>
      </div>
      <span style={{ color: c, fontWeight: 600 }}>{scoreLabel(score)}</span>
    </div>
  );
}
