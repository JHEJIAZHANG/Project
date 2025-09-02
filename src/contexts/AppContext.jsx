import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  // 筆記狀態
  const [notes, setNotes] = useState([
    {
      id: 1,
      title: '資料結構 - 樹狀結構',
      content: '二元樹的基本概念和操作方法...',
      category: 'course',
      createdAt: '2025-01-08',
      updatedAt: '2025-01-09',
      tags: ['資料結構', '演算法', '樹']
    },
    {
      id: 2,
      title: '期末專題想法',
      content: '想做一個校園生活管理系統，功能包括...',
      category: 'personal',
      createdAt: '2025-01-07',
      updatedAt: '2025-01-08',
      tags: ['專題', '想法', '規劃']
    },
    {
      id: 3,
      title: '實習面試準備',
      content: '需要準備的技術問題和作品集...',
      category: 'work',
      createdAt: '2025-01-06',
      updatedAt: '2025-01-07',
      tags: ['面試', '實習', '準備']
    },
    {
      id: 4,
      title: '線性代數筆記',
      content: '矩陣運算和向量空間的重要概念...',
      category: 'course',
      createdAt: '2025-01-05',
      updatedAt: '2025-01-06',
      tags: ['數學', '線性代數', '矩陣']
    }
  ]);

  // 待辦事項狀態
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

  // 日曆事件狀態
  const [events, setEvents] = useState([
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
  ]);

  // Google 日曆連接狀態
  const [isGoogleConnected, setIsGoogleConnected] = useState(false);

  // Google Classroom 連接狀態
  const [isClassroomConnected, setIsClassroomConnected] = useState(false);

  // 課程狀態
  const [courses, setCourses] = useState([]);

  // 通知狀態
  const [notifications, setNotifications] = useState([
    { id: 1, title: '資料結構作業即將到期', time: '2小時前', type: 'deadline' },
    { id: 2, title: '小組會議提醒', time: '1天前', type: 'event' }
  ]);

  // 筆記操作函數
  const addNote = (noteData) => {
    const newNote = {
      id: Date.now(),
      ...noteData,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0]
    };
    setNotes([newNote, ...notes]);
  };

  const updateNote = (id, noteData) => {
    setNotes(notes.map(note => 
      note.id === id 
        ? { ...note, ...noteData, updatedAt: new Date().toISOString().split('T')[0] }
        : note
    ));
  };

  const deleteNote = (id) => {
    setNotes(notes.filter(note => note.id !== id));
  };

  // 待辦事項操作函數
  const addTodo = (todoData) => {
    const newTodo = {
      id: Date.now(),
      ...todoData,
      completed: false,
      createdAt: new Date().toISOString().split('T')[0]
    };
    setTodos([newTodo, ...todos]);
  };

  const updateTodo = (id, todoData) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, ...todoData } : todo
    ));
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  // 事件操作函數
  const addEvent = (eventData) => {
    const newEvent = {
      id: Date.now(),
      ...eventData
    };
    setEvents([...events, newEvent]);
  };

  const updateEvent = (id, eventData) => {
    setEvents(events.map(event => 
      event.id === id ? { ...event, ...eventData } : event
    ));
  };

  const deleteEvent = (id) => {
    setEvents(events.filter(event => event.id !== id));
  };

  // 通知操作函數
  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now(),
      ...notification,
      time: '剛剛'
    };
    setNotifications([newNotification, ...notifications]);
  };

  const removeNotification = (id) => {
    setNotifications(notifications.filter(notification => notification.id !== id));
  };

  // 統計數據計算
  const getStats = () => {
    const todoStats = {
      total: todos.length,
      completed: todos.filter(todo => todo.completed).length,
      pending: todos.filter(todo => !todo.completed).length,
      overdue: todos.filter(todo => {
        if (todo.completed) return false;
        return new Date(todo.dueDate) < new Date();
      }).length
    };

    const noteStats = {
      total: notes.length,
      course: notes.filter(note => note.category === 'course').length,
      personal: notes.filter(note => note.category === 'personal').length,
      work: notes.filter(note => note.category === 'work').length
    };

    return { todoStats, noteStats };
  };

  // 取得今日事件
  const getTodayEvents = () => {
    const today = new Date().toDateString();
    return events.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate.toDateString() === today;
    });
  };

  // 取得即將到期的項目
  const getUpcomingDeadlines = () => {
    const now = new Date();
    const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    return todos
      .filter(todo => !todo.completed && new Date(todo.dueDate) <= nextWeek)
      .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
      .slice(0, 5);
  };

  const value = {
    // 狀態
    notes,
    todos,
    events,
    notifications,
    isGoogleConnected,
    isClassroomConnected,
    courses,
    
    // 筆記操作
    addNote,
    updateNote,
    deleteNote,
    
    // 待辦事項操作
    addTodo,
    updateTodo,
    toggleTodo,
    deleteTodo,
    
    // 事件操作
    addEvent,
    updateEvent,
    deleteEvent,
    
    // 通知操作
    addNotification,
    removeNotification,
    
    // Google 服務
    setIsGoogleConnected,
    setIsClassroomConnected,
    setCourses,
    
    // 統計和查詢
    getStats,
    getTodayEvents,
    getUpcomingDeadlines
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

