"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface AdvancedChartConfigProps {
  config: any;
  onChange: (config: any) => void;
}

export function AdvancedChartConfig({ config, onChange }: AdvancedChartConfigProps) {
  const [localConfig, setLocalConfig] = useState(config);

  const handleChange = (key: string, value: any) => {
    const newConfig = { ...localConfig, [key]: value };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  return (
    <Card className="p-4 space-y-4">
      <h3 className="font-semibold">Chart Customization</h3>
      
      <div>
        <label className="mb-2 block text-sm font-medium">Chart Title</label>
        <Input
          value={localConfig.title || ""}
          onChange={(e) => handleChange("title", e.target.value)}
          placeholder="Enter chart title"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium">X-Axis Label</label>
          <Input
            value={localConfig.xLabel || ""}
            onChange={(e) => handleChange("xLabel", e.target.value)}
            placeholder="X-axis label"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium">Y-Axis Label</label>
          <Input
            value={localConfig.yLabel || ""}
            onChange={(e) => handleChange("yLabel", e.target.value)}
            placeholder="Y-axis label"
          />
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium">Color Scheme</label>
        <div className="flex gap-2">
          {["#8B9BF8", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"].map((color) => (
            <button
              key={color}
              className="h-8 w-8 rounded border-2 border-border hover:border-primary"
              style={{ backgroundColor: color }}
              onClick={() => handleChange("color", color)}
            />
          ))}
        </div>
      </div>
    </Card>
  );
}
