"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Edit3,
  Trash2,
  Type,
  Plus,
  Filter,
  ArrowUpDown,
  Grid3x3,
  Merge,
} from "lucide-react";

interface TransformationPanelProps {
  columns: string[];
  onTransform: (operation: any) => void;
}

export function TransformationPanel({ columns, onTransform }: TransformationPanelProps) {
  const [selectedOperation, setSelectedOperation] = useState<string | null>(null);
  const [selectedColumn, setSelectedColumn] = useState("");
  const [newName, setNewName] = useState("");
  const [formula, setFormula] = useState("");

  const operations = [
    { id: "rename", name: "Rename Column", icon: Edit3, description: "Change column name" },
    { id: "delete", name: "Delete Column", icon: Trash2, description: "Remove a column" },
    { id: "cast", name: "Change Type", icon: Type, description: "Convert data type" },
    { id: "derive", name: "Derive Column", icon: Plus, description: "Create calculated column" },
    { id: "filter", name: "Filter Rows", icon: Filter, description: "Filter data" },
    { id: "sort", name: "Sort Data", icon: ArrowUpDown, description: "Sort by columns" },
    { id: "pivot", name: "Pivot Table", icon: Grid3x3, description: "Create pivot table" },
    { id: "merge", name: "Merge Datasets", icon: Merge, description: "Join with another dataset" },
  ];

  const handleApply = () => {
    if (!selectedOperation || !selectedColumn) return;

    const operation: any = {
      operation: selectedOperation,
      column: selectedColumn,
    };

    if (selectedOperation === "rename") {
      operation.new_name = newName;
    } else if (selectedOperation === "derive") {
      operation.formula = formula;
      operation.new_column = newName;
    }

    onTransform(operation);
    
    // Reset form
    setSelectedOperation(null);
    setSelectedColumn("");
    setNewName("");
    setFormula("");
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-3 text-lg font-semibold">Select Operation</h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {operations.map((op) => {
            const Icon = op.icon;
            return (
              <Card
                key={op.id}
                className={`cursor-pointer p-4 transition-colors hover:bg-accent ${
                  selectedOperation === op.id ? "border-primary bg-primary/5" : ""
                }`}
                onClick={() => setSelectedOperation(op.id)}
              >
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-sm">{op.name}</h4>
                      {selectedOperation === op.id && (
                        <Badge variant="default" className="h-5 text-xs">Selected</Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">{op.description}</p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {selectedOperation && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">Configure Operation</h3>
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium">Select Column</label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={selectedColumn}
                onChange={(e) => setSelectedColumn(e.target.value)}
              >
                <option value="">Choose a column...</option>
                {columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>

            {selectedOperation === "rename" && (
              <div>
                <label className="mb-2 block text-sm font-medium">New Name</label>
                <Input
                  placeholder="Enter new column name"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                />
              </div>
            )}

            {selectedOperation === "cast" && (
              <div>
                <label className="mb-2 block text-sm font-medium">New Data Type</label>
                <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                  <option>String</option>
                  <option>Integer</option>
                  <option>Float</option>
                  <option>Boolean</option>
                  <option>Date</option>
                </select>
              </div>
            )}

            {selectedOperation === "derive" && (
              <>
                <div>
                  <label className="mb-2 block text-sm font-medium">New Column Name</label>
                  <Input
                    placeholder="Enter column name"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium">Formula</label>
                  <Input
                    placeholder="e.g., col1 + col2"
                    value={formula}
                    onChange={(e) => setFormula(e.target.value)}
                  />
                  <p className="mt-1 text-xs text-muted-foreground">
                    Use column names and operators: +, -, *, /, **
                  </p>
                </div>
              </>
            )}

            <Button
              onClick={handleApply}
              disabled={!selectedColumn || (selectedOperation === "rename" && !newName)}
              className="w-full"
            >
              Apply Transformation
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
