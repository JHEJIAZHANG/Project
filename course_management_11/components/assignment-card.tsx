"use client"

import type React from "react"
import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { CheckIcon, ClockIcon, ExclamationIcon } from "@/components/icons"
import type { Assignment, Course } from "@/types/course"
import { getDaysDifferenceTaiwan, isTodayTaiwan, isTomorrowTaiwan } from "@/lib/taiwan-time"

// AssignmentCardProps 為組件參數的型別，包含作業資料、課程資料與多個事件回調函式
interface AssignmentCardProps {
  assignment: Assignment
  course?: Course
  onStatusChange: (id: string, status: Assignment["status"]) => void
  onEdit?: () => void
  onDelete?: () => void
  onViewDetail?: () => void
}

// AssignmentCard 元件，展示單筆作業的卡片 UI，根據作業狀態改變外觀與圖示
export function AssignmentCard({
  assignment,
  course,
  onStatusChange,
  onEdit,
  onDelete,
  onViewDetail,
}: AssignmentCardProps) {
  // 本地狀態：控制刪除確認對話框與描述欄位顯示
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showDescription, setShowDescription] = useState(false)

  // 根據作業狀態及到期日，回傳對應的顏色 class 用於樣式
  const getStatusColor = (status: Assignment["status"], dueDate: Date) => {
    if (status === "completed") {
      return "text-green-700 bg-green-100 border-green-300 dark:text-green-300 dark:bg-green-900/30 dark:border-green-700/50"
    }

    if (status === "pending") {
      return "text-blue-700 bg-blue-100 border-blue-300 dark:text-blue-300 dark:bg-blue-900/30 dark:border-blue-700/50"
    }

    const daysUntilDue = getDaysDifferenceTaiwan(new Date(), dueDate)

    if (daysUntilDue <= 0) {
      return "text-red-700 bg-red-100 border-red-300 dark:text-red-300 dark:bg-red-900/30 dark:border-red-700/50"
    }
    if (daysUntilDue <= 2) {
      return "text-orange-700 bg-orange-100 border-orange-300 dark:text-orange-300 dark:bg-orange-900/30 dark:border-orange-700/50"
    }
    if (daysUntilDue <= 7) {
      return "text-yellow-700 bg-yellow-100 border-yellow-300 dark:text-yellow-300 dark:bg-yellow-900/30 dark:border-yellow-700/50"
    }
    return "text-blue-700 bg-blue-100 border-blue-300 dark:text-blue-300 dark:bg-blue-900/30 dark:border-blue-700/50"
  }

  // 根據狀態返回對應的圖示組件
  const getStatusIcon = (status: Assignment["status"]) => {
    switch (status) {
      case "completed":
        return CheckIcon
      case "overdue":
        return ExclamationIcon
      default:
        return ClockIcon
    }
  }

  // 根據作業狀態回傳對應的中文狀態文字
  const getStatusText = (status: Assignment["status"]) => {
    switch (status) {
      case "completed":
        return "已完成"
      case "overdue":
        return "已逾期"
      default:
        return "進行中"
    }
  }

  // 計算並回傳離截止日的天數描述（含今天、明天、已逾期文字）
  const getDaysUntilDue = () => {
    const daysUntilDue = getDaysDifferenceTaiwan(new Date(), assignment.dueDate)

    if (daysUntilDue < 0) return "已逾期"
    if (isTodayTaiwan(assignment.dueDate)) return "今天到期"
    if (isTomorrowTaiwan(assignment.dueDate)) return "明天到期"
    return `${daysUntilDue}天後到期`
  }

  // 取得目前狀態的圖示組件
  const StatusIcon = getStatusIcon(assignment.status)

  // 處理卡片點擊事件，如果點擊到按鈕或超連結則不執行，如果有描述欄位則顯示/隱藏
  const handleCardClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest("button") || (e.target as HTMLElement).closest("a")) {
      return
    }
    if (assignment.description) {
      setShowDescription(!showDescription)
    }
  }

  // 點擊刪除按鈕時停止事件冒泡，並顯示刪除確認對話框
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    setShowDeleteDialog(true)
  }

  // 確認刪除時觸發傳入的刪除回調，並關閉對話框
  const handleDeleteConfirm = () => {
    onDelete?.()
    setShowDeleteDialog(false)
  }

  // 切換描述欄位的展開與隱藏，避免事件冒泡
  const handleToggleDescription = (e: React.MouseEvent) => {
    e.stopPropagation()
    setShowDescription(!showDescription)
  }

  // JSX 回傳：組件的 UI 結構
  return (
    <>
      <Card
        className={`p-5 cursor-pointer hover:shadow-xl hover:scale-[1.02] transition-all duration-200 ease-out hover:bg-white/90 dark:hover:bg-slate-900/90`}
        onClick={handleCardClick}
      >
        {/* 作業標題區與狀態圖示 */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-4 flex-1">
            <StatusIcon
              className={`w-5 h-5 mt-1 ${getStatusColor(assignment.status, assignment.dueDate).split(" ")[0]}`}
            />
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-foreground text-balance text-lg leading-tight mb-2">
                {assignment.title}
              </h3>
              <div className="flex items-center justify-between">
                {course && <p className="text-sm text-muted-foreground font-medium">{course.name}</p>}
                {assignment.source === "google_classroom" && (
                  <span className="text-xs rounded-full bg-blue-100 text-blue-800 border border-blue-300 font-medium dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-700/50 py-px px-2">
                    Google Classroom
                  </span>
                )}
              </div>
              {/* 描述欄位，點擊可展開與隱藏 */}
              {assignment.description && showDescription && (
                <div className="mt-3">
                  <p className="text-sm text-muted-foreground leading-relaxed">{assignment.description}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 作業狀態及截止時間區塊 */}
        <div
          className={`flex items-center justify-between p-4 rounded-2xl border-2 ${getStatusColor(assignment.status, assignment.dueDate)}`}
        >
          <div>
            <p
              className={`text-sm font-semibold ${getStatusColor(assignment.status, assignment.dueDate).split(" ")[0]}`}
            >
              {getStatusText(assignment.status)}
            </p>
            <p className="text-xs text-muted-foreground mt-1 font-medium">
              {assignment.dueDate.toLocaleDateString("zh-TW")}{" "}
              {assignment.dueDate.toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>

          {/* 若狀態為 pending，顯示距離截止的天數 */}
          {assignment.status === "pending" && (
            <div className="text-right">
              <p className="text-xs font-semibold text-foreground">{getDaysUntilDue()}</p>
            </div>
          )}
        </div>

        {/* 操作按鈕：根據不同狀態顯示標記完成、標記未完成、查看詳情、編輯及刪除 */}
        <div className="flex gap-2 mt-4">
          {(assignment.status === "pending" || assignment.status === "overdue") && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onStatusChange(assignment.id, "completed")}
              className="flex-1 rounded-xl font-medium"
            >
              標記完成
            </Button>
          )}
          {assignment.status === "completed" && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onStatusChange(assignment.id, "pending")}
              className="flex-1 rounded-xl font-medium"
            >
              標記未完成
            </Button>
          )}
          {onViewDetail && (
            <Button
              size="sm"
              variant="outline"
              onClick={onViewDetail}
              className="rounded-xl font-medium bg-transparent"
            >
              查看詳情
            </Button>
          )}
          {onEdit && (
            <Button size="sm" variant="outline" onClick={onEdit} className="rounded-xl font-medium bg-transparent">
              編輯
            </Button>
          )}
          {onDelete && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleDeleteClick}
              className="text-destructive hover:text-destructive bg-transparent rounded-xl font-medium"
            >
              刪除
            </Button>
          )}
        </div>
      </Card>

      {/* 刪除作業時彈跳的確認對話框 */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>確定要刪除這個作業嗎？</AlertDialogTitle>
            <AlertDialogDescription>此操作無法復原。作業「{assignment.title}」將被永久刪除。</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              刪除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
