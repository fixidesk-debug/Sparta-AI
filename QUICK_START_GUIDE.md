# 🚀 Quick Start Guide - Using the New Features

## Step-by-Step Integration

### 1. Add Features to Your Data Analysis Page

**File:** `frontend/src/app/analysis/[id]/page.tsx` (or similar)

```tsx
"use client";

import { useState } from "react";
import { UndoRedoToolbar } from "@/components/history/undo-redo-toolbar";
import { VersionHistory } from "@/components/versions/version-history";
import { EnhancedExportDialog } from "@/components/export/enhanced-export-dialog";
import { AdvancedCharts } from "@/components/charts/advanced-charts";
import { Button } from "@/components/ui/button";
import { Download, History, GitBranch } from "lucide-react";

export default function AnalysisPage({ params }: { params: { id: string } }) {
  const fileId = parseInt(params.id);
  const [exportOpen, setExportOpen] = useState(false);
  const [versionOpen, setVersionOpen] = useState(false);
  const [columns, setColumns] = useState<string[]>([]);

  const refreshData = () => {
    // Reload your data here
    console.log("Refreshing data...");
  };

  return (
    <div className="container mx-auto p-6">
      {/* Top Toolbar */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Data Analysis</h1>
        
        <div className="flex gap-2">
          {/* Undo/Redo */}
          <UndoRedoToolbar fileId={fileId} onUndo={refreshData} />
          
          {/* Export Button */}
          <Button onClick={() => setExportOpen(true)}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          
          {/* Version History Button */}
          <Button variant="outline" onClick={() => setVersionOpen(true)}>
            <GitBranch className="mr-2 h-4 w-4" />
            Versions
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Data View (2/3 width) */}
        <div className="lg:col-span-2">
          {/* Your existing data table/charts here */}
        </div>

        {/* Sidebar (1/3 width) */}
        {versionOpen && (
          <div className="lg:col-span-1">
            <VersionHistory fileId={fileId} onRestore={refreshData} />
          </div>
        )}
      </div>

      {/* Advanced Charts Section */}
      <div className="mt-6">
        <AdvancedCharts fileId={fileId} columns={columns} />
      </div>

      {/* Export Dialog */}
      <EnhancedExportDialog
        fileId={fileId}
        open={exportOpen}
        onOpenChange={setExportOpen}
      />
    </div>
  );
}
```

### 2. Create a Dashboards Page

**File:** `frontend/src/app/dashboards/page.tsx`

```tsx
import { DashboardBuilder } from "@/components/dashboards/dashboard-builder";

export default function DashboardsPage() {
  return (
    <div className="container mx-auto p-6">
      <DashboardBuilder />
    </div>
  );
}
```

### 3. Create a Data Sources Page

**File:** `frontend/src/app/data-sources/page.tsx`

```tsx
import { DataSourceConnector } from "@/components/datasources/datasource-connector";

export default function DataSourcesPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Data Source Connectors</h1>
      <DataSourceConnector />
    </div>
  );
}
```

### 4. Create a Scheduled Reports Page

**File:** `frontend/src/app/reports/page.tsx`

```tsx
import { ReportScheduler } from "@/components/scheduled-reports/report-scheduler";

export default function ReportsPage() {
  return (
    <div className="container mx-auto p-6">
      <ReportScheduler />
    </div>
  );
}
```

### 5. Update Your Navigation

**File:** `frontend/src/components/layout/sidebar.tsx` (or navigation component)

```tsx
import { LayoutDashboard, Database, Calendar, FileText } from "lucide-react";

const navigation = [
  // ... existing items
  {
    name: "Dashboards",
    href: "/dashboards",
    icon: LayoutDashboard,
  },
  {
    name: "Data Sources",
    href: "/data-sources",
    icon: Database,
  },
  {
    name: "Scheduled Reports",
    href: "/reports",
    icon: Calendar,
  },
];
```

---

## 🎯 Common Use Cases

### Use Case 1: Export Analysis Results

```tsx
import { useState } from "react";
import { EnhancedExportDialog } from "@/components/export/enhanced-export-dialog";
import { Button } from "@/components/ui/button";

function MyComponent({ fileId }: { fileId: number }) {
  const [exportOpen, setExportOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setExportOpen(true)}>
        Export Results
      </Button>
      
      <EnhancedExportDialog
        fileId={fileId}
        open={exportOpen}
        onOpenChange={setExportOpen}
      />
    </>
  );
}
```

### Use Case 2: Add Undo/Redo to Data Transformations

```tsx
import { UndoRedoToolbar } from "@/components/history/undo-redo-toolbar";
import { historyApi } from "@/lib/api";

function DataTransformationPanel({ fileId }: { fileId: number }) {
  const handleTransform = async (operation: string, params: any) => {
    // Perform transformation
    await transformationsApi.renameColumn(fileId, oldName, newName);
    
    // Record for undo/redo
    await historyApi.recordOperation(fileId, "rename_column", {
      old_name: oldName,
      new_name: newName,
    });
  };

  return (
    <div>
      <UndoRedoToolbar 
        fileId={fileId} 
        onUndo={() => {
          // Refresh your data
        }} 
      />
      {/* Your transformation UI */}
    </div>
  );
}
```

### Use Case 3: Create Version Before Major Changes

```tsx
import { versionsApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

function MyComponent({ fileId }: { fileId: number }) {
  const { toast } = useToast();

  const handleMajorChange = async () => {
    // Create version first
    await versionsApi.createVersion(fileId, "Before bulk delete");
    
    toast({
      title: "Version Created",
      description: "Safe to proceed with changes",
    });
    
    // Now perform the major change
    // ...
  };

  return <Button onClick={handleMajorChange}>Delete All Rows</Button>;
}
```

### Use Case 4: Schedule Weekly Reports

```tsx
import { reportsApi } from "@/lib/api";

async function scheduleWeeklyReport(fileId: number) {
  await reportsApi.createSchedule({
    name: "Weekly Sales Report",
    description: "Automated weekly sales analysis",
    analysis_id: fileId,
    schedule_type: "weekly",
    schedule_time: "09:00",
    recipients: "team@company.com, manager@company.com",
    format: "pdf",
  });
}
```

### Use Case 5: Generate Advanced Visualizations

```tsx
import { advancedChartsApi } from "@/lib/api";

async function generateCorrelationHeatmap(fileId: number) {
  const heatmap = await advancedChartsApi.generateHeatmap(
    fileId,
    ["sales", "profit", "quantity"],
    "pearson"
  );
  
  // Use heatmap.data to render visualization
  console.log(heatmap);
}
```

### Use Case 6: Connect to External Database

```tsx
import { dataSourcesApi } from "@/lib/api";

async function connectToPostgreSQL() {
  // Test connection
  const testResult = await dataSourcesApi.testConnection({
    name: "Production DB",
    type: "postgresql",
    config: {
      host: "db.example.com",
      port: 5432,
      database: "analytics",
      username: "analyst",
      password: "secure_password",
    },
  });

  if (testResult.data.success) {
    // List tables
    const tables = await dataSourcesApi.listTables(config);
    console.log("Available tables:", tables.data.tables);
    
    // Query data
    const result = await dataSourcesApi.query(config, {
      query: "SELECT * FROM sales WHERE date > '2024-01-01'",
      limit: 1000,
    });
    
    console.log("Data:", result.data);
  }
}
```

---

## 🔧 Configuration

### Environment Variables

Add to your `.env.local`:

```env
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Email Configuration (for scheduled reports)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Backend Configuration

Update `backend/app/core/config.py` if needed:

```python
class Settings(BaseSettings):
    # ... existing settings
    
    # Email settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    VERSION_DIR: str = "uploads/versions"
    BACKUP_DIR: str = "uploads/backups"
```

---

## 📝 Tips & Best Practices

### 1. Always Create Versions Before Major Changes
```tsx
// Good practice
await versionsApi.createVersion(fileId, "Before bulk operations");
await performBulkOperation();
```

### 2. Record Operations for Undo/Redo
```tsx
// After any transformation
await historyApi.recordOperation(fileId, operationType, parameters);
```

### 3. Handle Errors Gracefully
```tsx
try {
  await exportApi.exportPDF(fileId);
} catch (error: any) {
  toast({
    title: "Export Failed",
    description: error.response?.data?.detail || "Unknown error",
    variant: "destructive",
  });
}
```

### 4. Show Loading States
```tsx
const [loading, setLoading] = useState(false);

const handleExport = async () => {
  setLoading(true);
  try {
    await exportApi.exportExcel(fileId);
  } finally {
    setLoading(false);
  }
};
```

### 5. Refresh Data After Operations
```tsx
const refreshData = async () => {
  // Reload your data
  const data = await previewApi.getFileData(fileId);
  setData(data);
};

<UndoRedoToolbar fileId={fileId} onUndo={refreshData} />
```

---

## 🎨 Styling

All components use shadcn/ui and are fully styled. They will automatically match your theme.

To customize:

```tsx
// Example: Custom export dialog
<EnhancedExportDialog
  fileId={fileId}
  open={open}
  onOpenChange={setOpen}
  className="custom-class" // Add custom classes if needed
/>
```

---

## 🐛 Troubleshooting

### Issue: Export not downloading

**Solution:** Check that the backend is running and the file exists:
```tsx
// Verify file exists first
const file = await filesApi.get(fileId);
if (file) {
  await exportApi.exportPDF(fileId);
}
```

### Issue: Undo/Redo not working

**Solution:** Make sure operations are being recorded:
```tsx
// After each transformation
await historyApi.recordOperation(fileId, "operation_type", params);
```

### Issue: Database connection failing

**Solution:** Test connection first:
```tsx
const result = await dataSourcesApi.testConnection(config);
if (!result.data.success) {
  console.error("Connection failed:", result.data.message);
}
```

---

## ✅ Checklist for Integration

- [ ] Import components in your pages
- [ ] Add navigation links
- [ ] Test export functionality
- [ ] Test undo/redo
- [ ] Test version control
- [ ] Create a dashboard
- [ ] Connect to a database
- [ ] Schedule a report
- [ ] Generate advanced charts
- [ ] Verify all features work

---

## 🎉 You're Ready!

All features are now available in your SPARTA AI platform. Start using them in your pages!

**Need Help?**
- Check `FEATURES_IMPLEMENTED.md` for detailed API documentation
- Check `FRONTEND_INTEGRATION.md` for component details
- Check `COMPLETE_IMPLEMENTATION_SUMMARY.md` for overview

**Happy Coding! 🚀**
