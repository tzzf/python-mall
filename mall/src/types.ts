export interface ProductResponse {
  id: number
  name: string
  description: string | null
  price: string
  original_price?: string
  image?: string
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

export interface CartResponse {
  user_id: number
  items: CartItemResponse[]
  total_count: number
}

export interface CartItemResponse {
  product_id: number
  quantity: number
  product_name: string | null
  price: string | null
  image: string | null
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

export interface OrderItemResponse {
  id: number
  product_id: number
  product_name: string
  price: string
  quantity: number
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

export interface UserCouponDetail {
  id: number
  coupon_id: number
  code: string
  name: string
  discount_type: string
  discount_value: string
  status: string
  received_at: string
}

export interface V1UserResponse {
  id: number
  username: string
  email: string
  is_active: boolean
  is_channel: boolean
  channel_status: string
  created_at: string
}

export interface ApiResponse<T> {
  code: number
  data: T
  message: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  invite_code?: string
}

export interface CreateOrderRequest {
  address: string
  items: { product_id: number; quantity: number }[]
}

export interface PayCallbackRequest {
  order_id: number
  pay_status: 'success' | 'failed'
  transaction_id?: string
}

export interface ReceiveCouponRequest {
  coupon_id: number
}

export interface CalculateDiscountRequest {
  user_coupon_id: number
  order_amount: number
}

export interface DiscountCalculateResponse {
  original_amount: string
  discount_amount: string
  final_amount: string
  coupon_code: string
}

export interface PayResponse {
  order_id: number
  pay_url: string
  qr_code: string
  amount: string
}

export interface OrderCancelResponse {
  id: number
  status: string
  message: string
}

export interface OrderConfirmReceiptResponse {
  id: number
  status: string
  message: string
}
