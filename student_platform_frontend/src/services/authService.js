import axios from 'axios'; // 導入 axios 庫用於發送 HTTP 請求

// 設定 axios 於請求時攜帶 cookie
axios.defaults.withCredentials = true;

const API_BASE = "http://127.0.0.1:8000/api"; // 後端 API 基礎 URL

export const authService = {
  // 登入方法
  login: async (identifier, password) => {
    try {
      const response = await axios.post(`${API_BASE}/login/`, { identifier, password });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: "登入失敗" };
    }
  },

  // 社交登入方法
  socialLogin: async (provider, tokenField) => {
    try {
      const response = await axios.post(`${API_BASE}/social-login/`, { provider, ...tokenField });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: "社交登入失敗" };
    }
  },

  // 重設密碼
  resetPassword: async (email) => {
    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      if (!response.ok) throw new Error('Reset password request failed');
      return await response.json();
    } catch (error) {
      console.error('Error in resetPassword:', error);
      throw error;
    }
  },

  // 註冊方法（main 分支）
  register: async (email, password, name) => {
    try {
      console.log('註冊請求:', { email, password, name });
      await new Promise(resolve => setTimeout(resolve, 1000));
      return { success: true, message: '註冊成功' };
    } catch (error) {
      console.error('註冊錯誤:', error);
      throw new Error('註冊時發生錯誤，請稍後再試');
    }
  },

  // Google 登入
  loginWithGoogle: async () => {
    console.log('Google 登入');
  },

  // Line 登入
  loginWithLine: async () => {
    console.log('Line 登入');
  },
};
