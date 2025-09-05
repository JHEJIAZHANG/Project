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
  courses: [],
  assignments: [],
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
        }))
        parsedData.notes = parsedData.notes.map((note: any) => ({
          ...note,
          createdAt: new Date(note.createdAt),
          updatedAt: new Date(note.updatedAt),
        }))
        parsedData.exams = (parsedData.exams || []).map((exam: any) => ({
          ...exam,
          examDate: new Date(exam.examDate),
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
