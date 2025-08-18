import { useEffect, useState } from "react";
import liff from "@line/liff";
import { getProfile } from "../api";
import "./AlreadyRegistered.css";

export default function AlreadyRegistered() {
  const [info, setInfo] = useState<{name:string;role:string}|null>(null);

  useEffect(() => {
    (async () => {
      const lineId = liff.getDecodedIDToken()?.sub;
      if (!lineId) return;
      try {
        const { data } = await getProfile(lineId);
        setInfo(data);
        setTimeout(() => liff.closeWindow(), 2500);
      } catch (error) {
        console.error("Failed to get profile:", error);
      }
    })();
  }, []);

  return (
    <div className="already-container">
      <div className="already-icon">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" fill="#ff9500"/>
          <path d="M12 8V12L15 15" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      
      <h2 className="already-title">您已綁定</h2>
      
      {info && (
        <div className="user-info">
          <p className="user-name">{info.name}</p>
          <p className="user-role">({info.role === "teacher" ? "教師" : "學生"})</p>
        </div>
      )}
      
      <p className="close-message">視窗將自動關閉...</p>
    </div>
  );
}
