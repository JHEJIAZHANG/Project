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
import type { Exam, Course } from "@/types/course"
import { isExamEndedTaiwan, getDaysToExamEndTaiwan } from "@/lib/taiwan-time"

interface ExamDetailProps {
  exam: Exam
  course?: Course
  onBack: () => void
  onEdit: () => void
  onDelete: () => void
  onStatusChange: (status: Exam["status"]) => void
}

export function ExamDetail({ exam, course, onBack, onEdit, onDelete, onStatusChange }: ExamDetailProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const getExamStatus = (examDate: Date, duration: number) => {
    const isEnded = isExamEndedTaiwan(examDate, duration)
    const daysToExamEnd = getDaysToExamEndTaiwan(examDate, duration)

    if (isEnded) return { status: "已結束", color: "text-gray-700 bg-gray-100 border-gray-200" }
    if (daysToExamEnd <= 3)
      return { status: "即將到來", color: "text-destructive bg-destructive/10 border-destructive/20" }
    if (daysToExamEnd <= 7) return { status: "本週", color: "text-amber-800 bg-amber-50 border-amber-200" }
    return { status: "未來", color: "text-chart-1 bg-chart-1/10 border-chart-1/20" }
  }

  const getTypeText = (type: Exam["type"]) => {
    switch (type) {
      case "midterm":
        return "期中考"
      case "final":
        return "期末考"
      case "quiz":
        return "小考"
      default:
        return "其他"
    }
  }

  const examStatus = getExamStatus(exam.examDate, exam.duration)

  const handleDeleteConfirm = () => {
    onDelete()
    setShowDeleteDialog(false)
  }

  return (
    <>
      <PageHeader
        title={exam.title}
        action={
          <Button variant="outline" size="sm" onClick={onBack}>
            返回
          </Button>
        }
      />

      <div className="space-y-6 mb-6">
        {/* Status and Course Info */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className={`text-sm font-medium px-3 py-1 rounded-full ${examStatus.color}`}>
              {examStatus.status}
            </span>
            <span className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
              {getTypeText(exam.type)}
            </span>
          </div>

          {course && (
            <div>
              <p className="text-sm text-muted-foreground">課程：{course.name}</p>
            </div>
          )}
        </div>

        {/* Exam Date */}
        <div className="space-y-1">
          <span className="text-sm font-medium">考試時間</span>
          <p className="text-sm text-muted-foreground">{exam.examDate.toLocaleString("zh-TW")}</p>
        </div>

        {/* Duration */}
        <div className="space-y-1">
          <span className="text-sm font-medium">考試時長</span>
          <p className="text-sm text-muted-foreground">{exam.duration} 分鐘</p>
        </div>

        {/* Location */}
        {exam.location && (
          <div className="space-y-1">
            <span className="text-sm font-medium">考試地點</span>
            <p className="text-sm text-muted-foreground">{exam.location}</p>
          </div>
        )}

        {/* Description */}
        {exam.description && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium">考試備註</h3>
            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{exam.description}</p>
          </div>
        )}
      </div>

      <LearningResources
        assignment={{
          id: exam.id,
          title: exam.title,
          description: exam.description || "",
          type: "exam" as const,
          status: "pending" as const,
          dueDate: exam.examDate,
          courseId: exam.courseId,
          createdAt: new Date(),
          updatedAt: new Date(),
        }}
        course={course}
      />

      {/* Actions */}
      <div className="space-y-2 pb-20 lg:pb-0">
        <div className="flex gap-2">
          {(exam.status === "pending" || exam.status === "overdue") && (
            <Button onClick={() => onStatusChange("completed")} className="flex-1">
              <CheckIcon className="w-4 h-4 mr-2" />
              標記結束
            </Button>
          )}
          {exam.status === "completed" && (
            <Button variant="outline" onClick={() => onStatusChange("pending")} className="flex-1">
              <ClockIcon className="w-4 h-4 mr-2" />
              標記未結束
            </Button>
          )}
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={onEdit} className="flex-1 bg-transparent">
            編輯
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowDeleteDialog(true)}
            className="flex-1 text-destructive hover:text-destructive bg-transparent"
          >
            刪除考試
          </Button>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>確定要刪除這個考試嗎？</AlertDialogTitle>
            <AlertDialogDescription>此操作無法復原。考試「{exam.title}」將被永久刪除。</AlertDialogDescription>
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
