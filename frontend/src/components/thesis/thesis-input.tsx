import { thesisSamples } from "@/lib/constants";

export function ThesisInput({
  input,
  setInput,
  onAnalyze,
  onSave,
  onExport,
  loading,
  saving,
  note,
}: {
  input: string;
  setInput: (value: string) => void;
  onAnalyze: () => void;
  onSave: () => void;
  onExport: () => void;
  loading: boolean;
  saving: boolean;
  note: string | null;
}) {
  return (
    <div className="space-y-4">
      <textarea
        value={input}
        onChange={(event) => setInput(event.target.value)}
        className="min-h-[160px] w-full rounded-3xl border border-shell-border bg-black/20 px-4 py-4 text-[15px] text-shell-text outline-none transition focus:border-shell-accent/40 focus:ring-1 focus:ring-shell-accent/25"
        placeholder="Describe the macro or thematic thesis you want to convert into exposures."
      />

      <div className="flex flex-wrap gap-2">
        {thesisSamples.map((sample) => (
          <button
            key={sample}
            type="button"
            onClick={() => setInput(sample)}
            className="rounded-full border border-shell-border bg-white/5 px-3 py-2 text-xs text-shell-muted transition hover:border-shell-accent/30 hover:text-shell-text"
          >
            {sample}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onAnalyze}
          disabled={loading || !input.trim()}
          className="rounded-2xl bg-shell-accent px-4 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Analyzing..." : "Analyze Thesis"}
        </button>
        <button
          type="button"
          onClick={onSave}
          disabled={saving || !input.trim()}
          className="rounded-2xl border border-shell-border bg-white/5 px-4 py-3 text-sm font-semibold text-shell-text transition hover:border-shell-accent/30 hover:bg-shell-accent/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Saving..." : "Save Result"}
        </button>
        <button
          type="button"
          onClick={onExport}
          className="rounded-2xl border border-shell-border bg-black/20 px-4 py-3 text-sm font-semibold text-shell-text transition hover:border-shell-accent/30 hover:bg-shell-accent/10"
        >
          Export JSON
        </button>
      </div>

      {note ? <p className="text-sm text-shell-accentSoft">{note}</p> : null}
    </div>
  );
}
