"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Download, FileText, Image, FileSpreadsheet } from "lucide-react";

interface ExportDialogProps {
  data: any;
  type: "data" | "chart" | "report";
  onExport: (format: string) => void;
}

export function ExportDialog({ data, type, onExport }: ExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState("");

  const formats = {
    data: [
      { id: "csv", name: "CSV", icon: FileText, description: "Comma-separated values" },
      { id: "xlsx", name: "Excel", icon: FileSpreadsheet, description: "Microsoft Excel format" },
      { id: "json", name: "JSON", icon: FileText, description: "JavaScript Object Notation" },
    ],
    chart: [
      { id: "png", name: "PNG", icon: Image, description: "Portable Network Graphics" },
      { id: "svg", name: "SVG", icon: Image, description: "Scalable Vector Graphics" },
      { id: "pdf", name: "PDF", icon: FileText, description: "Portable Document Format" },
    ],
    report: [
      { id: "pdf", name: "PDF Report", icon: FileText, description: "Full analysis report" },
      { id: "html", name: "HTML", icon: FileText, description: "Web page format" },
      { id: "markdown", name: "Markdown", icon: FileText, description: "Plain text format" },
    ],
  };

  const availableFormats = formats[type];

  const handleExport = () => {
    if (selectedFormat) {
      onExport(selectedFormat);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="mb-3 text-lg font-semibold">Select Export Format</h3>
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
      </div>

      <Button
        onClick={handleExport}
        disabled={!selectedFormat}
        className="w-full"
      >
        <Download className="mr-2 h-4 w-4" />
        Export as {selectedFormat?.toUpperCase()}
      </Button>
    </div>
  );
}
