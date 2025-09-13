export interface Course {
  id: string
  name: string
  courseCode?: string // 添加課程代碼欄位
  instructor?: string
  classroom?: string
  studentCount?: number // 添加學生人數欄位
  schedule: {
    dayOfWeek: number // 0-6 (Sunday-Saturday)
    startTime: string // HH:MM format
    endTime: string // HH:MM format
  }[]
  color: string
  createdAt: Date
  source?: "google_classroom" | "manual" // Added source field to distinguish between Google Classroom and manual courses
}

export interface Assignment {
  id: string
  courseId: string
  title: string
  description?: string
  dueDate: Date
  notificationTime?: Date
  status: "pending" | "completed" | "overdue"
  googleClassroomId?: string
  googleClassroomUrl?: string
  source?: "manual" | "google_classroom"
}

export interface Note {
  id: string
  courseId: string
  title: string
  content: string
  attachments?: {
    id: string
    name: string
    size: number
    type: string
    url: string
  }[]
  createdAt: Date
  updatedAt: Date
}

export interface Exam {
  id: string
  courseId: string
  title: string
  description?: string
  examDate: Date
  notificationTime?: Date
  duration: number // in minutes
  location?: string
  type: "midterm" | "final" | "quiz" | "other"
  status: "pending" | "completed" | "overdue"
  createdAt: Date
  updatedAt: Date
}

export type Task = Assignment | Exam

export interface TaskFilter {
  type: "all" | "assignment" | "exam"
  status: "all" | "pending" | "completed" | "overdue" | "upcoming" | "scheduled"
}
