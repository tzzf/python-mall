import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, getCurrentUser as apiGetCurrentUser } from '@/api'
import type { LoginRequest, RegisterRequest, V1UserResponse } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const currentUser = ref<V1UserResponse | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (data: LoginRequest) => {
    const response = await apiLogin(data) as unknown as { access_token: string }
    token.value = response.access_token
    localStorage.setItem('access_token', response.access_token)
    await fetchCurrentUser()
    return response
  }

  const register = async (data: RegisterRequest) => {
    const response = await apiRegister(data)
    return response
  }

  const logout = () => {
    token.value = null
    currentUser.value = null
    localStorage.removeItem('access_token')
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return null
    try {
      const response = await apiGetCurrentUser() as unknown as V1UserResponse
      currentUser.value = response
      return response
    } catch {
      logout()
      return null
    }
  }

  return {
    token,
    currentUser,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser
  }
})
