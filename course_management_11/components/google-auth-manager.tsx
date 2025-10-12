"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { GoogleIcon, AlertTriangleIcon, CheckIcon, RefreshIcon, SettingsIcon, CalendarIcon } from "@/components/icons"
import { ApiService } from "@/services/apiService"
import { openGoogleAuthInLiff } from "@/lib/liff-environment"

interface GoogleAuthManagerProps {
  onAuthSuccess?: () => void
  onAuthError?: (error: string) => void
  showCalendarSync?: boolean
  showClassroomSync?: boolean
}

interface AuthStatus {
  isConnected: boolean
  hasValidCredentials: boolean
  lastError?: string
  connectionType?: 'classroom' | 'calendar' | 'both' | 'none'
}

export function GoogleAuthManager({ 
  onAuthSuccess, 
  onAuthError, 
  showCalendarSync = true, 
  showClassroomSync = true 
}: GoogleAuthManagerProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [authStatus, setAuthStatus] = useState<AuthStatus>({
    isConnected: false,
    hasValidCredentials: false,
    connectionType: 'none'
  })
  const [error, setError] = useState<string | null>(null)

  // 檢查授權狀態
  const checkAuthStatus = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // 檢查 Google API 狀態
      let classroomConnected = false
      let calendarConnected = false

      if (showClassroomSync) {
        try {
          const classroomResponse = await ApiService.getGoogleApiStatus()
          classroomConnected = (classroomResponse.data as any)?.is_connected || false
        } catch (error) {
          console.error('Classroom 狀態檢查失敗:', error)
        }
      }

      if (showCalendarSync) {
        try {
          const calendarResponse = await ApiService.getCalendarEvents({
            time_min: new Date().toISOString(),
            time_max: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
            max_results: 1
          })
          calendarConnected = !calendarResponse.error
        } catch (error) {
          console.error('Calendar 連接測試失敗:', error)
        }
      }

      // 確定連接類型
      let connectionType: AuthStatus['connectionType'] = 'none'
      if (classroomConnected && calendarConnected) {
        connectionType = 'both'
      } else if (classroomConnected) {
        connectionType = 'classroom'
      } else if (calendarConnected) {
        connectionType = 'calendar'
      }

      setAuthStatus({
        isConnected: classroomConnected || calendarConnected,
        hasValidCredentials: classroomConnected || calendarConnected,
        connectionType
      })

    } catch (error) {
      console.error('檢查授權狀態失敗:', error)
      setError('無法檢查授權狀態，請稍後再試')
      setAuthStatus({
        isConnected: false,
        hasValidCredentials: false,
        connectionType: 'none'
      })
    } finally {
      setIsLoading(false)
    }
  }

  // 處理 Google 授權
  const handleGoogleAuth = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // 從後端獲取 Google OAuth URL
      const resp = await ApiService.getGoogleOAuthUrl()
      if (resp.error) {
        throw new Error(resp.error)
      }
      const data: any = resp.data || {}
      const redirectUrl = data.redirectUrl || data.auth_url || ''
      if (!redirectUrl || typeof redirectUrl !== 'string') {
        throw new Error('未取得授權連結')
      }

      // 統一使用共用方法處理（LIFF：外部瀏覽器；非 LIFF：整頁導向）
      openGoogleAuthInLiff(redirectUrl)
      setError('已導向授權頁面，完成後返回應用程式')
      setIsLoading(false)
    } catch (error) {
      console.error('Google 授權失敗:', error)
      setError('授權過程中發生錯誤')
      onAuthError?.('授權過程中發生錯誤')
      setIsLoading(false)
    }
  }

  // 重新授權
  const handleReauth = async () => {
    setError(null)
    await handleGoogleAuth()
  }

  // 初始化時檢查授權狀態
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const getStatusBadge = () => {
    if (!authStatus.isConnected) {
      return <Badge variant="destructive">未連接</Badge>
    }

    switch (authStatus.connectionType) {
      case 'both':
        return <Badge variant="default" className="bg-green-100 text-green-800 border-green-300">完全連接</Badge>
      case 'classroom':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-300">Classroom 已連接</Badge>
      case 'calendar':
        return <Badge variant="secondary" className="bg-purple-100 text-purple-800 border-purple-300">Calendar 已連接</Badge>
      default:
        return <Badge variant="destructive">未連接</Badge>
    }
  }

  const getConnectionMessage = () => {
    if (!authStatus.isConnected) {
      return "需要連接 Google 帳戶以使用完整功能"
    }

    switch (authStatus.connectionType) {
      case 'both':
        return "✅ Google Classroom 和 Calendar 都已成功連接"
      case 'classroom':
        return "⚠️ 僅 Google Classroom 已連接，Calendar 功能可能受限"
      case 'calendar':
        return "⚠️ 僅 Google Calendar 已連接，Classroom 功能可能受限"
      default:
        return "需要連接 Google 帳戶以使用完整功能"
    }
  }

  return (
    <Card className="p-4 sm:p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <GoogleIcon className="w-6 h-6 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold">Google 服務授權</h3>
              <p className="text-sm text-muted-foreground">
                管理 Google Classroom 和 Calendar 的連接狀態
              </p>
            </div>
          </div>
          {getStatusBadge()}
        </div>

        {/* 連接狀態說明 */}
        <div className={`p-3 rounded-lg ${
          authStatus.isConnected 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-yellow-50 border border-yellow-200'
        }`}>
          <p className={`text-sm ${
            authStatus.isConnected ? 'text-green-800' : 'text-yellow-800'
          }`}>
            {getConnectionMessage()}
          </p>
        </div>

        {/* 錯誤訊息 */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 服務狀態詳情 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          {showClassroomSync && (
            <div className={`flex items-center gap-3 p-3 rounded-lg ${
              authStatus.connectionType === 'classroom' || authStatus.connectionType === 'both'
                ? 'bg-blue-50 dark:bg-blue-900/20' 
                : 'bg-gray-50 dark:bg-gray-900/20'
            }`}>
              <GoogleIcon className={`w-5 h-5 ${
                authStatus.connectionType === 'classroom' || authStatus.connectionType === 'both'
                  ? 'text-blue-600' : 'text-gray-400'
              }`} />
              <div>
                <div className={`font-medium ${
                  authStatus.connectionType === 'classroom' || authStatus.connectionType === 'both'
                    ? 'text-blue-900 dark:text-blue-100' 
                    : 'text-gray-600 dark:text-gray-400'
                }`}>
                  Google Classroom
                </div>
                <div className={`text-xs ${
                  authStatus.connectionType === 'classroom' || authStatus.connectionType === 'both'
                    ? 'text-blue-700 dark:text-blue-300' 
                    : 'text-gray-500 dark:text-gray-500'
                }`}>
                  {authStatus.connectionType === 'classroom' || authStatus.connectionType === 'both' 
                    ? '已連接' : '未連接'}
                </div>
              </div>
            </div>
          )}

          {showCalendarSync && (
            <div className={`flex items-center gap-3 p-3 rounded-lg ${
              authStatus.connectionType === 'calendar' || authStatus.connectionType === 'both'
                ? 'bg-purple-50 dark:bg-purple-900/20' 
                : 'bg-gray-50 dark:bg-gray-900/20'
            }`}>
              <CalendarIcon className={`w-5 h-5 ${
                authStatus.connectionType === 'calendar' || authStatus.connectionType === 'both'
                  ? 'text-purple-600' : 'text-gray-400'
              }`} />
              <div>
                <div className={`font-medium ${
                  authStatus.connectionType === 'calendar' || authStatus.connectionType === 'both'
                    ? 'text-purple-900 dark:text-purple-100' 
                    : 'text-gray-600 dark:text-gray-400'
                }`}>
                  Google Calendar
                </div>
                <div className={`text-xs ${
                  authStatus.connectionType === 'calendar' || authStatus.connectionType === 'both'
                    ? 'text-purple-700 dark:text-purple-300' 
                    : 'text-gray-500 dark:text-gray-500'
                }`}>
                  {authStatus.connectionType === 'calendar' || authStatus.connectionType === 'both' 
                    ? '已連接' : '未連接'}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 操作按鈕 */}
        <div className="flex gap-3">
          <Button 
            onClick={authStatus.isConnected ? handleReauth : handleGoogleAuth} 
            disabled={isLoading}
            className="flex-1 gap-2"
          >
            <GoogleIcon className="w-4 h-4" />
            {isLoading ? '處理中...' : authStatus.isConnected ? '重新授權' : '連接 Google 帳戶'}
          </Button>

          <Button 
            onClick={checkAuthStatus} 
            variant="outline" 
            size="sm"
            className="gap-2"
            disabled={isLoading}
          >
            <RefreshIcon className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            檢查狀態
          </Button>
        </div>

        {/* 使用說明 */}
        <div className="p-4 rounded-lg bg-muted/50">
          <h4 className="font-medium mb-2">授權說明</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• <strong>Google Classroom：</strong>同步課程、作業和學生資訊</li>
            <li>• <strong>Google Calendar：</strong>同步日曆事件和行程安排</li>
            <li>• 授權後可以透過 LINE Bot 自然語言查詢同步的資料</li>
            <li>• 我們只會讀取您的資料，不會修改任何內容</li>
            <li>• 您可以隨時在 Google 帳戶設定中撤銷授權</li>
          </ul>
          
          {!authStatus.isConnected && (
            <div className="mt-3 p-3 rounded-lg bg-blue-50 border border-blue-200">
              <p className="text-sm text-blue-800">
                💡 <strong>提示：</strong>首次使用需要授權 Google 帳戶，
                授權完成後即可享受完整的課程管理和行程同步功能。
              </p>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}