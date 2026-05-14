import Link from "next/link";
import { notFound } from "next/navigation";
import { ApiError } from "@/components/ApiError";
import {
  fetchDeviceContext,
  fetchLatestLogs,
} from "@/lib/api";
import type { IotLog } from "@/lib/types";

function formatTs(ts: string | undefined) {
  if (!ts) return "—";
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return ts;
  }
}

function LogsTable({ logs }: { logs: IotLog[] }) {
  if (logs.length === 0) {
    return (
      <p className="text-sm text-zinc-500">No log rows returned for this device.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr className="border-b border-zinc-800 text-xs uppercase tracking-wide text-zinc-500">
            <th className="pb-3 pr-3 font-medium">Time</th>
            <th className="pb-3 pr-3 font-medium">Error</th>
            <th className="pb-3 pr-3 font-medium">Hz</th>
            <th className="pb-3 pr-3 font-medium">Power W</th>
            <th className="pb-3 font-medium">Pressure</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/80">
          {logs.map((row, i) => (
            <tr key={`${row.timestamp ?? i}`}>
              <td className="py-2.5 pr-3 font-mono text-xs text-zinc-400">
                {formatTs(row.timestamp as string | undefined)}
              </td>
              <td className="py-2.5 pr-3 font-mono text-xs">
                {String(row.error_code ?? "—")}
              </td>
              <td className="py-2.5 pr-3 tabular-nums text-zinc-300">
                {row.compressor_frequency != null
                  ? String(row.compressor_frequency)
                  : "—"}
              </td>
              <td className="py-2.5 pr-3 tabular-nums text-zinc-300">
                {row.power_consumption != null
                  ? String(row.power_consumption)
                  : "—"}
              </td>
              <td className="py-2.5 tabular-nums text-zinc-300">
                {row.refrigerant_pressure != null
                  ? String(row.refrigerant_pressure)
                  : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type PageProps = { params: Promise<{ id: string }> };

export default async function DeviceDetailPage({ params }: PageProps) {
  const { id: rawId } = await params;
  const id = decodeURIComponent(rawId);

  let logs = null as Awaited<ReturnType<typeof fetchLatestLogs>> | null;
  let ctx = null as Awaited<ReturnType<typeof fetchDeviceContext>> | null;
  let error: string | null = null;

  try {
    [logs, ctx] = await Promise.all([
      fetchLatestLogs(id),
      fetchDeviceContext(id),
    ]);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    if (msg.includes("API 404") || msg.includes("PGRST116")) {
      notFound();
    }
    error = msg;
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <Link
        href="/devices"
        className="text-xs font-medium text-zinc-500 hover:text-cyan-400"
      >
        ← Back to devices
      </Link>
      <h1 className="mt-4 font-mono text-xl font-semibold text-white sm:text-2xl">
        {id}
      </h1>
      <p className="mt-2 text-sm text-zinc-400">
        Latest telemetry and maintenance context from the AeroFix API.
      </p>

      {error ? (
        <div className="mt-8">
          <ApiError message={error} />
        </div>
      ) : (
        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 shadow-xl shadow-black/20">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-zinc-400">
              Latest logs
            </h2>
            <LogsTable logs={logs?.logs ?? []} />
          </section>
          <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 shadow-xl shadow-black/20">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-zinc-400">
              Device context
            </h2>
            <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap rounded-xl bg-black/40 p-4 font-mono text-xs leading-relaxed text-zinc-300 ring-1 ring-zinc-800/80">
              {ctx?.context?.trim() || "—"}
            </pre>
          </section>
        </div>
      )}
    </div>
  );
}
