"use client";

import { useEffect, useState } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { 
  TrendingUp, 
  Users, 
  BarChart3, 
  Target,
  Clock,
  Grid3x3
} from "lucide-react";
import { useRouter } from "next/navigation";

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  config: any;
}

const categoryIcons: Record<string, any> = {
  business: TrendingUp,
  marketing: Users,
  forecasting: Clock,
  experimentation: Target,
  analytics: BarChart3,
  statistics: Grid3x3,
};

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    loadTemplates();
  }, [selectedCategory]);

  const loadTemplates = async () => {
    try {
      const url = selectedCategory 
        ? `/templates?category=${selectedCategory}`
        : "/templates";
      const response = await api.get(url);
      setTemplates(response.data.templates);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load templates",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: "business", name: "Business", color: "bg-blue-500" },
    { id: "marketing", name: "Marketing", color: "bg-purple-500" },
    { id: "forecasting", name: "Forecasting", color: "bg-green-500" },
    { id: "experimentation", name: "A/B Testing", color: "bg-orange-500" },
    { id: "analytics", name: "Analytics", color: "bg-pink-500" },
    { id: "statistics", name: "Statistics", color: "bg-indigo-500" },
  ];

  const handleApplyTemplate = async (templateId: string) => {
    // Navigate to analytics page with template
    router.push(`/analytics?template=${templateId}`);
  };

  return (
    <MainLayout>
      <div className="container mx-auto max-w-7xl p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Analysis Templates</h1>
          <p className="text-muted-foreground">
            Pre-built templates to jumpstart your analysis
          </p>
        </div>

        <div className="mb-6 flex flex-wrap gap-2">
          <Button
            variant={selectedCategory === null ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedCategory(null)}
          >
            All Templates
          </Button>
          {categories.map((category) => (
            <Button
              key={category.id}
              variant={selectedCategory === category.id ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category.id)}
            >
              {category.name}
            </Button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">Loading templates...</div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => {
              const Icon = categoryIcons[template.category] || BarChart3;
              return (
                <Card key={template.id} className="p-6 hover:shadow-lg transition-shadow">
                  <div className="mb-4 flex items-start justify-between">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <Badge variant="secondary">{template.category}</Badge>
                  </div>
                  <h3 className="mb-2 text-lg font-semibold">{template.name}</h3>
                  <p className="mb-4 text-sm text-muted-foreground">
                    {template.description}
                  </p>
                  <Button
                    className="w-full"
                    onClick={() => handleApplyTemplate(template.id)}
                  >
                    Use Template
                  </Button>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
