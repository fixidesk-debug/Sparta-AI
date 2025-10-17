"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Sparkles, Loader2 } from "lucide-react";

interface NLChartInputProps {
  onGenerate: (config: any) => void;
  fileId: number | null;
}

export function NLChartInput({ onGenerate, fileId }: NLChartInputProps) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !fileId || loading) return;

    setLoading(true);
    try {
      const { nlApi } = await import("@/lib/api");
      const response = await nlApi.nlToChart(fileId, query);
      onGenerate(response.data);
      setQuery("");
    } catch (error) {
      console.error("Failed to generate chart from NL:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="relative flex-1">
        <Sparkles className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe the chart you want... e.g., 'Show sales by region as a bar chart'"
          className="pl-10"
          disabled={loading || !fileId}
        />
      </div>
      <Button type="submit" disabled={loading || !fileId || !query.trim()}>
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          "Generate"
        )}
      </Button>
    </form>
  );
}
