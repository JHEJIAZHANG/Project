import React, { useState } from 'react';
import { useApp } from '../contexts/AppContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar, CheckSquare, BookOpen, Clock, Plus, X } from 'lucide-react';

const Dashboard = () => {
  const { getStats, getTodayEvents, getUpcomingDeadlines, addEvent, addTodo, addNote } = useApp();
  
  const { todoStats, noteStats } = getStats();
  const todayEvents = getTodayEvents();
  const upcomingDeadlines = getUpcomingDeadlines();

  // 快速操作狀態管理
  const [showAddEvent, setShowAddEvent] = useState(false);
  const [showAddTodo, setShowAddTodo] = useState(false);
  const [showAddNote, setShowAddNote] = useState(false);
  const [showViewSchedule, setShowViewSchedule] = useState(false);

  // 新增事件表單
  const [eventForm, setEventForm] = useState({
    title: '',
    start: '',
    end: '',
    type: 'course',
    location: ''
  });

  // 新增待辦表單
  const [todoForm, setTodoForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
    category: 'personal'
  });

  // 新增筆記表單
  const [noteForm, setNoteForm] = useState({
    title: '',
    content: '',
    category: 'course',
    tags: ''
  });

  // 處理新增事件
  const handleAddEvent = (e) => {
    e.preventDefault();
    if (!eventForm.title || !eventForm.start) return;

    const eventData = {
      title: eventForm.title,
      start: eventForm.start,
      end: eventForm.end || eventForm.start,
      type: eventForm.type,
      color: eventForm.type === 'course' ? 'blue' : 
             eventForm.type === 'meeting' ? 'green' : 
             eventForm.type === 'deadline' ? 'red' : 'purple',
      location: eventForm.location
    };

    addEvent(eventData);
    setEventForm({ title: '', start: '', end: '', type: 'course', location: '' });
    setShowAddEvent(false);
  };

  // 處理新增待辦
  const handleAddTodo = (e) => {
    e.preventDefault();
    if (!todoForm.title) return;

    addTodo(todoForm);
    setTodoForm({ title: '', description: '', priority: 'medium', dueDate: '', category: 'personal' });
    setShowAddTodo(false);
  };

  // 處理新增筆記
  const handleAddNote = (e) => {
    e.preventDefault();
    if (!noteForm.title) return;

    const noteData = {
      title: noteForm.title,
      content: noteForm.content,
      category: noteForm.category,
      tags: noteForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
    };

    addNote(noteData);
    setNoteForm({ title: '', content: '', category: 'course', tags: '' });
    setShowAddNote(false);
  };

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
            {/* 新增事件 */}
            <Dialog open={showAddEvent} onOpenChange={setShowAddEvent}>
              <DialogTrigger asChild>
                <Button variant="outline" className="h-20 flex flex-col gap-2">
                  <Calendar className="h-6 w-6" />
                  <span className="text-sm">新增事件</span>
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>新增事件</DialogTitle>
                  <DialogDescription>建立新的日曆事件</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleAddEvent} className="space-y-4">
                  <div>
                    <Label htmlFor="event-title">事件標題</Label>
                    <Input
                      id="event-title"
                      value={eventForm.title}
                      onChange={(e) => setEventForm({...eventForm, title: e.target.value})}
                      placeholder="輸入事件標題"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="event-start">開始時間</Label>
                      <Input
                        id="event-start"
                        type="datetime-local"
                        value={eventForm.start}
                        onChange={(e) => setEventForm({...eventForm, start: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="event-end">結束時間</Label>
                      <Input
                        id="event-end"
                        type="datetime-local"
                        value={eventForm.end}
                        onChange={(e) => setEventForm({...eventForm, end: e.target.value})}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="event-type">事件類型</Label>
                    <Select value={eventForm.type} onValueChange={(value) => setEventForm({...eventForm, type: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="course">課程</SelectItem>
                        <SelectItem value="meeting">會議</SelectItem>
                        <SelectItem value="deadline">截止日期</SelectItem>
                        <SelectItem value="study">讀書時間</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="event-location">地點</Label>
                    <Input
                      id="event-location"
                      value={eventForm.location}
                      onChange={(e) => setEventForm({...eventForm, location: e.target.value})}
                      placeholder="輸入地點（選填）"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setShowAddEvent(false)}>
                      取消
                    </Button>
                    <Button type="submit">新增事件</Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            {/* 新增待辦 */}
            <Dialog open={showAddTodo} onOpenChange={setShowAddTodo}>
              <DialogTrigger asChild>
                <Button variant="outline" className="h-20 flex flex-col gap-2">
                  <CheckSquare className="h-6 w-6" />
                  <span className="text-sm">新增待辦</span>
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>新增待辦事項</DialogTitle>
                  <DialogDescription>建立新的待辦任務</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleAddTodo} className="space-y-4">
                  <div>
                    <Label htmlFor="todo-title">待辦標題</Label>
                    <Input
                      id="todo-title"
                      value={todoForm.title}
                      onChange={(e) => setTodoForm({...todoForm, title: e.target.value})}
                      placeholder="輸入待辦事項"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="todo-description">詳細描述</Label>
                    <Textarea
                      id="todo-description"
                      value={todoForm.description}
                      onChange={(e) => setTodoForm({...todoForm, description: e.target.value})}
                      placeholder="輸入詳細描述（選填）"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="todo-priority">優先級</Label>
                      <Select value={todoForm.priority} onValueChange={(value) => setTodoForm({...todoForm, priority: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">低</SelectItem>
                          <SelectItem value="medium">中</SelectItem>
                          <SelectItem value="high">高</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="todo-due">截止日期</Label>
                      <Input
                        id="todo-due"
                        type="date"
                        value={todoForm.dueDate}
                        onChange={(e) => setTodoForm({...todoForm, dueDate: e.target.value})}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="todo-category">分類</Label>
                    <Select value={todoForm.category} onValueChange={(value) => setTodoForm({...todoForm, category: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="course">課程</SelectItem>
                        <SelectItem value="personal">個人</SelectItem>
                        <SelectItem value="work">工作</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setShowAddTodo(false)}>
                      取消
                    </Button>
                    <Button type="submit">新增待辦</Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            {/* 寫筆記 */}
            <Dialog open={showAddNote} onOpenChange={setShowAddNote}>
              <DialogTrigger asChild>
                <Button variant="outline" className="h-20 flex flex-col gap-2">
                  <BookOpen className="h-6 w-6" />
                  <span className="text-sm">寫筆記</span>
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>新增筆記</DialogTitle>
                  <DialogDescription>記錄學習心得和重要資訊</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleAddNote} className="space-y-4">
                  <div>
                    <Label htmlFor="note-title">筆記標題</Label>
                    <Input
                      id="note-title"
                      value={noteForm.title}
                      onChange={(e) => setNoteForm({...noteForm, title: e.target.value})}
                      placeholder="輸入筆記標題"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="note-content">筆記內容</Label>
                    <Textarea
                      id="note-content"
                      value={noteForm.content}
                      onChange={(e) => setNoteForm({...noteForm, content: e.target.value})}
                      placeholder="輸入筆記內容..."
                      rows={6}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="note-category">分類</Label>
                      <Select value={noteForm.category} onValueChange={(value) => setNoteForm({...noteForm, category: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="course">課程</SelectItem>
                          <SelectItem value="personal">個人</SelectItem>
                          <SelectItem value="work">工作</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="note-tags">標籤</Label>
                      <Input
                        id="note-tags"
                        value={noteForm.tags}
                        onChange={(e) => setNoteForm({...noteForm, tags: e.target.value})}
                        placeholder="用逗號分隔標籤"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setShowAddNote(false)}>
                      取消
                    </Button>
                    <Button type="submit">新增筆記</Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            {/* 查看行程 */}
            <Button 
              variant="outline" 
              className="h-20 flex flex-col gap-2"
              onClick={() => setShowViewSchedule(true)}
            >
              <Clock className="h-6 w-6" />
              <span className="text-sm">查看行程</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 查看行程對話框 */}
      <Dialog open={showViewSchedule} onOpenChange={setShowViewSchedule}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>今日行程</DialogTitle>
            <DialogDescription>查看今天的安排和事件</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {todayEvents.length > 0 ? (
              <div className="space-y-3">
                {todayEvents.map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${
                        event.color === 'blue' ? 'bg-blue-500' :
                        event.color === 'green' ? 'bg-green-500' :
                        event.color === 'red' ? 'bg-red-500' : 'bg-purple-500'
                      }`}></div>
                      <div>
                        <p className="font-medium text-sm">{event.title}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(event.start).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}
                          {event.end && event.end !== event.start && 
                            ` - ${new Date(event.end).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}`
                          }
                        </p>
                        {event.location && (
                          <p className="text-xs text-gray-400">{event.location}</p>
                        )}
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      event.type === 'course' ? 'bg-blue-100 text-blue-700' :
                      event.type === 'meeting' ? 'bg-green-100 text-green-700' :
                      event.type === 'deadline' ? 'bg-red-100 text-red-700' :
                      'bg-purple-100 text-purple-700'
                    }`}>
                      {event.type === 'course' ? '課程' :
                       event.type === 'meeting' ? '會議' :
                       event.type === 'deadline' ? '截止' : '讀書'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">今日沒有安排事件</p>
              </div>
            )}
          </div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={() => setShowViewSchedule(false)}>
              關閉
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Dashboard;

