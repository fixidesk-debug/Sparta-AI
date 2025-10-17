"use client";

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface ChartRendererProps {
  data: any[];
  config: {
    type: string;
    xColumn: string;
    yColumn: string;
    title?: string;
    color?: string;
  };
}

const COLORS = ['#8B9BF8', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6', '#06B6D4'];

export function ChartRenderer({ data, config }: ChartRendererProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-muted-foreground">
        No data to display
      </div>
    );
  }

  const { type, xColumn, yColumn, title, color = COLORS[0] } = config;

  // Prepare data based on chart type
  const prepareData = () => {
    if (type === "pie") {
      // For pie charts, count occurrences of xColumn values
      const counts = data.reduce((acc, item) => {
        const key = item[xColumn];
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      }, {});
      
      return Object.entries(counts).map(([name, value]) => ({ name, value }));
    }
    
    return data.map(item => ({
      [xColumn]: item[xColumn],
      [yColumn]: item[yColumn],
      ...item
    }));
  };

  const chartData = prepareData();

  const renderChart = () => {
    switch (type) {
      case "bar":
        return (
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xColumn} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey={yColumn} fill={color} />
          </BarChart>
        );

      case "line":
        return (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xColumn} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey={yColumn} stroke={color} strokeWidth={2} />
          </LineChart>
        );

      case "scatter":
        return (
          <ScatterChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xColumn} />
            <YAxis dataKey={yColumn} />
            <Tooltip />
            <Scatter fill={color} />
          </ScatterChart>
        );

      case "pie":
        return (
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill={color}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        );

      default:
        return (
          <div className="flex h-64 items-center justify-center text-muted-foreground">
            Unsupported chart type: {type}
          </div>
        );
    }
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="mb-4 text-center text-lg font-semibold">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={400}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
}
