"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Copy, Check, Globe, Lock, Users } from "lucide-react";

interface ShareDialogProps {
  analysisId: number;
  onClose: () => void;
}

export function ShareDialog({ analysisId, onClose }: ShareDialogProps) {
  const [shareType, setShareType] = useState("private");
  const [shareUrl, setShareUrl] = useState("");
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const shareTypes = [
    { id: "public", name: "Public", icon: Globe, description: "Anyone with the link" },
    { id: "private", name: "Private", icon: Lock, description: "Only invited people" },
    { id: "team", name: "Team", icon: Users, description: "Your team members" },
  ];

  const handleCreateShare = async () => {
    try {
      const response = await api.post("/sharing/share", {
        analysis_id: analysisId,
        share_type: shareType,
        permissions: ["view"],
      });

      const fullUrl = `${window.location.origin}${response.data.share_url}`;
      setShareUrl(fullUrl);

      toast({
        title: "Success",
        description: "Share link created successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to create share link",
        variant: "destructive",
      });
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    
    toast({
      title: "Copied",
      description: "Link copied to clipboard",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-3 text-lg font-semibold">Share Analysis</h3>
        <p className="text-sm text-muted-foreground">
          Choose who can access this analysis
        </p>
      </div>

      <div className="grid gap-3">
        {shareTypes.map((type) => {
          const Icon = type.icon;
          return (
            <Card
              key={type.id}
              className={`cursor-pointer p-4 transition-colors hover:bg-accent ${
                shareType === type.id ? "border-primary bg-primary/5" : ""
              }`}
              onClick={() => setShareType(type.id)}
            >
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-sm">{type.name}</h4>
                    {shareType === type.id && (
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

      {!shareUrl ? (
        <Button onClick={handleCreateShare} className="w-full">
          Create Share Link
        </Button>
      ) : (
        <div className="space-y-3">
          <div className="flex gap-2">
            <Input value={shareUrl} readOnly className="flex-1" />
            <Button onClick={handleCopy} variant="outline">
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Anyone with this link can view your analysis
          </p>
        </div>
      )}

      <Button variant="outline" onClick={onClose} className="w-full">
        Close
      </Button>
    </div>
  );
}
