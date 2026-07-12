<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <a-button @click="$router.push('/orders')" style="margin-bottom: 16px">
          返回订单列表
        </a-button>
        <a-spin :spinning="loading">
          <a-card v-if="order">
            <template #title>
              <div class="card-title">
                <span>订单详情</span>
                <OrderStatusTag :status="order.status" />
              </div>
            </template>
            <a-descriptions :column="2" bordered>
              <a-descriptions-item label="订单号">{{ order.id }}</a-descriptions-item>
              <a-descriptions-item label="订单状态">{{ getStatusText(order.status) }}</a-descriptions-item>
              <a-descriptions-item label="收货地址">{{ order.address }}</a-descriptions-item>
              <a-descriptions-item label="下单时间">{{ formatDate(order.created_at) }}</a-descriptions-item>
            </a-descriptions>
            <a-divider>商品清单</a-divider>
            <a-table
              :dataSource="order.items"
              :columns="itemColumns"
              row-key="id"
              :pagination="false"
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
            <div class="total-section">
              <span>订单总额:</span>
              <span class="total-amount">¥{{ order.total_amount }}</span>
            </div>
            <a-divider>订单操作</a-divider>
            <div class="actions">
              <template v-if="order.status === 'pending'">
                <a-button type="primary" @click="handlePay">去支付</a-button>
                <a-button @click="handleCancel">取消订单</a-button>
              </template>
              <template v-if="order.status === 'shipped'">
                <a-button @click="handleConfirmReceive">确认收货</a-button>
              </template>
            </div>
          </a-card>
        </a-spin>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import { getOrder, cancelOrder, confirmReceipt } from '@/api'
import { formatDate, formatOrderStatus } from '@/utils/format'
import type { OrderResponse } from '@/types'

const route = useRoute()
const router = useRouter()

const order = ref<OrderResponse | null>(null)
const loading = ref(false)

const itemColumns = [
  { title: '商品名称', dataIndex: 'product_name', key: 'product_name' },
  { title: '单价', dataIndex: 'price', key: 'price' },
  { title: '数量', dataIndex: 'quantity', key: 'quantity' },
  { title: '小计', key: 'subtotal' }
]

const getStatusText = (status: string) => {
  return formatOrderStatus(status)
}

const fetchOrder = async () => {
  loading.value = true
  try {
    const response = await getOrder(Number(route.params.id))
    order.value = response as unknown as OrderResponse
  } catch (error: any) {
    message.error(error.message || '获取订单详情失败')
  } finally {
    loading.value = false
  }
}

const handlePay = () => {
  if (order.value) {
    router.push(`/pay/${order.value.id}`)
  }
}

const handleCancel = () => {
  Modal.confirm({
    title: '确认取消订单?',
    async onOk() {
      try {
        await cancelOrder(order.value!.id)
        message.success('订单已取消，库存已退回')
        router.push('/orders')
      } catch (error: any) {
        message.error(error.message || '取消订单失败')
      }
    }
  })
}

const handleConfirmReceive = () => {
  Modal.confirm({
    title: '确认已收到货?',
    async onOk() {
      try {
        await confirmReceipt(order.value!.id)
        message.success('确认收货成功')
        fetchOrder()
      } catch (error: any) {
        message.error(error.message || '确认收货失败')
      }
    }
  })
}

onMounted(() => {
  fetchOrder()
})
</script>

<style scoped>
.main-content {
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
  padding: 20px 0;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-section {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
  font-size: 18px;
}

.total-amount {
  font-size: 24px;
  color: #ff4d4f;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 12px;
}
</style>
