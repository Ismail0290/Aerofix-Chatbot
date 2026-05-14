import Link from "next/link";

export default function DeviceNotFound() {
  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center">
      <h1 className="text-xl font-semibold text-white">Device not found</h1>
      <p className="mt-2 text-sm text-zinc-400">
        That ID is missing in Supabase or the API returned no match.
      </p>
      <Link
        href="/devices"
        className="mt-8 inline-block text-sm font-medium text-cyan-400 hover:text-cyan-300"
      >
        ← Browse devices
      </Link>
    </div>
  );
}
