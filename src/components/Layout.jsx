import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Home, 
  Calendar, 
  BookOpen, 
  CheckSquare, 
  Menu, 
  X,
  Bell,
  Settings,
  User,
  LogOut,
  Sun,
  Moon,
  GraduationCap
} from 'lucide-react';

const Layout = ({ children, currentPage, onNavigate }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, title: '資料結構作業即將到期', time: '2小時前', type: 'deadline' },
    { id: 2, title: '小組會議提醒', time: '1天前', type: 'event' }
  ]);

  // 導航項目
  const navigationItems = [
    {
      id: 'dashboard',
      name: '儀表板',
      icon: Home,
      badge: null
    },
    {
      id: 'calendar',
      name: '行事曆',
      icon: Calendar,
      badge: null
    },
    {
      id: 'courses',
      name: '課程',
      icon: GraduationCap,
      badge: 3
    },
    {
      id: 'notes',
      name: '筆記',
      icon: BookOpen,
      badge: 12
    },
    {
      id: 'todos',
      name: '待辦事項',
      icon: CheckSquare,
      badge: 5
    }
  ];

  const handleNavigation = (pageId) => {
    onNavigate(pageId);
    setSidebarOpen(false);
  };

  const toggleNotifications = () => {
    setShowNotifications((v) => !v);
  };

  const handleQuickAdd = () => {
    console.info('快速新增被點擊');
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${darkMode ? 'dark' : ''}`}>
      {/* 側邊欄遮罩 */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-50"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 抽屜式側邊欄（所有裝置統一） */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        
        {/* 側邊欄標題 */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-white" />
            </div>
            <span className="ml-3 text-lg font-semibold text-gray-900">校園生活</span>
          </div>
          
          {/* 關閉按鈕 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(false)}
            aria-label="關閉側邊欄"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* 導航選單 */}
        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigation(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center">
                    <Icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </div>
                  {item.badge && (
                    <Badge variant="secondary" className="ml-auto">
                      {item.badge}
                    </Badge>
                  )}
                </button>
              );
            })}
          </div>
        </nav>

        {/* 使用者資訊 */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <User className="h-5 w-5 text-gray-600" />
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">學生用戶</p>
              <p className="text-xs text-gray-500">student@example.com</p>
            </div>
          </div>
          
          <div className="flex items-center justify-between mt-3">
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setDarkMode(!darkMode)}
              aria-pressed={darkMode}
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="sm">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* 主要內容區域（不再預留側邊間距） */}
      <div>
        {/* 頂部導航欄 */}
        <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6">
            {/* 左側：統一使用漢堡按鈕控制抽屜 */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(true)}
              aria-label="開啟側邊欄"
            >
              <Menu className="h-5 w-5" />
            </Button>

            {/* 頁面標題 */}
            <div className="hidden sm:block">
              <h1 className="text-lg font-semibold text-gray-900">
                {navigationItems.find(item => item.id === currentPage)?.name || '校園生活管理'}
              </h1>
            </div>

            {/* 右側功能區 */}
            <div className="flex items-center gap-2">
              {/* 通知按鈕 */}
              <div className="relative">
                <Button variant="ghost" size="sm" onClick={toggleNotifications} aria-expanded={showNotifications} aria-controls="notification-panel">
                  <Bell className="h-5 w-5" />
                  {notifications.length > 0 && (
                    <Badge className="absolute -top-1 -right-1 w-5 h-5 p-0 flex items-center justify-center text-xs bg-red-500">
                      {notifications.length}
                    </Badge>
                  )}
                </Button>
                {showNotifications && (
                  <div id="notification-panel" className="absolute right-0 mt-2 w-72 bg-white border border-gray-200 rounded-md shadow-lg z-50 p-2">
                    {notifications.map(n => (
                      <div key={n.id} className="p-2 rounded hover:bg-gray-50">
                        <p className="text-sm text-gray-900">{n.title}</p>
                        <p className="text-xs text-gray-500">{n.time}</p>
                      </div>
                    ))}
                    {notifications.length === 0 && (
                      <p className="text-xs text-gray-500 p-2">目前沒有通知</p>
                    )}
                  </div>
                )}
              </div>

              {/* 快速新增按鈕 */}
              <Button size="sm" className="hidden sm:flex" onClick={handleQuickAdd}>
                <span className="mr-2">快速新增</span>
                <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                  <span className="text-xs">⌘</span>K
                </kbd>
              </Button>
            </div>
          </div>
        </header>

        {/* 頁面內容 */}
        <main className="flex-1">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 py-6">
            {children}
          </div>
        </main>
      </div>

      {/* 其他可選面板區域 */}
    </div>
  );
};

export default Layout;

