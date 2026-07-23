<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-select
        v-model:value="statusFilter"
        placeholder="筛选订单状态"
        style="width: 200px"
        allow-clear
        @change="handleStatusChange"
      >
        <a-select-option value="">全部</a-select-option>
        <a-select-option value="pending">待支付</a-select-option>
        <a-select-option value="paid">已支付</a-select-option>
        <a-select-option value="shipped">已发货</a-select-option>
        <a-select-option value="delivered">已送达</a-select-option>
        <a-select-option value="completed">已完成</a-select-option>
        <a-select-option value="cancelled">已取消</a-select-option>
        <a-select-option value="refunding">退款中</a-select-option>
        <a-select-option value="refunded">已退款</a-select-option>
      </a-select>
    </div>

    <ErrorBoundary @retry="loadOrders">
      <!-- Loading state: show skeleton -->
      <TableSkeleton v-if="isLoading" :columns="columns" :rows="10" />

      <!-- Empty state -->
      <EmptyState
        v-else-if="isEmpty"
        entity-name="订单"
        action-text="刷新"
        @action="loadOrders"
      />

      <!-- Data table -->
      <a-table
        v-else
        :columns="columns"
        :data-source="orders"
        row-key="id"
        :pagination="{ pageSize, total, current }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ isItemPending(record.id) ? '更新中...' : getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-button type="link" size="small" @click="handleViewDetail(record)">查看详情</a-button>
          </template>
        </template>
      </a-table>
    </ErrorBoundary>

    <a-drawer
      v-model:open="detailVisible"
      title="订单详情"
      width="600"
    >
      <a-descriptions :column="2" bordered v-if="currentOrder">
        <a-descriptions-item label="订单ID">{{ currentOrder.id }}</a-descriptions-item>
        <a-descriptions-item label="用户ID">{{ currentOrder.user_id }}</a-descriptions-item>
        <a-descriptions-item label="总金额">¥{{ currentOrder.total_amount }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-select
            v-model:value="currentOrder.status"
            style="width: 120px"
            @change="handleStatusUpdate"
          >
            <a-select-option value="pending">待支付</a-select-option>
            <a-select-option value="paid">已支付</a-select-option>
            <a-select-option value="shipped">已发货</a-select-option>
            <a-select-option value="delivered">已送达</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="cancelled">已取消</a-select-option>
            <a-select-option value="refunding">退款中</a-select-option>
            <a-select-option value="refunded">已退款</a-select-option>
          </a-select>
        </a-descriptions-item>
        <a-descriptions-item label="地址" :span="2">{{ currentOrder.address }}</a-descriptions-item>
        <a-descriptions-item label="创建时间">{{ currentOrder.created_at }}</a-descriptions-item>
      </a-descriptions>

      <a-divider>订单商品</a-divider>
      <a-table
        :columns="itemColumns"
        :data-source="currentOrder?.items || []"
        :pagination="false"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'price'">
            ¥{{ record.price }}
          </template>
          <template v-else-if="column.key === 'subtotal'">
            ¥{{ (parseFloat(record.price) * record.quantity).toFixed(2) }}
          </template>
        </template>
      </a-table>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import type { OrderResponse } from '../../types'
import { getOrders, updateOrderStatus } from '../../api'
import { useAsyncState } from '../../composables/useAsyncState'
import { useOptimistic } from '../../composables/useOptimistic'
import ErrorBoundary from '../../components/ui/ErrorBoundary.vue'
import TableSkeleton from '../../components/ui/TableSkeleton.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '用户ID', dataIndex: 'user_id', key: 'user_id', width: 100 },
  { title: '总金额', dataIndex: 'total_amount', key: 'total_amount', width: 120 },
  { title: '状态', key: 'status', width: 100 },
  { title: '地址', dataIndex: 'address', key: 'address', ellipsis: true },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 100 }
]

const itemColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '商品名称', dataIndex: 'product_name', key: 'product_name' },
  { title: '单价', key: 'price', width: 100 },
  { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80 },
  { title: '小计', key: 'subtotal', width: 100 }
]

const orders = ref<OrderResponse[]>([])
const statusFilter = ref<string>('')
const detailVisible = ref(false)
const currentOrder = ref<OrderResponse | null>(null)
const total = ref(0)
const current = ref(1)
const pageSize = ref(10)

const { isLoading, isEmpty, execute } = useAsyncState<OrderResponse[]>()
const { optimisticUpdate, isItemPending } = useOptimistic<OrderResponse>()

const statusMap: Record<string, string> = {
  pending: '待支付',
  paid: '已支付',
  completed: '已完成',
  shipped: '已发货',
  delivered: '已送达',
  cancelled: '已取消',
  refunding: '退款中',
  refunded: '已退款'
}

const statusColorMap: Record<string, string> = {
  pending: 'orange',
  paid: 'green',
  shipped: 'blue',
  delivered: 'cyan',
  cancelled: 'red',
  refunding: 'purple',
  refunded: 'gray'
}

const getStatusText = (status: string) => statusMap[status] || status
const getStatusColor = (status: string) => statusColorMap[status] || 'default'

const loadOrders = async () => {
  try {
    const result = await execute(async () => {
      const data = await getOrders(
        statusFilter.value || undefined,
        (current.value - 1) * pageSize.value,
        pageSize.value
      )
      total.value = (data as any).total || 0
      return data?.data as unknown as OrderResponse[]
    })

    if (result) {
      orders.value = result
    }
  } catch (error: any) {
    message.error(error.message || '加载订单失败')
  }
}

const handleStatusChange = () => {
  current.value = 1
  loadOrders()
}

const handleViewDetail = (order: OrderResponse) => {
  currentOrder.value = { ...order }
  detailVisible.value = true
}

const handleTableChange = (e: any) => {
  current.value = e.current
  loadOrders()
}

const handleStatusUpdate = async (newStatus: string) => {
  if (!currentOrder.value) return

  try {
    await optimisticUpdate(
      currentOrder.value.id,
      (order) => ({ ...order, status: newStatus }),
      async () => {
        await updateOrderStatus(currentOrder.value!.id, newStatus)
      }
    )
    message.success('状态更新成功')
    loadOrders()
  } catch (error: any) {
    message.error(error.message || '状态更新失败，已恢复原状态')
  }
}

loadOrders()
</script>
