"use client"

import { useState, useEffect } from "react"
import type { Course, Assignment, Note, Exam } from "@/types/course"

const STORAGE_KEY = "course-management-data"

interface CourseData {
  courses: Course[]
  assignments: Assignment[]
  notes: Note[]
  exams: Exam[] // 新增考試數據
}

const defaultData: CourseData = {
  courses: [
    {
      id: "gc-1",
      name: "計算機概論",
      courseCode: "CS101",
      instructor: "張教授",
      classroom: "資訊大樓 201",
      studentCount: 45,
      schedule: [], // Google Classroom courses don't have schedule initially
      color: "#3b82f6",
      createdAt: new Date("2024-09-01"),
      source: "google_classroom",
    },
    {
      id: "gc-2",
      name: "資料結構與演算法",
      courseCode: "CS201",
      instructor: "李教授",
      classroom: "資訊大樓 305",
      studentCount: 38,
      schedule: [], // Google Classroom courses don't have schedule initially
      color: "#10b981",
      createdAt: new Date("2024-09-01"),
      source: "google_classroom",
    },
    {
      id: "manual-1",
      name: "英文會話",
      instructor: "王老師",
      classroom: "語言中心 A102",
      schedule: [
        {
          dayOfWeek: 2, // Tuesday
          startTime: "14:00",
          endTime: "15:30",
        },
        {
          dayOfWeek: 4, // Thursday
          startTime: "14:00",
          endTime: "15:30",
        },
      ],
      color: "#f59e0b",
      createdAt: new Date("2024-09-05"),
      source: "manual",
    },
  ],
  assignments: [
    // Google Classroom assignments
    {
      id: "gc-assign-1",
      courseId: "gc-1",
      title: "程式設計基礎練習",
      description:
        "完成 Python 基礎語法練習題，包含變數、迴圈、條件判斷等概念。請在 Google Classroom 上提交程式碼檔案。",
      dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), // 3 days from now
      status: "pending" as const,
      source: "google_classroom",
      googleClassroomId: "gc_assignment_001",
      googleClassroomUrl: "https://classroom.google.com/c/NjA2NTg4NzE2NzNa/a/NjA2NTg4NzE2NzNa",
    },
    {
      id: "gc-assign-2",
      courseId: "gc-1",
      title: "資料庫設計報告",
      description: "設計一個小型資料庫系統，包含 ER 圖和正規化過程。報告需包含至少 5 個實體和相關關係。",
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 1 week from now
      status: "pending" as const,
      source: "google_classroom",
      googleClassroomId: "gc_assignment_002",
      googleClassroomUrl: "https://classroom.google.com/c/NjA2NTg4NzE2NzNa/a/NjA2NTg4NzE2NzRa",
    },
    {
      id: "gc-assign-3",
      courseId: "gc-2",
      title: "二元搜尋樹實作",
      description: "使用 C++ 實作二元搜尋樹，包含插入、刪除、搜尋功能。需要處理平衡問題並提供完整的測試案例。",
      dueDate: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000), // 10 days from now
      status: "pending" as const,
      source: "google_classroom",
      googleClassroomId: "gc_assignment_003",
      googleClassroomUrl: "https://classroom.google.com/c/NjA2NTg4NzE2NzRa/a/NjA2NTg4NzE2NzRa",
    },
    {
      id: "gc-assign-4",
      courseId: "gc-2",
      title: "演算法複雜度分析",
      description: "分析常見排序演算法的時間複雜度和空間複雜度，包含 Bubble Sort、Quick Sort、Merge Sort 等。",
      dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000), // 5 days from now
      status: "completed" as const,
      source: "google_classroom",
      googleClassroomId: "gc_assignment_004",
      googleClassroomUrl: "https://classroom.google.com/c/NjA2NTg4NzE2NzRa/a/NjA2NTg4NzE2NzVa",
    },
    // Manual assignments
    {
      id: "manual-assign-1",
      courseId: "manual-1",
      title: "英文口語報告準備",
      description: "準備 5 分鐘的英文口語報告，主題為「我的興趣愛好」。需要準備投影片並練習發音。",
      dueDate: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000), // 4 days from now
      status: "pending" as const,
      source: "manual",
    },
    {
      id: "manual-assign-2",
      courseId: "manual-1",
      title: "英文作文練習",
      description: "撰寫一篇 300 字的英文作文，主題為「科技對生活的影響」。注意文法和詞彙的使用。",
      dueDate: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000), // 6 days from now
      status: "pending" as const,
      source: "manual",
    },
    {
      id: "manual-assign-3",
      courseId: "gc-1",
      title: "期中專題企劃書",
      description: "提交期中專題的企劃書，包含專題目標、技術選擇、時程規劃等內容。需要老師面談確認。",
      dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 2 weeks from now
      status: "pending" as const,
      source: "manual",
    },
    {
      id: "manual-assign-4",
      courseId: "gc-2",
      title: "演算法競賽練習",
      description: "完成線上演算法競賽平台的 5 道題目，提升程式解題能力。記錄解題思路和優化過程。",
      dueDate: new Date(Date.now() + 8 * 24 * 60 * 60 * 1000), // 8 days from now
      status: "pending" as const,
      source: "manual",
    },
  ],
  notes: [],
  exams: [],
}

export function useCourses() {
  const [data, setData] = useState<CourseData>(defaultData)

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsedData = JSON.parse(stored)
        // Convert date strings back to Date objects
        parsedData.courses = parsedData.courses.map((course: any) => ({
          ...course,
          createdAt: new Date(course.createdAt),
        }))
        parsedData.assignments = parsedData.assignments.map((assignment: any) => ({
          ...assignment,
          dueDate: new Date(assignment.dueDate),
          notificationTime: assignment.notificationTime ? new Date(assignment.notificationTime) : undefined,
        }))
        parsedData.notes = parsedData.notes.map((note: any) => ({
          ...note,
          createdAt: new Date(note.createdAt),
          updatedAt: new Date(note.updatedAt),
        }))
        parsedData.exams = (parsedData.exams || []).map((exam: any) => ({
          ...exam,
          examDate: new Date(exam.examDate),
          notificationTime: exam.notificationTime ? new Date(exam.notificationTime) : undefined,
          status: exam.status || "pending", // Ensure status is always set
          createdAt: new Date(exam.createdAt),
          updatedAt: new Date(exam.updatedAt),
        }))
        setData(parsedData)
      } catch (error) {
        console.error("Failed to parse stored data:", error)
      }
    }
  }, [])

  const saveData = (newData: CourseData) => {
    setData(newData)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newData))
  }

  const addCourse = (course: Omit<Course, "id" | "createdAt">) => {
    const newCourse: Course = {
      ...course,
      id: Date.now().toString(),
      createdAt: new Date(),
    }
    const newData = {
      ...data,
      courses: [...data.courses, newCourse],
    }
    saveData(newData)
  }

  const updateCourse = (id: string, updates: Partial<Course>) => {
    const newData = {
      ...data,
      courses: data.courses.map((course) => (course.id === id ? { ...course, ...updates } : course)),
    }
    saveData(newData)
  }

  const deleteCourse = (id: string) => {
    const newData = {
      courses: data.courses.filter((course) => course.id !== id),
      assignments: data.assignments.filter((assignment) => assignment.courseId !== id),
      notes: data.notes.filter((note) => note.courseId !== id),
      exams: data.exams.filter((exam) => exam.courseId !== id), // 刪除課程時也刪除相關考試
    }
    saveData(newData)
  }

  const getCourseById = (id: string) => {
    return data.courses.find((course) => course.id === id)
  }

  const getAssignmentsByCourse = (courseId: string) => {
    return data.assignments.filter((assignment) => assignment.courseId === courseId)
  }

  const getNotesByCourse = (courseId: string) => {
    return data.notes.filter((note) => note.courseId === courseId)
  }

  const addAssignment = (assignment: Omit<Assignment, "id">) => {
    const newAssignment: Assignment = {
      ...assignment,
      id: Date.now().toString(),
    }
    const newData = {
      ...data,
      assignments: [...data.assignments, newAssignment],
    }
    saveData(newData)
  }

  const updateAssignment = (id: string, updates: Partial<Assignment>) => {
    const newData = {
      ...data,
      assignments: data.assignments.map((assignment) =>
        assignment.id === id ? { ...assignment, ...updates } : assignment,
      ),
    }
    saveData(newData)
  }

  const deleteAssignment = (id: string) => {
    const newData = {
      ...data,
      assignments: data.assignments.filter((assignment) => assignment.id !== id),
    }
    saveData(newData)
  }

  const getAssignmentById = (id: string) => {
    return data.assignments.find((assignment) => assignment.id === id)
  }

  const addNote = (note: Omit<Note, "id" | "createdAt" | "updatedAt">) => {
    const newNote: Note = {
      ...note,
      id: Date.now().toString(),
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    const newData = {
      ...data,
      notes: [...data.notes, newNote],
    }
    saveData(newData)
  }

  const updateNote = (id: string, updates: Partial<Omit<Note, "id" | "createdAt">>) => {
    const newData = {
      ...data,
      notes: data.notes.map((note) => (note.id === id ? { ...note, ...updates, updatedAt: new Date() } : note)),
    }
    saveData(newData)
  }

  const deleteNote = (id: string) => {
    const newData = {
      ...data,
      notes: data.notes.filter((note) => note.id !== id),
    }
    saveData(newData)
  }

  const getExamsByCourse = (courseId: string) => {
    return data.exams.filter((exam) => exam.courseId === courseId)
  }

  const addExam = (exam: Omit<Exam, "id" | "createdAt" | "updatedAt">) => {
    const newExam: Exam = {
      ...exam,
      id: Date.now().toString(),
      status: exam.status || "pending",
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    const newData = {
      ...data,
      exams: [...data.exams, newExam],
    }
    saveData(newData)
  }

  const updateExam = (id: string, updates: Partial<Omit<Exam, "id" | "createdAt">>) => {
    const newData = {
      ...data,
      exams: data.exams.map((exam) => (exam.id === id ? { ...exam, ...updates, updatedAt: new Date() } : exam)),
    }
    saveData(newData)
  }

  const deleteExam = (id: string) => {
    const newData = {
      ...data,
      exams: data.exams.filter((exam) => exam.id !== id),
    }
    saveData(newData)
  }

  const getExamById = (id: string) => {
    return data.exams.find((exam) => exam.id === id)
  }

  return {
    courses: data.courses,
    assignments: data.assignments,
    notes: data.notes,
    exams: data.exams, // 導出考試數據
    addCourse,
    updateCourse,
    deleteCourse,
    getCourseById,
    getAssignmentsByCourse,
    getNotesByCourse,
    getExamsByCourse, // 導出考試相關功能
    addAssignment,
    updateAssignment,
    deleteAssignment,
    getAssignmentById,
    addNote,
    updateNote,
    deleteNote,
    addExam, // 導出考試管理功能
    updateExam,
    deleteExam,
    getExamById,
  }
}
