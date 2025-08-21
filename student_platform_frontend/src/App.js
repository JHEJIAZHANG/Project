<<<<<<< HEAD
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import OAuthCallback from './components/OAuthCallback';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
=======
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import "./App.css";
>>>>>>> 18

function App() {
  return (
    <Router>
      <Routes>
<<<<<<< HEAD
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        {/*
          建議對 Dashboard 路由加入授權保護（例如：私有路由），
          以避免未授權存取，這裡僅做提示，實作時可加入驗證機制。
        */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/oauth-callback" element={<OAuthCallback />} />
=======
        <Route path="/" element={
          <div>
            <h1>首頁</h1>
            <a href="/register">前往註冊頁面</a>
          </div>
        } />
        <Route path="/register" element={<Register />} />
>>>>>>> 18
      </Routes>
    </Router>
  );
}

<<<<<<< HEAD
export default App;
=======
export default App;
>>>>>>> 18
