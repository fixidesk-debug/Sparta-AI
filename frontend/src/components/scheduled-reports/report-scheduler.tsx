"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Calendar, Clock, Mail, Play, Trash2 } from "lucide-react";
import { reportsApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export function ReportScheduler({ fileId }: { fileId?: number }) {
  const [schedules, setSchedules] = useState<any[]>([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSchedule, setNewSchedule] = useState({
    name: "",
    description: "",
    analysis_id: fileId || 0,
    schedule_type: "daily",
    schedule_time: "09:00",
    recipients: "",
    format: "pdf",
  });
  const { toast } = useToast();

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      const response = await reportsApi.listSchedules();
      setSchedules(response.data);
    } catch (error) {
      console.error("Failed to load schedules:", error);
    }
  };

  const handleCreateSchedule = async () => {
    if (!newSchedule.name || !newSchedule.recipients) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    try {
      await reportsApi.createSchedule(newSchedule);
      toast({
        title: "Schedule Created",
        description: `Report will be sent ${newSchedule.schedule_type} at ${newSchedule.schedule_time}`,
      });
      setCreateDialogOpen(false);
      setNewSchedule({
        name: "",
        description: "",
        analysis_id: fileId || 0,
        schedule_type: "daily",
        schedule_time: "09:00",
        recipients: "",
        format: "pdf",
      });
      loadSchedules();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create schedule",
        variant: "destructive",
      });
    }
  };

  const handleRunNow = async (scheduleId: number) => {
    try {
      await reportsApi.runNow(scheduleId);
      toast({
        title: "Report Sent",
        description: "Report has been generated and sent",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to run report",
        variant: "destructive",
      });
    }
  };

  const handleDeleteSchedule = async (scheduleId: number) => {
    if (!confirm("Are you sure you want to delete this schedule?")) return;

    try {
      await reportsApi.deleteSchedule(scheduleId);
      toast({
        title: "Schedule Deleted",
        description: "Schedule has been deleted",
      });
      loadSchedules();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to delete schedule",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="h-6 w-6" />
          <h2 className="text-2xl font-bold">Scheduled Reports</h2>
        </div>

        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Clock className="mr-2 h-4 w-4" />
              New Schedule
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Schedule Report</DialogTitle>
              <DialogDescription>
                Set up automatic report delivery via email
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Schedule Name</Label>
                <Input
                  id="name"
                  value={newSchedule.name}
                  onChange={(e) => setNewSchedule({ ...newSchedule, name: e.target.value })}
                  placeholder="Weekly Sales Report"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input
                  id="description"
                  value={newSchedule.description}
                  onChange={(e) => setNewSchedule({ ...newSchedule, description: e.target.value })}
                  placeholder="Report description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="schedule_type">Frequency</Label>
                  <Select
                    value={newSchedule.schedule_type}
                    onValueChange={(value) => setNewSchedule({ ...newSchedule, schedule_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="schedule_time">Time</Label>
                  <Input
                    id="schedule_time"
                    type="time"
                    value={newSchedule.schedule_time}
                    onChange={(e) => setNewSchedule({ ...newSchedule, schedule_time: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="format">Report Format</Label>
                <Select
                  value={newSchedule.format}
                  onValueChange={(value) => setNewSchedule({ ...newSchedule, format: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pdf">PDF</SelectItem>
                    <SelectItem value="excel">Excel</SelectItem>
                    <SelectItem value="html">HTML</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="recipients">Recipients (comma-separated emails)</Label>
                <Input
                  id="recipients"
                  value={newSchedule.recipients}
                  onChange={(e) => setNewSchedule({ ...newSchedule, recipients: e.target.value })}
                  placeholder="email1@example.com, email2@example.com"
                />
              </div>

              <Button onClick={handleCreateSchedule} className="w-full">
                Create Schedule
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4">
        {schedules.length === 0 ? (
          <Card className="p-8">
            <div className="text-center">
              <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No scheduled reports yet</p>
              <p className="text-sm text-muted-foreground mt-2">
                Create a schedule to automatically send reports via email
              </p>
            </div>
          </Card>
        ) : (
          schedules.map((schedule) => (
            <Card key={schedule.id} className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold">{schedule.name}</h3>
                    <span className="text-xs px-2 py-1 rounded bg-primary/10 text-primary capitalize">
                      {schedule.schedule_type}
                    </span>
                  </div>
                  
                  {schedule.description && (
                    <p className="text-sm text-muted-foreground mb-2">{schedule.description}</p>
                  )}

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>{schedule.schedule_time}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <span className="truncate">{schedule.recipients}</span>
                    </div>
                  </div>

                  <div className="mt-2 text-xs text-muted-foreground">
                    Format: {schedule.format?.toUpperCase()} • 
                    {schedule.last_run && ` Last run: ${new Date(schedule.last_run).toLocaleDateString()}`}
                    {!schedule.last_run && " Never run"}
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRunNow(schedule.id)}
                    title="Run now"
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeleteSchedule(schedule.id)}
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
