"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { PlusIcon, BookIcon, ClipboardIcon, DocumentIcon } from "@/components/icons"

interface QuickActionsProps {
  onAddCourse: () => void
  onAddAssignment: () => void
  onAddNote: () => void
  onViewCourses: () => void
}

export function QuickActions({ onAddCourse, onAddAssignment, onAddNote, onViewCourses }: QuickActionsProps) {
  const actions = [
    {
      label: "新增課程",
      icon: BookIcon,
      onClick: onAddCourse,
      variant: "default" as const,
    },
    {
      label: "新增作業",
      icon: ClipboardIcon,
      onClick: onAddAssignment,
      variant: "outline" as const,
    },
    {
      label: "新增筆記",
      icon: DocumentIcon,
      onClick: onAddNote,
      variant: "outline" as const,
    },
    {
      label: "查看課程",
      icon: BookIcon,
      onClick: onViewCourses,
      variant: "outline" as const,
    },
  ]

  return (
    <Card className="p-4 mb-4">
      <h2 className="font-semibold text-foreground mb-3 flex items-center gap-2">
        <PlusIcon className="w-5 h-5 text-primary" />
        快速操作
      </h2>
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action, index) => {
          const Icon = action.icon
          return (
            <Button
              key={index}
              variant={action.variant}
              size="sm"
              onClick={action.onClick}
              className="flex items-center gap-2 h-auto py-3"
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm">{action.label}</span>
            </Button>
          )
        })}
      </div>
    </Card>
  )
}
