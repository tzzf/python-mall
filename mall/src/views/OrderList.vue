<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <h1>我的订单</h1>
        <a-tabs v-model:activeKey="statusFilter" @change="handleStatusChange">
          <a-tab-pane key="all" tab="全部" />
          <a-tab-pane key="pending" tab="待支付" />
          <a-tab-pane key="paid" tab="已支付" />
          <a-tab-pane key="shipped" tab="已发货" />
          <a-tab-pane key="delivered" tab="已完成" />
          <a-tab-pane key="cancelled" tab="已取消" />
        </a-tabs>
        <a-spin :spinning="loading">
          <a-table
            :dataSource="orders"
            :columns="columns"
            row-key="id"
            :pagination="{ pageSize, total, current }"
            @change="handleTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'id'">
                #{{ record.id }}
              </template>
              <template v-else-if="column.key === 'items'">
                <div class="order-items">
                  <div v-for="item in record.items.slice(0, 2)" :key="item.id" class="order-item">
                    {{ item.product_name }} x {{ item.quantity }}
                  </div>
                  <div v-if="record.items.length > 2" class="more-items">
                    还有{{ record.items.length - 2 }}件商品
                  </div>
                </div>
              </template>
              <template v-else-if="column.key === 'total_amount'">
                ¥{{ record.total_amount }}
              </template>
              <template v-else-if="column.key === 'status'">
                <OrderStatusTag :status="record.status" />
              </template>
              <template v-else-if="column.key === 'created_at'">
                {{ formatDate(record.created_at) }}
              </template>
              <template v-else-if="column.key === 'action'">
                <a-button type="link" @click="$router.push(`/order/${record.id}`)">
                  查看详情
                </a-button>
              </template>
            </template>
          </a-table>
          <div v-if="orders.length === 0 && !loading" class="empty-state">
            <div class="icon">📦</div>
            <p>暂无订单</p>
            <a-button type="primary" @click="$router.push('/')">去购物</a-button>
          </div>
        </a-spin>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import { getOrders } from '@/api'
import { formatDate } from '@/utils/format'
import type { OrderResponse } from '@/types'

const orders = ref<OrderResponse[]>([])
const loading = ref(false)
const total = ref(0)
const pageSize = ref(10)
const current = ref(1)
const statusFilter = ref('all')

const columns = [
  { title: '订单号', key: 'id', width: 100 },
  { title: '商品', key: 'items' },
  { title: '总金额', key: 'total_amount', width: 120 },
  { title: '状态', key: 'status', width: 100 },
  { title: '时间', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 100 }
]

const fetchOrders = async ({
  skip,
  limit,
  status,
}: {
  skip: number
  limit: number
  status?: string
}) => {
  loading.value = true
  try {
    const response = await getOrders({
      skip,limit, status: status == 'all' ? '' : status
    }) as unknown as { data: OrderResponse[]; total: number }
    orders.value = response?.data || []
    total.value = response?.total || 0
  } catch (error: any) {
    message.error(error.message || '获取订单失败')
  } finally {
    loading.value = false
  }
}

const handleStatusChange = (e: any) => {
  current.value = 1
  fetchOrders({
    skip: (current.value - 1) * pageSize.value,
    limit: pageSize.value,
    status: e
  });
}

const handleTableChange = (e: any) => {
  current.value = e.current;
  fetchOrders({
    skip: (e.current - 1) * e.pageSize,
    limit: e.pageSize
  });
}

onMounted(() => {
  fetchOrders({
    skip: 0,
    limit: 10,
  })
})
</script>

<style scoped>
.main-content {
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
  padding: 20px 0;
}

h1 {
  margin-bottom: 24px;
}

.order-items {
  font-size: 13px;
}

.order-item {
  margin-bottom: 4px;
}

.more-items {
  color: #999;
  font-size: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state .icon {
  font-size: 48px;
  margin-bottom: 16px;
}
</style>
