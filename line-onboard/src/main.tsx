import { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import liff from "@line/liff";
import { getStatus } from "./api";
import IdentityStep from "./pages/IdentityStep";
import ProfileStep from "./pages/ProfileStep";
import Success from "./pages/Success";
import AlreadyRegistered from "./pages/AlreadyRegistered";
import "./styles/main.css";

type Page = "loading" | "identity" | "profile" | "success" | "already";

export default function App() {
  const [page, setPage] = useState<Page>("loading");
  const [role, setRole] = useState<"teacher" | "student">("student");
  const [lineId, setLineId] = useState("");

  useEffect(() => {
    (async () => {
      try {
        await liff.init({ liffId: import.meta.env.VITE_LIFF_ID });
        if (!liff.isLoggedIn()) {
          liff.login();
          return;
        }
        
        const id = liff.getDecodedIDToken()?.sub;
        if (!id) {
          alert("取 LINE ID 失敗");
          return;
        }
        setLineId(id);

        // Check if already registered
        try {
          const { data } = await getStatus(id);
          if (data.registered) {
            setPage("already");
            return;
          }
        } catch (e) {
          console.error("status API 錯誤", e);
        }

        // Check if returning from OAuth
        if (new URLSearchParams(location.search).get("status") === "success") {
          setPage("success");
          return;
        }

        // Start registration flow
        setPage("identity");
      } catch (error) {
        console.error("LIFF initialization failed:", error);
        alert("初始化失敗，請重新開啟");
      }
    })();
  }, []);

  if (page === "loading") {
    return (
      <div className="container">
        <div className="loading">載入中...</div>
      </div>
    );
  }
  
  if (page === "already") return <AlreadyRegistered />;
  if (page === "success") return <Success />;
  if (page === "identity") {
    return (
      <IdentityStep 
        next={(r) => {
          setRole(r);
          setPage("profile");
        }} 
      />
    );
  }
  if (page === "profile") {
    return (
      <ProfileStep 
        role={role} 
        lineUserId={lineId} 
        onWaitingAuth={() => setPage("loading")}
        onBack={() => setPage("identity")}
      />
    );
  }
  
  return null;
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
