"use client"

import type React from "react"
import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { CheckIcon, ClockIcon, ExclamationIcon } from "@/components/icons"
import type { Assignment, Course } from "@/types/course"
import { getDaysDifferenceTaiwan, isTodayTaiwan, isTomorrowTaiwan } from "@/lib/taiwan-time"

interface AssignmentCardProps {
  assignment: Assignment
  course?: Course
  onStatusChange: (id: string, status: Assignment["status"]) => void
  onEdit?: () => void
  onDelete?: () => void
  onViewDetail?: () => void
}

export function AssignmentCard({
  assignment,
  course,
  onStatusChange,
  onEdit,
  onDelete,
  onViewDetail,
}: AssignmentCardProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const getStatusColor = (status: Assignment["status"], dueDate: Date) => {
    if (status === "completed") {
      return "text-green-700 bg-green-100 border-green-300 dark:text-green-300 dark:bg-green-900/30 dark:border-green-700/50"
    }

    const daysUntilDue = getDaysDifferenceTaiwan(new Date(), dueDate)

    if (daysUntilDue <= 0) {
      return "text-red-700 bg-red-100 border-red-300 dark:text-red-300 dark:bg-red-900/30 dark:border-red-700/50"
    }
    if (daysUntilDue <= 2) {
      return "text-orange-700 bg-orange-100 border-orange-300 dark:text-orange-300 dark:bg-orange-900/30 dark:border-orange-700/50"
    }
    if (daysUntilDue <= 7) {
      return "text-yellow-700 bg-yellow-100 border-yellow-300 dark:text-yellow-300 dark:bg-yellow-900/30 dark:border-yellow-700/50"
    }
    return "text-blue-700 bg-blue-100 border-blue-300 dark:text-blue-300 dark:bg-blue-900/30 dark:border-blue-700/50"
  }

  const getStatusIcon = (status: Assignment["status"]) => {
    switch (status) {
      case "completed":
        return CheckIcon
      case "overdue":
        return ExclamationIcon
      default:
        return ClockIcon
    }
  }

  const getStatusText = (status: Assignment["status"]) => {
    switch (status) {
      case "completed":
        return "已完成"
      case "overdue":
        return "已逾期"
      default:
        return "進行中"
    }
  }

  const getTypeText = (type: Assignment["type"]) => {
    switch (type) {
      case "exam":
        return "考試"
      case "project":
        return "專案"
      default:
        return "作業"
    }
  }

  const getDaysUntilDue = () => {
    const daysUntilDue = getDaysDifferenceTaiwan(new Date(), assignment.dueDate)

    if (daysUntilDue < 0) return "已逾期"
    if (isTodayTaiwan(assignment.dueDate)) return "今天到期"
    if (isTomorrowTaiwan(assignment.dueDate)) return "明天到期"
    return `${daysUntilDue}天後到期`
  }

  const StatusIcon = getStatusIcon(assignment.status)

  const handleCardClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest("button")) {
      return
    }
    onViewDetail?.()
  }

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    setShowDeleteDialog(true)
  }

  const handleDeleteConfirm = () => {
    onDelete?.()
    setShowDeleteDialog(false)
  }

  return (
    <>
      <Card
        className={`p-5 ${onViewDetail ? "cursor-pointer hover:shadow-xl hover:scale-[1.02] transition-all duration-200 ease-out hover:bg-white/90 dark:hover:bg-slate-900/90" : ""}`}
        onClick={handleCardClick}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-4 flex-1">
            <StatusIcon
              className={`w-5 h-5 mt-1 ${getStatusColor(assignment.status, assignment.dueDate).split(" ")[0]}`}
            />
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-foreground text-balance text-lg leading-tight mb-2">
                {assignment.title}
              </h3>
              <div className="flex items-center gap-3">
                {course && <p className="text-sm text-muted-foreground font-medium">{course.name}</p>}
                {assignment.source === "google_classroom" && (
                  <span className="text-xs px-3 py-1.5 rounded-full bg-blue-100 text-blue-800 border border-blue-300 font-medium dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-700/50">
                    Google Classroom
                  </span>
                )}
              </div>
              {assignment.description && (
                <p className="text-sm text-muted-foreground mt-3 line-clamp-2 leading-relaxed">
                  {assignment.description}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 ml-3">
            <span className="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-800 font-medium dark:bg-gray-800/50 dark:text-gray-300">
              {getTypeText(assignment.type)}
            </span>
          </div>
        </div>

        <div
          className={`flex items-center justify-between p-4 rounded-2xl border-2 ${getStatusColor(assignment.status, assignment.dueDate)}`}
        >
          <div>
            <p
              className={`text-sm font-semibold ${getStatusColor(assignment.status, assignment.dueDate).split(" ")[0]}`}
            >
              {getStatusText(assignment.status)}
            </p>
            <p className="text-xs text-muted-foreground mt-1 font-medium">
              {assignment.dueDate.toLocaleDateString("zh-TW")}{" "}
              {assignment.dueDate.toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>

          {assignment.status === "pending" && (
            <div className="text-right">
              <p className="text-xs font-semibold text-foreground">{getDaysUntilDue()}</p>
            </div>
          )}
        </div>

        <div className="flex gap-2 mt-4">
          {assignment.source === "google_classroom" && assignment.googleClassroomUrl && (
            <Button
              size="sm"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation()
                window.open(assignment.googleClassroomUrl, "_blank")
              }}
              className="text-blue-700 hover:text-blue-800 border-blue-300 hover:border-blue-400 hover:bg-blue-50 rounded-xl font-medium dark:text-blue-300 dark:border-blue-700/50 dark:hover:bg-blue-900/20"
            >
              開啟 Classroom
            </Button>
          )}

          {(assignment.status === "pending" || assignment.status === "overdue") && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onStatusChange(assignment.id, "completed")}
              className="flex-1 rounded-xl font-medium"
            >
              標記完成
            </Button>
          )}
          {assignment.status === "completed" && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onStatusChange(assignment.id, "pending")}
              className="flex-1 rounded-xl font-medium"
            >
              標記未完成
            </Button>
          )}
          {onViewDetail && (
            <Button
              size="sm"
              variant="outline"
              onClick={onViewDetail}
              className="rounded-xl font-medium bg-transparent"
            >
              查看詳情
            </Button>
          )}
          {onEdit && (
            <Button size="sm" variant="outline" onClick={onEdit} className="rounded-xl font-medium bg-transparent">
              編輯
            </Button>
          )}
          {onDelete && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleDeleteClick}
              className="text-destructive hover:text-destructive bg-transparent rounded-xl font-medium"
            >
              刪除
            </Button>
          )}
        </div>
      </Card>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>確定要刪除這個作業嗎？</AlertDialogTitle>
            <AlertDialogDescription>此操作無法復原。作業「{assignment.title}」將被永久刪除。</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              刪除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
