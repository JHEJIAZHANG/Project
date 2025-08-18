import React from 'react';
import { FaSmile } from "react-icons/fa";
import '../styles/ForgotPasswordForm.css';
import { useForgotPassword } from '../hooks/useForgotPassword';

const ForgotPasswordForm = () => {
  const { email, setEmail, handleSubmit, loading } = useForgotPassword();

  return (
    <div className="forgot-password-container">
      <div className="logo-container">
        <span className="logo-text">
          <FaSmile className="logo-icon" /> Social
        </span>
      </div>
      
      <div className="forgot-password-form">
        <h1>忘記密碼</h1>
        <p>輸入的電子郵件地址以重設的密碼。收到一封包含明的電子郵件。</p>
        
        <div className="input-group">
          <label>電子郵件</label>
          <input 
            type="email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="電子郵件"
          />
        </div>
        
        <button 
          className="reset-button" 
          onClick={handleSubmit}
          disabled={loading}
        >
          發送重置連結
        </button>
        
        <div className="form-footer">
          <a href="/help" className="help-link">需要更多幫助？</a>
          <a href="/login" className="login-link">返回登入</a>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordForm;