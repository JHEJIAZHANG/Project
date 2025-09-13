"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckIcon } from "@/components/icons"
import {
  BookIcon,
  ClipboardIcon,
  ExclamationIcon,
  CalendarIcon,
  StarIcon,
  HeartIcon,
  LightbulbIcon,
  TargetIcon,
  FlagIcon,
} from "@/components/icons"
import type { Assignment, Exam } from "@/types/course"
import type { CustomCategoryItem } from "./custom-category-form"
import { getDaysDifferenceTaiwan, isTodayTaiwan } from "@/lib/taiwan-time"

interface TodoItem {
  id: string
  title: string
  type: "assignment" | "exam" | "custom"
  courseId: string
  courseName: string
  dueDate: Date
  status?: string
  priority: number // Lower number = higher priority
  category?: string // For custom category items
  icon?: string // For custom category items
}

interface UnifiedTodoSectionProps {
  assignments: Assignment[]
  exams: Exam[]
  customCategoryItems?: CustomCategoryItem[]
  courses: any[]
  selectedDate?: Date
  notificationSettings?: {
    assignmentReminderTiming: string
  }
  onViewItem?: (id: string, type: "assignment" | "exam" | "custom") => void
  onViewAllTodos?: () => void
}

export function UnifiedTodoSection({
  assignments,
  exams,
  customCategoryItems = [],
  courses,
  selectedDate,
  notificationSettings,
  onViewItem,
  onViewAllTodos,
}: UnifiedTodoSectionProps) {
  const viewingDate = selectedDate || new Date()
  const isViewingToday = isTodayTaiwan(viewingDate)

  // Convert reminder timing to days
  const getReminderDays = (timing: string) => {
    switch (timing) {
      case "15min":
      case "30min":
      case "1hour":
      case "2hours":
        return 0 // Same day
      case "1day":
        return 1
      case "2days":
        return 2
      case "1week":
        return 7
      default:
        return 1 // Default to 1 day
    }
  }

  const reminderDays = notificationSettings ? getReminderDays(notificationSettings.assignmentReminderTiming) : 1

  const getCourseById = (courseId: string) => {
    return courses.find((c) => c.id === courseId)
  }

  // Filter and convert assignments to todo items
  const assignmentTodos: TodoItem[] = assignments
    .filter((assignment) => {
      if (assignment.status === "completed") return false

      const daysUntilDue = getDaysDifferenceTaiwan(viewingDate, assignment.dueDate)
      return daysUntilDue <= reminderDays && daysUntilDue >= 0
    })
    .map((assignment) => {
      const course = getCourseById(assignment.courseId)
      const daysUntilDue = getDaysDifferenceTaiwan(viewingDate, assignment.dueDate)

      return {
        id: assignment.id,
        title: assignment.title,
        type: "assignment" as const,
        courseId: assignment.courseId,
        courseName: course?.name || "未知課程",
        dueDate: assignment.dueDate,
        status: assignment.status,
        priority: daysUntilDue <= 1 ? 1 : daysUntilDue <= 2 ? 2 : 3,
      }
    })

  // Filter and convert exams to todo items
  const examTodos: TodoItem[] = exams
    .filter((exam) => {
      if (exam.status === "completed") return false

      const daysUntilExam = getDaysDifferenceTaiwan(viewingDate, exam.examDate)
      return daysUntilExam <= reminderDays && daysUntilExam >= 0
    })
    .map((exam) => {
      const course = getCourseById(exam.courseId)
      const daysUntilExam = getDaysDifferenceTaiwan(viewingDate, exam.examDate)

      return {
        id: exam.id,
        title: exam.title,
        type: "exam" as const,
        courseId: exam.courseId,
        courseName: course?.name || "未知課程",
        dueDate: exam.examDate,
        status: exam.status,
        priority: daysUntilExam <= 1 ? 1 : daysUntilExam <= 2 ? 2 : 3,
      }
    })

  // Filter and convert custom category items to todo items
  const customTodos: TodoItem[] = customCategoryItems
    .filter((item) => {
      if (item.status === "completed") return false

      // Use notification time if available, otherwise use due date with reminder days
      const referenceDate = item.notificationTime || item.dueDate
      const daysUntilReference = getDaysDifferenceTaiwan(viewingDate, referenceDate)

      // If notification time is set, show from notification time onwards
      if (item.notificationTime) {
        return daysUntilReference <= 0 && getDaysDifferenceTaiwan(viewingDate, item.dueDate) >= 0
      }

      // Otherwise use the standard reminder days logic
      return daysUntilReference <= reminderDays && daysUntilReference >= 0
    })
    .map((item) => {
      const course = getCourseById(item.courseId)
      const daysUntilDue = getDaysDifferenceTaiwan(viewingDate, item.dueDate)

      return {
        id: item.id,
        title: item.title,
        type: "custom" as const,
        courseId: item.courseId,
        courseName: course?.name || "未知課程",
        dueDate: item.dueDate,
        status: item.status,
        category: item.category,
        icon: item.icon,
        priority: daysUntilDue <= 1 ? 1 : daysUntilDue <= 2 ? 2 : 3,
      }
    })

  // Combine and sort all todo items
  const allTodos = [...assignmentTodos, ...examTodos, ...customTodos]
    .sort((a, b) => {
      // Sort by priority first, then by due date
      if (a.priority !== b.priority) {
        return a.priority - b.priority
      }
      return a.dueDate.getTime() - b.dueDate.getTime()
    })
    .slice(0, 5) // Show top 5 items

  const getItemColor = (item: TodoItem) => {
    const daysUntil = getDaysDifferenceTaiwan(viewingDate, item.dueDate)

    if (item.status === "pending") {
      return "#3b82f6" // Blue for all in-progress items
    }

    if (daysUntil <= 0) {
      return "#ef4444" // Red for overdue/today
    }
    if (daysUntil <= 1) {
      return "#f97316" // Orange for urgent (tomorrow)
    }
    if (daysUntil <= 2) {
      return "#eab308" // Yellow for soon
    }
    return "#3b82f6" // Blue for future
  }

  const getItemTextColor = (item: TodoItem) => {
    const daysUntil = getDaysDifferenceTaiwan(viewingDate, item.dueDate)

    if (item.status === "pending") {
      return "text-blue-700"
    }

    if (daysUntil <= 0) {
      return "text-red-700"
    }
    if (daysUntil <= 1) {
      return "text-orange-700"
    }
    if (daysUntil <= 2) {
      return "text-yellow-700"
    }
    return "text-blue-700"
  }

  const formatDueDate = (dueDate: Date) => {
    const daysUntil = getDaysDifferenceTaiwan(viewingDate, dueDate)

    if (daysUntil === 0) {
      return isViewingToday ? "今天" : "當天"
    }
    if (daysUntil === 1) {
      return isViewingToday ? "明天" : "隔天"
    }
    if (daysUntil > 0) {
      return `${daysUntil}天後`
    }
    return `${Math.abs(daysUntil)}天前`
  }

  const getIconComponent = (iconId?: string) => {
    const iconMap = {
      book: BookIcon,
      clipboard: ClipboardIcon,
      exclamation: ExclamationIcon,
      calendar: CalendarIcon,
      star: StarIcon,
      heart: HeartIcon,
      lightbulb: LightbulbIcon,
      target: TargetIcon,
      flag: FlagIcon,
      check: CheckIcon,
    }
    return iconMap[iconId as keyof typeof iconMap] || ClipboardIcon
  }

  const getTypeLabel = (type: "assignment" | "exam" | "custom", category?: string, icon?: string) => {
    if (type === "custom" && category) {
      const IconComponent = getIconComponent(icon)
      return (
        <span className="flex items-center gap-1">
          <IconComponent className="w-3 h-3" />
          {category}
        </span>
      )
    }
    return type === "assignment" ? "作業" : "考試"
  }

  return (
    <Card className="bg-white p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-foreground flex items-center gap-2">
          <CheckIcon className="w-5 h-5 text-primary" />
          待辦事項
        </h2>
        <Button variant="outline" size="sm" onClick={onViewAllTodos}>
          查看全部
        </Button>
      </div>

      {allTodos.length > 0 ? (
        <div className="space-y-3">
          {allTodos.map((item) => (
            <div
              key={`${item.type}-${item.id}`}
              className="flex items-center justify-between p-2 bg-muted rounded-lg cursor-pointer hover:shadow-sm transition-shadow"
              onClick={() => onViewItem?.(item.id, item.type)}
            >
              <div className="flex items-center gap-2">
                <div className="w-1 h-8 flex-shrink-0 rounded-sm" style={{ backgroundColor: getItemColor(item) }} />
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-foreground">{item.title}</p>
                    <span className="text-xs px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded">
                      {getTypeLabel(item.type, item.category, item.icon)}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{item.courseName}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-xs font-medium ${getItemTextColor(item)}`}>{formatDueDate(item.dueDate)}</p>
                <p className="text-xs text-slate-600">{item.dueDate.toLocaleDateString("zh-TW")}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground text-center py-4">暫無待辦事項</p>
      )}

      {reminderDays > 0 && (
        <div className="mt-3 pt-3 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">顯示 {reminderDays} 天內的待辦事項</p>
        </div>
      )}
    </Card>
  )
}
