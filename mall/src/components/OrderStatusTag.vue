<template>
  <a-tag :color="colorMap[status] || 'default'">
    {{ labelMap[status] || status }}
  </a-tag>
</template>

<script setup lang="ts">
defineProps<{
  status: string
}>()

const labelMap: Record<string, string> = {
  pending: '待支付',
  paid: '已支付',
  shipped: '已发货',
  delivered: '已完成',
  cancelled: '已取消',
  refunding: '退款中',
  refunded: '已退款'
}

const colorMap: Record<string, string> = {
  pending: 'orange',
  paid: 'blue',
  shipped: 'cyan',
  delivered: 'green',
  cancelled: 'default',
  refunding: 'orange',
  refunded: 'default'
}
</script>
