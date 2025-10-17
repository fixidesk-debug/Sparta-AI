"use client";

import { Sparkles, Upload, MessageSquare, BarChart3, Zap } from "lucide-react";

export function WelcomeScreen() {
  const features = [
    {
      icon: Upload,
      title: "Upload Data",
      description: "CSV, Excel, JSON files supported",
    },
    {
      icon: MessageSquare,
      title: "Natural Language",
      description: "Ask questions in plain English",
    },
    {
      icon: BarChart3,
      title: "Visualizations",
      description: "Auto-generated charts and graphs",
    },
    {
      icon: Zap,
      title: "AI-Powered",
      description: "Advanced analysis with GPT-4",
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-8 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-primary/60">
        <Sparkles className="h-10 w-10 text-primary-foreground" />
      </div>
      <h1 className="mb-3 text-4xl font-bold">Welcome to SPARTA AI</h1>
      <p className="mb-12 max-w-md text-lg text-muted-foreground">
        Your intelligent data analysis companion. Upload data and start asking questions.
      </p>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((feature) => (
          <div
            key={feature.title}
            className="flex flex-col items-center rounded-lg border border-border bg-card p-6 transition-colors hover:bg-accent"
          >
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <feature.icon className="h-6 w-6 text-primary" />
            </div>
            <h3 className="mb-1 font-semibold">{feature.title}</h3>
            <p className="text-sm text-muted-foreground">{feature.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
