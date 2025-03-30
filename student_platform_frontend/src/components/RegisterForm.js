import React, { useState, useEffect } from 'react';
import { useRegister } from '../hooks/useRegister';
import '../styles/RegisterForm.css';
import { useNavigate } from 'react-router-dom';

// 嘗試直接導入圖片（方法1）
// 如果您使用這種方法，請取消下面這行的註釋，並在src目錄放置line.png
// import lineLogo from '../assets/line.png';

const RegisterForm = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [lineImgSrc, setLineImgSrc] = useState('/line.png');
  const { register, error, loading } = useRegister();
  const navigate = useNavigate();
  
  // 圖片加載錯誤處理（方法2）
  useEffect(() => {
    const img = new Image();
    img.src = lineImgSrc;
    img.onload = () => console.log('LINE 圖片加載成功');
    img.onerror = () => {
      console.log('LINE 圖片加載失敗，嘗試其他路徑');
      // 嘗試不同的路徑
      if (lineImgSrc === '/line.png') {
        setLineImgSrc('./line.png');
      } else if (lineImgSrc === './line.png') {
        setLineImgSrc('../line.png');
      } else if (lineImgSrc === '../line.png') {
        setLineImgSrc('line.png');
      }
    };
  }, [lineImgSrc]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setPasswordError('密碼與確認密碼不匹配');
      return;
    }
    
    setPasswordError('');
    await register(email, password, username);
  };

  return (
    <div className="register-page">
      <div className="register-header">
        <div className="logo">
          <span className="logo-circle">S</span>
          <span className="logo-text">Social</span>
        </div>
      </div>
      
      <div className="register-form-container">
        <h1>加入我們</h1>
        <p className="subtitle">建立帳號</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>電子郵件地址</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              placeholder="請輸入電子郵件"
            />
          </div>

          <div className="form-group">
            <label>姓名</label>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="輸入名稱/暱稱"
            />
          </div>

          <div className="form-group">
            <label>密碼</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="請輸入密碼"
            />
          </div>

          <div className="form-group">
            <label>確認密碼</label>
            <input 
              type="password" 
              value={confirmPassword} 
              onChange={(e) => setConfirmPassword(e.target.value)} 
              placeholder="請再次輸入密碼"
            />
          </div>

          {passwordError && <div className="error">{passwordError}</div>}
          {error && <div className="error">{error}</div>}

          <button className="register-btn" disabled={loading}>
            註冊
          </button>
        </form>

        <div className="social-login">
          <div className="or-divider">或是</div>
          <div className="social-buttons">
            <button type="button" className="social-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 48 48" style={{marginRight: "8px"}}>
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
              </svg>
              Google
            </button>
            <button type="button" className="social-btn">
              {/* 方法1：導入的圖片 */}
              {/* <img src={lineLogo} alt="Line" style={{width: "18px", height: "18px", marginRight: "8px"}} /> */}
              
              {/* 方法2：動態路徑 */}
              <img 
                src={lineImgSrc}
                alt="Line" 
                style={{
                  width: "18px", 
                  height: "18px", 
                  marginRight: "8px",
                  objectFit: "contain"
                }} 
                onError={(e) => {
                  console.log('圖片加載失敗');
                  // 如果失敗，使用線上圖片URL
                  e.target.src = "https://upload.wikimedia.org/wikipedia/commons/4/41/LINE_logo.svg";
                }}
              />
              Line
            </button>
          </div>
        </div>
      </div>
      
      <div className="blue-footer"></div>
    </div>
  );
};

export default RegisterForm;