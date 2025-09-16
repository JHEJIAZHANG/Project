"use client"

import { useState, useEffect, useCallback } from "react"
import { ApiService } from "@/services/apiService"

export interface CustomTodoItem {
  id: string
  category?: string | null
  course?: string | null
  title: string
  description?: string
  dueDate: Date
  status: "pending" | "completed" | "overdue"
  createdAt: Date
  updatedAt: Date
}

function fromBackend(item: any): CustomTodoItem {
  return {
    id: item.id,
    category: item.category ?? null,
    course: item.course ?? null,
    title: item.title,
    description: item.description || "",
    dueDate: new Date(item.due_date),
    status: item.status,
    createdAt: new Date(item.created_at),
    updatedAt: new Date(item.updated_at),
  }
}

function toBackend(item: Omit<CustomTodoItem, "id" | "createdAt" | "updatedAt">) {
  return {
    category: item.category ?? null,
    course: item.course ?? null,
    title: item.title,
    description: item.description || "",
    due_date: item.dueDate.toISOString(),
    status: item.status,
  }
}

export function useCustomTodos(lineUserId: string) {
  const [items, setItems] = useState<CustomTodoItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchItems = useCallback(async () => {
    if (!lineUserId) return
    try {
      setIsLoading(true)
      setError(null)
      const resp = await ApiService.getCustomTodos(lineUserId)
      const data = resp.data?.results || resp.data || []
      if (Array.isArray(data)) {
        setItems(data.map(fromBackend))
      } else {
        setItems([])
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "載入自訂待辦失敗")
    } finally {
      setIsLoading(false)
    }
  }, [lineUserId])

  useEffect(() => {
    fetchItems()
  }, [fetchItems])

  const addItem = useCallback(async (data: Omit<CustomTodoItem, "id" | "createdAt" | "updatedAt">) => {
    const payload = toBackend(data)
    const resp = await ApiService.createCustomTodo(payload)
    if (resp.error) throw new Error(resp.error)
    const created = fromBackend(resp.data)
    setItems(prev => [...prev, created])
    return created
  }, [])

  const updateItem = useCallback(async (id: string, updates: Partial<Omit<CustomTodoItem, "id" | "createdAt" | "updatedAt">>) => {
    const current = items.find(i => i.id === id)
    const base: any = current
      ? {
          title: current.title,
          description: current.description || "",
          due_date: current.dueDate.toISOString(),
          status: current.status,
          category: current.category ?? null,
          course: current.course ?? null,
        }
      : {}

    const payload: any = { ...base }
    if (updates.title !== undefined) payload.title = updates.title
    if (updates.description !== undefined) payload.description = updates.description
    if (updates.dueDate !== undefined) payload.due_date = updates.dueDate.toISOString()
    if (updates.status !== undefined) payload.status = updates.status
    if (updates.category !== undefined) payload.category = updates.category
    if (updates.course !== undefined) payload.course = updates.course

    const resp = await ApiService.updateCustomTodo(id, payload)
    if (resp.error) throw new Error(resp.error)
    const updated = fromBackend(resp.data)
    setItems(prev => prev.map(i => (i.id === id ? updated : i)))
    return updated
  }, [items])

  const deleteItem = useCallback(async (id: string) => {
    const resp = await ApiService.deleteCustomTodo(id)
    if (resp.error) throw new Error(resp.error)
    setItems(prev => prev.filter(i => i.id !== id))
  }, [])

  const getById = (id: string) => items.find(i => i.id === id)

  return { items, isLoading, error, addItem, updateItem, deleteItem, getById, refetch: fetchItems }
}
