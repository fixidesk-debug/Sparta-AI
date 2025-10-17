"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { filesApi } from "@/lib/api";
import { useChatStore } from "@/store/chat-store";
import { useToast } from "@/hooks/use-toast";

export function FileUpload() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const { setCurrentFile } = useChatStore();
  const { toast } = useToast();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    setFiles([file]);
    setUploading(true);

    try {
      const response = await filesApi.upload(file);
      const fileData = {
        id: response.data.id,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date(),
      };
      setCurrentFile(fileData);
      
      // Emit event for other components to listen
      window.dispatchEvent(new CustomEvent('fileUploaded', { 
        detail: fileData 
      }));
      
      toast({
        title: "Success",
        description: "File uploaded successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to upload file",
        variant: "destructive",
      });
      setFiles([]);
    } finally {
      setUploading(false);
    }
  }, [setCurrentFile, toast]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".xls"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/json": [".json"],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  const removeFile = () => {
    setFiles([]);
    setCurrentFile(null);
  };

  if (files.length > 0) {
    return (
      <div className="mb-6">
        <div className="flex items-center justify-between rounded-lg border border-border bg-card p-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              {uploading ? (
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
              ) : (
                <FileText className="h-5 w-5 text-primary" />
              )}
            </div>
            <div>
              <p className="text-sm font-medium">{files[0].name}</p>
              <p className="text-xs text-muted-foreground">
                {(files[0].size / 1024).toFixed(2)} KB
              </p>
            </div>
          </div>
          {!uploading && (
            <Button
              variant="ghost"
              size="icon"
              onClick={removeFile}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "mb-6 cursor-pointer rounded-lg border-2 border-dashed border-border bg-muted/50 p-8 text-center transition-colors hover:border-primary/50 hover:bg-muted",
        isDragActive && "border-primary bg-primary/5",
        uploading && "pointer-events-none opacity-50"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-2">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
          <Upload className="h-6 w-6 text-primary" />
        </div>
        <div>
          <p className="text-sm font-medium">
            {isDragActive ? "Drop file here" : "Upload your data"}
          </p>
          <p className="text-xs text-muted-foreground">
            CSV, Excel, or JSON files
          </p>
        </div>
      </div>
    </div>
  );
}
