import Link from "next/link";
import { ApiError } from "@/components/ApiError";
import { FailureChart } from "@/components/FailureChart";
import {
  fetchFailureAnalytics,
  fetchPriorityTickets,
} from "@/lib/api";

function scoreTone(score: number) {
  if (score >= 120) return "text-red-400";
  if (score >= 90) return "text-orange-400";
  if (score >= 60) return "text-amber-300";
  return "text-zinc-300";
}

export default async function DashboardPage() {
  let tickets = null as Awaited<ReturnType<typeof fetchPriorityTickets>> | null;
  let failures = null as Awaited<
    ReturnType<typeof fetchFailureAnalytics>
  > | null;
  let error: string | null = null;

  try {
    [tickets, failures] = await Promise.all([
      fetchPriorityTickets(),
      fetchFailureAnalytics(),
    ]);
  } catch (e) {
    error = e instanceof Error ? e.message : "Unknown error";
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <div className="mb-10">
        <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
          Operations dashboard
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-400">
          Live view of prioritized service tickets and failure code
          distribution from your Supabase-backed IoT pipeline.
        </p>
      </div>

      {error ? (
        <ApiError message={error} />
      ) : (
        <div className="grid gap-8 lg:grid-cols-5">
          <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 shadow-xl shadow-black/20 lg:col-span-3">
            <div className="mb-4 flex items-center justify-between gap-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
                Priority tickets
              </h2>
              <Link
                href="/devices"
                className="text-xs font-medium text-cyan-400 hover:text-cyan-300"
              >
                All devices →
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[520px] text-left text-sm">
                <thead>
                  <tr className="border-b border-zinc-800 text-xs uppercase tracking-wide text-zinc-500">
                    <th className="pb-3 pr-3 font-medium">Score</th>
                    <th className="pb-3 pr-3 font-medium">Device</th>
                    <th className="pb-3 pr-3 font-medium">Model</th>
                    <th className="pb-3 pr-3 font-medium">Building</th>
                    <th className="pb-3 font-medium">Error</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/80">
                  {(tickets?.tickets ?? []).slice(0, 20).map((t) => (
                    <tr key={t.device_id} className="group">
                      <td className="py-3 pr-3">
                        <span
                          className={`font-mono text-sm tabular-nums font-semibold ${scoreTone(t.priority_score)}`}
                        >
                          {t.priority_score}
                        </span>
                      </td>
                      <td className="py-3 pr-3">
                        <Link
                          href={`/devices/${encodeURIComponent(t.device_id)}`}
                          className="font-mono text-xs text-cyan-400 underline-offset-2 hover:underline"
                        >
                          {t.device_id.slice(0, 8)}…
                        </Link>
                      </td>
                      <td className="max-w-[180px] truncate py-3 pr-3 text-zinc-300">
                        {t.model}
                      </td>
                      <td className="py-3 pr-3 text-zinc-400">{t.building}</td>
                      <td className="py-3 font-mono text-xs text-zinc-300">
                        {t.error_code}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {(tickets?.tickets?.length ?? 0) === 0 && (
                <p className="py-8 text-center text-sm text-zinc-500">
                  No tickets yet. Ensure devices have IoT logs in Supabase.
                </p>
              )}
            </div>
          </section>

          <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 shadow-xl shadow-black/20 lg:col-span-2">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-zinc-400">
              Failure analytics
            </h2>
            <FailureChart counts={failures?.failure_counts ?? {}} />
          </section>
        </div>
      )}
    </div>
  );
}
