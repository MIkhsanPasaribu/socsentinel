/** SOCsentinel — Confidence score gauge component. */

interface ConfidenceGaugeProps {
  /** Confidence score between 0 and 1. */
  score: number;
  /** Size variant. */
  size?: "sm" | "md" | "lg";
  /** Show percentage text. */
  showLabel?: boolean;
  /** Label text (overrides default "Confidence"). */
  label?: string;
}

/** Get color class based on confidence level. */
function getConfidenceColor(score: number): string {
  if (score >= 0.7) return "text-green-400";
  if (score >= 0.4) return "text-orange-400";
  return "text-red-400";
}

function getConfidenceGradient(score: number): string {
  if (score >= 0.7) return "from-green-500 to-emerald-400";
  if (score >= 0.4) return "from-orange-500 to-amber-400";
  return "from-red-500 to-pink-400";
}

function getConfidenceLabel(score: number): string {
  if (score >= 0.8) return "High";
  if (score >= 0.6) return "Moderate";
  if (score >= 0.4) return "Low";
  return "Very Low";
}

export function ConfidenceGauge({
  score,
  size = "md",
  showLabel = true,
  label,
}: ConfidenceGaugeProps) {
  const pct = Math.round(score * 100);
  const colorClass = getConfidenceColor(score);
  const gradientClass = getConfidenceGradient(score);

  const sizeMap = {
    sm: { ring: 40, stroke: 3, text: "text-xs", labelText: "text-[9px]" },
    md: { ring: 56, stroke: 4, text: "text-sm", labelText: "text-[10px]" },
    lg: { ring: 72, stroke: 5, text: "text-lg", labelText: "text-xs" },
  };

  const s = sizeMap[size];
  const radius = (s.ring - s.stroke * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score * circumference);

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: s.ring, height: s.ring }}>
        {/* Background ring */}
        <svg
          width={s.ring}
          height={s.ring}
          className="rotate-[-90deg]"
        >
          <circle
            cx={s.ring / 2}
            cy={s.ring / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth={s.stroke}
          />
          <circle
            cx={s.ring / 2}
            cy={s.ring / 2}
            r={radius}
            fill="none"
            className={`stroke-current ${colorClass}`}
            strokeWidth={s.stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{
              transition: "stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1)",
            }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold ${colorClass} ${s.text}`}>{pct}%</span>
        </div>
      </div>
      {showLabel && (
        <div className="text-center">
          <p className={`font-medium ${colorClass} ${s.labelText}`}>
            {getConfidenceLabel(score)}
          </p>
          {label && (
            <p className={`text-gray-500 ${s.labelText}`}>{label}</p>
          )}
        </div>
      )}
    </div>
  );
}

/** Inline horizontal confidence bar (compact version). */
export function ConfidenceBar({
  score,
  showPct = true,
}: {
  score: number;
  showPct?: boolean;
}) {
  const colorClass = getConfidenceColor(score);
  const gradientClass = getConfidenceGradient(score);

  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${gradientClass}`}
          style={{
            width: `${score * 100}%`,
            transition: "width 0.6s cubic-bezier(0.4,0,0.2,1)",
          }}
        />
      </div>
      {showPct && (
        <span className={`text-[10px] font-medium ${colorClass}`}>
          {Math.round(score * 100)}%
        </span>
      )}
    </div>
  );
}
