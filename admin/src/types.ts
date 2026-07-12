export interface AdminUserResponse {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export interface ProductResponse {
  id: number
  name: string
  description: string | null
  price: string
  stock: number
  is_active: boolean
  category_id: number | null
  created_at: string
}

export interface CategoryResponse {
  id: number
  name: string
  parent_id: number | null
}

export interface OrderItemResponse {
  id: number
  product_id: number
  product_name: string
  price: string
  quantity: number
}

export interface OrderResponse {
  id: number
  user_id: number
  total_amount: string
  status: string
  address: string
  created_at: string
  items: OrderItemResponse[]
}

export interface CouponInfo {
  id: number
  code: string
  name: string
  discount_type: string
  discount_value: string
  min_order_amount: string
  max_discount_amount: string | null
  remain_count: number
  start_time: string
  end_time: string
}

export interface ApiResponse<T> {
  code: number
  data: T
  message: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface ChangePasswordResponse {
  message: string
}

export interface OrderStatusMessage {
  message: string
  status: string
}

export interface UpdateCouponResponse {
  id: number
  code: string
  name: string
  discount_type: string
  discount_value: string
  min_order_amount: string
  max_discount_amount: string | null
  remain_count?: number
  start_time: string
  end_time: string
}
