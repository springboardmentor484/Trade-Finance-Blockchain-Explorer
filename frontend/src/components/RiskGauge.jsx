export default function RiskGauge({ score, size = "md" }) {
  const getColor = () => {
    if (score < 20) return "#10b981"; // green
    if (score < 40) return "#f59e0b"; // amber
    if (score < 60) return "#f97316"; // orange
    return "#dc2626"; // red
  };

  const getLabel = () => {
    if (score < 20) return "LOW";
    if (score < 40) return "MEDIUM";
    if (score < 60) return "HIGH";
    return "CRITICAL";
  };

  const sizeClass =
    size === "lg"
      ? "w-24 h-24 text-3xl"
      : size === "sm"
        ? "w-12 h-12 text-sm"
        : "w-16 h-16 text-xl";

  return (
    <div className={`flex flex-col items-center ${sizeClass}`}>
      <div
        className="rounded-full flex items-center justify-center font-bold text-white"
        style={{
          backgroundColor: getColor(),
          width: "100%",
          height: "100%",
        }}
      >
        {score.toFixed(0)}
      </div>
      <div className="text-xs font-semibold mt-1" style={{ color: getColor() }}>
        {getLabel()}
      </div>
    </div>
  );
}
