"use client";

import { useEffect, useState } from "react";

import { AnomalyFeedList } from "@/components/feed/anomaly-feed-list";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { getAnomalies } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import { AnomalyResponse } from "@/lib/types";

export default function FeedPage() {
  const [data, setData] = useState<AnomalyResponse | null>(null);

  useEffect(() => {
    void getAnomalies().then(setData);
  }, []);

  if (!data) {
    return (
      <Card title="Loading anomaly feed" eyebrow="Curiosity Scanner">
        <p className="text-sm text-shell-muted">Ranking cross-asset divergences and novelty signals.</p>
      </Card>
    );
  }

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Curiosity Feed"
        description="Daily anomaly tape for unusual cross-asset behavior. Signals are ranked by divergence, novelty, breadth, and practical market importance."
        action={<Badge tone="accent">Feed time {formatTimestamp(data.as_of)}</Badge>}
      />
      <AnomalyFeedList data={data} />
    </div>
  );
}
