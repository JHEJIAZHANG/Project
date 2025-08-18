import { useState } from "react";
import { preRegister } from "../api";
import liff from "@line/liff";
import "./ProfileStep.css";

interface Props {
  role: "teacher" | "student";
  lineUserId: string;
  onWaitingAuth: () => void;
  onBack: () => void;
}

export default function ProfileStep({ role, lineUserId, onWaitingAuth, onBack }: Props) {
  const [name, setName] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const submit = async () => {
    if (!name.trim()) {
      alert("請輸入姓名");
      return;
    }

    setIsLoading(true);
    try {
      const { data } = await preRegister({
        line_user_id: lineUserId,
        role,
        name: name.trim(),
        id_token: liff.getIDToken(), 
      });

      if (!data.redirectUrl) {
        alert("後端未回傳 redirectUrl");
        return;
      }

      liff.openWindow({ url: data.redirectUrl, external: true });
      onWaitingAuth();
    } catch (error) {
      console.error("Registration error:", error);
      alert("註冊失敗，請重試");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="profile-container">
      <h2 className="profile-title">個人資料</h2>
      
      <div className="role-display">
        <span className="role-label">身分：</span>
        <span className="role-value">{role === "teacher" ? "教師" : "學生"}</span>
      </div>

      <div className="input-group">
        <label className="input-label">姓名</label>
        <input 
          type="text"
          className="name-input"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="請輸入您的姓名"
          maxLength={20}
        />
      </div>

      <div className="button-group">
        <button className="back-button" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>上一步</span>
        </button>
        
        <button 
          className="auth-button" 
          onClick={submit}
          disabled={isLoading || !name.trim()}
        >
          {isLoading ? (
            <span>授權中...</span>
          ) : (
            <>
              <span>授權 Google</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="currentColor"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="currentColor"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="currentColor"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="currentColor"/>
              </svg>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
