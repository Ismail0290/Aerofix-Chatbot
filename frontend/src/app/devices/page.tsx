import Link from "next/link";
import { ApiError } from "@/components/ApiError";
import { fetchDevices } from "@/lib/api";

function statusPill(status: string | undefined) {
  const s = (status ?? "UNKNOWN").toUpperCase();
  const map: Record<string, string> = {
    ACTIVE: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
    MAINTENANCE: "bg-amber-500/15 text-amber-200 ring-amber-500/30",
    OFFLINE: "bg-zinc-500/15 text-zinc-300 ring-zinc-500/30",
  };
  const cls = map[s] ?? "bg-zinc-500/15 text-zinc-300 ring-zinc-500/30";
  return (
    <span
      className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ring-1 ring-inset ${cls}`}
    >
      {s}
    </span>
  );
}

export default async function DevicesPage() {
  let data = null as Awaited<ReturnType<typeof fetchDevices>> | null;
  let error: string | null = null;
  try {
    data = await fetchDevices();
  } catch (e) {
    error = e instanceof Error ? e.message : "Unknown error";
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <h1 className="text-2xl font-semibold tracking-tight text-white">
        Devices
      </h1>
      <p className="mt-2 max-w-xl text-sm text-zinc-400">
        Fleet inventory from Supabase. Open a device for live logs and
        aggregated context for diagnostics.
      </p>

      <div className="mt-8">
        {error ? (
          <ApiError message={error} />
        ) : (
          <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/40 shadow-xl shadow-black/20">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900/80 text-xs uppercase tracking-wide text-zinc-500">
                  <th className="px-4 py-3 font-medium sm:px-6">ID</th>
                  <th className="px-4 py-3 font-medium sm:px-6">Model</th>
                  <th className="px-4 py-3 font-medium sm:px-6">Building</th>
                  <th className="px-4 py-3 font-medium sm:px-6">Status</th>
                  <th className="px-4 py-3 font-medium sm:px-6" />
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/80">
                {(data?.devices ?? []).map((d) => (
                  <tr key={d.id} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 font-mono text-xs text-zinc-400 sm:px-6">
                      {d.id}
                    </td>
                    <td className="px-4 py-3 text-zinc-200 sm:px-6">
                      {String(d.model_number ?? "—")}
                    </td>
                    <td className="px-4 py-3 text-zinc-400 sm:px-6">
                      {String(d.building_type ?? "—")}
                    </td>
                    <td className="px-4 py-3 sm:px-6">
                      {statusPill(
                        d.current_status ? String(d.current_status) : undefined
                      )}
                    </td>
                    <td className="px-4 py-3 text-right sm:px-6">
                      <Link
                        href={`/devices/${encodeURIComponent(d.id)}`}
                        className="text-xs font-medium text-cyan-400 hover:text-cyan-300"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(data?.devices?.length ?? 0) === 0 && (
              <p className="py-12 text-center text-sm text-zinc-500">
                No devices found. Run{" "}
                <code className="rounded bg-black/40 px-1.5 py-0.5 font-mono text-[11px]">
                  python seed_devices.py
                </code>{" "}
                after configuring Supabase credentials.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
