import { useState } from 'react';

export const useResetPassword = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const resetPassword = async ({ token, newPassword }) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 這裡是發送 API 請求重設密碼的邏輯
      // 您需要根據您的後端 API 進行調整
      const response = await fetch('/api/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, newPassword }),
      });
      
      if (!response.ok) {
        throw new Error('重設密碼失敗');
      }
      
      const data = await response.json();
      setIsLoading(false);
      return data;
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      throw err;
    }
  };

  return { resetPassword, isLoading, error };
};

export default useResetPassword;