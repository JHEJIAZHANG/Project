"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { FileText, Calendar, Camera, Upload } from "lucide-react"
import type { Course } from "@/types/course"

interface CourseFormProps {
  onSubmit: (course: Omit<Course, "id" | "createdAt">) => void
  onCancel: () => void
  onBulkImport?: (courses: Omit<Course, "id" | "createdAt">[]) => void
  initialCourse?: Course
  existingCourses?: Course[] // 用於檢查衝突
}

const COLORS = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"]

const DAYS = [
  { value: 1, label: "週一" },
  { value: 2, label: "週二" },
  { value: 3, label: "週三" },
  { value: 4, label: "週四" },
  { value: 5, label: "週五" },
  { value: 6, label: "週六" },
  { value: 0, label: "週日" },
]

export function CourseForm({ onSubmit, onCancel, onBulkImport, initialCourse, existingCourses = [] }: CourseFormProps) {
  const [formData, setFormData] = useState({
    name: initialCourse?.name || "",
    courseCode: initialCourse?.courseCode || "", // 添加課程代碼欄位
    instructor: initialCourse?.instructor || "",
    classroom: initialCourse?.classroom || "",
    color: initialCourse?.color || COLORS[0],
    schedule: initialCourse?.schedule || [{ dayOfWeek: 1, startTime: "07:00", endTime: "22:00" }],
  })

  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>, type: "csv" | "ical") => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      console.log(`[v0] Importing ${type} file:`, content)
      // TODO: Implement actual parsing logic for CSV/iCal files
      // Mock multiple courses for demonstration
      const mockCourses = [
        {
          name: "匯入課程1",
          courseCode: "IMP001", // 添加課程代碼到模擬數據
          instructor: "教師A",
          classroom: "A101",
          color: COLORS[0],
          schedule: [{ dayOfWeek: 1, startTime: "09:00", endTime: "11:00" }],
        },
        {
          name: "匯入課程2",
          courseCode: "IMP002", // 添加課程代碼到模擬數據
          instructor: "教師B",
          classroom: "B202",
          color: COLORS[1],
          schedule: [{ dayOfWeek: 2, startTime: "14:00", endTime: "16:00" }],
        },
      ]
      onBulkImport?.(mockCourses)
      alert(`成功匯入 ${mockCourses.length} 個課程`)
    }
    reader.readAsText(file)
  }

  const handleImageScan = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const imageUrl = e.target?.result as string
      console.log("[v0] Scanning image:", imageUrl)
      // TODO: Implement OCR/image scanning logic
      // Mock multiple courses from image scan
      const mockCourses = [
        {
          name: "掃描課程1",
          courseCode: "SCAN001", // 添加課程代碼到模擬數據
          instructor: "教師C",
          classroom: "C303",
          color: COLORS[2],
          schedule: [{ dayOfWeek: 3, startTime: "10:00", endTime: "12:00" }],
        },
      ]
      onBulkImport?.(mockCourses)
      alert(`從圖片識別並匯入 ${mockCourses.length} 個課程`)
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name.trim()) return

    // 檢查課程時段衝突：同一星期日，時間區間重疊則視為衝突
    const conflicts: { with: string; day: number; start: string; end: string }[] = []
    for (const slot of formData.schedule) {
      const newStart = slot.startTime
      const newEnd = slot.endTime
      if (!newStart || !newEnd || newStart >= newEnd) {
        alert('請確認上課時間區間有效（開始時間需早於結束時間）')
        return
      }
      existingCourses.forEach((c) => {
        // 編輯時忽略自身
        if (initialCourse && c.id === initialCourse.id) return
        c.schedule.forEach((s) => {
          if (s.dayOfWeek === slot.dayOfWeek) {
            const overlap = !(newEnd <= s.startTime || newStart >= s.endTime)
            if (overlap) {
              conflicts.push({ with: c.name, day: slot.dayOfWeek, start: s.startTime, end: s.endTime })
            }
          }
        })
      })
    }
    if (conflicts.length > 0) {
      const dayLabel = (d: number) => ['週日','週一','週二','週三','週四','週五','週六'][d]
      const msg = conflicts
        .map((c) => `與「${c.with}」在 ${dayLabel(c.day)} ${c.start}~${c.end} 衝突`)
        .join('\n')
      alert(`時段衝突，無法新增/更新：\n${msg}`)
      return
    }

    onSubmit({
      name: formData.name.trim(),
      courseCode: formData.courseCode.trim() || undefined, // 包含課程代碼在提交數據中
      instructor: formData.instructor.trim() || undefined,
      classroom: formData.classroom.trim() || undefined,
      color: formData.color,
      schedule: formData.schedule,
    })
  }

  const addScheduleSlot = () => {
    setFormData((prev) => ({
      ...prev,
      schedule: [...prev.schedule, { dayOfWeek: 1, startTime: "07:00", endTime: "22:00" }],
    }))
  }

  const updateScheduleSlot = (index: number, field: string, value: string | number) => {
    setFormData((prev) => ({
      ...prev,
      schedule: prev.schedule.map((slot, i) => (i === index ? { ...slot, [field]: value } : slot)),
    }))
  }

  const removeScheduleSlot = (index: number) => {
    if (formData.schedule.length > 1) {
      setFormData((prev) => ({
        ...prev,
        schedule: prev.schedule.filter((_, i) => i !== index),
      }))
    }
  }

  const getTimeConstraints = (timeValue: string, isStartTime: boolean) => {
    const hour = Number.parseInt(timeValue.split(":")[0])

    // For AM times (before 12:00), don't allow hours before 7
    if (hour < 12) {
      return { min: "07:00", max: "11:59" }
    }
    // For PM times (12:00 and after), don't allow hours after 22 (10 PM)
    else {
      return { min: "12:00", max: "22:00" }
    }
  }

  return (
    <div className="space-y-6">
      {!initialCourse && (
        <Card className="p-6 bg-blue-50 border-blue-200">
          <div className="flex items-center gap-2 mb-4">
            <Upload className="w-5 h-5 text-blue-600" />
            <Label className="font-bold text-lg text-blue-800">批量匯入課程</Label>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="relative">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => handleFileImport(e, "csv")}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Button type="button" variant="outline" className="w-full bg-white hover:bg-blue-50 border-blue-300">
                <FileText className="w-4 h-4 mr-2" />
                CSV檔案
              </Button>
            </div>

            <div className="relative">
              <input
                type="file"
                accept=".ics,.ical"
                onChange={(e) => handleFileImport(e, "ical")}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Button type="button" variant="outline" className="w-full bg-white hover:bg-blue-50 border-blue-300">
                <Calendar className="w-4 h-4 mr-2" />
                iCal檔案
              </Button>
            </div>

            <div className="relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageScan}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Button type="button" variant="outline" className="w-full bg-white hover:bg-blue-50 border-blue-300">
                <Camera className="w-4 h-4 mr-2" />
                圖片掃描
              </Button>
            </div>
          </div>
        </Card>
      )}

      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Label className="font-bold text-lg">{initialCourse ? "編輯課程" : "手動新增課程"}</Label>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name" className="font-bold">
              課程名稱 *
            </Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="輸入課程名稱"
              required
            />
          </div>

          <div>
            <Label htmlFor="courseCode" className="font-bold">
              課程代碼
            </Label>
            <Input
              id="courseCode"
              value={formData.courseCode}
              onChange={(e) => setFormData((prev) => ({ ...prev, courseCode: e.target.value }))}
              placeholder="輸入課程代碼 (例如: CS101)"
            />
          </div>

          <div>
            <Label htmlFor="instructor" className="font-bold">
              授課教師
            </Label>
            <Input
              id="instructor"
              value={formData.instructor}
              onChange={(e) => setFormData((prev) => ({ ...prev, instructor: e.target.value }))}
              placeholder="輸入教師姓名"
            />
          </div>

          <div>
            <Label htmlFor="classroom" className="font-bold">
              教室
            </Label>
            <Input
              id="classroom"
              value={formData.classroom}
              onChange={(e) => setFormData((prev) => ({ ...prev, classroom: e.target.value }))}
              placeholder="輸入教室位置"
            />
          </div>

          <div>
            <Label className="font-bold">課程顏色</Label>
            <div className="flex gap-2 mt-2">
              {COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  className={`w-8 h-8 rounded-full border-2 ${
                    formData.color === color ? "border-foreground" : "border-border"
                  }`}
                  style={{ backgroundColor: color }}
                  onClick={() => setFormData((prev) => ({ ...prev, color }))}
                />
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <Label className="font-bold">上課時間</Label>
              <Button type="button" variant="outline" size="sm" onClick={addScheduleSlot}>
                新增時段
              </Button>
            </div>

            {formData.schedule.map((slot, index) => (
              <div key={index} className="flex items-center gap-2 mb-2">
                <select
                  value={slot.dayOfWeek}
                  onChange={(e) => updateScheduleSlot(index, "dayOfWeek", Number.parseInt(e.target.value))}
                  className="px-3 py-2 border border-border rounded-md bg-background"
                >
                  {DAYS.map((day) => (
                    <option key={day.value} value={day.value}>
                      {day.label}
                    </option>
                  ))}
                </select>

                <Input
                  type="time"
                  value={slot.startTime}
                  onChange={(e) => updateScheduleSlot(index, "startTime", e.target.value)}
                  className="flex-1"
                  {...getTimeConstraints(slot.startTime, true)}
                />

                <span className="text-muted-foreground">至</span>

                <Input
                  type="time"
                  value={slot.endTime}
                  onChange={(e) => updateScheduleSlot(index, "endTime", e.target.value)}
                  className="flex-1"
                  {...getTimeConstraints(slot.endTime, false)}
                />

                {formData.schedule.length > 1 && (
                  <Button type="button" variant="outline" size="sm" onClick={() => removeScheduleSlot(index)}>
                    刪除
                  </Button>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              {initialCourse ? "更新課程" : "新增課程"}
            </Button>
            <Button type="button" variant="outline" onClick={onCancel} className="flex-1 bg-transparent">
              取消
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
