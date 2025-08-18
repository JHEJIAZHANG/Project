// src/contexts/LiffContext.tsx
import React, { createContext, useContext, useEffect, useState } from "react";
import liff from "@line/liff";

interface LiffState {
  ready: boolean;
  userId: string;
  idToken: string;
}

const LiffCtx = createContext<LiffState>({
  ready: false,
  userId: "",
  idToken: "",
});

export const LiffProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<LiffState>({ ready: false, userId: "", idToken: "" });

  useEffect(() => {
    (async () => {
      await liff.init({ liffId: import.meta.env.VITE_LIFF_ID });
      if (!liff.isLoggedIn()) liff.login();
      const decoded = liff.getDecodedIDToken();
      setState({
        ready: true,
        userId: decoded && decoded.sub ? decoded.sub : "",     // LINE User ID
        idToken: liff.getIDToken()!,
      });
    })().catch(console.error);
  }, []);

  return <LiffCtx.Provider value={state}>{children}</LiffCtx.Provider>;
};

export const useLiff = () => useContext(LiffCtx);
