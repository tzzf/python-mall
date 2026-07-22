import axios from 'axios'
import type {
  AdminUserResponse,
  ProductResponse,
  CategoryResponse,
  OrderResponse,
  CouponInfo,
  TokenResponse,
  OrderStatusMessage,
  UpdateCouponResponse
} from '../types'
import { useAuthStore } from '../stores/auth'
import router from '../router'


const api = axios.create({
  baseURL: '/api/admin',
  timeout: 10000 * 200
})

api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    if (response.data.code === 200) {

      return response.request?.responseURL?.includes('/users/login') ? response.data : response.data.data
    }
    if (response.data.code === 401) {
      router.push('/login')
    }
    return Promise.reject(new Error(response.data.message || '请求失败'))
  },
  (error) => {
    if (error?.response?.data?.code === 401) {
      router.push('/login')
    }
    if (error.response?.data?.message) {
      return Promise.reject(new Error(error.response.data.message))
    }
    return Promise.reject(error)
  }
)

// Auth APIs
export const login = (username: string, password: string) =>
  api.post<TokenResponse>('/users/login', { username, password })

// User APIs
export const getUsers = () => api.get<AdminUserResponse[]>('/users/')

export const updateUser = (id: number, data: Partial<AdminUserResponse>) =>
  api.put<AdminUserResponse>(`/users/${id}`, data)

export const deleteUser = (id: number) => api.delete(`/users/${id}`)

export const changePassword = (id: number, oldPassword: string, newPassword: string) =>
  api.put<{ message: string }>(`/users/${id}/password`, { old_password: oldPassword, new_password: newPassword })

// Product APIs
export const getProducts = (params: {
  limit: number,
  skip: number,
}) => api.get<{
  data: ProductResponse[],
  total: number
}>('/products/', { params })

export const getProduct = (id: number) => api.get<ProductResponse>(`/products/${id}`)

export const createProduct = (data: Partial<ProductResponse>) =>
  api.post<ProductResponse>('/products/', data)

export const updateProduct = (id: number, data: Partial<ProductResponse>) =>
  api.put<ProductResponse>(`/products/${id}`, data)

export const deleteProduct = (id: number) => api.delete(`/products/${id}`)

export const regenerateProductImage = (id: number) =>
  api.post(`/products/${id}/generate-image`)

// Category APIs
export const getCategories = () => api.get<CategoryResponse[]>('/products/categories')

export const createCategory = (data: { name: string; parent_id?: number | null }) =>
  api.post<CategoryResponse>('/products/categories', data)

export const updateCategory = (id: number, data: { name?: string; parent_id?: number | null }) =>
  api.patch<CategoryResponse>(`/products/categories/${id}`, data)

export const deleteCategory = (id: number) => api.delete(`/products/categories/${id}`)

// Order APIs
export const getOrders = (status?: string, skip?: number, limit?: number) => {
  const params = status ? { status, skip, limit } : { skip, limit }
  return api.get<{
    data: OrderResponse[],
    total: number
  }>('/orders/', { params })
}

export const updateOrderStatus = (orderId: number, status: string) =>
  api.put<OrderStatusMessage>(`/orders/${orderId}/status`, { status })

// Coupon APIs
export const getCoupons = (params: {
  limit: number,
  skip: number,
}) => api.get<CouponInfo[]>('/coupons/', { params })

export const createCoupon = (data: Partial<CouponInfo>) =>
  api.post<CouponInfo>('/coupons/', data)

export const updateCoupon = (id: number, data: Partial<CouponInfo>) =>
  api.patch<UpdateCouponResponse>(`/coupons/${id}`, data)

export default api
