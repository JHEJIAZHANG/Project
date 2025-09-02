import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  Plus, 
  Search, 
  Edit3, 
  Trash2, 
  Filter,
  FileText,
  User,
  Briefcase,
  Calendar
} from 'lucide-react';

const Notes = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isCreating, setIsCreating] = useState(false);

  // 筆記分類
  const categories = [
    { id: 'all', name: '全部', icon: FileText, color: 'gray' },
    { id: 'course', name: '課程', icon: BookOpen, color: 'blue' },
    { id: 'personal', name: '個人', icon: User, color: 'green' },
    { id: 'work', name: '工作', icon: Briefcase, color: 'purple' }
  ];

  // 模擬筆記資料
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

  // 篩選筆記
  const filteredNotes = notes.filter(note => {
    const matchesSearch = note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         note.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         note.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || note.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // 取得分類資訊
  const getCategoryInfo = (categoryId) => {
    return categories.find(cat => cat.id === categoryId) || categories[0];
  };

  // 刪除筆記
  const deleteNote = (noteId) => {
    setNotes(notes.filter(note => note.id !== noteId));
  };

  // 新增筆記表單
  const CreateNoteForm = () => {
    const [newNote, setNewNote] = useState({
      title: '',
      content: '',
      category: 'course',
      tags: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!newNote.title.trim()) return;

      const note = {
        id: Date.now(),
        title: newNote.title,
        content: newNote.content,
        category: newNote.category,
        createdAt: new Date().toISOString().split('T')[0],
        updatedAt: new Date().toISOString().split('T')[0],
        tags: newNote.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };

      setNotes([note, ...notes]);
      setNewNote({ title: '', content: '', category: 'course', tags: '' });
      setIsCreating(false);
    };

    return (
      <Card>
        <CardHeader>
          <CardTitle>新增筆記</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                placeholder="筆記標題"
                value={newNote.title}
                onChange={(e) => setNewNote({...newNote, title: e.target.value})}
                className="mb-2"
              />
            </div>
            
            <div>
              <select 
                value={newNote.category}
                onChange={(e) => setNewNote({...newNote, category: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                {categories.slice(1).map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <textarea
                placeholder="筆記內容..."
                value={newNote.content}
                onChange={(e) => setNewNote({...newNote, content: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-md h-32 resize-none"
              />
            </div>

            <div>
              <Input
                placeholder="標籤 (用逗號分隔)"
                value={newNote.tags}
                onChange={(e) => setNewNote({...newNote, tags: e.target.value})}
              />
            </div>

            <div className="flex gap-2">
              <Button type="submit">儲存筆記</Button>
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
          <h1 className="text-3xl font-bold text-gray-900">筆記</h1>
          <p className="text-gray-600 mt-1">記錄學習心得和重要資訊</p>
        </div>
        
        <Button 
          onClick={() => setIsCreating(!isCreating)}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          新增筆記
        </Button>
      </div>

      {/* 搜尋和篩選 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* 搜尋框 */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="搜尋筆記標題、內容或標籤..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* 分類篩選 */}
            <div className="flex gap-2 flex-wrap">
              {categories.map((category) => {
                const Icon = category.icon;
                return (
                  <Button
                    key={category.id}
                    variant={selectedCategory === category.id ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedCategory(category.id)}
                    className="flex items-center gap-2"
                  >
                    <Icon className="h-4 w-4" />
                    {category.name}
                    {category.id !== 'all' && (
                      <Badge variant="secondary" className="ml-1">
                        {notes.filter(note => note.category === category.id).length}
                      </Badge>
                    )}
                  </Button>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 新增筆記表單 */}
      {isCreating && <CreateNoteForm />}

      {/* 筆記列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredNotes.map((note) => {
          const categoryInfo = getCategoryInfo(note.category);
          const CategoryIcon = categoryInfo.icon;
          
          return (
            <Card key={note.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg line-clamp-2">{note.title}</CardTitle>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge 
                        variant="outline" 
                        className={`${
                          categoryInfo.color === 'blue' ? 'border-blue-500 text-blue-700' :
                          categoryInfo.color === 'green' ? 'border-green-500 text-green-700' :
                          categoryInfo.color === 'purple' ? 'border-purple-500 text-purple-700' :
                          'border-gray-500 text-gray-700'
                        }`}
                      >
                        <CategoryIcon className="h-3 w-3 mr-1" />
                        {categoryInfo.name}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm">
                      <Edit3 className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNote(note.id);
                      }}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <p className="text-gray-600 text-sm line-clamp-3 mb-4">
                  {note.content}
                </p>
                
                {/* 標籤 */}
                {note.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {note.tags.slice(0, 3).map((tag, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {note.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{note.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                )}
                
                {/* 日期資訊 */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    建立：{note.createdAt}
                  </span>
                  {note.updatedAt !== note.createdAt && (
                    <span>更新：{note.updatedAt}</span>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 空狀態 */}
      {filteredNotes.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm || selectedCategory !== 'all' ? '找不到符合條件的筆記' : '還沒有筆記'}
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || selectedCategory !== 'all' 
                ? '試試調整搜尋條件或篩選器' 
                : '開始記錄您的學習心得和重要資訊吧！'
              }
            </p>
            {!searchTerm && selectedCategory === 'all' && (
              <Button onClick={() => setIsCreating(true)}>
                <Plus className="h-4 w-4 mr-2" />
                建立第一個筆記
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* 統計資訊 */}
      <Card>
        <CardHeader>
          <CardTitle>筆記統計</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {categories.slice(1).map((category) => {
              const count = notes.filter(note => note.category === category.id).length;
              const Icon = category.icon;
              
              return (
                <div key={category.id} className="text-center p-4 bg-gray-50 rounded-lg">
                  <Icon className={`h-8 w-8 mx-auto mb-2 ${
                    category.color === 'blue' ? 'text-blue-600' :
                    category.color === 'green' ? 'text-green-600' :
                    'text-purple-600'
                  }`} />
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                  <p className="text-sm text-gray-600">{category.name}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Notes;

