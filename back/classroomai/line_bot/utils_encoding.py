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

def encode_coursework_id_for_google_classroom(coursework_id: str) -> str:
    """
    將作業 ID 編碼為 Google Classroom 可用的格式
    
    Args:
        coursework_id (str): 原始作業 ID
        
    Returns:
        str: 編碼後的作業 ID
        
    Example:
        >>> encode_coursework_id_for_google_classroom("796003477940")
        >>> "Nzk2MDAzNDc3OTQw"
    """
    try:
        # 將作業 ID 轉換為 bytes，然後進行 base64 編碼
        coursework_id_bytes = coursework_id.encode('utf-8')
        encoded_bytes = base64.b64encode(coursework_id_bytes)
        encoded_id = encoded_bytes.decode('utf-8')
        
        # 移除可能的填充字符 '='
        encoded_id = encoded_id.rstrip('=')
        
        return encoded_id
    except Exception as e:
        # 如果編碼失敗，返回原始 ID 並記錄錯誤
        print(f"作業 ID 編碼失敗: {coursework_id}, 錯誤: {str(e)}")
        return coursework_id

def create_google_classroom_course_url(course_id: str) -> str:
    """
    建立 Google Classroom 課程連結
    
    Args:
        course_id (str): 原始課程 ID
        
    Returns:
        str: 完整的課程連結
    """
    encoded_course_id = encode_course_id_for_google_classroom(course_id)
    return f"https://classroom.google.com/c/{encoded_course_id}"

def create_google_classroom_assignment_url(course_id: str, coursework_id: str) -> str:
    """
    建立 Google Classroom 作業連結
    
    Args:
        course_id (str): 原始課程 ID
        coursework_id (str): 原始作業 ID
        
    Returns:
        str: 完整的作業連結
        
    Example:
        >>> create_google_classroom_assignment_url("800118618225", "796003477940")
        >>> "https://classroom.google.com/c/ODAwMTE4NjE4MjI1/a/Nzk2MDAzNDc3OTQw/details"
    """
    encoded_course_id = encode_course_id_for_google_classroom(course_id)
    encoded_coursework_id = encode_coursework_id_for_google_classroom(coursework_id)
    return f"https://classroom.google.com/c/{encoded_course_id}/a/{encoded_coursework_id}/details"
