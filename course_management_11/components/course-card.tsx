"use client"

import { Card } from "@/components/ui/card"
import { CalendarIcon } from "@/components/icons"
import type { Course } from "@/types/course"

interface CourseCardProps {
  course: Course
  onClick: () => void
}

const DAYS = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]

export function CourseCard({ course, onClick }: CourseCardProps) {
  const formatSchedule = () => {
    return course.schedule.map((slot) => `${DAYS[slot.dayOfWeek]} ${slot.startTime}-${slot.endTime}`).join(", ")
  }

  return (
    <Card
      className="p-5 cursor-pointer hover:shadow-xl hover:scale-[1.02] transition-all duration-200 ease-out hover:bg-white/90 dark:hover:bg-slate-900/90 relative"
      onClick={onClick}
    >
      <div className="absolute left-2 top-4 bottom-4 w-1 rounded-lg" style={{ backgroundColor: course.color }} />
      <div className="flex items-start gap-4 ml-6">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-foreground text-balance text-lg leading-tight">{course.name}</h3>

          {course.instructor && <p className="text-sm text-muted-foreground mt-2 font-medium">{course.instructor}</p>}

          <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <CalendarIcon className="w-3.5 h-3.5" />
              <span className="font-medium">{formatSchedule()}</span>
            </div>
          </div>

          {course.classroom && (
            <div className="flex items-center gap-1.5 mt-2 text-xs text-muted-foreground">
              <span className="font-medium">📍 {course.classroom}</span>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}
