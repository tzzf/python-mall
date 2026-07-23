export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const formatPrice = (price: string | number): string => {
  const num = typeof price === 'string' ? parseFloat(price) : price
  return `¥${num.toFixed(2)}`
}

export const formatOrderStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待支付',
    paid: '已支付',
    completed: '已完成',
    shipped: '已发货',
    delivered: '已完成',
    cancelled: '已取消',
    refunding: '退款中',
    refunded: '已退款'
  }
  return statusMap[status] || status
}

export const formatCouponStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    unused: '未使用',
    used: '已使用',
    expired: '已过期',
    reserved: '已使用',
  }
  return statusMap[status] || status
}

export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    pending: 'orange',
    paid: 'blue',
    shipped: 'cyan',
    delivered: 'green',
    cancelled: 'default',
    refunding: 'orange',
    refunded: 'default'
  }
  return colorMap[status] || 'default'
}
