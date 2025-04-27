import React, { useState } from 'react';
import { useLogin } from '../hooks/useLogin';
import '../styles/LoginForm.css';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, error, isLoading } = useLogin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(email, password);
  };

  // 處理 Google 登入的函式
  const handleGoogleLogin = () => {
    // 產生隨機的 state 值以防止 CSRF 攻擊，並存入 sessionStorage
    const state = crypto.randomUUID(); // 使用 crypto.randomUUID() 產生唯一值
    sessionStorage.setItem('oauth_state_google', state); // 將 state 儲存於 sessionStorage

    // 定義 Google OAuth 所需的參數
    const client_id = "448182731678-g7b3qs9t2fldltht51ih0rejra9r4gl6.apps.googleusercontent.com"; // Google OAuth 客戶端 ID
    const redirect_uri = "http://localhost:3000/oauth-callback"; // OAuth 回呼網址
    const scope = "email profile"; // 要求的權限範圍
    const response_type = "code"; // 授權碼流程的 response_type

    // 組合 Google OAuth 的授權 URL
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=${encodeURIComponent(redirect_uri)}&response_type=${response_type}&scope=${encodeURIComponent(scope)}&state=${state}`;
    window.location.href = authUrl; // 導向至 Google 授權頁面
  };

  // 處理 LINE 登入的函式
  const handleLineLogin = () => {
    // 產生隨機的 state 值以防止 CSRF 攻擊，並存入 sessionStorage
    const state = crypto.randomUUID(); // 使用 crypto.randomUUID() 產生唯一值
    sessionStorage.setItem('oauth_state_line', state); // 將 state 儲存於 sessionStorage

    // 定義 LINE OAuth 所需的參數
    const client_id = "2007149294"; // LINE OAuth 客戶端 ID
    const redirect_uri = "http://localhost:3000/oauth-callback"; // OAuth 回呼網址
    const scope = "openid profile email"; // 要求的權限範圍
    const response_type = "code"; // 授權碼流程的 response_type

    // 組合 LINE OAuth 的授權 URL
    const lineAuthURL = `https://access.line.me/oauth2/v2.1/authorize?response_type=${response_type}&client_id=${client_id}&redirect_uri=${encodeURIComponent(redirect_uri)}&state=${state}&scope=${encodeURIComponent(scope)}`;
    window.location.href = lineAuthURL; // 導向至 LINE 授權頁面
  };

  return (
    <div className="login-form-container">
      <h1 className="login-title">登入</h1>
      <p className="login-subtitle">使用者名稱/電子郵件</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="電子郵件/使用者名稱"
            required
          />
        </div>
        
        <div className="form-group">
          <label>密碼</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="輸入密碼"
            required
          />
        </div>
        
        <button className="login-button" disabled={isLoading}>
          Login
        </button>
        
        {error && <div className="error">{error}</div>}
      </form>
      
      <div className="login-options">
        <div className="auth-links">
          <a href="/forgot-password" className="forgot-password">忘記密碼</a>
          <a href="/register" className="register-link">註冊</a>
        </div>

        <div className="divider">
          <span className="or-text">或</span>
        </div>
        <div className="social-login">
          <button className="google-login" onClick={handleGoogleLogin}>
            <img src="/images/google.png" alt="Google" />
            Google
          </button>
          <button className="line-login" onClick={handleLineLogin}>
            <img src="/images/line.png" alt="Line" />
            Line
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;