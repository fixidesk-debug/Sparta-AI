"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Play, Save, Clock, Code } from "lucide-react";

interface SQLQueryEditorProps {
  fileId: number | null;
  onResult: (result: any) => void;
}

const QUERY_TEMPLATES = [
  {
    name: "Select All",
    query: "SELECT * FROM data LIMIT 100",
  },
  {
    name: "Group By",
    query: "SELECT column_name, COUNT(*) as count\nFROM data\nGROUP BY column_name\nORDER BY count DESC",
  },
  {
    name: "Filter",
    query: "SELECT *\nFROM data\nWHERE column_name > value",
  },
  {
    name: "Aggregate",
    query: "SELECT \n  AVG(column1) as avg_value,\n  SUM(column2) as total,\n  COUNT(*) as count\nFROM data",
  },
];

export function SQLQueryEditor({ fileId, onResult }: SQLQueryEditorProps) {
  const [query, setQuery] = useState("SELECT * FROM data LIMIT 100");
  const [history, setHistory] = useState<string[]>([]);
  const [executing, setExecuting] = useState(false);

  const handleExecute = async () => {
    if (!query.trim() || !fileId || executing) return;

    setExecuting(true);
    try {
      const { sqlApi } = await import("@/lib/api");
      const response = await sqlApi.execute(fileId, query);
      
      onResult({
        success: true,
        data: response.data.data,
        columns: response.data.columns,
        rowCount: response.data.row_count
      });
      
      setHistory((prev) => [query, ...prev.slice(0, 9)]);
    } catch (error: any) {
      onResult({
        success: false,
        error: error.response?.data?.detail || "Query execution failed"
      });
    } finally {
      setExecuting(false);
    }
  };

  const handleTemplateClick = (templateQuery: string) => {
    setQuery(templateQuery);
  };

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">SQL Query</h3>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Save className="mr-2 h-4 w-4" />
              Save
            </Button>
            <Button size="sm" onClick={handleExecute} disabled={!fileId || executing}>
              <Play className="mr-2 h-4 w-4" />
              {executing ? "Running..." : "Run Query"}
            </Button>
          </div>
        </div>

        <Textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter SQL query..."
          className="font-mono text-sm min-h-[150px]"
        />

        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-sm text-muted-foreground">Templates:</span>
          {QUERY_TEMPLATES.map((template) => (
            <Badge
              key={template.name}
              variant="secondary"
              className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
              onClick={() => handleTemplateClick(template.query)}
            >
              {template.name}
            </Badge>
          ))}
        </div>
      </Card>

      {history.length > 0 && (
        <Card className="p-4">
          <div className="mb-3 flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <h4 className="text-sm font-medium">Query History</h4>
          </div>
          <div className="space-y-2">
            {history.map((q, i) => (
              <div
                key={i}
                className="cursor-pointer rounded-lg bg-muted p-2 text-sm font-mono hover:bg-accent"
                onClick={() => setQuery(q)}
              >
                {q.length > 100 ? q.substring(0, 100) + "..." : q}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
