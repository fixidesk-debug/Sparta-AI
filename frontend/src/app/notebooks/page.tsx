"use client";

import { useEffect, useState } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { BookOpen, Plus, Trash2 } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface Notebook {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export default function NotebooksPage() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const router = useRouter();

  const loadNotebooks = async () => {
    try {
      const response = await api.get("/notebooks/");
      setNotebooks(response.data.notebooks);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load notebooks",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotebooks();
  }, []);

  const handleCreate = async () => {
    try {
      const response = await api.post("/notebooks/", {
        title: "Untitled Notebook",
      });
      router.push(`/notebooks/${response.data.id}`);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to create notebook",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this notebook?")) return;

    try {
      await api.delete(`/notebooks/${id}`);
      toast({
        title: "Success",
        description: "Notebook deleted successfully",
      });
      loadNotebooks();
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to delete notebook",
        variant: "destructive",
      });
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto max-w-6xl p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Notebooks</h1>
            <p className="text-muted-foreground">Interactive Python notebooks</p>
          </div>
          <Button onClick={handleCreate}>
            <Plus className="mr-2 h-4 w-4" />
            New Notebook
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading notebooks...</div>
        ) : notebooks.length === 0 ? (
          <Card className="p-12 text-center">
            <BookOpen className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No notebooks yet</h3>
            <p className="text-muted-foreground mb-4">Create your first notebook to start coding</p>
            <Button onClick={handleCreate}>
              <Plus className="mr-2 h-4 w-4" />
              New Notebook
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {notebooks.map((notebook) => (
              <Card
                key={notebook.id}
                className="p-4 cursor-pointer hover:bg-accent transition-colors"
                onClick={() => router.push(`/notebooks/${notebook.id}`)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <BookOpen className="h-5 w-5 text-primary" />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(notebook.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <h3 className="font-semibold mb-1">{notebook.title}</h3>
                <p className="text-xs text-muted-foreground">
                  Updated {formatDate(notebook.updated_at)}
                </p>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
