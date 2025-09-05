"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import type { Course, Exam } from "@/types/course"

interface ExamFormProps {
  courses: Course[]
  initialData?: Exam
  onSubmit: (examData: Omit<Exam, "id" | "createdAt" | "updatedAt">) => void
  onCancel: () => void
}

export function ExamForm({ courses, initialData, onSubmit, onCancel }: ExamFormProps) {
  const [formData, setFormData] = useState({
    title: initialData?.title || "",
    courseId: initialData?.courseId || "",
    examDate: initialData?.examDate ? initialData.examDate.toISOString().slice(0, 16) : "",
    notificationTime: initialData?.notificationTime ? initialData.notificationTime.toISOString().slice(0, 16) : "",
    duration: initialData?.duration || 60,
    location: initialData?.location || "",
    description: initialData?.description || "",
    type: initialData?.type || ("midterm" as const),
  })

  const [errors, setErrors] = useState<{ [key: string]: string }>({})

  const validateNotificationTime = (notificationTime: string, examDate: string) => {
    if (!notificationTime || !examDate) return ""

    const notificationDate = new Date(notificationTime)
    const examDateObj = new Date(examDate)

    if (notificationDate > examDateObj) {
      return "通知時間不能超過考試日期"
    }
    return ""
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title || !formData.courseId || !formData.examDate) return

    const notificationError = validateNotificationTime(formData.notificationTime, formData.examDate)
    if (notificationError) {
      setErrors({ notificationTime: notificationError })
      return
    }

    onSubmit({
      title: formData.title,
      courseId: formData.courseId,
      examDate: new Date(formData.examDate),
      notificationTime: formData.notificationTime ? new Date(formData.notificationTime) : undefined,
      duration: formData.duration,
      location: formData.location,
      description: formData.description,
      type: formData.type,
    })
  }

  const handleDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    if (value === "") {
      setFormData({ ...formData, duration: 0 })
    } else {
      const numValue = Number.parseInt(value)
      if (!isNaN(numValue) && numValue >= 0) {
        setFormData({ ...formData, duration: Math.min(300, numValue) })
      }
    }
  }

  const handleNotificationTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newNotificationTime = e.target.value
    setFormData({ ...formData, notificationTime: newNotificationTime })

    // 实时验证
    const error = validateNotificationTime(newNotificationTime, formData.examDate)
    setErrors((prev) => ({ ...prev, notificationTime: error }))
  }

  const handleExamDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newExamDate = e.target.value
    setFormData({ ...formData, examDate: newExamDate })

    // 如果有通知时间，重新验证
    if (formData.notificationTime) {
      const error = validateNotificationTime(formData.notificationTime, newExamDate)
      setErrors((prev) => ({ ...prev, notificationTime: error }))
    }
  }

  return (
    <Card className="bg-white p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">考試名稱</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="輸入考試名稱"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">選擇課程</label>
          <select
            value={formData.courseId}
            onChange={(e) => setFormData({ ...formData, courseId: e.target.value })}
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            required
          >
            <option value="">請選擇課程</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">考試類型</label>
          <select
            value={formData.type}
            onChange={(e) =>
              setFormData({ ...formData, type: e.target.value as "midterm" | "final" | "quiz" | "other" })
            }
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="midterm">期中考</option>
            <option value="final">期末考</option>
            <option value="quiz">小考</option>
            <option value="other">其他</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">考試時間</label>
          <input
            type="datetime-local"
            value={formData.examDate}
            onChange={handleExamDateChange}
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">通知時間</label>
          <input
            type="datetime-local"
            value={formData.notificationTime}
            onChange={handleNotificationTimeChange}
            max={formData.examDate}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
              errors.notificationTime ? "border-red-500" : "border-input"
            }`}
          />
          {errors.notificationTime && <p className="text-xs text-red-500 mt-1">{errors.notificationTime}</p>}
          <p className="text-xs text-muted-foreground mt-1">設定通知時間後，考試將從此時間開始在首頁顯示</p>
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">考試時長（分鐘）</label>
          <input
            type="number"
            value={formData.duration || ""}
            onChange={handleDurationChange}
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            min="15"
            max="300"
            placeholder="輸入考試時長"
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">考試地點</label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="輸入考試地點"
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">備註</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            rows={3}
            placeholder="考試相關備註..."
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button type="button" variant="outline" onClick={onCancel} className="flex-1 bg-transparent">
            取消
          </Button>
          <Button type="submit" className="flex-1">
            {initialData ? "更新考試" : "新增考試"}
          </Button>
        </div>
      </form>
    </Card>
  )
}
