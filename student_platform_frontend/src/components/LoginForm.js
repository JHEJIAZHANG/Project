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
          <button className="google-login">
            <img src="/images/google.png" alt="Google" />
            Google
          </button>
          <button className="line-login">
            <img src="/images/line.png" alt="Line" />
            Line
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;