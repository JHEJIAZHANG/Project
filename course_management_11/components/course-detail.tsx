"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckIcon, ExclamationIcon, ClockIcon } from "@/components/icons"
import { useCourses } from "@/hooks/use-courses"
import { CourseForm } from "@/components/course-form"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import type { Assignment, Exam } from "@/types/course"

interface CourseDetailProps {
  courseId: string
  showBackButton?: boolean
}

const DAYS = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]

export function CourseDetail({ courseId, showBackButton = true }: CourseDetailProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  const { getCourseById, getAssignmentsByCourse, getNotesByCourse, getExamsByCourse, deleteCourse, updateCourse } =
    useCourses()

  const course = getCourseById(courseId)
  const assignments = getAssignmentsByCourse(courseId)
  const notes = getNotesByCourse(courseId)
  const exams = getExamsByCourse(courseId)

  if (!course) {
    return <div className="p-4 text-center text-muted-foreground">課程不存在</div>
  }

  const formatSchedule = () => {
    return course.schedule.map((slot) => `${DAYS[slot.dayOfWeek]} ${slot.startTime}-${slot.endTime}`).join(", ")
  }

  const getStatusColor = (status: Assignment["status"]) => {
    switch (status) {
      case "completed":
        return "text-chart-4"
      case "overdue":
        return "text-destructive"
      default:
        return "text-chart-5"
    }
  }

  const getAssignmentDateColor = (status: Assignment["status"]) => {
    switch (status) {
      case "completed":
        return "text-chart-4" // Green for completed
      case "overdue":
        return "text-destructive" // Red for overdue
      default:
        return "text-chart-5" // Orange for in progress
    }
  }

  const getExamDateColor = (exam: Exam) => {
    const now = new Date()
    const examDate = new Date(exam.examDate)
    const daysDiff = Math.ceil((examDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (exam.status === "completed" || daysDiff < 0) {
      return "text-chart-4" // Green for finished
    } else if (daysDiff <= 7) {
      return "text-chart-5" // Orange for upcoming (within 7 days)
    } else {
      return "text-chart-3" // Blue for scheduled (8+ days)
    }
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

  const getExamTypeText = (type: Exam["type"]) => {
    switch (type) {
      case "midterm":
        return "期中考"
      case "final":
        return "期末考"
      case "quiz":
        return "小考"
      default:
        return "其他考試"
    }
  }

  const sortedAssignments = [...assignments].sort((a, b) => {
    if (a.status === "completed" && b.status !== "completed") return 1
    if (a.status !== "completed" && b.status === "completed") return -1
    return 0
  })

  const activeExams = exams.filter((exam) => {
    const now = new Date()
    const examDate = new Date(exam.examDate)
    const daysDiff = Math.ceil((examDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    return !(exam.status === "completed" || daysDiff < 0)
  })

  const handleCourseUpdate = (updatedCourse: Omit<typeof course, "id" | "createdAt">) => {
    updateCourse(courseId, updatedCourse)
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
  }

  if (isEditing) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-foreground">編輯課程</h1>
        </div>
        <CourseForm initialCourse={course} onSubmit={handleCourseUpdate} onCancel={handleCancelEdit} />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">{course.name}</h1>
      </div>

      {/* Course Info */}
      <div className="space-y-6">
        {/* Course Color and Basic Info */}
        <div className="space-y-3">
          <span className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200">課程</span>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-4">
            {course.courseCode && (
              <div className="space-y-1">
                <span className="text-sm font-medium">課程代碼</span>
                <p className="text-sm text-muted-foreground font-medium">{course.courseCode}</p>
              </div>
            )}

            {course.instructor && (
              <div className="space-y-1">
                <span className="text-sm font-medium">授課教師</span>
                <p className="text-sm text-muted-foreground">{course.instructor}</p>
              </div>
            )}

            {course.classroom && (
              <div className="space-y-1">
                <span className="text-sm font-medium">教室</span>
                <p className="text-sm text-muted-foreground">{course.classroom}</p>
              </div>
            )}
          </div>

          <div className="space-y-4">
            {course.studentCount && (
              <div className="space-y-1">
                <span className="text-sm font-medium">學生人數</span>
                <p className="text-sm text-muted-foreground">{course.studentCount} 人</p>
              </div>
            )}

            <div className="space-y-1">
              <span className="text-sm font-medium">上課時間</span>
              <p className="text-sm text-muted-foreground">{formatSchedule()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Assignments */}
      <Card className="p-4">
        <h2 className="font-semibold text-foreground mb-3">作業與報告</h2>
        {sortedAssignments.length > 0 ? (
          <div className="space-y-3">
            {sortedAssignments.map((assignment) => {
              const StatusIcon = getStatusIcon(assignment.status)
              return (
                <div
                  key={assignment.id}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <StatusIcon className={`w-4 h-4 ${getStatusColor(assignment.status)}`} />
                    <div>
                      <p
                        className={`font-medium text-foreground ${assignment.status === "completed" ? "line-through" : ""}`}
                      >
                        {assignment.title}
                      </p>
                      {assignment.description && (
                        <p
                          className={`text-sm text-muted-foreground ${assignment.status === "completed" ? "line-through" : ""}`}
                        >
                          {assignment.description}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p
                      className={`text-sm font-medium ${getAssignmentDateColor(assignment.status)} ${assignment.status === "completed" ? "line-through" : ""}`}
                    >
                      {assignment.dueDate.toLocaleDateString("zh-TW")}
                    </p>
                    <p
                      className={`text-xs text-muted-foreground ${assignment.status === "completed" ? "line-through" : ""}`}
                    >
                      {assignment.dueDate.toLocaleTimeString("zh-TW", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-4">暫無作業</p>
        )}
      </Card>

      {/* Exams */}
      <Card className="p-4">
        <h2 className="font-semibold text-foreground mb-3">考試時間</h2>
        {activeExams.length > 0 ? (
          <div className="space-y-3">
            {activeExams.map((exam) => (
              <div
                key={exam.id}
                className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors cursor-pointer"
              >
                <div>
                  <p className="font-medium text-foreground">{exam.title}</p>
                  {exam.description && <p className="text-sm text-muted-foreground">{exam.description}</p>}
                  <div className="flex items-center gap-4 mt-1">
                    <span className="text-xs text-muted-foreground">{getExamTypeText(exam.type)}</span>
                    <span className="text-xs text-muted-foreground">時長：{exam.duration} 分鐘</span>
                    {exam.location && <span className="text-xs text-muted-foreground">地點：{exam.location}</span>}
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-medium ${getExamDateColor(exam)}`}>
                    {exam.examDate.toLocaleDateString("zh-TW")}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {exam.examDate.toLocaleTimeString("zh-TW", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-4">暫無考試</p>
        )}
      </Card>

      {/* Notes */}
      <Card className="p-4">
        <h2 className="font-semibold text-foreground mb-3">課程筆記</h2>
        {notes.length > 0 ? (
          <div className="space-y-3">
            {notes.map((note) => (
              <div key={note.id} className="p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors cursor-pointer">
                <h3 className="font-medium text-foreground mb-1">{note.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2">{note.content}</p>
                <p className="text-xs text-slate-600 mt-2">{note.updatedAt.toLocaleDateString("zh-TW")}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-4">暫無筆記</p>
        )}
      </Card>

      <div className="flex gap-2">
        <Button variant="outline" className="flex-1 bg-transparent" onClick={() => setIsEditing(true)}>
          編輯
        </Button>
        <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <AlertDialogTrigger asChild>
            <Button variant="outline" className="flex-1 text-destructive hover:text-destructive bg-transparent">
              刪除課程
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>確認刪除課程</AlertDialogTitle>
              <AlertDialogDescription>
                您確定要刪除「{course.name}」這門課程嗎？此操作將同時刪除該課程的所有作業、筆記和考試，且無法復原。
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>取消</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => {
                  deleteCourse(courseId)
                  setShowDeleteDialog(false)
                }}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                確認刪除
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  )
}
