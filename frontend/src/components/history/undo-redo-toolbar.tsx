"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Undo2, Redo2, History, Save } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { historyApi, versionsApi } from "@/lib/api";

interface UndoRedoToolbarProps {
  fileId: number | null;
  onUndo: () => void;
}

export function UndoRedoToolbar({ fileId, onUndo }: UndoRedoToolbarProps) {
  const [operationCount, setOperationCount] = useState(0);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (fileId) {
      loadHistory();
    }
  }, [fileId]);

  const loadHistory = async () => {
    if (!fileId) return;
    
    try {
      const response = await historyApi.getHistory(fileId);
      const undoOps = response.data.undo_operations || [];
      const redoOps = response.data.redo_operations || [];
      setOperationCount(undoOps.length);
      setCanUndo(response.data.can_undo || undoOps.length > 0);
      setCanRedo(response.data.can_redo || redoOps.length > 0);
    } catch (error) {
      console.error("Failed to load history:", error);
    }
  };

  const handleUndo = async () => {
    if (!fileId) return;

    try {
      await historyApi.undo(fileId);
      toast({
        title: "Undone",
        description: "Last operation has been undone",
      });
      onUndo();
      loadHistory();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to undo",
        variant: "destructive",
      });
    }
  };

  const handleRedo = async () => {
    if (!fileId) return;

    try {
      await historyApi.redo(fileId);
      toast({
        title: "Redone",
        description: "Operation has been redone",
      });
      onUndo();
      loadHistory();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to redo",
        variant: "destructive",
      });
    }
  };

  const handleSaveVersion = async () => {
    if (!fileId) return;

    try {
      await versionsApi.createVersion(fileId, "Manual save");
      toast({
        title: "Version Saved",
        description: "Current state has been saved as a version",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save version",
        variant: "destructive",
      });
    }
  };

  if (!fileId) return null;

  return (
    <div className="flex items-center gap-2 rounded-lg border border-border bg-card p-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={handleUndo}
        disabled={!canUndo}
        title="Undo last operation"
      >
        <Undo2 className="h-4 w-4 mr-2" />
        Undo
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleRedo}
        disabled={!canRedo}
        title="Redo last undone operation"
      >
        <Redo2 className="h-4 w-4 mr-2" />
        Redo
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleSaveVersion}
        title="Save current version"
      >
        <Save className="h-4 w-4 mr-2" />
        Save Version
      </Button>
      <div className="flex items-center gap-2 px-2">
        <History className="h-4 w-4 text-muted-foreground" />
        <Badge variant="secondary">{operationCount} operations</Badge>
      </div>
    </div>
  );
}
