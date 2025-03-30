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
  };