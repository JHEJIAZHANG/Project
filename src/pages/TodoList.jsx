import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  CheckSquare, 
  Plus, 
  Calendar,
  Clock,
  Flag,
  Trash2,
  Edit3,
  GripVertical,
  Filter,
  AlertCircle
} from 'lucide-react';

const TodoList = () => {
  const [filter, setFilter] = useState('all'); // 'all', 'pending', 'completed', 'overdue'
  const [isCreating, setIsCreating] = useState(false);

  // 模擬待辦事項資料
  const [todos, setTodos] = useState([
    {
      id: 1,
      title: '完成資料結構作業',
      description: '實作二元搜尋樹的插入和刪除功能',
      completed: false,
      priority: 'high',
      dueDate: '2025-01-10',
      category: 'course',
      createdAt: '2025-01-08'
    },
    {
      id: 2,
      title: '準備期中考',
      description: '複習線性代數第1-5章',
      completed: false,
      priority: 'high',
      dueDate: '2025-01-15',
      category: 'course',
      createdAt: '2025-01-07'
    },
    {
      id: 3,
      title: '更新履歷',
      description: '加入最新的專案經驗',
      completed: true,
      priority: 'medium',
      dueDate: '2025-01-08',
      category: 'personal',
      createdAt: '2025-01-06'
    },
    {
      id: 4,
      title: '買教科書',
      description: '到書店購買下學期的教科書',
      completed: false,
      priority: 'low',
      dueDate: '2025-01-20',
      category: 'personal',
      createdAt: '2025-01-05'
    },
    {
      id: 5,
      title: '繳交報告',
      description: '軟體工程期末報告',
      completed: false,
      priority: 'high',
      dueDate: '2025-01-05', // 已逾期
      category: 'course',
      createdAt: '2025-01-01'
    }
  ]);

  // 優先級設定
  const priorities = {
    high: { label: '高', color: 'red', bgColor: 'bg-red-100', textColor: 'text-red-700' },
    medium: { label: '中', color: 'yellow', bgColor: 'bg-yellow-100', textColor: 'text-yellow-700' },
    low: { label: '低', color: 'green', bgColor: 'bg-green-100', textColor: 'text-green-700' }
  };

  // 檢查是否逾期
  const isOverdue = (dueDate, completed) => {
    if (completed) return false;
    return new Date(dueDate) < new Date();
  };

  // 篩選待辦事項
  const filteredTodos = todos.filter(todo => {
    switch (filter) {
      case 'pending':
        return !todo.completed;
      case 'completed':
        return todo.completed;
      case 'overdue':
        return isOverdue(todo.dueDate, todo.completed);
      default:
        return true;
    }
  });

  // 切換完成狀態
  const toggleTodo = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  // 刪除待辦事項
  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  // 統計資料
  const stats = {
    total: todos.length,
    completed: todos.filter(todo => todo.completed).length,
    pending: todos.filter(todo => !todo.completed).length,
    overdue: todos.filter(todo => isOverdue(todo.dueDate, todo.completed)).length
  };

  // 新增待辦事項表單
  const CreateTodoForm = () => {
    const [newTodo, setNewTodo] = useState({
      title: '',
      description: '',
      priority: 'medium',
      dueDate: '',
      category: 'personal'
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!newTodo.title.trim()) return;

      const todo = {
        id: Date.now(),
        title: newTodo.title,
        description: newTodo.description,
        completed: false,
        priority: newTodo.priority,
        dueDate: newTodo.dueDate,
        category: newTodo.category,
        createdAt: new Date().toISOString().split('T')[0]
      };

      setTodos([todo, ...todos]);
      setNewTodo({ title: '', description: '', priority: 'medium', dueDate: '', category: 'personal' });
      setIsCreating(false);
    };

    return (
      <Card>
        <CardHeader>
          <CardTitle>新增待辦事項</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                placeholder="待辦事項標題"
                value={newTodo.title}
                onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
              />
            </div>
            
            <div>
              <textarea
                placeholder="詳細描述 (選填)"
                value={newTodo.description}
                onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-md h-20 resize-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">優先級</label>
                <select 
                  value={newTodo.priority}
                  onChange={(e) => setNewTodo({...newTodo, priority: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="low">低</option>
                  <option value="medium">中</option>
                  <option value="high">高</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
                <Input
                  type="date"
                  value={newTodo.dueDate}
                  onChange={(e) => setNewTodo({...newTodo, dueDate: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">分類</label>
                <select 
                  value={newTodo.category}
                  onChange={(e) => setNewTodo({...newTodo, category: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="course">課程</option>
                  <option value="personal">個人</option>
                  <option value="work">工作</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2">
              <Button type="submit">新增待辦</Button>
              <Button type="button" variant="outline" onClick={() => setIsCreating(false)}>
                取消
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* 頁面標題 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">待辦事項</h1>
          <p className="text-gray-600 mt-1">管理您的任務和截止日期</p>
        </div>
        
        <Button 
          onClick={() => setIsCreating(!isCreating)}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          新增待辦
        </Button>
      </div>

      {/* 統計卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-600">總計</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.pending}</p>
              <p className="text-sm text-gray-600">待完成</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              <p className="text-sm text-gray-600">已完成</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{stats.overdue}</p>
              <p className="text-sm text-gray-600">已逾期</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 篩選器 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-2">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              全部 ({stats.total})
            </Button>
            <Button
              variant={filter === 'pending' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('pending')}
            >
              待完成 ({stats.pending})
            </Button>
            <Button
              variant={filter === 'completed' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('completed')}
            >
              已完成 ({stats.completed})
            </Button>
            <Button
              variant={filter === 'overdue' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('overdue')}
              className="text-red-600"
            >
              已逾期 ({stats.overdue})
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 新增待辦表單 */}
      {isCreating && <CreateTodoForm />}

      {/* 待辦事項列表 */}
      <div className="space-y-3">
        {filteredTodos.map((todo) => {
          const priorityInfo = priorities[todo.priority];
          const overdue = isOverdue(todo.dueDate, todo.completed);
          
          return (
            <Card key={todo.id} className={`transition-all hover:shadow-md ${
              todo.completed ? 'opacity-75' : ''
            } ${overdue ? 'border-red-200 bg-red-50' : ''}`}>
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  {/* 拖曳手柄 */}
                  <div className="cursor-move text-gray-400 hover:text-gray-600">
                    <GripVertical className="h-5 w-5" />
                  </div>

                  {/* 完成狀態 */}
                  <div className="flex items-center pt-1">
                    <Checkbox
                      checked={todo.completed}
                      onCheckedChange={() => toggleTodo(todo.id)}
                    />
                  </div>

                  {/* 主要內容 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className={`font-medium ${
                          todo.completed ? 'line-through text-gray-500' : 'text-gray-900'
                        }`}>
                          {todo.title}
                        </h3>
                        
                        {todo.description && (
                          <p className={`text-sm mt-1 ${
                            todo.completed ? 'text-gray-400' : 'text-gray-600'
                          }`}>
                            {todo.description}
                          </p>
                        )}

                        {/* 標籤和資訊 */}
                        <div className="flex items-center gap-2 mt-3 flex-wrap">
                          {/* 優先級 */}
                          <Badge className={`${priorityInfo.bgColor} ${priorityInfo.textColor} border-0`}>
                            <Flag className="h-3 w-3 mr-1" />
                            {priorityInfo.label}
                          </Badge>

                          {/* 分類 */}
                          <Badge variant="outline">
                            {todo.category === 'course' ? '課程' : 
                             todo.category === 'personal' ? '個人' : '工作'}
                          </Badge>

                          {/* 截止日期 */}
                          {todo.dueDate && (
                            <Badge 
                              variant="outline" 
                              className={overdue ? 'border-red-500 text-red-700' : ''}
                            >
                              <Calendar className="h-3 w-3 mr-1" />
                              {todo.dueDate}
                              {overdue && <AlertCircle className="h-3 w-3 ml-1" />}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* 操作按鈕 */}
                      <div className="flex gap-1 ml-4">
                        <Button variant="ghost" size="sm">
                          <Edit3 className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => deleteTodo(todo.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 空狀態 */}
      {filteredTodos.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <CheckSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filter === 'all' ? '還沒有待辦事項' : 
               filter === 'completed' ? '還沒有已完成的事項' :
               filter === 'overdue' ? '沒有逾期的事項' : '沒有待完成的事項'}
            </h3>
            <p className="text-gray-600 mb-4">
              {filter === 'all' ? '開始新增您的第一個待辦事項吧！' : '切換到其他篩選器查看更多內容'}
            </p>
            {filter === 'all' && (
              <Button onClick={() => setIsCreating(true)}>
                <Plus className="h-4 w-4 mr-2" />
                建立第一個待辦事項
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* 進度統計 */}
      {stats.total > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>完成進度</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>已完成 {stats.completed} / {stats.total} 項</span>
                <span>{Math.round((stats.completed / stats.total) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(stats.completed / stats.total) * 100}%` }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TodoList;

