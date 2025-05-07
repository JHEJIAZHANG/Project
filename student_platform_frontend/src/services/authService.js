<<<<<<< HEAD
// 為初學者簡化版本
export const authService = {
    login: async (email, password) => {
      // 實際應用中，這裡會是API請求
      // 這是一個簡化的示例
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          // 模擬驗證
          if (email === 'test@example.com' && password === 'password') {
            resolve({
              user: {
                id: 1,
                email: email,
                name: 'Test User'
              }
            });
          } else {
            reject({ message: '無效的電子郵件或密碼' });
          }
        }, 1000);
      });
    },
    
    // 您可以添加更多方法，如註冊、登出等
=======
export const authService = {
    register: async (email, password, name) => {
      // 這是示例實作，實際需根據您的後端 API 或認證服務調整
      try {
        console.log('註冊請求:', { email, password, name });
        await new Promise(resolve => setTimeout(resolve, 1000));
        return { success: true, message: '註冊成功' };
      } catch (error) {
        console.error('註冊錯誤:', error);
        throw new Error('註冊時發生錯誤，請稍後再試');
      }
    },
  
    loginWithGoogle: async () => {
      console.log('Google 登入');
    },
  
    loginWithLine: async () => {
      console.log('Line 登入');
    }
>>>>>>> 18
  };