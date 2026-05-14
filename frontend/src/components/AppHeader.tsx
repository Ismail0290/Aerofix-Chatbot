import Link from "next/link";

const linkClass =
  "text-sm font-medium text-zinc-400 transition hover:text-cyan-300";

export function AppHeader() {
  return (
    <header className="border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-4 py-4 sm:px-6">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="text-lg font-semibold tracking-tight text-white">
            AeroFix
          </span>
          <span className="hidden text-xs font-medium uppercase tracking-widest text-zinc-500 sm:inline">
            HVAC ops
          </span>
        </Link>
        <nav className="flex items-center gap-5">
          <Link href="/" className={linkClass}>
            Dashboard
          </Link>
          <Link href="/devices" className={linkClass}>
            Devices
          </Link>
        </nav>
      </div>
    </header>
  );
}
