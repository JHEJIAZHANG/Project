const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v2'

export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
  details?: any
}

export class ApiService {
  private static lineUserId: string = ''
  static get backendOrigin() {
    try { return new URL(API_BASE_URL).origin } catch { return '' }
  }

  static setLineUserId(userId: string) {
    this.lineUserId = userId
  }

  static getLineUserId() {
    return this.lineUserId
  }

  // 訪客模式：在瀏覽器產生並保存 guest lineUserId
  static bootstrapLineUserId(): string {
    if (typeof window === 'undefined') return this.lineUserId || ''
    try {
      const KEY = 'lineUserId'
      let id = localStorage.getItem(KEY) || ''
      if (!id) {
        const uuid = (globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`)
        id = `guest-${uuid}`
        localStorage.setItem(KEY, id)
      }
      this.setLineUserId(id)
      return id
    } catch {
      // 無法使用 localStorage 時，回退為臨時 ID（不持久化）
      const temp = this.lineUserId || `guest-${Date.now()}`
      this.setLineUserId(temp)
      return temp
    }
  }

  private static async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData
      const baseHeaders: Record<string, any> = {
        'X-Line-User-Id': this.lineUserId,
        ...(options.headers || {}),
      }
      if (!isFormData) {
        baseHeaders['Content-Type'] = 'application/json'
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: baseHeaders,
      })

      if (!response.ok) {
        // 後端可能回傳非 JSON 錯誤或空 body
        const errText = await response.text().catch(() => '')
        let errJson: any = {}
        try { errJson = errText ? JSON.parse(errText) : {} } catch { errJson = {} }
        return {
          error: errJson.message || `HTTP ${response.status}`,
          details: errJson || errText
        }
      }

      // 處理 204 或空 body
      const contentType = response.headers.get('content-type') || ''
      if (response.status === 204) {
        return { data: null as any }
      }
      const raw = await response.text()
      if (!raw) {
        return { data: null as any }
      }
      if (!contentType.includes('application/json')) {
        return { data: raw as any }
      }
      const data = JSON.parse(raw)
      return { data }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : '網路錯誤'
      }
    }
  }

  // 用戶相關 API
  static async getProfile(lineUserId: string) {
    return this.request(`/profile/${lineUserId}/`)
  }

  static async updateProfile(lineUserId: string, data: any) {
    return this.request(`/profile/${lineUserId}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  // 課程相關 API
  static async getCourses(lineUserId: string) {
    this.setLineUserId(lineUserId)
    return this.request('/courses/')
  }

  static async createCourse(data: any) {
    return this.request('/courses/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  static async updateCourse(courseId: string, data: any) {
    return this.request(`/courses/${courseId}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  static async deleteCourse(courseId: string) {
    return this.request(`/courses/${courseId}/`, {
      method: 'DELETE'
    })
  }

  // 作業相關 API
  static async getAssignments(lineUserId: string) {
    this.setLineUserId(lineUserId)
    return this.request('/assignments/')
  }

  static async createAssignment(data: any) {
    return this.request('/assignments/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  static async updateAssignment(assignmentId: string, data: any) {
    return this.request(`/assignments/${assignmentId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  static async updateAssignmentStatus(assignmentId: string, status: 'pending' | 'completed' | 'overdue') {
    return this.request(`/assignments/${assignmentId}/status/`, {
      method: 'POST',
      body: JSON.stringify({ status })
    })
  }

  static async deleteAssignment(assignmentId: string) {
    return this.request(`/assignments/${assignmentId}/`, {
      method: 'DELETE'
    })
  }

  static async getAssignmentRecommendations(assignmentId: string, options?: { limit?: number; perSource?: number; q?: string }) {
    const limit = options?.limit
    const perSource = options?.perSource
    const q = options?.q
    const qs = new URLSearchParams()
    if (typeof limit === 'number') qs.set('limit', String(limit))
    if (typeof perSource === 'number') qs.set('per_source', String(perSource))
    if (typeof q === 'string' && q.trim()) qs.set('q', q.trim())
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return this.request<{
      assignment: string
      query: string
      results: Array<{ source: string; url: string; title: string; snippet?: string; score?: number }>
      meta?: { sources?: Record<string, number> }
    }>(`/assignments/${assignmentId}/recommendations/${suffix}`)
  }

  // 筆記相關 API
  static async getNotes(lineUserId: string) {
    this.setLineUserId(lineUserId)
    return this.request('/notes/')
  }

  static async createNote(data: any) {
    return this.request('/notes/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  static async updateNote(noteId: string, data: any) {
    return this.request(`/notes/${noteId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  static async deleteNote(noteId: string) {
    return this.request(`/notes/${noteId}/`, {
      method: 'DELETE'
    })
  }

  // 考試相關 API
  static async getExams(lineUserId: string) {
    this.setLineUserId(lineUserId)
    return this.request('/exams/')
  }

  static async createExam(data: any) {
    return this.request('/exams/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  static async updateExam(examId: string, data: any) {
    return this.request(`/exams/${examId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  static async updateExamStatus(examId: string, status: 'pending' | 'completed' | 'overdue') {
    return this.request(`/exams/${examId}/status/`, {
      method: 'POST',
      body: JSON.stringify({ status })
    })
  }

  static async deleteExam(examId: string) {
    return this.request(`/exams/${examId}/`, {
      method: 'DELETE'
    })
  }

  // 檔案相關 API
  static async uploadFile(file: File, extra?: { noteId?: string; courseId?: string; assignmentId?: string; examId?: string }) {
    // 確保 lineUserId 已初始化
    if (!this.lineUserId) {
      this.bootstrapLineUserId()
    }

    const formData = new FormData()
    formData.append('file', file)
    if (extra?.noteId) formData.append('noteId', extra.noteId)
    if (extra?.courseId) formData.append('courseId', extra.courseId)
    if (extra?.assignmentId) formData.append('assignmentId', extra.assignmentId)
    if (extra?.examId) formData.append('examId', extra.examId)

    return this.request('/files/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-Line-User-Id': this.lineUserId,
        // 不設定 Content-Type，讓瀏覽器自動設定 multipart/form-data
      }
    })
  }

  static async getFile(fileId: string) {
    return this.request(`/files/${fileId}/`)
  }

  static async deleteFile(fileId: string) {
    return this.request(`/files/${fileId}/`, {
      method: 'DELETE'
    })
  }

  // 自訂分類 API
  static async getCustomCategories(lineUserId: string) {
    this.setLineUserId(lineUserId)
    return this.request('/custom-categories/')
  }

  static async createCustomCategory(data: { name: string; icon?: string; color?: string }) {
    return this.request('/custom-categories/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  static async updateCustomCategory(id: string, data: Partial<{ name: string; icon: string; color: string }>) {
    return this.request(`/custom-categories/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  static async deleteCustomCategory(id: string) {
    return this.request(`/custom-categories/${id}/`, {
      method: 'DELETE'
    })
  }

  // 自訂待辦 API
  static async getCustomTodos(lineUserId: string, params?: Record<string, string>) {
    this.setLineUserId(lineUserId)
    const query = params ? `?${new URLSearchParams(params).toString()}` : ''
    return this.request(`/custom-todos/${query}`)
  }

  static async createCustomTodo(data: {
    category?: string | null
    course?: string | null
    title: string
    description?: string
    due_date: string
    status?: 'pending' | 'completed' | 'overdue'
  }) {
    return this.request('/custom-todos/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  static async updateCustomTodo(id: string, data: Partial<{ title: string; description: string; due_date: string; status: 'pending' | 'completed' | 'overdue'; category: string | null; course: string | null }>) {
    return this.request(`/custom-todos/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  static async deleteCustomTodo(id: string) {
    return this.request(`/custom-todos/${id}/`, {
      method: 'DELETE'
    })
  }
}
