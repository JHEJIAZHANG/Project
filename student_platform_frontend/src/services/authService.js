import axios from 'axios'; // 導入 axios 庫用於發送 HTTP 請求

// 設定 axios 於請求時攜帶 cookie（含 httpOnly cookies，由瀏覽器自動處理）
axios.defaults.withCredentials = true; // 啟用 withCredentials，讓 axios 自動攜帶瀏覽器的 cookies（包括 httpOnly cookies）

const API_BASE = "http://127.0.0.1:8000/api"; // 定義後端 API 的基礎 URL

export const authService = {
  // 帳密登入方法，後端成功登入時會在回應中設定 httpOnly cookies  
  login: async (identifier, password) => {
    try { // 開始 try-catch 區塊處理可能的錯誤
      const response = await axios.post(`${API_BASE}/login/`, { // 使用 axios 發送 POST 請求到登入端點
        identifier, // 傳送使用者識別碼（例如使用者名稱或電子郵件）
        password, // 傳送密碼
      });
      return response.data; // 成功時回傳後端回應的資料
    } catch (error) { // 捕獲請求過程中可能發生的錯誤
      throw error.response?.data || { message: "登入失敗" }; // 拋出錯誤，優先使用後端回應的資料，否則回傳預設錯誤訊息
    }
  },

  // 社交登入方法，後端依據 provider 與 code 進行 token 交換並設定 httpOnly cookies
  socialLogin: async (provider, tokenField) => { // 定義社交登入的非同步方法
    try { // 開始 try-catch 區塊處理可能的錯誤
      const response = await axios.post(`${API_BASE}/social-login/`, { // 使用 axios 發送 POST 請求到社交登入端點
        provider, // 傳送社交登入的提供者（例如 "google" 或 "line"）
        ...tokenField, // 展開 tokenField 物件，包含 code 和 redirect_uri 等欄位
      });
      return response.data; // 成功時回傳後端回應的資料
    } catch (error) { // 捕獲請求過程中可能發生的錯誤
      throw error.response?.data || { message: "社交登入失敗" }; // 拋出錯誤，優先使用後端回應的資料，否則回傳預設錯誤訊息
    }
  },

  // 重設密碼功能
  resetPassword: async (email) => {
    try {
        const response = await fetch('/api/auth/forgot-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });
        
        if (!response.ok) {
            throw new Error('Reset password request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error in resetPassword:', error);
        throw error;
    }
  }
};