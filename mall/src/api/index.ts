import axios from 'axios'
import type {
  ProductResponse,
  CartResponse,
  OrderResponse,
  CouponInfo,
  UserCouponDetail,
  V1UserResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  CreateOrderRequest,
  PayCallbackRequest,
  ReceiveCouponRequest,
  CalculateDiscountRequest,
  DiscountCalculateResponse,
  PayResponse,
  OrderCancelResponse,
  OrderConfirmReceiptResponse
} from '@/types'
import router from "../router";
import { useAuthStore } from '@/stores/auth';


// helper 函数放这儿
const handleUnauthorized = () => {
  const authStore = useAuthStore()
  authStore.logout()
  router.push('/login')
}

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => {
    if (response.data.code === 200) {
      return response.request?.responseURL?.includes('/users/login') ? response.data : response.data.data
    }
    if (response.data.code === 401) {
      handleUnauthorized();
    }
    return Promise.reject(new Error(response.data.message || '请求失败'))
  },
  (error) => {
    if (error?.response?.data?.code === 401) {
      handleUnauthorized();
    }
    if (error.response?.data?.message) {
      return Promise.reject(new Error(error.response.data.message))
    }
    return Promise.reject(error)
  }
)

export const getProducts = (params?: { skip?: number; limit?: number; category_id?: number }) => {
  return apiClient.get<{
    data: ProductResponse[],
    total: number
  }>('/products/', { params })
}

export const getProduct = (id: number) => {
  return apiClient.get<ProductResponse>(`/products/${id}`)
}

export const getCart = () => {
  return apiClient.get<CartResponse>('/cart/')
}

export const addCartItem = (productId: number, quantity: number = 1) => {
  return apiClient.post('/cart/items', { product_id: productId, quantity })
}

export const updateCartItem = (productId: number, quantity: number) => {
  return apiClient.put(`/cart/items/${productId}`, { quantity })
}

export const removeCartItem = (productId: number) => {
  return apiClient.delete(`/cart/items/${productId}`)
}

export const clearCart = () => {
  return apiClient.delete('/cart/')
}

export const createOrder = (data: CreateOrderRequest) => {
  return apiClient.post<OrderResponse>('/orders/', data)
}

export const getOrders = (params: {
  limit: number,
  skip: number,
}) => {
  return apiClient.get<{
    data: OrderResponse[],
    total: number
  }>('/orders/', { params })
}

export const getOrder = (orderId: number) => {
  return apiClient.get<OrderResponse>(`/orders/${orderId}`)
}

export const payOrder = (orderId: number) => {
  return apiClient.post<PayResponse>(`/pay/${orderId}`)
}

export const payCallback = (data: PayCallbackRequest) => {
  return apiClient.post('/pay/callback', data)
}

export const cancelOrder = (orderId: number) => {
  return apiClient.post<OrderCancelResponse>(`/orders/${orderId}/cancel`)
}

export const confirmReceipt = (orderId: number) => {
  return apiClient.post<OrderConfirmReceiptResponse>(`/orders/${orderId}/confirm-receipt`)
}

export const getCoupons = () => {
  return apiClient.get<CouponInfo[]>('/coupons/')
}

export const receiveCoupon = (couponId: number) => {
  return apiClient.post<UserCouponDetail>('/coupons/receive', { coupon_id: couponId } as ReceiveCouponRequest)
}

export const getMyCoupons = () => {
  return apiClient.get<UserCouponDetail[]>('/coupons/my')
}

export const calculateDiscount = (userCouponId: number, orderAmount: number) => {
  return apiClient.get<DiscountCalculateResponse>('/coupons/calculate', {
    params: { user_coupon_id: userCouponId, order_amount: orderAmount } as CalculateDiscountRequest
  })
}

export const login = (data: LoginRequest) => {
  return apiClient.post<LoginResponse>('/users/login', data)
}

export const register = (data: RegisterRequest) => {
  return apiClient.post<V1UserResponse>('/users/register', data)
}

export const getCurrentUser = () => {
  return apiClient.get<V1UserResponse>('/users/me')
}

export default apiClient
