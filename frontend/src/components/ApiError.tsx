export function ApiError({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
      <p className="font-medium text-amber-50">Could not load data</p>
      <p className="mt-1 text-amber-100/80">{message}</p>
      <p className="mt-2 text-xs text-amber-200/60">
        Start the API with{" "}
        <code className="rounded bg-black/30 px-1 py-0.5 font-mono text-[11px]">
          uvicorn main:app --reload
        </code>{" "}
        and set{" "}
        <code className="rounded bg-black/30 px-1 py-0.5 font-mono text-[11px]">
          NEXT_PUBLIC_AEROFIX_API_URL
        </code>{" "}
        if it is not on 127.0.0.1:8000.
      </p>
    </div>
  );
}
