"use client";

import { useEffect, useState } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { reportsApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Calendar, Clock, Mail, Plus, Play, Trash2 } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface Schedule {
  id: number;
  name: string;
  description: string;
  schedule_type: string;
  schedule_time: string;
  recipients: string;
  format: string;
  is_active: boolean;
  last_run: string | null;
}

export default function ReportsPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      const response = await reportsApi.listSchedules();
      setSchedules(response.data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load schedules",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRunNow = async (scheduleId: number) => {
    try {
      await reportsApi.runNow(scheduleId);
      toast({
        title: "Success",
        description: "Report generation started",
      });
      loadSchedules();
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to run report",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (scheduleId: number) => {
    if (!confirm("Are you sure you want to delete this schedule?")) return;

    try {
      await reportsApi.deleteSchedule(scheduleId);
      toast({
        title: "Success",
        description: "Schedule deleted successfully",
      });
      loadSchedules();
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to delete schedule",
        variant: "destructive",
      });
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto max-w-6xl p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Scheduled Reports</h1>
            <p className="text-muted-foreground">
              Automate your analysis reports
            </p>
          </div>
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Schedule
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading schedules...</div>
        ) : schedules.length === 0 ? (
          <Card className="p-12 text-center">
            <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No scheduled reports</h3>
            <p className="text-muted-foreground mb-4">
              Create your first scheduled report to automate analysis
            </p>
            <Button onClick={() => setShowCreate(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Schedule
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4">
            {schedules.map((schedule) => (
              <Card key={schedule.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{schedule.name}</h3>
                      <Badge variant={schedule.is_active ? "default" : "secondary"}>
                        {schedule.is_active ? "Active" : "Inactive"}
                      </Badge>
                      <Badge variant="outline">{schedule.schedule_type}</Badge>
                    </div>
                    {schedule.description && (
                      <p className="text-sm text-muted-foreground mb-3">
                        {schedule.description}
                      </p>
                    )}
                    <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        {schedule.schedule_time}
                      </div>
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        {schedule.recipients.split(",").length} recipient(s)
                      </div>
                      {schedule.last_run && (
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          Last run: {formatDate(schedule.last_run)}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleRunNow(schedule.id)}
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(schedule.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {showCreate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <Card className="w-full max-w-2xl p-6">
              <h2 className="mb-4 text-xl font-semibold">Create Scheduled Report</h2>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium">Report Name</label>
                  <Input placeholder="Weekly Sales Report" />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium">Description</label>
                  <Input placeholder="Automated weekly sales analysis" />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium">Schedule Type</label>
                    <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                      <option>Daily</option>
                      <option>Weekly</option>
                      <option>Monthly</option>
                    </select>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Time</label>
                    <Input type="time" defaultValue="09:00" />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium">Recipients (comma-separated)</label>
                  <Input placeholder="email1@example.com, email2@example.com" />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium">Format</label>
                  <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option>PDF</option>
                    <option>HTML</option>
                    <option>CSV</option>
                  </select>
                </div>
                <div className="flex gap-3">
                  <Button className="flex-1">Create Schedule</Button>
                  <Button variant="outline" onClick={() => setShowCreate(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
