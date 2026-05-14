type Props = { counts: Record<string, number> };

export function FailureChart({ counts }: Props) {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const max = Math.max(...entries.map(([, n]) => n), 1);

  if (entries.length === 0) {
    return (
      <p className="text-sm text-zinc-500">
        No failure codes in the dataset (all clear or no logs yet).
      </p>
    );
  }

  return (
    <ul className="space-y-3">
      {entries.map(([code, count]) => (
        <li key={code} className="flex items-center gap-3">
          <span className="w-10 shrink-0 font-mono text-xs text-cyan-400">
            {code}
          </span>
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-800">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-600 to-emerald-500"
                style={{ width: `${(count / max) * 100}%` }}
              />
            </div>
            <span className="w-8 shrink-0 text-right text-xs tabular-nums text-zinc-400">
              {count}
            </span>
          </div>
        </li>
      ))}
    </ul>
  );
}
