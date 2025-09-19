"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { UserIcon, SettingsIcon, GoogleIcon, ChevronRightIcon } from "@/components/icons"
import { PageHeader } from "@/components/page-header"

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  isLoggedIn: boolean
}

interface SemesterSettings {
  totalWeeks: number
  startDate: string
  endDate: string
}

interface NotificationSettings {
  assignmentReminders: boolean
  examReminders: boolean
  assignmentReminderTiming: string
  browserNotifications: boolean
  doNotDisturbEnabled: boolean
  doNotDisturbStart: string
  doNotDisturbEnd: string
}

interface ProfileContentProps {
  user?: User
  onUserChange?: (user: User) => void
}

export function ProfileContent({ user: propUser, onUserChange }: ProfileContentProps) {
  const [isGoogleClassroomConnected, setIsGoogleClassroomConnected] = useState(false)
  const [showSemesterSettings, setShowSemesterSettings] = useState(false)
  const [showNotificationSettings, setShowNotificationSettings] = useState(false)

  const [semesterSettings, setSemesterSettings] = useState<SemesterSettings>({
    totalWeeks: 18,
    startDate: "2025-09-01",
    endDate: "2025-12-31",
  })

  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    assignmentReminders: true,
    examReminders: true,
    assignmentReminderTiming: "1day",
    browserNotifications: true,
    doNotDisturbEnabled: false,
    doNotDisturbStart: "22:00",
    doNotDisturbEnd: "08:00",
  })

  useEffect(() => {
    const savedSettings = localStorage.getItem("notificationSettings")
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings)
        setNotificationSettings(parsedSettings)
      } catch (error) {
        console.error("Failed to parse notification settings:", error)
      }
    }
  }, [])

  useEffect(() => {
    localStorage.setItem("notificationSettings", JSON.stringify(notificationSettings))
    window.dispatchEvent(
      new CustomEvent("notificationSettingsChanged", {
        detail: notificationSettings,
      }),
    )
  }, [notificationSettings])

  const handleGoogleClassroomConnect = () => {
    setIsGoogleClassroomConnected(!isGoogleClassroomConnected)

    if (!isGoogleClassroomConnected) {
      alert("已成功連接 Google Classroom！")
    } else {
      alert("已中斷 Google Classroom 連接")
    }
  }

  const handleSemesterSettingsSave = () => {
    setShowSemesterSettings(false)
    alert("學期設定已儲存！")
  }

  const handleTestNotification = () => {
    if (notificationSettings.browserNotifications) {
      if (Notification.permission === "default") {
        Notification.requestPermission().then((permission) => {
          if (permission === "granted") {
            new Notification("測試通知", {
              body: "這是一個測試推播通知",
              icon: "/favicon.ico",
            })
          }
        })
      } else if (Notification.permission === "granted") {
        new Notification("測試通知", {
          body: "這是一個測試推播通知",
          icon: "/favicon.ico",
        })
      }
    }

    if (!notificationSettings.browserNotifications) {
      alert("請先啟用瀏覽器通知")
    }
  }

  if (showSemesterSettings) {
    return (
      <div>
        <PageHeader title="學期設定" onBack={() => setShowSemesterSettings(false)} />

        <Card className="p-6">
          <div className="space-y-4">
            <div>
              <Label htmlFor="totalWeeks">學期總週數</Label>
              <Input
                id="totalWeeks"
                type="number"
                value={semesterSettings.totalWeeks}
                onChange={(e) =>
                  setSemesterSettings({
                    ...semesterSettings,
                    totalWeeks: Number.parseInt(e.target.value) || 18,
                  })
                }
                min="1"
                max="52"
              />
            </div>

            <div>
              <Label htmlFor="startDate">學期開始日期</Label>
              <Input
                id="startDate"
                type="date"
                value={semesterSettings.startDate}
                onChange={(e) =>
                  setSemesterSettings({
                    ...semesterSettings,
                    startDate: e.target.value,
                  })
                }
              />
            </div>

            <div>
              <Label htmlFor="endDate">學期結束日期</Label>
              <Input
                id="endDate"
                type="date"
                value={semesterSettings.endDate}
                onChange={(e) =>
                  setSemesterSettings({
                    ...semesterSettings,
                    endDate: e.target.value,
                  })
                }
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={handleSemesterSettingsSave} className="flex-1">
                儲存設定
              </Button>
              <Button variant="outline" onClick={() => setShowSemesterSettings(false)} className="flex-1">
                取消
              </Button>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  if (showNotificationSettings) {
    return (
      <div>
        <PageHeader title="通知設定" onBack={() => setShowNotificationSettings(false)} />

        <div className="space-y-6 pb-20 lg:pb-0">
          <div>
            <h3 className="font-bold text-lg mb-3">一般通知</h3>
            <Card className="p-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">作業提醒</p>
                    <p className="text-sm text-muted-foreground">作業截止前提醒</p>
                  </div>
                  <Switch
                    checked={notificationSettings.assignmentReminders}
                    onCheckedChange={(checked) =>
                      setNotificationSettings({
                        ...notificationSettings,
                        assignmentReminders: checked,
                      })
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">考試提醒</p>
                    <p className="text-sm text-muted-foreground">考試前提醒</p>
                  </div>
                  <Switch
                    checked={notificationSettings.examReminders}
                    onCheckedChange={(checked) =>
                      setNotificationSettings({
                        ...notificationSettings,
                        examReminders: checked,
                      })
                    }
                  />
                </div>
              </div>
            </Card>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-3">提醒時間</h3>
            <Card className="p-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="reminderTiming" className="font-medium text-base">
                  待辦事項提醒時機
                </Label>
                <Select
                  value={notificationSettings.assignmentReminderTiming}
                  onValueChange={(value) =>
                    setNotificationSettings({
                      ...notificationSettings,
                      assignmentReminderTiming: value,
                    })
                  }
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="15min">15分鐘前</SelectItem>
                    <SelectItem value="30min">30分鐘前</SelectItem>
                    <SelectItem value="1hour">1小時前</SelectItem>
                    <SelectItem value="2hours">2小時前</SelectItem>
                    <SelectItem value="1day">1天前</SelectItem>
                    <SelectItem value="2days">2天前</SelectItem>
                    <SelectItem value="1week">1週前</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </Card>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-3">通知方式</h3>
            <Card className="p-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">瀏覽器推播</p>
                    <p className="text-sm text-muted-foreground">網頁推播通知</p>
                  </div>
                  <Switch
                    checked={notificationSettings.browserNotifications}
                    onCheckedChange={(checked) =>
                      setNotificationSettings({
                        ...notificationSettings,
                        browserNotifications: checked,
                      })
                    }
                  />
                </div>
              </div>
            </Card>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-3">勿擾時間</h3>
            <Card className="p-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">啟用勿擾模式</p>
                    <p className="text-sm text-muted-foreground">特定時間內不接收通知</p>
                  </div>
                  <Switch
                    checked={notificationSettings.doNotDisturbEnabled}
                    onCheckedChange={(checked) =>
                      setNotificationSettings({
                        ...notificationSettings,
                        doNotDisturbEnabled: checked,
                      })
                    }
                  />
                </div>

                {notificationSettings.doNotDisturbEnabled && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="startTime">開始時間</Label>
                      <Input
                        id="startTime"
                        type="time"
                        value={notificationSettings.doNotDisturbStart}
                        onChange={(e) =>
                          setNotificationSettings({
                            ...notificationSettings,
                            doNotDisturbStart: e.target.value,
                          })
                        }
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="endTime">結束時間</Label>
                      <Input
                        id="endTime"
                        type="time"
                        value={notificationSettings.doNotDisturbEnd}
                        onChange={(e) =>
                          setNotificationSettings({
                            ...notificationSettings,
                            doNotDisturbEnd: e.target.value,
                          })
                        }
                        className="mt-1"
                      />
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>

          <div className="flex flex-col gap-3">
            <Button onClick={handleTestNotification} variant="outline" className="w-full bg-transparent">
              測試推播通知
            </Button>

            <div className="flex gap-2">
              <Button
                onClick={() => {
                  setShowNotificationSettings(false)
                  alert("通知設定已儲存！")
                }}
                className="flex-1"
              >
                儲存設定
              </Button>
              <Button variant="outline" onClick={() => setShowNotificationSettings(false)} className="flex-1">
                取消
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      <PageHeader
        title={
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <UserIcon className="w-5 h-5 text-gray-500" />
            </div>
            我的
          </div>
        }
        subtitle="個人資料與設定"
      />

      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <GoogleIcon className="w-8 h-8" />
            <div>
              <h3 className="font-semibold">Google Classroom</h3>
              <p className="text-sm text-muted-foreground">{isGoogleClassroomConnected ? "已連接" : "未連接"}</p>
            </div>
          </div>

          <Button
            variant={isGoogleClassroomConnected ? "outline" : "default"}
            size="sm"
            onClick={handleGoogleClassroomConnect}
          >
            {isGoogleClassroomConnected ? "中斷連接" : "開始連接"}
          </Button>
        </div>

        {isGoogleClassroomConnected && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg">
            <p className="text-sm text-green-700">✓ 已成功連接 Google Classroom，可以同步課程和作業資料</p>
          </div>
        )}
      </Card>

      <Card className="p-6">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <SettingsIcon className="w-5 h-5" />
          設定
        </h3>

        <div className="space-y-1">
          <button
            onClick={() => setShowSemesterSettings(true)}
            className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
          >
            <div className="text-left">
              <p className="font-medium">學期設定</p>
              <p className="text-sm text-muted-foreground">
                {semesterSettings.totalWeeks}週 • {semesterSettings.startDate} 至 {semesterSettings.endDate}
              </p>
            </div>
            <ChevronRightIcon className="w-5 h-5 text-muted-foreground" />
          </button>

          <Separator />

          <button
            onClick={() => setShowNotificationSettings(true)}
            className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
          >
            <div className="text-left">
              <p className="font-medium">通知設定</p>
              <p className="text-sm text-muted-foreground">管理提醒和通知偏好</p>
            </div>
            <ChevronRightIcon className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>
      </Card>

      <Card className="p-6">
        <div className="text-center text-muted-foreground">
          <p className="text-sm">課程管理系統</p>
          <p className="text-xs mt-1">版本 1.0.0</p>
        </div>
      </Card>
    </div>
  )
}

export function getNotificationSettings(): NotificationSettings {
  if (typeof window === "undefined") {
    return {
      assignmentReminders: true,
      examReminders: true,
      assignmentReminderTiming: "1day",
      browserNotifications: true,
      doNotDisturbEnabled: false,
      doNotDisturbStart: "22:00",
      doNotDisturbEnd: "08:00",
    }
  }

  const savedSettings = localStorage.getItem("notificationSettings")
  if (savedSettings) {
    try {
      return JSON.parse(savedSettings)
    } catch (error) {
      console.error("Failed to parse notification settings:", error)
    }
  }

  return {
    assignmentReminders: true,
    examReminders: true,
    assignmentReminderTiming: "1day",
    browserNotifications: true,
    doNotDisturbEnabled: false,
    doNotDisturbStart: "22:00",
    doNotDisturbEnd: "08:00",
  }
}
