"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { GoogleIcon, RefreshIcon, CheckIcon, AlertTriangleIcon } from "@/components/icons"
import { useCourses } from "@/hooks/use-courses"

interface GoogleClassroomSyncProps {
  onSync?: () => void
}

export function GoogleClassroomSync({ onSync }: GoogleClassroomSyncProps) {
  const { assignments, courses, addAssignment } = useCourses()
  const [isLoading, setIsLoading] = useState(false)
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null)

  // Mock Google Classroom assignments for demonstration
  const mockGoogleClassroomAssignments = [
    {
      id: "gc_new_001",
      title: "JavaScript 進階概念練習",
      description: "學習 Promise、async/await 和 ES6+ 新特性，完成相關練習題目。",
      courseId: "gc-1",
      dueDate: new Date(Date.now() + 12 * 24 * 60 * 60 * 1000),
      googleClassroomId: "gc_assignment_005",
      googleClassroomUrl: "https://classroom.google.com/c/NjA2NTg4NzE2NzNa/a/NjA2NTg4NzE2NzZa",
    },
    {
      id: "gc_new_002",
      title: "圖論演算法實作",
      description: "實作 Dijkstra 最短路徑演算法和 Kruskal 最小生成樹演算法。",
      courseId: "gc-2",
      dueDate: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000),
      googleClassroomId: "gc_assignment_006",
      googleClassroomUrl: "https://classroom.google.com/c/NjA2NTg4NzE2NzRa/a/NjA2NTg4NzE2NzZa",
    },
  ]

  const googleClassroomCourses = courses.filter((course) => course.source === "google_classroom")
  const existingGoogleAssignments = assignments.filter((assignment) => assignment.source === "google_classroom")

  const handleSync = async () => {
    setIsLoading(true)

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Add new assignments from mock data
    mockGoogleClassroomAssignments.forEach((mockAssignment) => {
      const exists = assignments.some((assignment) => assignment.googleClassroomId === mockAssignment.googleClassroomId)

      if (!exists) {
        addAssignment({
          courseId: mockAssignment.courseId,
          title: mockAssignment.title,
          description: mockAssignment.description,
          dueDate: mockAssignment.dueDate,
          status: "pending",
          source: "google_classroom",
          googleClassroomId: mockAssignment.googleClassroomId,
          googleClassroomUrl: mockAssignment.googleClassroomUrl,
        })
      }
    })

    setLastSyncTime(new Date())
    setIsLoading(false)
    onSync?.()
  }

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <GoogleIcon className="w-6 h-6 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold">Google Classroom 同步</h3>
              <p className="text-sm text-muted-foreground">同步 Google Classroom 中的最新作業</p>
            </div>
          </div>

          <Button onClick={handleSync} disabled={isLoading} className="gap-2">
            <RefreshIcon className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            {isLoading ? "同步中..." : "立即同步"}
          </Button>
        </div>

        {/* Sync Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
            <GoogleIcon className="w-5 h-5 text-blue-600" />
            <div>
              <div className="font-medium text-blue-900 dark:text-blue-100">{googleClassroomCourses.length} 個課程</div>
              <div className="text-xs text-blue-700 dark:text-blue-300">已連接 Google Classroom</div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
            <CheckIcon className="w-5 h-5 text-green-600" />
            <div>
              <div className="font-medium text-green-900 dark:text-green-100">
                {existingGoogleAssignments.length} 個作業
              </div>
              <div className="text-xs text-green-700 dark:text-green-300">已同步至系統</div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 rounded-lg bg-orange-50 dark:bg-orange-900/20">
            <AlertTriangleIcon className="w-5 h-5 text-orange-600" />
            <div>
              <div className="font-medium text-orange-900 dark:text-orange-100">
                {mockGoogleClassroomAssignments.length} 個新作業
              </div>
              <div className="text-xs text-orange-700 dark:text-orange-300">等待同步</div>
            </div>
          </div>
        </div>

        {/* Last Sync Time */}
        {lastSyncTime && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <CheckIcon className="w-4 h-4 text-green-600" />
            上次同步時間：{lastSyncTime.toLocaleString("zh-TW")}
          </div>
        )}

        {/* Connected Courses */}
        <div className="space-y-3">
          <h4 className="font-medium">已連接的 Google Classroom 課程</h4>
          <div className="grid gap-2">
            {googleClassroomCourses.map((course) => (
              <div key={course.id} className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: course.color }} />
                  <div>
                    <div className="font-medium">{course.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {course.courseCode} • {course.instructor}
                    </div>
                  </div>
                </div>

                <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-300">
                  {existingGoogleAssignments.filter((a) => a.courseId === course.id).length} 個作業
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Sync Instructions */}
        <div className="p-4 rounded-lg bg-muted/50">
          <h4 className="font-medium mb-2">同步說明</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• 系統會自動檢查 Google Classroom 中的新作業</li>
            <li>• 已同步的作業會保持與 Google Classroom 的連結</li>
            <li>• 可以點擊作業卡片上的「開啟 Classroom」按鈕直接跳轉</li>
            <li>• 建議定期同步以獲取最新的作業資訊</li>
          </ul>
        </div>
      </div>
    </Card>
  )
}
