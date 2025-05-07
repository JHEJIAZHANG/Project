import { useState } from 'react';
import { authService } from '../services/authService';

export const useRegister = () => {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const register = async (email, password, name) => {
    setError(null);
    setLoading(true);

    try {
      await authService.register(email, password, name);
      setLoading(false);
      // 註冊成功後的導向或其他邏輯
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return { register, error, loading };
};