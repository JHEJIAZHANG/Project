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
import { useCustomCategories } from "@/hooks/use-custom-categories"
import { useCustomTodos } from "@/hooks/use-custom-todos"

interface CourseDetailProps {
  courseId: string
  lineUserId: string
  showBackButton?: boolean
  onOpenAssignment?: (id: string) => void
  onOpenExam?: (id: string) => void
  onOpenNote?: (id: string) => void
  onDeleted?: () => void
  onOpenCustomTodo?: (id: string) => void
}

const DAYS = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]

export function CourseDetail({ courseId, lineUserId, showBackButton = true, onOpenAssignment, onOpenExam, onOpenNote, onDeleted, onOpenCustomTodo }: CourseDetailProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  const { getCourseById, getAssignmentsByCourse, getNotesByCourse, getExamsByCourse, deleteCourse, updateCourse } =
    useCourses(lineUserId)

  const course = getCourseById(courseId)
  const assignments = getAssignmentsByCourse(courseId)
  const notes = getNotesByCourse(courseId)
  const exams = getExamsByCourse(courseId)

  // 自訂分類與待辦（課程內視圖）
  const { categories: customCategories } = useCustomCategories(lineUserId)
  const { items: customTodos } = useCustomTodos(lineUserId)

  console.log('🔍 課程詳情資料:', {
    courseId,
    course,
    assignments,
    notes,
    exams
  })

  if (!course) {
    // 尚未取得課程資料時顯示載入狀態（避免誤關閉）
    return (
      <div className="p-6 text-center text-muted-foreground">
        <p className="text-sm">正在載入課程資料...</p>
      </div>
    )
  }

  const formatSchedule = () => {
    if (!course.schedule || course.schedule.length === 0) {
      return "未設定上課時間"
    }
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
            <div className="space-y-1">
              <span className="text-sm font-medium">課程代碼</span>
              <p className={`text-sm font-medium ${course.courseCode ? 'text-muted-foreground' : 'text-gray-400 italic'}`}>
                {course.courseCode || "未設定"}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-sm font-medium">授課教師</span>
              <p className={`text-sm ${course.instructor ? 'text-muted-foreground' : 'text-gray-400 italic'}`}>
                {course.instructor || "未設定"}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-sm font-medium">教室</span>
              <p className={`text-sm ${course.classroom ? 'text-muted-foreground' : 'text-gray-400 italic'}`}>
                {course.classroom || "未設定"}
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-1">
              <span className="text-sm font-medium">學生人數</span>
              <p className={`text-sm ${course.studentCount ? 'text-muted-foreground' : 'text-gray-400 italic'}`}>
                {course.studentCount ? `${course.studentCount} 人` : "未設定"}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-sm font-medium">上課時間</span>
              <p className={`text-sm ${course.schedule && course.schedule.length > 0 ? 'text-muted-foreground' : 'text-gray-400 italic'}`}>
                {formatSchedule()}
              </p>
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
                  onClick={() => onOpenAssignment && onOpenAssignment(assignment.id)}
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
          <div className="text-center py-8">
            <p className="text-gray-400 italic">暫無作業</p>
            <p className="text-xs text-gray-400 mt-1">此課程目前沒有相關作業</p>
          </div>
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
                onClick={() => onOpenExam && onOpenExam(exam.id)}
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
          <div className="text-center py-8">
            <p className="text-gray-400 italic">暫無考試</p>
            <p className="text-xs text-gray-400 mt-1">此課程目前沒有相關考試</p>
          </div>
        )}
      </Card>

      {/* Notes */}
      <Card className="p-4">
        <h2 className="font-semibold text-foreground mb-3">課程筆記</h2>
        {notes.length > 0 ? (
          <div className="space-y-3">
            {notes.map((note) => (
              <div key={note.id} className="p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors cursor-pointer" onClick={() => onOpenNote && onOpenNote(note.id)}>
                <h3 className="font-medium text-foreground mb-1">{note.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2">{note.content}</p>
                <p className="text-xs text-slate-600 mt-2">{note.updatedAt.toLocaleDateString("zh-TW")}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-400 italic">暫無筆記</p>
            <p className="text-xs text-gray-400 mt-1">此課程目前沒有相關筆記</p>
          </div>
        )}
      </Card>

      {/* 自訂分類（僅顯示此課程已新增的待辦） */}
      <Card className="p-4">
        <h2 className="font-semibold text-foreground mb-3">自訂分類</h2>
        <div className="space-y-3">
          {customCategories.map((cat) => {
            const items = customTodos.filter((t) => t.course === courseId && t.category === cat.id)
            if (items.length === 0) return null
            return (
              <div key={cat.id} className="border rounded-md p-3">
                <div className="text-sm font-medium mb-2">{cat.name}</div>
                <div className="space-y-2">
                  {items.map((it) => (
                    <div
                      key={it.id}
                      className="flex items-center justify-between text-sm bg-muted rounded px-3 py-2 cursor-pointer hover:bg-muted/80"
                      onClick={() => onOpenCustomTodo && onOpenCustomTodo(it.id)}
                    >
                      <div className="min-w-0 mr-2">
                        <div className="font-medium truncate">{it.title}</div>
                        <div className="text-xs text-muted-foreground">{new Date(it.dueDate).toLocaleString('zh-TW')}</div>
                      </div>
                      <span className="text-xs text-muted-foreground">{it.status === 'completed' ? '已完成' : it.status === 'overdue' ? '已逾期' : '進行中'}</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
          {customCategories.every(cat => !customTodos.some(t => t.course === courseId && t.category === cat.id)) && (
            <p className="text-sm text-muted-foreground">此課程尚未有自訂分類待辦</p>
          )}
        </div>
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
                disabled={deleting}
                onClick={async () => {
                  try {
                    setDeleting(true)
                    await deleteCourse(courseId)
                    // 先關閉子層 AlertDialog，再關閉父層 Dialog，避免焦點殘留觸發 aria-hidden 警告
                    setShowDeleteDialog(false)
                    // 主動移除目前焦點，避免被 aria-hidden 的容器持有
                    try { (document.activeElement as HTMLElement | null)?.blur?.() } catch {}
                    // 等待下一個微任務/動畫桢，讓子層完全卸載再關閉父層
                    setTimeout(() => { if (onDeleted) onDeleted() }, 80)
                  } finally {
                    setDeleting(false)
                  }
                }}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {deleting ? '刪除中...' : '確認刪除'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  )
}
