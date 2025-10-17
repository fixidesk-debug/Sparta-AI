"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { EnhancedConnector } from "@/components/datasources/enhanced-connector";

export default function DataSourcesPage() {
  return (
    <MainLayout>
      <div className="container mx-auto max-w-7xl p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">External Data Sources</h1>
          <p className="text-muted-foreground">
            Connect to databases, cloud warehouses, and other data sources
          </p>
        </div>

        <EnhancedConnector />
      </div>
    </MainLayout>
  );
}
