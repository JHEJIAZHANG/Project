import React, { useState } from 'react';
import '../styles/ResetPassword.css';

const ResetPassword = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // 這裡可以加入密碼重設邏輯
    console.log('嘗試重設密碼：');
  };

  return (
    <div className="reset-page">
      <header className="reset-header">
        <div className="logo">
          <span className="logo-icon">S</span>
          <span>Social</span>
        </div>
      </header>
      
      <main className="reset-main">
        <h2 className="reset-title">重設密碼</h2>
        <p className="reset-desc">請輸入您的新密碼以完成重設。</p>
        
        <form onSubmit={handleSubmit} className="reset-form">
          <div className="form-field">
            <label htmlFor="newPassword">新密碼</label>
            <input 
              type="password" 
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="輸入新密碼"
            />
          </div>
          
          <div className="form-field">
            <label htmlFor="confirmPassword">確認密碼</label>
            <input 
              type="password" 
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="再次輸入新密碼"
            />
          </div>
          
          <button type="submit" className="reset-button">重設密碼</button>
        </form>
      </main>
    </div>
  );
};

export default ResetPassword;