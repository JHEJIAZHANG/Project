"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { PageHeader } from "@/components/page-header"
import { LearningResources } from "@/components/learning-resources"
import { CheckIcon, ClockIcon } from "@/components/icons"
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
import type { Assignment, Course } from "@/types/course"

interface AssignmentDetailProps {
  assignment: Assignment
  course?: Course
  onBack: () => void
  onEdit: () => void
  onDelete: () => void
  onStatusChange: (status: Assignment["status"]) => void
}

export function AssignmentDetail({
  assignment,
  course,
  onBack,
  onEdit,
  onDelete,
  onStatusChange,
}: AssignmentDetailProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const getStatusColor = (status: Assignment["status"]) => {
    switch (status) {
      case "completed":
        return "text-chart-4 bg-chart-4/10 border-chart-4/20"
      case "overdue":
        return "text-destructive bg-destructive/10 border-destructive/20"
      default:
        return "text-amber-800 bg-amber-50 border-amber-200"
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

  const handleDeleteConfirm = () => {
    onDelete()
    setShowDeleteDialog(false)
  }

  return (
    <>
      <PageHeader
        title={assignment.title}
        action={
          <Button variant="outline" size="sm" onClick={onBack}>
            返回
          </Button>
        }
      />

      {/* Assignment Info */}
      <div className="space-y-6 mb-6">
        {/* Status and Course Info */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className={`text-sm font-medium px-3 py-1 rounded-full ${getStatusColor(assignment.status)}`}>
              {getStatusText(assignment.status)}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {course && <p className="text-sm text-muted-foreground">課程：{course.name}</p>}
            {assignment.source === "google_classroom" && (
              <span className="text-sm px-3 py-1 rounded-full bg-blue-100 text-blue-700 border border-blue-200">
                Google Classroom
              </span>
            )}
          </div>
        </div>

        {/* Due Date */}
        <div className="space-y-1">
          <span className="text-sm font-medium">截止時間</span>
          <p className="text-sm text-muted-foreground">{assignment.dueDate.toLocaleString("zh-TW")}</p>
        </div>

        {/* Description */}
        {assignment.description && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium">作業描述</h3>
            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
              {assignment.description}
            </p>
          </div>
        )}
      </div>

      {/* Learning Resources */}
      <div className="mb-4">
        <LearningResources assignment={assignment} course={course} />
      </div>

      {/* Actions */}
      <div className="space-y-2 pb-20 lg:pb-0">
        <div className="flex gap-2">
          {(assignment.status === "pending" || assignment.status === "overdue") && (
            <Button onClick={() => onStatusChange("completed")} className="flex-1">
              <CheckIcon className="w-4 h-4 mr-2" />
              標記完成
            </Button>
          )}
          {assignment.status === "completed" && (
            <Button variant="outline" onClick={() => onStatusChange("pending")} className="flex-1">
              <ClockIcon className="w-4 h-4 mr-2" />
              標記未完成
            </Button>
          )}
          <Button variant="outline" onClick={onEdit}>
            編輯
          </Button>
        </div>

        <Button
          variant="outline"
          onClick={() => setShowDeleteDialog(true)}
          className="w-full text-destructive hover:text-destructive bg-transparent"
        >
          刪除作業
        </Button>
      </div>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>確定要刪除這個作業？</AlertDialogTitle>
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
