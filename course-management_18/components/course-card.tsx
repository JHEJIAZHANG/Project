"use client"

import { Card } from "@/components/ui/card"
import { CalendarIcon } from "@/components/icons"
import { Users } from "lucide-react"
import { useRouter } from "next/navigation"
import type { Course } from "@/types/course"

interface CourseCardProps {
  course: Course
}

const DAYS = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]

export function CourseCard({ course }: CourseCardProps) {
  const router = useRouter()

  const formatSchedule = () => {
    return course.schedule.map((slot) => `${DAYS[slot.dayOfWeek]} ${slot.startTime}-${slot.endTime}`).join(", ")
  }

  const handleClick = () => {
    router.push(`/course/${course.id}`)
  }

  return (
    <Card
      className="p-5 cursor-pointer hover:shadow-xl hover:scale-[1.02] transition-all duration-200 ease-out hover:bg-white/90 dark:hover:bg-slate-900/90 relative"
      onClick={handleClick}
    >
      <div className="absolute left-2 top-4 bottom-4 w-1 rounded-lg" style={{ backgroundColor: course.color }} />
      <div className="flex items-start gap-4 ml-6">
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <h3 className="font-semibold text-foreground text-balance text-lg leading-tight flex-1 min-w-0">
              {course.name}
            </h3>
            {course.source === "google_classroom" && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 flex-shrink-0">
                Google Classroom
              </span>
            )}
          </div>

          {course.instructor && <p className="text-sm text-muted-foreground mt-2 font-medium">{course.instructor}</p>}

          <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
            {course.schedule.length > 0 && (
              <div className="flex items-center gap-1.5">
                <CalendarIcon className="w-3.5 h-3.5" />
                <span className="font-medium">{formatSchedule()}</span>
              </div>
            )}
            {course.studentCount && course.source === "google_classroom" && (
              <div className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5" />
                <span className="font-medium">{course.studentCount} 位學生</span>
              </div>
            )}
          </div>

          {course.classroom && (
            <div className="flex items-center gap-1.5 mt-2 text-xs text-muted-foreground">
              <span className="font-medium">📍 {course.classroom}</span>
            </div>
          )}

          {course.source === "google_classroom" && course.schedule.length === 0 && (
            <div className="mt-2 text-xs text-muted-foreground italic">可點擊進入課程詳細頁面新增課程時間</div>
          )}
        </div>
      </div>
    </Card>
  )
}
