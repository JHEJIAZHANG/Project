import { useEffect, useState } from "react";
import { getProfile } from "../api";
import liff from "@line/liff";
import "./Success.css";

export default function Success() {
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
    <div className="success-container">
      <div className="success-icon">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" fill="#34c759"/>
          <path d="M9 12L11 14L15 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      
      <h2 className="success-title">綁定完成</h2>
      
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
