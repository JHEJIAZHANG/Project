import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Calendar as CalendarIcon, 
  ChevronLeft, 
  ChevronRight, 
  Plus,
  Grid3X3,
  List,
  Eye
} from 'lucide-react';

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('month'); // 'day', 'week', 'month'
  const [isGoogleConnected, setIsGoogleConnected] = useState(false);

  // 模擬 Google 日曆事件資料
  const mockEvents = [
    {
      id: 1,
      title: '資料結構課程',
      start: '2025-01-09T09:00:00',
      end: '2025-01-09T10:30:00',
      type: 'course',
      color: 'blue',
      location: '資工系館 101'
    },
    {
      id: 2,
      title: '小組會議',
      start: '2025-01-09T14:00:00',
      end: '2025-01-09T15:00:00',
      type: 'meeting',
      color: 'green',
      location: '圖書館討論室'
    },
    {
      id: 3,
      title: '程式設計作業截止',
      start: '2025-01-10T23:59:00',
      end: '2025-01-10T23:59:00',
      type: 'deadline',
      color: 'red',
      location: ''
    },
    {
      id: 4,
      title: '讀書時間',
      start: '2025-01-11T19:00:00',
      end: '2025-01-11T21:00:00',
      type: 'study',
      color: 'purple',
      location: '圖書館'
    }
  ];

  // 取得當前月份的日期陣列
  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // 添加上個月的日期
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const prevDate = new Date(year, month, -i);
      days.push({ date: prevDate, isCurrentMonth: false });
    }
    
    // 添加當前月份的日期
    for (let day = 1; day <= daysInMonth; day++) {
      days.push({ date: new Date(year, month, day), isCurrentMonth: true });
    }
    
    // 添加下個月的日期以填滿網格
    const remainingDays = 42 - days.length;
    for (let day = 1; day <= remainingDays; day++) {
      days.push({ date: new Date(year, month + 1, day), isCurrentMonth: false });
    }
    
    return days;
  };

  // 取得特定日期的事件
  const getEventsForDate = (date) => {
    return mockEvents.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  // 導航函數
  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  // Google 日曆連接模擬
  const handleGoogleConnect = () => {
    // 這裡會實現 Google OAuth 流程
    setIsGoogleConnected(!isGoogleConnected);
  };

  const monthDays = getDaysInMonth(currentDate);
  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];

  return (
    <div className="p-6 space-y-6">
      {/* 頁面標題和控制項 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">行事曆</h1>
          <p className="text-gray-600 mt-1">管理您的課程和活動安排</p>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Google 日曆連接狀態 */}
          <Button 
            variant={isGoogleConnected ? "default" : "outline"}
            onClick={handleGoogleConnect}
            className="flex items-center gap-2"
          >
            <CalendarIcon className="h-4 w-4" />
            {isGoogleConnected ? 'Google 已連接' : '連接 Google 日曆'}
          </Button>
          
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            新增事件
          </Button>
        </div>
      </div>

      {/* 日曆控制列 */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            {/* 月份導航 */}
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" onClick={() => navigateMonth(-1)}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="text-xl font-semibold">
                {currentDate.getFullYear()}年 {currentDate.getMonth() + 1}月
              </h2>
              <Button variant="outline" size="sm" onClick={() => navigateMonth(1)}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* 視圖切換 */}
            <div className="flex items-center gap-2">
              <Button 
                variant={viewMode === 'day' ? 'default' : 'outline'} 
                size="sm"
                onClick={() => setViewMode('day')}
              >
                <Eye className="h-4 w-4 mr-1" />
                日
              </Button>
              <Button 
                variant={viewMode === 'week' ? 'default' : 'outline'} 
                size="sm"
                onClick={() => setViewMode('week')}
              >
                <List className="h-4 w-4 mr-1" />
                週
              </Button>
              <Button 
                variant={viewMode === 'month' ? 'default' : 'outline'} 
                size="sm"
                onClick={() => setViewMode('month')}
              >
                <Grid3X3 className="h-4 w-4 mr-1" />
                月
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {viewMode === 'month' && (
            <div className="space-y-4">
              {/* 星期標題 */}
              <div className="grid grid-cols-7 gap-1">
                {weekDays.map((day) => (
                  <div key={day} className="p-2 text-center font-medium text-gray-600 bg-gray-50 rounded">
                    {day}
                  </div>
                ))}
              </div>

              {/* 日期網格 */}
              <div className="grid grid-cols-7 gap-1">
                {monthDays.map((dayInfo, index) => {
                  const events = getEventsForDate(dayInfo.date);
                  const isToday = dayInfo.date.toDateString() === new Date().toDateString();
                  
                  return (
                    <div 
                      key={index}
                      className={`min-h-[100px] p-2 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${
                        dayInfo.isCurrentMonth ? 'bg-white' : 'bg-gray-100'
                      } ${isToday ? 'ring-2 ring-blue-500' : ''}`}
                    >
                      <div className={`text-sm font-medium mb-1 ${
                        dayInfo.isCurrentMonth ? 'text-gray-900' : 'text-gray-400'
                      } ${isToday ? 'text-blue-600' : ''}`}>
                        {dayInfo.date.getDate()}
                      </div>
                      
                      {/* 事件列表 */}
                      <div className="space-y-1">
                        {events.slice(0, 2).map((event) => (
                          <div 
                            key={event.id}
                            className={`text-xs p-1 rounded truncate ${
                              event.color === 'blue' ? 'bg-blue-100 text-blue-700' :
                              event.color === 'green' ? 'bg-green-100 text-green-700' :
                              event.color === 'red' ? 'bg-red-100 text-red-700' :
                              'bg-purple-100 text-purple-700'
                            }`}
                          >
                            {event.title}
                          </div>
                        ))}
                        {events.length > 2 && (
                          <div className="text-xs text-gray-500">
                            +{events.length - 2} 更多
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {viewMode === 'week' && (
            <div className="space-y-4">
              <p className="text-center text-gray-500">週視圖開發中...</p>
            </div>
          )}

          {viewMode === 'day' && (
            <div className="space-y-4">
              <p className="text-center text-gray-500">日視圖開發中...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 事件類型說明 */}
      <Card>
        <CardHeader>
          <CardTitle>事件類型</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-sm">課程</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-sm">會議</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span className="text-sm">截止日期</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-purple-500 rounded"></div>
              <span className="text-sm">讀書時間</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 即將到來的事件 */}
      <Card>
        <CardHeader>
          <CardTitle>即將到來的事件</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockEvents.slice(0, 3).map((event) => (
              <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    event.color === 'blue' ? 'bg-blue-500' :
                    event.color === 'green' ? 'bg-green-500' :
                    event.color === 'red' ? 'bg-red-500' :
                    'bg-purple-500'
                  }`}></div>
                  <div>
                    <p className="font-medium text-sm">{event.title}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(event.start).toLocaleDateString('zh-TW')} {new Date(event.start).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                    {event.location && (
                      <p className="text-xs text-gray-400">{event.location}</p>
                    )}
                  </div>
                </div>
                <Badge variant="outline">
                  {event.type === 'course' ? '課程' :
                   event.type === 'meeting' ? '會議' :
                   event.type === 'deadline' ? '截止' : '讀書'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Calendar;

