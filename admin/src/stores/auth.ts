import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const removeToken = () => {
    token.value = null
    localStorage.removeItem('token')
  }

  const login = async (username: string, password: string) => {
    const response = await loginApi(username, password)
    setToken((response as any).access_token)
    return response
  }

  const logout = () => {
    removeToken()
  }

  return {
    token,
    isAuthenticated,
    setToken,
    removeToken,
    login,
    logout
  }
})
