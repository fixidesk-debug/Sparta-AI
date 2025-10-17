"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Download, FileText, Image, FileSpreadsheet, FileType, Presentation } from "lucide-react";
import { exportApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface EnhancedExportDialogProps {
  fileId: number | null;
  chartConfig?: any;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EnhancedExportDialog({ fileId, chartConfig, open, onOpenChange }: EnhancedExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState("");
  const [exporting, setExporting] = useState(false);
  const { toast } = useToast();

  const formats = [
    { id: "pdf", name: "PDF Report", icon: FileText, description: "Full analysis report", requiresFile: true },
    { id: "excel", name: "Excel", icon: FileSpreadsheet, description: "Multi-sheet workbook with stats", requiresFile: true },
    { id: "word", name: "Word Document", icon: FileType, description: "Microsoft Word format", requiresFile: true },
    { id: "powerpoint", name: "PowerPoint", icon: Presentation, description: "Presentation slides", requiresFile: true },
    { id: "png", name: "PNG Chart", icon: Image, description: "High-quality chart image", requiresFile: false },
  ];

  const handleExport = async () => {
    if (!selectedFormat) return;

    setExporting(true);
    try {
      let blob: Blob;
      let filename: string;

      switch (selectedFormat) {
        case "pdf":
          if (!fileId) throw new Error("File ID required");
          const pdfResponse = await exportApi.exportPDF(fileId);
          blob = pdfResponse.data;
          filename = `analysis_${fileId}.pdf`;
          break;

        case "excel":
          if (!fileId) throw new Error("File ID required");
          const excelResponse = await exportApi.exportExcel(fileId);
          blob = excelResponse.data;
          filename = `data_${fileId}.xlsx`;
          break;

        case "word":
          if (!fileId) throw new Error("File ID required");
          const wordResponse = await exportApi.exportWord(fileId);
          blob = wordResponse.data;
          filename = `analysis_${fileId}.docx`;
          break;

        case "powerpoint":
          if (!fileId) throw new Error("File ID required");
          const pptResponse = await exportApi.exportPowerPoint(fileId);
          blob = pptResponse.data;
          filename = `presentation_${fileId}.pptx`;
          break;

        case "png":
          if (!chartConfig) throw new Error("Chart configuration required");
          const pngResponse = await exportApi.exportChartPNG(chartConfig);
          blob = pngResponse.data;
          filename = "chart.png";
          break;

        default:
          throw new Error("Invalid format");
      }

      // Download file
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: "Export Successful",
        description: `File exported as ${selectedFormat.toUpperCase()}`,
      });

      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: "Export Failed",
        description: error.message || "Failed to export file",
        variant: "destructive",
      });
    } finally {
      setExporting(false);
    }
  };

  const availableFormats = formats.filter(f => {
    if (f.requiresFile && !fileId) return false;
    if (f.id === 'png' && !chartConfig) return false;
    return true;
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Export Data</DialogTitle>
          <DialogDescription>
            Choose a format to export your analysis
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2">
            {availableFormats.map((format) => {
              const Icon = format.icon;
              return (
                <Card
                  key={format.id}
                  className={`cursor-pointer p-4 transition-colors hover:bg-accent ${
                    selectedFormat === format.id ? "border-primary bg-primary/5" : ""
                  }`}
                  onClick={() => setSelectedFormat(format.id)}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm mb-1">{format.name}</h4>
                      <p className="text-xs text-muted-foreground">{format.description}</p>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          <Button
            onClick={handleExport}
            disabled={!selectedFormat || exporting}
            className="w-full"
          >
            <Download className="mr-2 h-4 w-4" />
            {exporting ? "Exporting..." : `Export as ${selectedFormat?.toUpperCase()}`}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
