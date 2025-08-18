import { useState } from 'react';
import { authService } from '../services/authService';

export const useForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async () => {
    if (!email) {
      setError('請輸入電子郵件地址');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await authService.resetPassword(email);
      setSuccess(true);
    } catch (err) {
      setError('發送重置連結時出錯，請稍後再試');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return {
    email,
    setEmail,
    loading,
    error,
    success,
    handleSubmit
  };
};
