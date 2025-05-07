import React, { useState } from 'react';
import { useResetPassword } from '../hooks/useResetPassword';

const ResetPasswordForm = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const { resetPassword, isLoading } = useResetPassword();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // 確認密碼是否一致
    if (newPassword !== confirmPassword) {
      setError('密碼不一致，請重新輸入');
      return;
    }

    try {
      // 從 URL 取得重設 token (如果有的話)
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      
      await resetPassword({ token, newPassword });
      // 成功重設後的處理，例如導向登入頁面或顯示成功訊息
      alert('密碼重設成功！');
      // 可以加入重定向到登入頁面的程式碼
    } catch (err) {
      setError('重設密碼失敗，請稍後再試');
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="reset-password-form">
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="newPassword">新密碼</label>
        <input
          type="password"
          id="newPassword"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          className="form-control"
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="confirmPassword">確認密碼</label>
        <input
          type="password"
          id="confirmPassword"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          className="form-control"
        />
      </div>
      
      <button 
        type="submit" 
        className="reset-button"
        disabled={isLoading}
      >
        {isLoading ? '處理中...' : '重設密碼'}
      </button>
    </form>
  );
};

export default ResetPasswordForm;