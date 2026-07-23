<template>
  <div>
    <ErrorBoundary @retry="loadChannels">
      <TableSkeleton v-if="loading" :columns="columns" :rows="10" />
      <EmptyState v-else-if="!loading && channels.length === 0" entity-name="渠道商" @action="loadChannels" />
      <a-table
        v-else
        :columns="columns"
        :data-source="channels"
        :pagination="{ pageSize: 20, current: currentPage, total }"
        row-key="id"
        @change="onTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'channel_status'">
            <a-tag :color="statusColor(record.channel_status)">
              {{ statusText(record.channel_status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-button type="link" size="small" @click="handleViewOrders(record)">
              推广订单
            </a-button>
          </template>
        </template>
      </a-table>
    </ErrorBoundary>

    <a-modal
      v-model:open="ordersModalVisible"
      title="推广订单"
      :width="700"
      :footer="null"
    >
      <a-table
        :columns="orderColumns"
        :data-source="channelOrders"
        :pagination="{ pageSize: 50, current: ordersPage, total: ordersTotal }"
        row-key="order_id"
        :loading="ordersLoading"
        @change="onOrdersChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actual_amount'">
            ¥{{ record.actual_amount }}
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import type { TableProps } from 'ant-design-vue'
import {
  getChannelList,
  getChannelOrders,
  type ChannelListItem,
  type ChannelOrderDetail
} from '../../api/channel'
import ErrorBoundary from '../../components/ui/ErrorBoundary.vue'
import TableSkeleton from '../../components/ui/TableSkeleton.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const columns = [
  { title: '用户ID', dataIndex: 'id', key: 'id', width: 100 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '状态', key: 'channel_status', width: 120 },
  { title: '上级ID', dataIndex: 'referrer_id', key: 'referrer_id', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 100 }
]

const orderColumns = [
  { title: '订单ID', dataIndex: 'order_id', key: 'order_id', width: 100 },
  { title: '订单金额', key: 'actual_amount', width: 120 },
  { title: '下单时间', dataIndex: 'order_created_at', key: 'order_created_at', width: 180 }
]

const PAGE_SIZE = 20

const channels = ref<ChannelListItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const channelOrders = ref<ChannelOrderDetail[]>([])
const ordersModalVisible = ref(false)
const ordersLoading = ref(false)
const ordersTotal = ref(0)
const ordersPage = ref(1)
const currentChannelId = ref<number | null>(null)

const statusColor = (status: string) => {
  if (status === 'approved') return 'green'
  if (status === 'rejected') return 'red'
  return 'orange'
}

const statusText = (status: string) => {
  if (status === 'approved') return '已通过'
  if (status === 'rejected') return '已拒绝'
  return '待审核'
}

const loadChannels = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * PAGE_SIZE
    const res = await getChannelList(undefined, skip, PAGE_SIZE)
    channels.value = res.data
    total.value = res.total
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const onTableChange: TableProps['onChange'] = (pagination) => {
  currentPage.value = pagination.current || 1
  loadChannels()
}

const loadOrders = async () => {
  if (!currentChannelId.value) return
  ordersLoading.value = true
  try {
    const skip = (ordersPage.value - 1) * 50
    const res = await getChannelOrders(currentChannelId.value, skip, 50)
    channelOrders.value = res.data
    ordersTotal.value = res.total
  } catch (error: any) {
    message.error(error.message || '加载订单失败')
  } finally {
    ordersLoading.value = false
  }
}

const handleViewOrders = async (record: ChannelListItem) => {
  currentChannelId.value = record.id
  ordersPage.value = 1
  ordersModalVisible.value = true
  loadOrders()
}

const onOrdersChange: TableProps['onChange'] = (pagination) => {
  ordersPage.value = pagination.current || 1
  loadOrders()
}

loadChannels()
</script>
