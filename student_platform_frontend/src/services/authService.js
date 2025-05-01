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
  };