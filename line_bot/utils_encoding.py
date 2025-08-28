# line_bot/utils_encoding.py
"""
編碼相關的工具函數
避免循環導入問題
"""

import base64

def encode_course_id_for_google_classroom(course_id: str) -> str:
    """
    將課程 ID 編碼為 Google Classroom 可用的格式
    
    Google Classroom 的課程 ID 需要進行 base64 編碼才能正確連接。
    這個函數會將課程 ID 轉換為正確的格式。
    
    Args:
        course_id (str): 原始課程 ID
        
    Returns:
        str: 編碼後的課程 ID
        
    Example:
        >>> encode_course_id_for_google_classroom("799315197222")
        >>> "Nzk5MzE1MTk3MjIy"
    """
    try:
        # 將課程 ID 轉換為 bytes，然後進行 base64 編碼
        course_id_bytes = course_id.encode('utf-8')
        encoded_bytes = base64.b64encode(course_id_bytes)
        encoded_id = encoded_bytes.decode('utf-8')
        
        # 移除可能的填充字符 '='
        encoded_id = encoded_id.rstrip('=')
        
        return encoded_id
    except Exception as e:
        # 如果編碼失敗，返回原始 ID 並記錄錯誤
        print(f"課程 ID 編碼失敗: {course_id}, 錯誤: {str(e)}")
        return course_id
