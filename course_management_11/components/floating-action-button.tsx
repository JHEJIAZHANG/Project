"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { PlusIcon, BookIcon, ClipboardIcon, NoteIcon } from "@/components/icons"

interface FloatingActionButtonProps {
  onAddCourse: () => void
  onAddAssignment: () => void
  onAddNote: () => void
  onAddExam: () => void // 新增考試回調函數
}

export function FloatingActionButton({
  onAddCourse,
  onAddAssignment,
  onAddNote,
  onAddExam,
}: FloatingActionButtonProps) {
  const [isOpen, setIsOpen] = useState(false)

  const actions = [
    {
      label: "新增課程",
      icon: BookIcon,
      onClick: () => {
        onAddCourse()
        setIsOpen(false)
      },
      color: "bg-primary text-primary-foreground",
    },
    {
      label: "新增作業",
      icon: ClipboardIcon,
      onClick: () => {
        onAddAssignment()
        setIsOpen(false)
      },
      color: "bg-green-600 text-white",
    },
    {
      label: "新增考試",
      icon: ClipboardIcon,
      onClick: () => {
        onAddExam()
        setIsOpen(false)
      },
      color: "bg-amber-600 text-white",
    },
    {
      label: "新增筆記",
      icon: NoteIcon,
      onClick: () => {
        onAddNote()
        setIsOpen(false)
      },
      color: "bg-blue-600 text-white",
    },
  ]

  return (
    /* hide floating action button on desktop with lg:hidden wrapper */
    <div className="lg:hidden">
      {/* Backdrop */}
      {isOpen && <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setIsOpen(false)} />}

      {/* Action Menu */}
      {isOpen && (
        <div className="fixed bottom-32 right-4 z-50">
          <Card className="bg-white border shadow-lg p-2 min-w-[110px]">
            <div className="space-y-2">
              {actions.map((action, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start gap-2 h-10 px-3"
                  onClick={action.onClick}
                >
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center ${action.color}`}>
                    <action.icon className="w-3 h-3" />
                  </div>
                  <span className="text-sm">{action.label}</span>
                </Button>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Main FAB */}
      <Button
        size="lg"
        className={`fixed bottom-20 right-4 z-50 w-14 h-14 rounded-full shadow-lg transition-transform ${
          isOpen ? "rotate-45" : ""
        }`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <PlusIcon className="w-6 h-6" />
      </Button>
    </div>
  )
}
