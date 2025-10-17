"use client";

import { useState } from "react";
import { 
  MessageSquare, 
  FileText, 
  BarChart3, 
  Settings, 
  Plus,
  ChevronLeft,
  Trash2,
  BookOpen,
  Brain
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const [conversations] = useState<any[]>([]);

  const navItems = [
    { href: "/", icon: MessageSquare, label: "Chat" },
    { href: "/files", icon: FileText, label: "Files" },
    { href: "/analytics", icon: BarChart3, label: "Analytics" },
    { href: "/templates", icon: BookOpen, label: "Templates" },
    { href: "/notebooks", icon: BookOpen, label: "Notebooks" },
    { href: "/models", icon: Brain, label: "ML Models" },
    { href: "/reports", icon: Settings, label: "Reports" },
    { href: "/settings", icon: Settings, label: "Settings" },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-border bg-card transition-transform duration-200 lg:relative lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-14 items-center justify-between border-b border-border px-4">
          <h2 className="text-sm font-semibold text-muted-foreground">Conversations</h2>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 lg:hidden"
            onClick={onToggle}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-3">
          <Link href="/">
            <Button className="w-full justify-start gap-2" size="sm">
              <Plus className="h-4 w-4" />
              New Chat
            </Button>
          </Link>
        </div>

        <ScrollArea className="flex-1 px-3">
          <div className="space-y-1">
            {conversations.length === 0 ? (
              <div className="px-3 py-8 text-center text-sm text-muted-foreground">
                No conversations yet
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className="group flex items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-accent cursor-pointer"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <MessageSquare className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <p className="truncate font-medium">{conv.title}</p>
                      <p className="text-xs text-muted-foreground">{conv.date}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        <div className="border-t border-border p-3">
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link key={item.href} href={item.href}>
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    className="w-full justify-start gap-2"
                    size="sm"
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Button>
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}
