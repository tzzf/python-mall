import api from './index'

export interface ChannelApplicationItem {
  id: number
  user_id: number
  username: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  reviewed_at: string | null
  reject_reason: string | null
}

export interface ChannelListItem {
  id: number
  username: string
  is_channel: boolean
  channel_status: string
  referrer_id: number | null
  created_at: string
}

export interface ChannelSettingResponse {
  l1_rate: string
  l2_rate: string
  updated_at: string
}

export interface WithdrawalListItem {
  id: number
  channel_id: number
  username: string
  amount: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  reviewed_at: string | null
  reject_reason: string | null
}

export interface ChannelOrderDetail {
  order_id: number
  actual_amount: string
  l1_amount: string | null
  l2_amount: string | null
  order_created_at: string
}

// 申请列表
export const getChannelApplications = (
  status?: string,
  skip = 0,
  limit = 20
): Promise<{ data: ChannelApplicationItem[]; total: number; skip: number; limit: number }> =>
  api.get('/channel/applications', { params: { status, skip, limit } }) as any

// 审核申请
export const reviewChannelApplication = (
  appId: number,
  action: 'approved' | 'rejected',
  rejectReason?: string
) =>
  api.put<{ message: string }>(`/channel/applications/${appId}/review`, {
    action,
    reject_reason: rejectReason || null
  })

// 渠道商列表
export const getChannelList = (
  status?: string,
  skip = 0,
  limit = 20
): Promise<{ data: ChannelListItem[]; total: number; skip: number; limit: number }> =>
  api.get('/channel/list', { params: { status, skip, limit } }) as any

// 佣金设置 - 获取
export const getChannelSetting = (): Promise<ChannelSettingResponse> =>
api.get('/channel/setting')

// 佣金设置 - 更新
export const updateChannelSetting = (l1Rate: string, l2Rate: string) =>
  api.put<ChannelSettingResponse>('/channel/setting', {
    l1_rate: l1Rate,
    l2_rate: l2Rate
  })

// 提现列表
export const getChannelWithdrawals = (
  status?: string,
  skip = 0,
  limit = 20
): Promise<{ data: WithdrawalListItem[]; total: number; skip: number; limit: number }> =>
  api.get('/channel/withdrawals', { params: { status, skip, limit } }) as any

// 审核提现
export const reviewChannelWithdrawal = (
  withdrawalId: number,
  action: 'approved' | 'rejected',
  rejectReason?: string
) =>
  api.put<{ message: string }>(`/channel/withdrawals/${withdrawalId}/review`, {
    action,
    reject_reason: rejectReason || null
  })

// 渠道商订单明细
export const getChannelOrders = (
  channelId: number,
  skip = 0,
  limit = 50
): Promise<{ data: ChannelOrderDetail[]; total: number; skip: number; limit: number }> =>
  api.get(`/channel/orders/${channelId}`, { params: { skip, limit } }) as any
