"use client"

import { Button } from "@/components/ui/button"

interface ExamFiltersProps {
  activeFilter: string
  onFilterChange: (filter: string) => void
  counts: {
    all: number
    upcoming: number
    completed: number
    scheduled: number
  }
}

export function ExamFilters({ activeFilter, onFilterChange, counts }: ExamFiltersProps) {
  const filters = [
    { id: "all", label: "全部", count: counts.all },
    { id: "scheduled", label: "已排程", count: counts.scheduled },
    { id: "upcoming", label: "即將來臨", count: counts.upcoming },
    { id: "completed", label: "已結束", count: counts.completed },
  ]

  return (
    <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
      {filters.map((filter) => (
        <Button
          key={filter.id}
          variant={activeFilter === filter.id ? "default" : "outline"}
          size="sm"
          onClick={() => onFilterChange(filter.id)}
          className="whitespace-nowrap"
        >
          {filter.label} ({filter.count})
        </Button>
      ))}
    </div>
  )
}
