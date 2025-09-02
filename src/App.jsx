import React, { useState } from 'react';
import { AppProvider } from './contexts/AppContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Calendar from './pages/Calendar';
import Courses from './pages/Courses';
import Notes from './pages/Notes';
import TodoList from './pages/TodoList';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  // 頁面路由映射
  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'calendar':
        return <Calendar />;
      case 'courses':
        return <Courses />;
      case 'notes':
        return <Notes />;
      case 'todos':
        return <TodoList />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <AppProvider>
      <Layout 
        currentPage={currentPage} 
        onNavigate={setCurrentPage}
      >
        {renderPage()}
      </Layout>
    </AppProvider>
  );
}

export default App;
