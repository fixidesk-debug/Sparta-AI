"use client";

import { useEffect, useState } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { filesApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { FileText, Trash2, Upload, Download } from "lucide-react";
import { formatDate, formatFileSize } from "@/lib/utils";

interface FileItem {
  id: number;
  filename: string;
  file_size: number;
  file_type: string;
  upload_time: string;
}

export default function FilesPage() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const loadFiles = async () => {
    try {
      const response = await filesApi.list();
      setFiles(response.data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load files",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this file?")) return;

    try {
      await filesApi.delete(id);
      toast({
        title: "Success",
        description: "File deleted successfully",
      });
      loadFiles();
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to delete file",
        variant: "destructive",
      });
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto max-w-6xl p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Files</h1>
            <p className="text-muted-foreground">Manage your uploaded datasets</p>
          </div>
          <Button>
            <Upload className="mr-2 h-4 w-4" />
            Upload File
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading files...</div>
        ) : files.length === 0 ? (
          <Card className="p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No files yet</h3>
            <p className="text-muted-foreground mb-4">Upload your first dataset to get started</p>
            <Button>
              <Upload className="mr-2 h-4 w-4" />
              Upload File
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4">
            {files.map((file) => (
              <Card key={file.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{file.filename}</h3>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(file.file_size)} • {formatDate(file.upload_time)}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon">
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(file.id)}
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
