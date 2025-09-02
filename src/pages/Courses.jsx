import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  Users, 
  Calendar, 
  FileText, 
  ExternalLink,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Plus
} from 'lucide-react';

const Courses = () => {
  const { isClassroomConnected, setIsClassroomConnected, courses, setCourses } = useApp();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 模擬 Google Classroom 課程資料
  const mockCourses = [
    {
      id: '123456789',
      name: '資料結構與演算法',
      section: '資工系三年級',
      description: '學習基本資料結構和演算法設計與分析',
      teacher: '張教授',
      studentCount: 45,
      courseState: 'ACTIVE',
      creationTime: '2025-01-01T00:00:00Z',
      updateTime: '2025-01-08T10:30:00Z',
      enrollmentCode: 'abc123',
      courseGroupEmail: 'datastructure2025@classroom.google.com',
      alternateLink: 'https://classroom.google.com/c/123456789',
      room: '資工館 301',
      ownerId: 'teacher123',
      coursework: [
        {
          id: 'cw1',
          title: '二元樹實作作業',
          description: '實作二元搜尋樹的插入、刪除和搜尋功能',
          dueDate: '2025-01-15T23:59:00Z',
          state: 'PUBLISHED',
          workType: 'ASSIGNMENT',
          maxPoints: 100
        },
        {
          id: 'cw2',
          title: '期中考試',
          description: '涵蓋第1-8章內容',
          dueDate: '2025-01-20T14:00:00Z',
          state: 'PUBLISHED',
          workType: 'SHORT_ANSWER_QUESTION',
          maxPoints: 100
        }
      ]
    },
    {
      id: '987654321',
      name: '軟體工程',
      section: '資工系三年級',
      description: '軟體開發生命週期與專案管理',
      teacher: '李教授',
      studentCount: 38,
      courseState: 'ACTIVE',
      creationTime: '2025-01-01T00:00:00Z',
      updateTime: '2025-01-07T15:20:00Z',
      enrollmentCode: 'def456',
      courseGroupEmail: 'softwareeng2025@classroom.google.com',
      alternateLink: 'https://classroom.google.com/c/987654321',
      room: '資工館 205',
      ownerId: 'teacher456',
      coursework: [
        {
          id: 'cw3',
          title: '需求分析報告',
          description: '選擇一個軟體專案進行需求分析',
          dueDate: '2025-01-18T23:59:00Z',
          state: 'PUBLISHED',
          workType: 'ASSIGNMENT',
          maxPoints: 80
        }
      ]
    },
    {
      id: '456789123',
      name: '線性代數',
      section: '數學系二年級',
      description: '向量空間、矩陣運算與線性變換',
      teacher: '王教授',
      studentCount: 52,
      courseState: 'ACTIVE',
      creationTime: '2025-01-01T00:00:00Z',
      updateTime: '2025-01-06T09:15:00Z',
      enrollmentCode: 'ghi789',
      courseGroupEmail: 'linearalgebra2025@classroom.google.com',
      alternateLink: 'https://classroom.google.com/c/456789123',
      room: '數學館 102',
      ownerId: 'teacher789',
      coursework: [
        {
          id: 'cw4',
          title: '矩陣運算練習',
          description: '完成課本第3章習題',
          dueDate: '2025-01-12T23:59:00Z',
          state: 'PUBLISHED',
          workType: 'ASSIGNMENT',
          maxPoints: 50
        },
        {
          id: 'cw5',
          title: '期中報告',
          description: '線性變換的實際應用',
          dueDate: '2025-01-25T23:59:00Z',
          state: 'PUBLISHED',
          workType: 'ASSIGNMENT',
          maxPoints: 100
        }
      ]
    }
  ];

  // 模擬 Google Classroom API 連接
  const connectToGoogleClassroom = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 模擬 OAuth 2.0 認證流程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 模擬成功連接
      setIsClassroomConnected(true);
      setCourses(mockCourses);
      
    } catch (err) {
      setError('連接 Google Classroom 失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  // 重新整理課程資料
  const refreshCourses = async () => {
    if (!isClassroomConnected) return;
    
    setLoading(true);
    try {
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      setCourses(mockCourses);
    } catch (err) {
      setError('重新整理失敗');
    } finally {
      setLoading(false);
    }
  };

  // 取得課程作業統計
  const getCourseWorkStats = (coursework) => {
    const now = new Date();
    const upcoming = coursework.filter(cw => new Date(cw.dueDate) > now);
    const overdue = coursework.filter(cw => new Date(cw.dueDate) < now);
    
    return { total: coursework.length, upcoming: upcoming.length, overdue: overdue.length };
  };

  // 格式化日期
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  useEffect(() => {
    if (isClassroomConnected) {
      setCourses(mockCourses);
    }
  }, [isClassroomConnected]);

  return (
    <div className="p-6 space-y-6">
      {/* 頁面標題 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">課程管理</h1>
          <p className="text-gray-600 mt-1">管理您的 Google Classroom 課程</p>
        </div>
        <div className="flex gap-2">
          {isClassroomConnected && (
            <Button 
              variant="outline" 
              onClick={refreshCourses}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              重新整理
            </Button>
          )}
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            加入課程
          </Button>
        </div>
      </div>

      {/* Google Classroom 連接狀態 */}
      {!isClassroomConnected ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              連接 Google Classroom
            </CardTitle>
            <CardDescription>
              連接您的 Google Classroom 帳號以同步課程資料
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center space-y-4 py-8">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <BookOpen className="h-8 w-8 text-blue-600" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold">尚未連接 Google Classroom</h3>
                <p className="text-gray-600 mt-1">
                  連接後可以自動同步您的課程、作業和成績
                </p>
              </div>
              <Button 
                onClick={connectToGoogleClassroom}
                disabled={loading}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <ExternalLink className="h-4 w-4" />
                )}
                {loading ? '連接中...' : '連接 Google Classroom'}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* 連接成功狀態 */}
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-800">已連接 Google Classroom</p>
                  <p className="text-sm text-green-600">
                    最後同步時間：{new Date().toLocaleString('zh-TW')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 錯誤訊息 */}
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <AlertCircle className="h-5 w-5 text-red-600" />
                  <p className="text-red-800">{error}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 課程統計 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">總課程數</p>
                    <p className="text-2xl font-bold text-blue-600">{courses.length}</p>
                  </div>
                  <BookOpen className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">總學生數</p>
                    <p className="text-2xl font-bold text-green-600">
                      {courses.reduce((sum, course) => sum + course.studentCount, 0)}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">待完成作業</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {courses.reduce((sum, course) => {
                        const stats = getCourseWorkStats(course.coursework);
                        return sum + stats.upcoming;
                      }, 0)}
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 課程列表 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {courses.map((course) => {
              const workStats = getCourseWorkStats(course.coursework);
              
              return (
                <Card key={course.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{course.name}</CardTitle>
                        <CardDescription>{course.section}</CardDescription>
                      </div>
                      <Badge variant="secondary">
                        {course.courseState === 'ACTIVE' ? '進行中' : '已結束'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-gray-600">{course.description}</p>
                    
                    {/* 課程資訊 */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-gray-500" />
                        <span>{course.teacher}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <span>{course.room}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-gray-500" />
                        <span>{course.studentCount} 位學生</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-gray-500" />
                        <span>{workStats.total} 個作業</span>
                      </div>
                    </div>

                    {/* 作業統計 */}
                    {workStats.total > 0 && (
                      <div className="flex gap-2">
                        {workStats.upcoming > 0 && (
                          <Badge variant="outline" className="text-orange-600 border-orange-600">
                            {workStats.upcoming} 個即將到期
                          </Badge>
                        )}
                        {workStats.overdue > 0 && (
                          <Badge variant="outline" className="text-red-600 border-red-600">
                            {workStats.overdue} 個已逾期
                          </Badge>
                        )}
                      </div>
                    )}

                    {/* 最近作業 */}
                    {course.coursework.length > 0 && (
                      <div className="border-t pt-4">
                        <h4 className="font-medium text-sm mb-2">最近作業</h4>
                        <div className="space-y-2">
                          {course.coursework.slice(0, 2).map((work) => (
                            <div key={work.id} className="flex justify-between items-center text-sm">
                              <span className="truncate">{work.title}</span>
                              <span className="text-gray-500 text-xs">
                                {formatDate(work.dueDate)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 操作按鈕 */}
                    <div className="flex gap-2 pt-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        className="flex-1"
                        onClick={() => window.open(course.alternateLink, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        開啟課程
                      </Button>
                      <Button variant="outline" size="sm">
                        查看作業
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default Courses;

