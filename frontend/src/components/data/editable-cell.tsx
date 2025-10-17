"use client";

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";

interface EditableCellProps {
  value: any;
  rowIndex: number;
  columnId: string;
  onUpdate: (rowIndex: number, columnId: string, value: any) => void;
}

export function EditableCell({ value, rowIndex, columnId, onUpdate }: EditableCellProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleDoubleClick = () => {
    setIsEditing(true);
  };

  const handleBlur = () => {
    setIsEditing(false);
    if (editValue !== value) {
      onUpdate(rowIndex, columnId, editValue);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      setIsEditing(false);
      if (editValue !== value) {
        onUpdate(rowIndex, columnId, editValue);
      }
    } else if (e.key === "Escape") {
      setEditValue(value);
      setIsEditing(false);
    }
  };

  if (isEditing) {
    return (
      <Input
        ref={inputRef}
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        className="h-8 px-2 py-1"
      />
    );
  }

  return (
    <div
      onDoubleClick={handleDoubleClick}
      className="cursor-pointer hover:bg-accent/50 px-2 py-1 rounded"
      title="Double-click to edit"
    >
      {value === null || value === undefined ? (
        <span className="text-muted-foreground">—</span>
      ) : (
        String(value)
      )}
    </div>
  );
}
