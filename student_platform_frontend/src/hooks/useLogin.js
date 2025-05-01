import { useState } from 'react';
import { authService } from '../services/authService';

export const useLogin = () => {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (identifier, password) => { // 定義傳統帳號密碼登入的非同步函數
    setIsLoading(true); // 將 isLoading 設為 true，表示正在處理登入
    setError(null); // 重置錯誤訊息為 null
    try { // 開始 try-catch 區塊處理可能的錯誤
      // 呼叫後端 API 登入，後端會在成功後透過 Set-Cookie 設定 httpOnly cookies
      await authService.login(identifier, password); // 呼叫 authService 的 login 方法進行登入
      // 不再使用 localStorage 儲存 token，直接跳轉
      window.location.href = "/dashboard"; // 登入成功後重定向到 dashboard 頁面
    } catch (err) { // 捕獲登入過程中可能發生的錯誤
      setError(err.detail || err.message || "登入失敗"); // 設置錯誤訊息，優先使用 err.detail 或 err.message，否則顯示預設訊息
    } finally { // 無論成功或失敗都會執行的區塊
      setIsLoading(false); // 將 isLoading 設為 false，表示登入過程結束
    }
  };

  const loginWithGoogle = async (code) => { // 定義 Google 社交登入的非同步函數
    setIsLoading(true); // 將 isLoading 設為 true，表示正在處理登入
    setError(null); // 重置錯誤訊息為 null
    try { // 開始 try-catch 區塊處理可能的錯誤
      await authService.socialLogin("google", { // 呼叫 authService 的 socialLogin 方法進行 Google 登入
        code, // 傳入從 OAuth 回調取得的授權碼
        redirect_uri: "http://localhost:3000/oauth-callback", // 指定 OAuth 回調的重新導向 URI
      });
      window.location.href = "/dashboard"; // 登入成功後重定向到 dashboard 頁面
    } catch (err) { // 捕獲登入過程中可能發生的錯誤
      setError(err.detail || err.message || "Google 登入失敗"); // 設置錯誤訊息，優先使用 err.detail 或 err.message，否則顯示預設訊息
    } finally { // 無論成功或失敗都會執行的區塊
      setIsLoading(false); // 將 isLoading 設為 false，表示登入過程結束
    }
  };

  const loginWithLine = async (code) => { // 定義 LINE 社交登入的非同步函數
    setIsLoading(true); // 將 isLoading 設為 true，表示正在處理登入
    setError(null); // 重置錯誤訊息為 null
    try { // 開始 try-catch 區塊處理可能的錯誤
      await authService.socialLogin("line", { // 呼叫 authService 的 socialLogin 方法進行 LINE 登入
        code, // 傳入從 OAuth 回調取得的授權碼
        redirect_uri: "http://localhost:3000/oauth-callback", // 指定 OAuth 回調的重新導向 URI
      });
      window.location.href = "/dashboard"; // 登入成功後重定向到 dashboard 頁面
    } catch (err) { // 捕獲登入過程中可能發生的錯誤
      setError(err.detail || err.message || "LINE 登入失敗"); // 設置錯誤訊息，優先使用 err.detail 或 err.message，否則顯示預設訊息
    } finally { // 無論成功或失敗都會執行的區塊
      setIsLoading(false); // 將 isLoading 設為 false，表示登入過程結束
    }
  };

  return { // 回傳包含登入方法和狀態的物件
    login, // 傳統帳號密碼登入方法
    loginWithGoogle, // Google 社交登入方法
    loginWithLine, // LINE 社交登入方法
    error, // 錯誤訊息狀態
    isLoading, // 載入狀態
  };
};