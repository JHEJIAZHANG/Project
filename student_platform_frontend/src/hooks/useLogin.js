import { useState } from 'react';
import { authService } from '../services/authService';

export const useLogin = () => {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email, password) => {
    setIsLoading(true);
    setError(null);

    try {
      // 使用authService進行API呼叫
      const response = await authService.login(email, password);
      
      // 儲存用戶資訊或token到本地存儲
      localStorage.setItem('user', JSON.stringify(response.user));
      
      setIsLoading(false);
      
      // 重定向到首頁或儀表板
      window.location.href = '/dashboard';
    } catch (err) {
      setIsLoading(false);
      setError(err.message || '登入失敗，請檢查您的憑證');
    }
  };

  return { login, error, isLoading };
};