"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { LayoutDashboard, Plus, Trash2, Edit, Copy, Download, Upload } from "lucide-react";
import { dashboardsApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export function DashboardBuilder() {
  const [dashboards, setDashboards] = useState<any[]>([]);
  const [selectedDashboard, setSelectedDashboard] = useState<any>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newDashboardName, setNewDashboardName] = useState("");
  const [newDashboardDesc, setNewDashboardDesc] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    loadDashboards();
  }, []);

  const loadDashboards = async () => {
    try {
      const response = await dashboardsApi.list(true);
      setDashboards(response.data);
    } catch (error) {
      console.error("Failed to load dashboards:", error);
    }
  };

  const handleCreateDashboard = async () => {
    if (!newDashboardName) {
      toast({
        title: "Name Required",
        description: "Please enter a dashboard name",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await dashboardsApi.create(newDashboardName, newDashboardDesc);
      toast({
        title: "Dashboard Created",
        description: `Dashboard "${newDashboardName}" has been created`,
      });
      setCreateDialogOpen(false);
      setNewDashboardName("");
      setNewDashboardDesc("");
      loadDashboards();
      setSelectedDashboard(response.data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create dashboard",
        variant: "destructive",
      });
    }
  };

  const handleDeleteDashboard = async (dashboardId: number) => {
    if (!confirm("Are you sure you want to delete this dashboard?")) return;

    try {
      await dashboardsApi.delete(dashboardId);
      toast({
        title: "Dashboard Deleted",
        description: "Dashboard has been deleted",
      });
      loadDashboards();
      if (selectedDashboard?.id === dashboardId) {
        setSelectedDashboard(null);
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to delete dashboard",
        variant: "destructive",
      });
    }
  };

  const handleDuplicateDashboard = async (dashboardId: number, name: string) => {
    try {
      await dashboardsApi.duplicate(dashboardId, `${name} (Copy)`);
      toast({
        title: "Dashboard Duplicated",
        description: "Dashboard has been duplicated",
      });
      loadDashboards();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to duplicate dashboard",
        variant: "destructive",
      });
    }
  };

  const handleExportDashboard = async (dashboardId: number) => {
    try {
      const response = await dashboardsApi.export(dashboardId);
      const dataStr = JSON.stringify(response.data, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `dashboard_${dashboardId}.json`;
      link.click();
      URL.revokeObjectURL(url);
      
      toast({
        title: "Dashboard Exported",
        description: "Dashboard configuration has been downloaded",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to export dashboard",
        variant: "destructive",
      });
    }
  };

  const handleAddWidget = async (type: string) => {
    if (!selectedDashboard) return;

    try {
      const widget = {
        type,
        config: {
          title: `New ${type} Widget`,
          position: { x: 0, y: 0, w: 4, h: 4 },
        },
      };

      await dashboardsApi.addWidget(selectedDashboard.id, widget);
      toast({
        title: "Widget Added",
        description: `${type} widget has been added`,
      });
      
      // Reload dashboard
      const response = await dashboardsApi.get(selectedDashboard.id);
      setSelectedDashboard(response.data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add widget",
        variant: "destructive",
      });
    }
  };

  const handleRemoveWidget = async (widgetId: number) => {
    if (!selectedDashboard) return;

    try {
      await dashboardsApi.removeWidget(selectedDashboard.id, widgetId);
      toast({
        title: "Widget Removed",
        description: "Widget has been removed",
      });
      
      // Reload dashboard
      const response = await dashboardsApi.get(selectedDashboard.id);
      setSelectedDashboard(response.data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to remove widget",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <LayoutDashboard className="h-6 w-6" />
          <h2 className="text-2xl font-bold">Dashboard Builder</h2>
        </div>

        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Dashboard
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Dashboard</DialogTitle>
              <DialogDescription>
                Create a custom dashboard to visualize your data
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Dashboard Name</Label>
                <Input
                  id="name"
                  value={newDashboardName}
                  onChange={(e) => setNewDashboardName(e.target.value)}
                  placeholder="My Dashboard"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input
                  id="description"
                  value={newDashboardDesc}
                  onChange={(e) => setNewDashboardDesc(e.target.value)}
                  placeholder="Dashboard description"
                />
              </div>
              <Button onClick={handleCreateDashboard} className="w-full">
                Create Dashboard
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Dashboard List */}
        <Card className="p-4 md:col-span-1">
          <h3 className="font-semibold mb-4">My Dashboards</h3>
          <div className="space-y-2">
            {dashboards.length === 0 ? (
              <p className="text-sm text-muted-foreground">No dashboards yet</p>
            ) : (
              dashboards.map((dashboard) => (
                <Card
                  key={dashboard.id}
                  className={`p-3 cursor-pointer transition-colors ${
                    selectedDashboard?.id === dashboard.id ? 'border-primary bg-primary/5' : 'hover:bg-accent'
                  }`}
                  onClick={() => setSelectedDashboard(dashboard)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">{dashboard.name}</p>
                      {dashboard.description && (
                        <p className="text-xs text-muted-foreground">{dashboard.description}</p>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        {dashboard.widgets?.length || 0} widgets
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDuplicateDashboard(dashboard.id, dashboard.name);
                        }}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExportDashboard(dashboard.id);
                        }}
                      >
                        <Download className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteDashboard(dashboard.id);
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </Card>

        {/* Dashboard Editor */}
        <Card className="p-4 md:col-span-2">
          {selectedDashboard ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">{selectedDashboard.name}</h3>
                  {selectedDashboard.description && (
                    <p className="text-sm text-muted-foreground">{selectedDashboard.description}</p>
                  )}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Add Widget</h4>
                <div className="flex gap-2 flex-wrap">
                  <Button size="sm" variant="outline" onClick={() => handleAddWidget('chart')}>
                    <Plus className="mr-2 h-3 w-3" />
                    Chart
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleAddWidget('table')}>
                    <Plus className="mr-2 h-3 w-3" />
                    Table
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleAddWidget('metric')}>
                    <Plus className="mr-2 h-3 w-3" />
                    Metric
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleAddWidget('text')}>
                    <Plus className="mr-2 h-3 w-3" />
                    Text
                  </Button>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Widgets ({selectedDashboard.widgets?.length || 0})</h4>
                <div className="grid gap-2">
                  {selectedDashboard.widgets?.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No widgets yet. Add some above!</p>
                  ) : (
                    selectedDashboard.widgets?.map((widget: any) => (
                      <Card key={widget.id} className="p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-sm">{widget.config?.title || widget.type}</p>
                            <p className="text-xs text-muted-foreground capitalize">{widget.type} Widget</p>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveWidget(widget.id)}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <LayoutDashboard className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Select a dashboard or create a new one</p>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
