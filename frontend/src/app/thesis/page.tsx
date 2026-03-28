"use client";

import { useEffect, useState } from "react";

import { ThesisInput } from "@/components/thesis/thesis-input";
import { ThesisResult } from "@/components/thesis/thesis-result";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/ui/loading-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { UnavailablePanel } from "@/components/ui/unavailable-panel";
import { analyzeThesis, describeApiError, getSavedTheses, persistThesis } from "@/lib/api";
import { thesisSamples } from "@/lib/constants";
import { formatTimestamp } from "@/lib/format";
import { SavedThesisResponse, ThesisResult as ThesisResultType } from "@/lib/types";

export default function ThesisPage() {
  const [input, setInput] = useState(thesisSamples[0]);
  const [result, setResult] = useState<ThesisResultType | null>(null);
  const [saved, setSaved] = useState<SavedThesisResponse[]>([]);
  const [bootstrapping, setBootstrapping] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  async function loadData() {
    setError(null);
    setBootstrapping(true);

    try {
      const [remote, analysis] = await Promise.all([getSavedTheses(), analyzeThesis(thesisSamples[0])]);
      setSaved(remote.slice(0, 12));
      setResult(analysis);
    } catch (loadError) {
      setError(describeApiError(loadError));
      setSaved([]);
      setResult(null);
    } finally {
      setBootstrapping(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleAnalyze() {
    setLoading(true);
    setNote(null);
    try {
      setResult(await analyzeThesis(input));
    } catch (analyzeError) {
      setNote(describeApiError(analyzeError));
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!result) {
      return;
    }

    setSaving(true);
    setNote(null);

    try {
      const savedResult = await persistThesis(input);
      setSaved((current) => [savedResult, ...current.filter((item) => item.id !== savedResult.id)].slice(0, 12));
      setNote("Saved to backend persistence.");
    } catch (saveError) {
      setNote(`${describeApiError(saveError)} No local fallback is enabled.`);
    } finally {
      setSaving(false);
    }
  }

  function handleExport() {
    if (!result || typeof window === "undefined") {
      return;
    }

    const blob = new Blob([JSON.stringify({ input, exported_at: new Date().toISOString(), result }, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `signalstack-thesis-${Date.now()}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    setNote("Exported the current thesis result to JSON.");
  }

  if (bootstrapping) {
    return (
      <LoadingPanel
        title="Loading thesis desk"
        eyebrow="Thesis Builder"
        description="Preparing the saved-thesis library and running the default sample analysis."
      />
    );
  }

  if (error) {
    return (
      <UnavailablePanel
        title="Thesis desk unavailable"
        eyebrow="Thesis Builder"
        description="The thesis desk relies on the live backend for analysis and saved results. No browser-local fallback is enabled."
        error={error}
        action={
          <button
            type="button"
            onClick={() => void loadData()}
            className="inline-flex items-center justify-center rounded-full border border-shell-border bg-white/[0.04] px-4 py-2 text-sm font-medium text-shell-text transition hover:border-shell-accent/30 hover:bg-shell-accent/10"
          >
            Retry live load
          </button>
        }
      />
    );
  }

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Thesis Builder"
        description="Translate a plain-English macro or thematic hypothesis into transmission channels, sector implications, ETF ideas, single-name examples, and the signals that should confirm or invalidate the view."
        action={
          <>
            <Badge tone="neutral">{saved.length} saved</Badge>
            {result ? <Badge tone="accent">{Math.round(result.confidence * 100)}% mapped confidence</Badge> : null}
          </>
        }
      />

      <div className="grid gap-6 xl:grid-cols-[1.12fr_0.88fr]">
        <div className="space-y-6">
          <Card title="Translate a Thesis" eyebrow="Rules-Based Engine">
            <ThesisInput
              input={input}
              setInput={setInput}
              onAnalyze={() => void handleAnalyze()}
              onSave={() => void handleSave()}
              onExport={handleExport}
              loading={loading}
              saving={saving}
              note={note}
            />
          </Card>

          {loading && !result ? (
            <LoadingPanel
              title="Analyzing thesis"
              eyebrow="Parser"
              description="Mapping theme family, expression style, sectors, and confirming signals."
            />
          ) : null}

          {result ? <ThesisResult result={result} /> : null}
        </div>

        <div className="space-y-6 xl:sticky xl:top-[96px] xl:self-start">
          <Card title="Saved Thesis Library" eyebrow="Persistence">
            <div className="space-y-3">
              {saved.length ? (
                saved.map((item) => (
                  <button
                    key={`${item.id}-${item.created_at}`}
                    type="button"
                    onClick={() => {
                      setInput(item.input_text);
                      setResult(item.result);
                    }}
                    className="w-full rounded-[22px] border border-shell-border bg-white/[0.03] p-4 text-left transition hover:border-shell-accent/30 hover:bg-shell-accent/5"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm font-semibold text-shell-text">{item.interpreted_theme}</h3>
                      <Badge tone="neutral">{formatTimestamp(item.created_at)}</Badge>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-shell-muted">{item.input_text}</p>
                  </button>
                ))
              ) : (
                <p className="text-sm text-shell-muted">Saved theses will appear here after you persist an analysis.</p>
              )}
            </div>
          </Card>

          <Card title="How This Works" eyebrow="Transparent Logic">
            <div className="space-y-4 text-sm leading-7 text-shell-muted">
              <p>SignalStack does not rely on a generic LLM call for the core mapping step in this MVP.</p>
              <p>Instead, it uses explicit theme libraries, keyword rules, and a structured macro taxonomy so you can edit the logic as your process evolves.</p>
              <p>The next upgrade path is better entity extraction, richer exposure ranking, and statistical validation layered on top of the same transparent framework.</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
