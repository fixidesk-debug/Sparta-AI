"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { Sparkles, Lock } from "lucide-react";

export default function SharedAnalysisPage() {
  const params = useParams();
  const token = params.token as string;
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSharedAnalysis();
  }, [token]);

  const loadSharedAnalysis = async () => {
    try {
      const response = await api.get(`/sharing/shared/${token}`);
      setAnalysis(response.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || "Failed to load shared analysis");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <div className="mb-4 flex h-12 w-12 mx-auto items-center justify-center rounded-lg bg-primary animate-pulse">
            <Sparkles className="h-6 w-6 text-primary-foreground" />
          </div>
          <p className="text-muted-foreground">Loading shared analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <Card className="max-w-md p-8 text-center">
          <Lock className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={() => window.location.href = "/"}>
            Go to Home
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="container mx-auto max-w-6xl">
        <Card className="p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold mb-2">Shared Analysis</h1>
            <p className="text-sm text-muted-foreground">
              Permissions: {analysis?.permissions?.join(", ")}
            </p>
          </div>
          
          <div className="space-y-4">
            <p className="text-muted-foreground">
              Analysis ID: {analysis?.analysis_id}
            </p>
            <p className="text-sm text-muted-foreground">
              Shared on: {new Date(analysis?.created_at).toLocaleDateString()}
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
