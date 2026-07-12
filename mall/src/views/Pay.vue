<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <h1>订单支付</h1>
        <a-spin :spinning="loading">
          <a-card v-if="order" class="pay-card">
            <a-result
              v-if="payStatus === 'success'"
              status="success"
              title="支付成功"
              sub-title="您的订单已支付成功"
            >
              <template #extra>
                <a-button type="primary" @click="$router.push('/orders')">
                  查看订单
                </a-button>
                <a-button @click="$router.push('/')">
                  继续购物
                </a-button>
              </template>
            </a-result>
            <a-result
              v-else-if="payStatus === 'failed'"
              status="error"
              title="支付失败"
              sub-title="支付过程中出现问题，请重试"
            >
              <template #extra>
                <a-button type="primary" @click="handlePay">
                  重新支付
                </a-button>
                <a-button @click="$router.push('/orders')">
                  查看订单
                </a-button>
              </template>
            </a-result>
            <template v-else>
              <div class="order-info">
                <h2>订单信息</h2>
                <a-descriptions :column="2">
                  <a-descriptions-item label="订单号">{{ order.id }}</a-descriptions-item>
                  <a-descriptions-item label="订单状态">
                    <OrderStatusTag :status="order.status" />
                  </a-descriptions-item>
                  <a-descriptions-item label="收货地址">{{ order.address }}</a-descriptions-item>
                  <a-descriptions-item label="订单金额">
                    <span class="amount">¥{{ order.total_amount }}</span>
                  </a-descriptions-item>
                </a-descriptions>
              </div>
              <a-divider />
              <div class="order-items">
                <h3>商品清单</h3>
                <a-list :dataSource="order.items">
                  <template #renderItem="{ item }">
                    <a-list-item>
                      <a-list-item-meta :title="item.product_name" />
                      <template #actions>
                        <span>¥{{ item.price }} x {{ item.quantity }}</span>
                      </template>
                    </a-list-item>
                  </template>
                </a-list>
              </div>
              <a-divider />
              <div class="pay-actions">
                <a-button type="primary" size="large" @click="handlePay" :loading="paying">
                  确认支付 ¥{{ order.total_amount }}
                </a-button>
              </div>
            </template>
          </a-card>
        </a-spin>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import { getOrder, payOrder, payCallback } from '@/api'
import type { OrderResponse } from '@/types'

const route = useRoute()
const order = ref<OrderResponse | null>(null)
const loading = ref(false)
const paying = ref(false)
const payStatus = ref<'success' | 'failed' | null>(null)

const fetchOrder = async () => {
  loading.value = true
  try {
    const response = await getOrder(Number(route.params.orderId))
    order.value = response as unknown as OrderResponse
  } catch (error: any) {
    message.error(error.message || '获取订单失败')
  } finally {
    loading.value = false
  }
}

const handlePay = async () => {
  if (!order.value) return
  paying.value = true
  try {
    await payOrder(order.value.id)
    await payCallback({
      order_id: order.value.id,
      pay_status: 'success',
      transaction_id: `TXN_${Date.now()}`
    })
    payStatus.value = 'success'
    message.success('支付成功')
  } catch (error: any) {
    payStatus.value = 'failed'
    message.error(error.message || '支付失败')
  } finally {
    paying.value = false
  }
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

h1 {
  margin-bottom: 24px;
}

.pay-card {
  max-width: 600px;
  margin: 0 auto;
}

.order-info h2 {
  margin-bottom: 16px;
}

.amount {
  font-size: 24px;
  color: #ff4d4f;
  font-weight: bold;
}

.order-items h3 {
  margin-bottom: 12px;
}

.pay-actions {
  text-align: center;
}
</style>
