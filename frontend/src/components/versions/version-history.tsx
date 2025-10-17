"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Clock, RotateCcw, Trash2, GitCompare } from "lucide-react";
import { versionsApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { formatDate, formatFileSize } from "@/lib/utils";

interface VersionHistoryProps {
  fileId: number;
  onRestore: () => void;
}

export function VersionHistory({ fileId, onRestore }: VersionHistoryProps) {
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadVersions();
  }, [fileId]);

  const loadVersions = async () => {
    try {
      const response = await versionsApi.listVersions(fileId);
      setVersions(response.data.versions);
    } catch (error) {
      console.error("Failed to load versions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (versionName: string) => {
    if (!confirm("Are you sure you want to restore this version? Current data will be backed up.")) {
      return;
    }

    try {
      await versionsApi.restoreVersion(fileId, versionName);
      toast({
        title: "Version Restored",
        description: "Data has been restored to the selected version",
      });
      onRestore();
      loadVersions();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to restore version",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (versionName: string) => {
    if (!confirm("Are you sure you want to delete this version?")) {
      return;
    }

    try {
      await versionsApi.deleteVersion(fileId, versionName);
      toast({
        title: "Version Deleted",
        description: "Version has been deleted",
      });
      loadVersions();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete version",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return <div className="text-center py-4 text-sm text-muted-foreground">Loading versions...</div>;
  }

  if (versions.length === 0) {
    return (
      <div className="text-center py-8">
        <Clock className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
        <p className="text-sm text-muted-foreground">No versions saved yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {versions.map((version, i) => (
        <Card key={i} className="p-3">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Badge variant={i === 0 ? "default" : "secondary"} className="text-xs">
                  {i === 0 ? "Latest" : `Version ${versions.length - i}`}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {formatDate(version.created_at)}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                {version.file_size ? formatFileSize(version.file_size) : formatFileSize(version.size)}
              </p>
              {version.description && (
                <p className="text-xs text-muted-foreground mt-1">{version.description}</p>
              )}
            </div>
            {i > 0 && (
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRestore(version.version_name || version.filename)}
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Restore
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(version.version_name || version.filename)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}
