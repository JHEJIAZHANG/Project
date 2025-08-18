// OAuthCallback.js
import React, { useEffect } from 'react'; // 導入 React 和 useEffect hook 用於處理副作用
import { useNavigate } from 'react-router-dom'; // 導入 useNavigate hook 用於路由導航
import { useLogin } from '../hooks/useLogin'; // 導入自訂 hook useLogin 用於處理登入邏輯

const OAuthCallback = () => { // 定義 OAuthCallback 組件
  const navigate = useNavigate(); // 初始化 navigate 函數用於頁面跳轉
  const { loginWithGoogle, loginWithLine } = useLogin(); // 從 useLogin hook 中解構出 Google 和 LINE 的登入方法

  useEffect(() => { // 使用 useEffect hook 在組件渲染後執行副作用
    // 從 URL 取得授權碼 (code) 與 state
    const query = new URLSearchParams(window.location.search); // 解析當前 URL 的查詢參數
    const code = query.get("code"); // 從查詢參數中獲取授權碼
    const state = query.get("state"); // 從查詢參數中獲取 state 值

    if (code && state) { // 檢查是否同時存在 code 和 state
      const googleState = sessionStorage.getItem('oauth_state_google'); // 從 sessionStorage 獲取 Google 的 state 值
      const lineState = sessionStorage.getItem('oauth_state_line'); // 從 sessionStorage 獲取 LINE 的 state 值

      if (state === googleState) { // 如果 URL 中的 state 與 Google 的 state 匹配
        loginWithGoogle(code) // 呼叫 loginWithGoogle 函數並傳入授權碼進行登入
          .then(() => { // 登入成功後執行
            sessionStorage.removeItem('oauth_state_google'); // 清除 sessionStorage 中的 Google state
            navigate('/dashboard'); // 導航到 dashboard 頁面
          })
          .catch((err) => { // 處理登入失敗的情況
            console.error("Google login error:", err); // 在控制台記錄錯誤訊息
            navigate('/login'); // 導航回登入頁面
          });
        return; // 結束本次 useEffect 執行
      } else if (state === lineState) { // 如果 URL 中的 state 與 LINE 的 state 匹配
        loginWithLine(code) // 呼叫 loginWithLine 函數並傳入授權碼進行登入
          .then(() => { // 登入成功後執行
            sessionStorage.removeItem('oauth_state_line'); // 清除 sessionStorage 中的 LINE state
            navigate('/dashboard'); // 導航到 dashboard 頁面
          })
          .catch((err) => { // 處理登入失敗的情況
            console.error("LINE login error:", err); // 在控制台記錄錯誤訊息
            navigate('/login'); // 導航回登入頁面
          });
        return; // 結束本次 useEffect 執行
      } else { // 如果 state 與 Google 和 LINE 的 state 都不匹配
        // state 驗證失敗，可能為 CSRF 攻擊
        console.error("State mismatch in OAuth callback"); // 在控制台記錄 state 不匹配的錯誤
        navigate('/login'); // 導航回登入頁面
        return; // 結束本次 useEffect 執行
      }
    } else { // 如果缺少 code 或 state
      navigate('/login'); // 導航回登入頁面
    }
  }, [loginWithGoogle, loginWithLine, navigate]); // useEffect 的依賴數組，當這些值變化時重新執行

  return <div>正在登入中...</div>; // 渲染組件時顯示「正在登入中」的訊息
};

export default OAuthCallback; // 匯出 OAuthCallback 組件作為預設匯出