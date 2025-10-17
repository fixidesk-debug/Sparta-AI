"use client";

import { useEffect, useState } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Brain, Plus, Trash2, Eye } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface MLModel {
  model_id: string;
  model_type: string;
  created_at: string;
  visibility: string;
  owner: string;
}

export default function ModelsPage() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const loadModels = async () => {
    try {
      const response = await api.get("/ml_models/list");
      setModels(response.data.models);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load models",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  const handleDelete = async (modelId: string) => {
    if (!confirm("Are you sure you want to delete this model?")) return;

    try {
      await api.delete(`/ml_models/${modelId}`);
      toast({
        title: "Success",
        description: "Model deleted successfully",
      });
      loadModels();
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to delete model",
        variant: "destructive",
      });
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto max-w-6xl p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">ML Models</h1>
            <p className="text-muted-foreground">Manage your trained machine learning models</p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Train Model
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading models...</div>
        ) : models.length === 0 ? (
          <Card className="p-12 text-center">
            <Brain className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No models yet</h3>
            <p className="text-muted-foreground mb-4">Train your first ML model to get started</p>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Train Model
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4">
            {models.map((model) => (
              <Card key={model.model_id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <Brain className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">{model.model_type}</h3>
                        <Badge variant={model.visibility === "public" ? "default" : "secondary"}>
                          {model.visibility}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Created {formatDate(model.created_at)} • {model.owner}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(model.model_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
