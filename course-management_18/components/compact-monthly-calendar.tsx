"use client"

import { useState, useEffect } from "react"
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface CalendarEvent {
  id: string
  title: string
  date: Date
  time: string // Added time field for events
  type: "assignment" | "exam" | "course" | "note"
  color: string
}

interface CompactMonthlyCalendarProps {
  className?: string
  selectedDate?: Date
  onDateSelect?: (date: Date) => void
}

export function CompactMonthlyCalendar({ className, selectedDate, onDateSelect }: CompactMonthlyCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date())

  const defaultEvents: CalendarEvent[] = [
    {
      id: "1",
      title: "數學作業",
      date: new Date(2024, 11, 15), // December 15, 2024
      time: "09:00", // Added time for each event
      type: "assignment",
      color: "bg-blue-500",
    },
    {
      id: "2",
      title: "英文考試",
      date: new Date(2024, 11, 20), // December 20, 2024
      time: "14:00",
      type: "exam",
      color: "bg-red-500",
    },
    {
      id: "3",
      title: "物理課程",
      date: new Date(2024, 11, 18), // December 18, 2024
      time: "10:30",
      type: "course",
      color: "bg-green-500",
    },
    {
      id: "4",
      title: "化學筆記",
      date: new Date(2024, 11, 22), // December 22, 2024
      time: "16:00",
      type: "note",
      color: "bg-yellow-500",
    },
    {
      id: "5",
      title: "歷史報告",
      date: new Date(2024, 11, 25), // December 25, 2024
      time: "11:00",
      type: "assignment",
      color: "bg-blue-500",
    },
    {
      id: "6",
      title: "生物實驗",
      date: new Date(2024, 11, 28), // December 28, 2024
      time: "13:30",
      type: "course",
      color: "bg-green-500",
    },
    {
      id: "7",
      title: "英文作業",
      date: new Date(2024, 11, 15), // December 15, 2024 - same day as math
      time: "15:30",
      type: "assignment",
      color: "bg-blue-500",
    },
    {
      id: "8",
      title: "科學筆記整理",
      date: new Date(2024, 11, 15), // December 15, 2024 - same day
      time: "19:00",
      type: "note",
      color: "bg-yellow-500",
    },
  ]

  useEffect(() => {
    if (selectedDate) {
      setCurrentDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1))
    }
  }, [selectedDate])

  const today = new Date()
  const currentMonth = currentDate.getMonth()
  const currentYear = currentDate.getFullYear()

  // Get first day of month and number of days
  const firstDayOfMonth = new Date(currentYear, currentMonth, 1)
  const lastDayOfMonth = new Date(currentYear, currentMonth + 1, 0)
  const daysInMonth = lastDayOfMonth.getDate()
  const startingDayOfWeek = firstDayOfMonth.getDay()

  // Adjust for Monday start (0 = Sunday, 1 = Monday, etc.)
  const adjustedStartDay = startingDayOfWeek === 0 ? 6 : startingDayOfWeek - 1

  const monthNames = [
    "一月",
    "二月",
    "三月",
    "四月",
    "五月",
    "六月",
    "七月",
    "八月",
    "九月",
    "十月",
    "十一月",
    "十二月",
  ]

  const dayNames = ["一", "二", "三", "四", "五", "六", "日"]

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentYear, currentMonth - 1, 1))
  }

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentYear, currentMonth + 1, 1))
  }

  const isToday = (day: number) => {
    return today.getDate() === day && today.getMonth() === currentMonth && today.getFullYear() === currentYear
  }

  const isSelected = (day: number) => {
    if (!selectedDate) return false
    return (
      selectedDate.getDate() === day &&
      selectedDate.getMonth() === currentMonth &&
      selectedDate.getFullYear() === currentYear
    )
  }

  const getEventsForDay = (day: number) => {
    return defaultEvents.filter(
      (event) =>
        event.date.getDate() === day &&
        event.date.getMonth() === currentMonth &&
        event.date.getFullYear() === currentYear,
    )
  }

  const getDailySchedule = (date: Date) => {
    const dayEvents = defaultEvents.filter(
      (event) =>
        event.date.getDate() === date.getDate() &&
        event.date.getMonth() === date.getMonth() &&
        event.date.getFullYear() === date.getFullYear() &&
        event.type !== "course", // Exclude courses
    )

    // Sort by time
    return dayEvents.sort((a, b) => a.time.localeCompare(b.time))
  }

  const handleDateClick = (day: number) => {
    if (onDateSelect) {
      const newDate = new Date(currentYear, currentMonth, day)
      onDateSelect(newDate)
    }
  }

  // Generate calendar days
  const calendarDays = []

  // Add empty cells for days before month starts
  for (let i = 0; i < adjustedStartDay; i++) {
    calendarDays.push(null)
  }

  // Add days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push(day)
  }

  return (
    <div className={className}>
      <Card className="p-3">
        {/* Header with month navigation */}
        <div className="flex items-center justify-between mb-3">
          <Button variant="ghost" size="sm" onClick={goToPreviousMonth} className="h-7 w-7 p-0">
            <ChevronLeftIcon className="h-4 w-4" />
          </Button>

          <h3 className="font-medium text-sm">
            {currentYear}年 {monthNames[currentMonth]}
          </h3>

          <Button variant="ghost" size="sm" onClick={goToNextMonth} className="h-7 w-7 p-0">
            <ChevronRightIcon className="h-4 w-4" />
          </Button>
        </div>

        {/* Day headers */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {dayNames.map((day) => (
            <div key={day} className="text-center text-xs font-medium text-foreground/70 py-1">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className="grid grid-cols-7 gap-1">
          {calendarDays.map((day, index) => {
            const dayEvents = day ? getEventsForDay(day) : []

            return (
              <div
                key={index}
                className={`
                  aspect-square flex flex-col items-start justify-start text-xs rounded p-1 relative
                  ${day === null ? "" : "hover:bg-accent cursor-pointer"}
                  ${day === null ? "text-transparent" : ""}
                `}
                onClick={day ? () => handleDateClick(day) : undefined}
              >
                {day && (
                  <>
                    <span
                      className={`
                      text-foreground
                      ${isToday(day) ? "border border-primary rounded-full w-5 h-5 flex items-center justify-center text-primary font-medium" : ""}
                      ${isSelected(day) && !isToday(day) ? "bg-primary text-primary-foreground rounded-full w-5 h-5 flex items-center justify-center font-medium" : ""}
                    `}
                    >
                      {day}
                    </span>
                    {dayEvents.length > 0 && (
                      <div className="flex flex-wrap gap-0.5 mt-0.5">
                        {dayEvents.slice(0, 3).map((event, eventIndex) => (
                          <div
                            key={event.id}
                            className={`w-1.5 h-1.5 rounded-full ${event.color}`}
                            title={event.title}
                          />
                        ))}
                        {dayEvents.length > 3 && (
                          <div
                            className="w-1.5 h-1.5 rounded-full bg-gray-400"
                            title={`+${dayEvents.length - 3} more`}
                          />
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            )
          })}
        </div>
      </Card>

      {selectedDate && (
        <Card className="p-3 mt-3">
          <h4 className="font-medium text-sm mb-3">
            {selectedDate.getMonth() + 1}月{selectedDate.getDate()}日 行程
          </h4>
          <div className="space-y-2">
            {getDailySchedule(selectedDate).length > 0 ? (
              getDailySchedule(selectedDate).map((event) => (
                <div key={event.id} className="flex items-center gap-3 p-2 rounded-lg bg-muted/50">
                  <div className={`w-3 h-3 rounded-full ${event.color}`} />
                  <div className="flex-1">
                    <div className="text-sm font-medium">{event.title}</div>
                    <div className="text-xs text-muted-foreground">{event.time}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-muted-foreground text-center py-4">今日無行程</div>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}
