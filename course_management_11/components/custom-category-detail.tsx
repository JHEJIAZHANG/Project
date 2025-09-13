"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ClockIcon, EditIcon, TrashIcon, CheckIcon, ArrowLeftIcon } from "@/components/icons"
import type { Course } from "@/types/course"
import type { CustomCategoryItem } from "./custom-category-form"
import { getDaysDifferenceTaiwan, isTodayTaiwan, isSameDayTaiwan } from "@/lib/taiwan-time"

interface CustomCategoryDetailProps {
  item: CustomCategoryItem
  course?: Course
  onBack: () => void
  onEdit: () => void
  onDelete: () => void
  onStatusChange: (id: string, status: "pending" | "completed" | "overdue") => void
}

export function CustomCategoryDetail({
  item,
  course,
  onBack,
  onEdit,
  onDelete,
  onStatusChange,
}: CustomCategoryDetailProps) {
  const today = new Date()
  const daysUntilDue = getDaysDifferenceTaiwan(today, item.dueDate)
  const isOverdue = item.status === "overdue" || (item.status === "pending" && daysUntilDue < 0)
  const isDueToday = isSameDayTaiwan(item.dueDate, today)
  const isViewingToday = isTodayTaiwan(today)

  const getStatusColor = () => {
    switch (item.status) {
      case "completed":
        return "bg-green-100 text-green-800 border-green-200"
      case "overdue":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        if (isOverdue) return "bg-red-100 text-red-800 border-red-200"
        if (isDueToday) return "bg-orange-100 text-orange-800 border-orange-200"
        return "bg-blue-100 text-blue-800 border-blue-200"
    }
  }

  const getStatusText = () => {
    if (item.status === "completed") return "已完成"
    if (item.status === "overdue" || isOverdue) return "已逾期"
    if (isDueToday) return isViewingToday ? "今天到期" : "當天到期"
    if (daysUntilDue === 1) return isViewingToday ? "明天到期" : "隔天到期"
    if (daysUntilDue > 1) return `${daysUntilDue}天後到期`
    return "進行中"
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={onBack}>
          <ArrowLeftIcon className="w-4 h-4" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold">{item.title}</h1>
            <Badge variant="outline" className={getStatusColor()}>
              {getStatusText()}
            </Badge>
          </div>
          {course && <p className="text-muted-foreground">{course.name}</p>}
        </div>
        <div className="flex items-center gap-2">
          {item.status === "pending" && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onStatusChange(item.id, "completed")}
              className="text-green-600 hover:text-green-700 hover:bg-green-50"
            >
              <CheckIcon className="w-4 h-4 mr-1" />
              標記完成
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={onEdit}>
            <EditIcon className="w-4 h-4 mr-1" />
            編輯
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onDelete}
            className="text-destructive hover:text-destructive bg-transparent"
          >
            <TrashIcon className="w-4 h-4 mr-1" />
            刪除
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="grid gap-6">
        <Card className="p-6">
          <h2 className="font-semibold mb-4">基本資訊</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">分類</p>
                <p className="text-sm">{item.category}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">狀態</p>
                <Badge variant="outline" className={getStatusColor()}>
                  {getStatusText()}
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">截止日期</p>
                <div className="flex items-center gap-1 text-sm">
                  <ClockIcon className="w-4 h-4" />
                  <span>
                    {item.dueDate.toLocaleDateString("zh-TW")}{" "}
                    {item.dueDate.toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
              </div>
              {item.notificationTime && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">通知時間</p>
                  <div className="flex items-center gap-1 text-sm">
                    <ClockIcon className="w-4 h-4" />
                    <span>
                      {item.notificationTime.toLocaleDateString("zh-TW")}{" "}
                      {item.notificationTime.toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {item.description && (
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">描述</p>
                <div className="bg-muted p-3 rounded-lg">
                  <p className="text-sm whitespace-pre-wrap">{item.description}</p>
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="font-semibold mb-4">時間資訊</h2>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">建立時間</span>
              <span>
                {item.createdAt.toLocaleDateString("zh-TW")}{" "}
                {item.createdAt.toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">最後更新</span>
              <span>
                {item.updatedAt.toLocaleDateString("zh-TW")}{" "}
                {item.updatedAt.toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
