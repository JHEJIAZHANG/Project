"use client"

import { Button } from "@/components/ui/button"
import { ExclamationIcon, ClipboardIcon } from "@/components/icons"

interface TaskTypeToggleProps {
  activeType: "assignment" | "exam"
  onTypeChange: (type: "assignment" | "exam") => void
}

export function TaskTypeToggle({ activeType, onTypeChange }: TaskTypeToggleProps) {
  return (
    <div className="flex bg-muted rounded-lg p-1 mb-4">
      <Button
        variant={activeType === "assignment" ? "default" : "ghost"}
        size="sm"
        onClick={() => onTypeChange("assignment")}
        className="flex-1 flex items-center gap-2"
      >
        <ExclamationIcon className="w-4 h-4" />
        作業
      </Button>
      <Button
        variant={activeType === "exam" ? "default" : "ghost"}
        size="sm"
        onClick={() => onTypeChange("exam")}
        className="flex-1 flex items-center gap-2"
      >
        <ClipboardIcon className="w-4 h-4" />
        考試
      </Button>
    </div>
  )
}
