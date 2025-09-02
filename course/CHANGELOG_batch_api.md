# 批量作業提交狀態查詢 API 優化 - 變更日誌

## 版本: v2.0.0
## 日期: 2024-01-XX
## 類型: 功能增強 + 向後相容

## 🎯 主要改進

### 1. 新增批量查詢功能
- **支援多課程多作業查詢**：一次 API 呼叫可以查詢多個課程的多個作業
- **兩種批量查詢方式**：
  - `course_coursework_pairs`：明確指定課程作業對應關係
  - `course_ids + coursework_ids`：並行陣列方式
- **智能角色辨識**：自動識別用戶在不同課程中的角色（教師/學生）

### 2. 保持向後相容性
- **原有 API 呼叫方式完全不受影響**
- **單一查詢模式**：`course_id + coursework_id` 參數仍然有效
- **回傳格式一致**：單一查詢的回傳格式保持不變

### 3. 增強錯誤處理
- **批量查詢中的個別失敗不影響其他查詢**
- **詳細的錯誤報告**：包含成功查詢數量和失敗查詢數量
- **參數驗證增強**：更嚴格的輸入驗證和錯誤提示

## 🔧 技術改進

### 1. Serializer 優化
```python
# 新增欄位
course_ids = serializers.ListField(...)
coursework_ids = serializers.ListField(...)
course_coursework_pairs = serializers.ListField(...)

# 智能驗證
def validate(self, data):
    # 檢查查詢模式
    # 驗證參數完整性
    # 確保數量匹配
```

### 2. View 邏輯重構
```python
# 查詢模式判斷
if ser.validated_data.get("course_id") and ser.validated_data.get("coursework_id"):
    query_mode = "single"
else:
    query_mode = "batch"

# 批量處理
for query_item in query_items:
    # 處理每個課程作業組合
    # 角色辨識和權限驗證
    # 資料查詢和暫存
```

### 3. 結果處理優化
```python
# 單一查詢：保持原有行為
if query_mode == "single":
    # 教師：發送 Flex Message
    # 學生：回傳詳細狀態

# 批量查詢：回傳綜合結果
else:
    return Response({
        "query_mode": "batch",
        "total_queries": len(query_items),
        "successful_queries": successful_count,
        "failed_queries": failed_count,
        "results": all_results
    })
```

## 📊 效能提升

### 1. 減少 API 呼叫次數
- **批量查詢**：一次呼叫處理多個課程作業
- **資料庫暫存**：教師查詢使用暫存機制
- **智能快取**：避免重複查詢相同資料

### 2. 並行處理
- **批量處理**：同時處理多個查詢項目
- **錯誤隔離**：個別失敗不影響整體效能
- **資源優化**：減少網路延遲和等待時間

## 🛡️ 安全性增強

### 1. 角色驗證
- **Google API 驗證**：使用官方 API 驗證教師身份
- **備用驗證機制**：課程擁有者檢查
- **權限隔離**：學生只能查看自己的狀態

### 2. 資料保護
- **個資暫存**：學生資料存在資料庫，不透過 API 回傳
- **隱私保護**：教師統計不包含學生個資
- **存取控制**：LINE 用戶身份驗證

## 📝 API 使用範例

### 單一查詢（原有方式）
```bash
POST /api/classroom/submissions/status
{
  "line_user_id": "U1234567890abcdef",
  "course_id": "course_id_1",
  "coursework_id": "coursework_id_1"
}
```

### 批量查詢 - 方法一
```bash
POST /api/classroom/submissions/status
{
  "line_user_id": "U1234567890abcdef",
  "course_coursework_pairs": [
    {"course_id": "course_1", "coursework_id": "hw_1"},
    {"course_id": "course_2", "coursework_id": "hw_2"}
  ]
}
```

### 批量查詢 - 方法二
```bash
POST /api/classroom/submissions/status
{
  "line_user_id": "U1234567890abcdef",
  "course_ids": ["course_1", "course_2"],
  "coursework_ids": ["hw_1", "hw_2"]
}
```

## 🧪 測試覆蓋

### 1. 單元測試
- **參數驗證**：各種輸入組合的驗證
- **查詢模式**：單一查詢和批量查詢的切換
- **錯誤處理**：異常情況的處理邏輯

### 2. 整合測試
- **角色辨識**：教師和學生角色的正確識別
- **資料暫存**：暫存機制的正常運作
- **API 回傳**：各種查詢模式的回傳格式

### 3. 效能測試
- **批量查詢效能**：多課程作業查詢的響應時間
- **記憶體使用**：大量查詢的記憶體消耗
- **並發處理**：多用戶同時查詢的穩定性

## 🚀 部署注意事項

### 1. 資料庫
- **無需遷移**：現有資料庫結構完全相容
- **暫存清理**：定期清理過期的作業統計暫存資料

### 2. 環境變數
- **無新增需求**：使用現有的 Google API 和 LINE Bot 設定
- **權限檢查**：確保 Google Classroom API 權限正常

### 3. 監控建議
- **API 響應時間**：監控批量查詢的效能
- **錯誤率**：追蹤查詢失敗的頻率
- **暫存命中率**：監控暫存機制的效果

## 🔮 未來規劃

### 1. 進階功能
- **查詢條件過濾**：支援時間範圍、狀態篩選等
- **分頁查詢**：大量課程作業的分頁處理
- **即時通知**：作業狀態變更的即時推送

### 2. 效能優化
- **非同步處理**：大量查詢的非同步執行
- **分散式快取**：Redis 等分散式快取支援
- **查詢預熱**：定期預熱常用查詢結果

### 3. 監控增強
- **詳細指標**：查詢效能、成功率等詳細指標
- **告警機制**：異常情況的自動告警
- **效能分析**：查詢模式的效能分析報告

## 📞 技術支援

如有任何問題或建議，請聯繫開發團隊或查看相關文件：
- API 文檔：`README_batch_submissions_api.md`
- 測試腳本：`test_batch_api.py`
- 變更日誌：`CHANGELOG_batch_api.md`
