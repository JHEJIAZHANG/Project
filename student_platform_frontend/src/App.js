import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={
          <div>
            <h1>首頁</h1>
            <a href="/register">前往註冊頁面</a>
          </div>
        } />
        <Route path="/register" element={<Register />} />
      </Routes>
    </Router>
  );
}

export default App;