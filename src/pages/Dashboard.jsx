import React from 'react';
import { useApp } from '../contexts/AppContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, CheckSquare, BookOpen, Clock, Plus } from 'lucide-react';

const Dashboard = () => {
  const { getStats, getTodayEvents, getUpcomingDeadlines } = useApp();
  
  const { todoStats, noteStats } = getStats();
  const todayEvents = getTodayEvents();
  const upcomingDeadlines = getUpcomingDeadlines();

  const semesterProgress = {
    currentWeek: 8,
    totalWeeks: 18,
    percentage: Math.round((8 / 18) * 100)
  };

  return (
    <div className="p-6 space-y-6">
      {/* 頁面標題 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">儀表板</h1>
          <p className="text-gray-600 mt-1">歡迎回來！今天是 {new Date().toLocaleDateString('zh-TW')}</p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          快速新增
        </Button>
      </div>

      {/* 學期進度條 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            學期進度
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>第 {semesterProgress.currentWeek} 週 / 共 {semesterProgress.totalWeeks} 週</span>
              <span>{semesterProgress.percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${semesterProgress.percentage}%` }}
              ></div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 主要資訊卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* 今日行程 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              今日行程
            </CardTitle>
            <CardDescription>
              共 {todayEvents.length} 個事件
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {todayEvents.map((event) => (
                <div key={event.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{event.title}</p>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(event.start).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${
                    event.type === 'course' ? 'bg-blue-500' :
                    event.type === 'meeting' ? 'bg-green-500' : 
                    event.type === 'deadline' ? 'bg-red-500' : 'bg-purple-500'
                  }`}></div>
                </div>
              ))}
              {todayEvents.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">今日沒有安排事件</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 待辦事項統計 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckSquare className="h-5 w-5" />
              待辦事項
            </CardTitle>
            <CardDescription>
              進度追蹤
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{todoStats.pending}</p>
                  <p className="text-xs text-gray-500">待完成</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{todoStats.completed}</p>
                  <p className="text-xs text-gray-500">已完成</p>
                </div>
              </div>
              {todoStats.overdue > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-red-700 text-sm font-medium">
                    ⚠️ {todoStats.overdue} 個項目已逾期
                  </p>
                </div>
              )}
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${todoStats.total > 0 ? (todoStats.completed / todoStats.total) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 即將到期 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              即將到期
            </CardTitle>
            <CardDescription>
              需要注意的截止日期
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingDeadlines.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{item.title}</p>
                    <p className="text-xs text-gray-500">{item.dueDate}</p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    item.priority === 'high' ? 'bg-red-100 text-red-700' :
                    item.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {item.priority === 'high' ? '高' : item.priority === 'medium' ? '中' : '低'}
                  </div>
                </div>
              ))}
              {upcomingDeadlines.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">暫無即將到期的項目</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 快速操作區 */}
      <Card>
        <CardHeader>
          <CardTitle>快速操作</CardTitle>
          <CardDescription>常用功能快速入口</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <Calendar className="h-6 w-6" />
              <span className="text-sm">新增事件</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <CheckSquare className="h-6 w-6" />
              <span className="text-sm">新增待辦</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <BookOpen className="h-6 w-6" />
              <span className="text-sm">寫筆記</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <Clock className="h-6 w-6" />
              <span className="text-sm">查看行程</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

