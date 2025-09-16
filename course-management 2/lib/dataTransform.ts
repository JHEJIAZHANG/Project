import { Course, Assignment, Note, Exam } from '@/types/course'

// 後端 Course 轉換為前端 Course
export function transformBackendCourse(backendCourse: any): Course {
  return {
    id: backendCourse.id.toString(),
    name: backendCourse.title || backendCourse.name || '',
    courseCode: backendCourse.section || '',
    instructor: backendCourse.instructor || '',
    classroom: backendCourse.classroom || '',
    studentCount: backendCourse.student_count || 0,
    schedule: backendCourse.schedules?.map((schedule: any) => ({
      dayOfWeek: schedule.day_of_week,
      startTime: schedule.start_time,
      endTime: schedule.end_time
    })) || [],
    color: backendCourse.color || '#3B82F6',
    createdAt: new Date(backendCourse.created_at),
    source: backendCourse.is_google_classroom ? 'google_classroom' : 'manual'
  }
}

// 前端 Course 轉換為後端格式
export function transformFrontendCourse(frontendCourse: Course, lineUserId: string) {
  return {
    title: frontendCourse.name,
    description: frontendCourse.courseCode || '',
    instructor: frontendCourse.instructor || '',
    classroom: frontendCourse.classroom || '',
    color: frontendCourse.color,
    is_google_classroom: frontendCourse.source === 'google_classroom',
    schedules: frontendCourse.schedule.map(schedule => ({
      day_of_week: schedule.dayOfWeek,
      start_time: schedule.startTime,
      end_time: schedule.endTime
    }))
  }
}

// 後端 Homework 轉換為前端 Assignment
export function transformBackendAssignment(backendAssignment: any): Assignment {
  return {
    id: String(backendAssignment.id),
    title: backendAssignment.title,
    description: backendAssignment.description || '',
    dueDate: backendAssignment.due_date ? new Date(backendAssignment.due_date) : new Date(),
    // 後端 serializer 的 course 為 UUID 字串
    courseId: backendAssignment.course ? String(backendAssignment.course) : '',
    courseName: '',
    status: backendAssignment.status || 'pending',
    priority: 'medium',
    createdAt: new Date(backendAssignment.created_at),
    updatedAt: new Date(backendAssignment.updated_at),
    googleClassroomId: undefined,
    source: 'manual'
  }
}

// 前端 Assignment 轉換為後端格式
export function transformFrontendAssignment(frontendAssignment: Assignment, lineUserId: string) {
  return {
    // 後端從 Header 取得 line user，無需傳 line_user_id
    title: frontendAssignment.title,
    description: frontendAssignment.description || '',
    // 後端 due_date 為 DateTime
    due_date: frontendAssignment.dueDate ? frontendAssignment.dueDate.toISOString() : null,
    // 通知時間暫不使用
    notification_time: null,
    // 後端使用 UUID 字串
    course: frontendAssignment.courseId || null,
    // 與 AssignmentV2 欄位對齊
    type: 'assignment',
    status: frontendAssignment.status || 'pending'
  }
}

// 後端 StudentNote 轉換為前端 Note
export function transformBackendNote(backendNote: any): Note {
  return {
    id: backendNote.id.toString(),
    title: backendNote.title,
    content: backendNote.content || '',
    courseId: backendNote.course ? String(backendNote.course) : (backendNote.course?.id?.toString() || ''),
    courseName: backendNote.course_name || backendNote.course?.name || '',
    createdAt: new Date(backendNote.created_at),
    updatedAt: new Date(backendNote.updated_at),
    attachments: backendNote.attachments?.map((attachment: any) => ({
      id: attachment.id.toString(),
      name: attachment.name,
      size: attachment.size,
      type: attachment.type,
      url: attachment.url
    })) || []
  }
}

// 前端 Note 轉換為後端格式
export function transformFrontendNote(frontendNote: Note, lineUserId: string) {
  return {
    // 後端從 Header 取得 line user
    title: frontendNote.title,
    content: frontendNote.content,
    course: frontendNote.courseId || null, // UUID 字串
    tags: frontendNote.tags || [],
    attachment_ids: Array.isArray(frontendNote.attachments)
      ? frontendNote.attachments.map((a: any) => a.id)
      : []
  }
}

// 後端 Exam 轉換為前端 Exam
export function transformBackendExam(backendExam: any): Exam {
  return {
    id: backendExam.id.toString(),
    title: backendExam.title,
    description: backendExam.description || '',
    examDate: backendExam.exam_date ? new Date(backendExam.exam_date) : new Date(),
    courseId: backendExam.course ? String(backendExam.course) : (backendExam.course?.id?.toString() || ''),
    courseName: backendExam.course_name || backendExam.course?.name || '',
    location: backendExam.location || '',
    duration: backendExam.duration || 120,
    type: backendExam.type || 'other',
    status: backendExam.status || 'pending',
    createdAt: new Date(backendExam.created_at),
    updatedAt: new Date(backendExam.updated_at)
  }
}

// 前端 Exam 轉換為後端格式
export function transformFrontendExam(frontendExam: Exam, lineUserId: string) {
  return {
    line_user_id: lineUserId,
    title: frontendExam.title,
    description: frontendExam.description,
    exam_date: frontendExam.examDate?.toISOString() || null,
    // 後端使用 UUID，不能 parseInt，直接傳字串
    course: frontendExam.courseId || null,
    location: frontendExam.location,
    duration: frontendExam.duration,
    type: frontendExam.type,
    status: frontendExam.status
  }
}
