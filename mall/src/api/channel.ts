import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { handleUnauthorized } from './index'

const api = axios.create({
  baseURL: '/api/v1',
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
      return response.request?.responseURL?.includes('/users/login')
        ? response.data
        : response.data.data
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

export interface ChannelProfile {
  id: number
  username: string
  is_channel: boolean
  channel_status: string
  referrer_id: number | null
  bank: ChannelBank | null
  commission_summary: {
    total_frozen: string
    total_available: string
    total_withdrawn: string
  }
}

export interface ChannelBank {
  id: number
  channel_id: number
  bank_name: string
  bank_account: string
  account_holder: string
  created_at: string
}

export interface ChannelCommission {
  id: number
  order_id: number
  level: 1 | 2
  amount: string
  status: 'frozen' | 'available' | 'withdrawn'
  created_at: string
}

export interface ChannelWithdrawal {
  id: number
  channel_id: number
  amount: string
  status: string
  created_at: string
}

export interface ReferralUser {
  id: number
  username: string
  created_at: string
}

export interface InviteCode {
  invite_code: string
  is_custom: boolean
}

// 获取渠道商资料
export const getChannelProfile = (): Promise<ChannelProfile> =>
  api.get('/channel/profile') as any

// 申请成为渠道商
export const applyChannel = () =>
  api.post<{ status: string; message: string }>('/channel/apply')

// 获取我的邀请码
export const getMyInviteCode = (): Promise<InviteCode> =>
  api.get('/channel/invite-code') as any

// 自定义邀请码
export const setCustomInviteCode = (code: string): Promise<{ invite_code: string; is_custom: boolean }> =>
  api.put('/channel/invite-code', null, {
    params: { code }
  }) as any

// 获取银行卡
export const getMyBank = (): Promise<ChannelBank | null> =>
  api.get('/channel/bank') as any

// 保存银行卡
export const saveMyBank = (data: {
  bank_name: string
  bank_account: string
  account_holder: string
}) =>
  api.post<ChannelBank>('/channel/bank', data)

// 获取佣金明细（分页）
export const getMyCommissions = (
  status?: string,
  skip = 0,
  limit = 50
): Promise<{ data: ChannelCommission[]; total: number; skip: number; limit: number }> =>
  api.get('/channel/commissions', { params: { status, skip, limit } }) as any

// 获取佣金汇总
export const getCommissionSummary = (): Promise<ChannelProfile['commission_summary']> =>
  api.get('/channel/commissions/summary') as any

// 申请提现
export const applyWithdrawal = (amount: string) =>
  api.post<ChannelWithdrawal>('/channel/withdraw', { amount })

// 获取我的下级
export const getMyReferrals = (): Promise<{ l1_referrals: ReferralUser[]; l2_referrals: ReferralUser[] }> =>
  api.get('/channel/referrals') as any

export default api
