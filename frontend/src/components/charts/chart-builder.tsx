"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
    BarChart3,
    LineChart,
    PieChart,
    ScatterChart,
    TrendingUp,
    Download,
} from "lucide-react";

interface ChartBuilderProps {
    data: any[];
    onGenerate: (config: ChartConfig) => void;
}

interface ChartConfig {
    type: string;
    xColumn: string;
    yColumn: string;
    title?: string;
    color?: string;
}

const chartTypes = [
    { id: "bar", name: "Bar Chart", icon: BarChart3, description: "Compare categories" },
    { id: "line", name: "Line Chart", icon: LineChart, description: "Show trends over time" },
    { id: "scatter", name: "Scatter Plot", icon: ScatterChart, description: "Show relationships" },
    { id: "pie", name: "Pie Chart", icon: PieChart, description: "Show proportions" },
    { id: "area", name: "Area Chart", icon: TrendingUp, description: "Show cumulative data" },
];

export function ChartBuilder({ data, onGenerate }: ChartBuilderProps) {
    const [selectedType, setSelectedType] = useState("bar");
    const [xColumn, setXColumn] = useState("");
    const [yColumn, setYColumn] = useState("");
    const [title, setTitle] = useState("");

    const columns = data.length > 0 ? Object.keys(data[0]) : [];

    const handleGenerate = () => {
        if (!xColumn || !yColumn) return;

        onGenerate({
            type: selectedType,
            xColumn,
            yColumn,
            title: title || `${yColumn} by ${xColumn}`,
        });
    };

    return (
        <div className="space-y-6">
            <div>
                <h3 className="mb-3 text-lg font-semibold">Select Chart Type</h3>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {chartTypes.map((type) => {
                        const Icon = type.icon;
                        return (
                            <Card
                                key={type.id}
                                className={`cursor-pointer p-4 transition-colors hover:bg-accent ${selectedType === type.id ? "border-primary bg-primary/5" : ""
                                    }`}
                                onClick={() => setSelectedType(type.id)}
                            >
                                <div className="flex items-start gap-3">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                        <Icon className="h-5 w-5 text-primary" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <h4 className="font-semibold text-sm">{type.name}</h4>
                                            {selectedType === type.id && (
                                                <Badge variant="default" className="h-5 text-xs">Selected</Badge>
                                            )}
                                        </div>
                                        <p className="text-xs text-muted-foreground">{type.description}</p>
                                    </div>
                                </div>
                            </Card>
                        );
                    })}
                </div>
            </div>

            <div>
                <h3 className="mb-3 text-lg font-semibold">Configure Data</h3>
                <div className="space-y-4">
                    <div>
                        <label className="mb-2 block text-sm font-medium">Chart Title (Optional)</label>
                        <Input
                            placeholder="Enter chart title"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                            <label className="mb-2 block text-sm font-medium">X-Axis Column</label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                value={xColumn}
                                onChange={(e) => setXColumn(e.target.value)}
                            >
                                <option value="">Select column...</option>
                                {columns.map((col) => (
                                    <option key={col} value={col}>
                                        {col}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="mb-2 block text-sm font-medium">Y-Axis Column</label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                value={yColumn}
                                onChange={(e) => setYColumn(e.target.value)}
                            >
                                <option value="">Select column...</option>
                                {columns.map((col) => (
                                    <option key={col} value={col}>
                                        {col}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex gap-3">
                <Button
                    onClick={handleGenerate}
                    disabled={!xColumn || !yColumn}
                    className="flex-1"
                >
                    Generate Chart
                </Button>
                <Button variant="outline">
                    <Download className="mr-2 h-4 w-4" />
                    Export
                </Button>
            </div>
        </div>
    );
}
