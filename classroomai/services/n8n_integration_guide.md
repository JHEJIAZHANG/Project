# n8n 工作流整合指南

## 自然語言意圖識別規則

### 1. 本地課程操作意圖

#### 創建本地課程
- **意圖類型**: `create_local_course`
- **觸發關鍵詞**: 
  - "新增課程", "創建課程", "建立課程"
  - "我想新增一個課程", "幫我創建課程"
  - "新增一個我的自訂課程"
- **參數提取**:
  ```javascript
  {
    intent: 'create_local_course',
    parameters: {
      title: '課程名稱',
      description: '課程描述（可選）',
      instructor: '講師名稱（可選）',
      classroom: '教室位置（可選）',
      color: '顏色代碼（可選，預設 #8b5cf6）'
    }
  }
  ```
- **API 路由**: `POST /api/v2/web/courses/create/`

#### 更新本地課程
- **意圖類型**: `update_local_course`
- **觸發關鍵詞**:
  - "修改課程", "更新課程", "改課程"
  - "幫我把XXX課程的名稱改成YYY"
  - "更新資料結構課程的教室位置"
- **參數提取**:
  ```javascript
  {
    intent: 'update_local_course',
    parameters: {
      course_name: '課程名稱（用於查找）',
      title: '新課程名稱（可選）',
      description: '新描述（可選）',
      instructor: '新講師（可選）',
      classroom: '新教室（可選）'
    }
  }
  ```
- **API 路由**: `PATCH /api/v2/web/courses/update/`

#### 刪除本地課程
- **意圖類型**: `delete_local_course`
- **觸發關鍵詞**:
  - "刪除課程", "移除課程", "取消課程"
  - "幫我刪除XXX課程"
- **參數提取**:
  ```javascript
  {
    intent: 'delete_local_course',
    parameters: {
      course_name: '要刪除的課程名稱'
    }
  }
  ```
- **API 路由**: `DELETE /api/v2/web/courses/delete/`

### 2. 本地作業操作意圖

#### 創建本地作業
- **意圖類型**: `create_local_assignment`
- **觸發關鍵詞**:
  - "新增作業", "創建作業", "建立作業"
  - "幫我在XXX課程新增一個作業"
  - "我要新增一個作業到資料結構課程"
- **參數提取**:
  ```javascript
  {
    intent: 'create_local_assignment',
    parameters: {
      course_name: '課程名稱',
      title: '作業標題',
      description: '作業描述（可選）',
      due_date: '截止日期',
      type: '作業類型（可選）'
    }
  }
  ```
- **API 路由**: `POST /api/v2/web/assignments/create/`

#### 更新本地作業
- **意圖類型**: `update_local_assignment`
- **觸發關鍵詞**:
  - "修改作業", "更新作業", "改作業截止日期"
  - "幫我把XXX課程的作業Y截止改到9/30"
  - "更新資料結構作業1的截止時間"
- **參數提取**:
  ```javascript
  {
    intent: 'update_local_assignment',
    parameters: {
      course_name: '課程名稱（可選）',
      assignment_name: '作業名稱',
      title: '新標題（可選）',
      description: '新描述（可選）',
      due_date: '新截止日期（可選）',
      status: '新狀態（可選）'
    }
  }
  ```
- **API 路由**: `PATCH /api/v2/web/assignments/update/`

#### 刪除本地作業
- **意圖類型**: `delete_local_assignment`
- **觸發關鍵詞**:
  - "刪除作業", "移除作業", "取消作業"
  - "幫我刪除XXX作業"
- **參數提取**:
  ```javascript
  {
    intent: 'delete_local_assignment',
    parameters: {
      assignment_name: '作業名稱',
      course_name: '課程名稱（可選，用於精確匹配）'
    }
  }
  ```
- **API 路由**: `DELETE /api/v2/web/assignments/delete/`

### 3. 課程時間設定意圖

#### 設定課程時間
- **意圖類型**: `set_course_schedule`
- **觸發關鍵詞**:
  - "設定課程時間", "設定上課時間", "課程時間"
  - "幫我設定資料結構課程的時間是週二上午9點到10點半"
  - "XXX課程的上課時間是週三下午2點到4點"
- **參數提取**:
  ```javascript
  {
    intent: 'set_course_schedule',
    parameters: {
      course_name: '課程名稱',
      schedules: [
        {
          day_of_week: 1, // 0=週一, 1=週二, ...
          start_time: '09:00:00',
          end_time: '10:30:00',
          location: '教室位置（可選）'
        }
      ]
    }
  }
  ```
- **API 路由**: `POST /api/v2/web/courses/schedule/`

### 4. 查詢整合資料意圖

#### 查詢我的課程
- **意圖類型**: `list_my_courses`
- **觸發關鍵詞**:
  - "我的課程", "查看課程", "課程列表"
  - "顯示我所有的課程"
- **API 路由**: `GET /api/v2/web/courses/list/`

#### 查詢我的作業
- **意圖類型**: `list_my_assignments`
- **觸發關鍵詞**:
  - "我的作業", "查看作業", "作業列表"
  - "顯示即將到期的作業", "未完成的作業"
- **參數提取**:
  ```javascript
  {
    intent: 'list_my_assignments',
    parameters: {
      status: 'pending|completed|overdue（可選）',
      upcomingWithinDays: 7 // 幾天內到期（可選）
    }
  }
  ```
- **API 路由**: `GET /api/v2/web/assignments/list/`

### 5. 同步操作意圖

#### 全量同步
- **意圖類型**: `sync_all_classroom`
- **觸發關鍵詞**:
  - "同步所有課程", "更新所有資料", "全量同步"
  - "幫我同步 Classroom 的所有課程"
- **API 路由**: `POST /api/v2/sync/classroom-to-v2/`

#### 單一課程同步
- **意圖類型**: `sync_single_course`
- **觸發關鍵詞**:
  - "同步XXX課程", "更新XXX課程資料"
  - "幫我同步資料結構課程"
- **參數提取**:
  ```javascript
  {
    intent: 'sync_single_course',
    parameters: {
      course_name: '課程名稱'
    }
  }
  ```
- **API 路由**: `POST /api/v2/sync/classroom-course/`

## n8n 工作流實作範例

### 1. 意圖識別節點
```javascript
// AI Agent 回傳的意圖識別結果
const aiResponse = {
  intent: 'create_local_course',
  parameters: {
    title: '機器學習導論',
    instructor: '張教授',
    classroom: 'A101'
  },
  confidence: 0.95
};

// 根據意圖路由到對應的 API
switch(aiResponse.intent) {
  case 'create_local_course':
    return {
      endpoint: '/api/v2/web/courses/create/',
      method: 'POST',
      data: {
        line_user_id: $('Webhook').first().body.line_user_id,
        title: aiResponse.parameters.title,
        instructor: aiResponse.parameters.instructor,
        classroom: aiResponse.parameters.classroom
      }
    };
  
  case 'update_local_assignment':
    // 先查找作業 ID
    const assignment = await findAssignmentByName(
      aiResponse.parameters.assignment_name,
      aiResponse.parameters.course_name
    );
    
    return {
      endpoint: '/api/v2/web/assignments/update/',
      method: 'PATCH',
      data: {
        line_user_id: $('Webhook').first().body.line_user_id,
        assignment_id: assignment.id,
        due_date: aiResponse.parameters.due_date
      }
    };
}
```

### 2. 課程/作業查找節點
```javascript
// 根據名稱查找課程 ID
async function findCourseByName(courseName, userId) {
  const response = await $http.request({
    method: 'GET',
    url: `/api/v2/web/courses/list/?line_user_id=${userId}`,
  });
  
  const courses = response.data.courses;
  const course = courses.find(c => 
    c.title.includes(courseName) || 
    courseName.includes(c.title)
  );
  
  if (!course) {
    throw new Error(`找不到課程: ${courseName}`);
  }
  
  return course;
}

// 根據名稱查找作業 ID
async function findAssignmentByName(assignmentName, courseName, userId) {
  const response = await $http.request({
    method: 'GET',
    url: `/api/v2/web/assignments/list/?line_user_id=${userId}`,
  });
  
  let assignments = response.data.assignments;
  
  // 如果指定了課程名稱，先篩選課程
  if (courseName) {
    assignments = assignments.filter(a => 
      a.course.title.includes(courseName) || 
      courseName.includes(a.course.title)
    );
  }
  
  // 查找作業
  const assignment = assignments.find(a => 
    a.title.includes(assignmentName) || 
    assignmentName.includes(a.title)
  );
  
  if (!assignment) {
    throw new Error(`找不到作業: ${assignmentName}`);
  }
  
  return assignment;
}
```

### 3. 自動同步觸發節點
```javascript
// 在老師 Classroom 操作成功後觸發
if (response.success && userRole === 'teacher') {
  // 觸發單一課程同步
  const syncResponse = await $http.request({
    method: 'POST',
    url: '/api/v2/sync/classroom-course/',
    data: {
      line_user_id: userId,
      google_course_id: response.data.course_id
    }
  });
  
  if (syncResponse.success) {
    console.log(`課程同步成功: ${syncResponse.data.assignments_synced} 個作業已更新`);
  }
}
```

### 4. 時間解析節點
```javascript
// 解析自然語言中的時間表達
function parseScheduleFromText(text) {
  const dayMap = {
    '週一': 0, '週二': 1, '週三': 2, '週四': 3, '週五': 4, '週六': 5, '週日': 6,
    '星期一': 0, '星期二': 1, '星期三': 2, '星期四': 3, '星期五': 4, '星期六': 5, '星期日': 6
  };
  
  // 解析星期幾
  let dayOfWeek = null;
  for (const [day, num] of Object.entries(dayMap)) {
    if (text.includes(day)) {
      dayOfWeek = num;
      break;
    }
  }
  
  // 解析時間 (簡化版本)
  const timeRegex = /(\d{1,2})[點:](\d{0,2})/g;
  const times = [];
  let match;
  
  while ((match = timeRegex.exec(text)) !== null) {
    const hour = parseInt(match[1]);
    const minute = match[2] ? parseInt(match[2]) : 0;
    times.push(`${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}:00`);
  }
  
  if (dayOfWeek !== null && times.length >= 2) {
    return {
      day_of_week: dayOfWeek,
      start_time: times[0],
      end_time: times[1]
    };
  }
  
  return null;
}

// 使用範例
const scheduleText = "週二上午9點到10點半";
const schedule = parseScheduleFromText(scheduleText);
// 結果: { day_of_week: 1, start_time: "09:00:00", end_time: "10:30:00" }
```

## 錯誤處理和回應格式

### 成功回應處理
```javascript
if (apiResponse.success) {
  // 根據不同操作類型回傳適當的訊息
  switch(intent) {
    case 'create_local_course':
      return `✅ 課程「${apiResponse.data.title}」創建成功！`;
    
    case 'update_local_assignment':
      return `✅ 作業「${apiResponse.data.title}」更新成功！`;
    
    case 'set_course_schedule':
      return `✅ 課程時間設定成功！已設定 ${apiResponse.data.schedules_count} 個時段。`;
    
    case 'sync_all_classroom':
      return `✅ 同步完成！已同步 ${apiResponse.data.courses_synced} 個課程，${apiResponse.data.assignments_synced} 個作業。`;
  }
}
```

### 錯誤處理
```javascript
if (!apiResponse.success) {
  switch(apiResponse.code) {
    case 'CLASSROOM_DATA_READONLY':
      return '❌ 無法修改 Google Classroom 同步的資料，請在 Classroom 中進行修改。';
    
    case 'MISSING_LINE_USER_ID':
      return '❌ 系統錯誤：無法識別使用者身份。';
    
    case 'WEB_DATA_ERROR':
      return `❌ 操作失敗：${apiResponse.message}`;
    
    default:
      return `❌ 發生錯誤：${apiResponse.message}`;
  }
}
```

## 部署注意事項

1. **API 端點配置**: 確保 n8n 能夠訪問 Django API 端點
2. **錯誤重試**: 實作適當的重試機制處理網路錯誤
3. **日誌記錄**: 記錄所有 API 呼叫和回應以便除錯
4. **權限驗證**: 確保所有 API 呼叫都包含正確的 line_user_id
5. **資料驗證**: 在呼叫 API 前驗證參數格式和必要欄位