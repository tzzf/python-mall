<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <h1>确认订单</h1>
        <a-spin :spinning="loading">
          <a-row :gutter="24">
            <a-col :span="16">
              <a-card title="收货地址" class="section-card">
                <a-form-item label="收货地址">
                  <a-input v-model:value="address" placeholder="请输入收货地址" />
                </a-form-item>
              </a-card>
              <a-card title="商品清单" class="section-card" style="margin-top: 16px">
                <a-table
                  :dataSource="cartStore.items"
                  :columns="itemColumns"
                  row-key="product_id"
                  :pagination="false"
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.key === 'name'">
                      {{ record.product_name || `商品 #${record.product_id}` }}
                    </template>
                    <template v-else-if="column.key === 'price'">
                      ¥{{ record.price || '0.00' }}
                    </template>
                    <template v-else-if="column.key === 'subtotal'">
                      ¥{{ (parseFloat(record.price || '0') * record.quantity).toFixed(2) }}
                    </template>
                  </template>
                </a-table>
              </a-card>
              <a-card title="优惠券" class="section-card" style="margin-top: 16px">
                <a-tabs v-model:activeKey="couponTab">
                  <a-tab-pane key="available" tab="可用优惠券">
                    <a-list :data-source="availableCoupons" :loading="couponLoading">
                      <template #renderItem="{ item }">
                        <a-list-item>
                          <a-list-item-meta
                            :title="item.name"
                            :description="`满${item.min_order_amount}减${item.discount_value}`"
                          />
                          <template #actions>
                            <a-button
                              v-if="!myCouponIds.includes(item.id)"
                              size="small"
                              @click="handleReceiveCoupon(item.id)"
                            >
                              领取
                            </a-button>
                            <a-tag v-else color="green">已领取</a-tag>
                          </template>
                        </a-list-item>
                      </template>
                    </a-list>
                  </a-tab-pane>
                  <a-tab-pane key="my" tab="我的优惠券">
                    <a-list :data-source="myCoupons" :loading="couponLoading">
                      <template #renderItem="{ item }">
                        <a-list-item>
                          <a-list-item-meta
                            :title="item.name"
                            :description="`${formatCouponStatus(item.status)} | ${item.code}`"
                          />
                          <template #actions>
                            <a-button
                              v-if="item.status === 'unused'"
                              type="primary"
                              size="small"
                              @click="handleSelectCoupon(item)"
                            >
                              使用
                            </a-button>
                          </template>
                        </a-list-item>
                      </template>
                    </a-list>
                  </a-tab-pane>
                </a-tabs>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card title="订单摘要" class="order-summary">
                <div class="summary-item">
                  <span>商品总额:</span>
                  <span>¥{{ cartStore.totalPrice }}</span>
                </div>
                <div class="summary-item" v-if="selectedCoupon">
                  <span>优惠券:</span>
                  <span>-¥{{ discountAmount }}</span>
                </div>
                <a-divider />
                <div class="summary-item total">
                  <span>应付金额:</span>
                  <span class="final-amount">¥{{ finalAmount }}</span>
                </div>
                <a-button type="primary" block size="large" @click="handleSubmitOrder" :loading="submitting">
                  提交订单
                </a-button>
              </a-card>
            </a-col>
          </a-row>
        </a-spin>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { useCartStore } from '@/stores/cart'
import { getCoupons, receiveCoupon, getMyCoupons, calculateDiscount, createOrder } from '@/api'
import { formatCouponStatus } from '@/utils/format'
import type { CouponInfo, UserCouponDetail } from '@/types'

const router = useRouter()
const cartStore = useCartStore()

const loading = ref(false)
const submitting = ref(false)
const couponLoading = ref(false)
const address = ref('')
const couponTab = ref('available')
const availableCoupons = ref<CouponInfo[]>([])
const myCoupons = ref<UserCouponDetail[]>([])
const selectedCoupon = ref<UserCouponDetail | null>(null)
const discountAmount = ref('0.00')

const myCouponIds = computed(() => myCoupons.value.map(c => c.coupon_id))

const finalAmount = computed(() => {
  const original = parseFloat(cartStore.totalPrice)
  const discount = parseFloat(discountAmount.value)
  return (original - discount).toFixed(2)
})

const itemColumns = [
  { title: '商品名称', dataIndex: 'product_name', key: 'name' },
  { title: '单价', dataIndex: 'price', key: 'price' },
  { title: '数量', dataIndex: 'quantity', key: 'quantity' },
  { title: '小计', key: 'subtotal' }
]

const fetchCoupons = async () => {
  couponLoading.value = true
  try {
    const [available, my] = await Promise.all([
      getCoupons() as unknown as Promise<CouponInfo[]>,
      getMyCoupons() as unknown as Promise<UserCouponDetail[]>
    ])
    availableCoupons.value = available
    myCoupons.value = my
  } catch (error: any) {
    message.error(error.message || '获取优惠券失败')
  } finally {
    couponLoading.value = false
  }
}

const handleReceiveCoupon = async (couponId: number) => {
  try {
    await receiveCoupon(couponId)
    message.success('领取成功')
    await fetchCoupons()
  } catch (error: any) {
    message.error(error.message || '领取失败')
  }
}

const handleSelectCoupon = async (coupon: UserCouponDetail) => {
  selectedCoupon.value = coupon
  try {
    const response = await calculateDiscount(coupon.id, parseFloat(cartStore.totalPrice)) as unknown as { discount_amount: string }
    discountAmount.value = response.discount_amount || '0.00'
    message.success('已选择优惠券')
  } catch (error: any) {
    message.error(error.message || '优惠券计算失败')
  }
}

const handleSubmitOrder = async () => {
  if (!address.value.trim()) {
    message.warning('请输入收货地址')
    return
  }
  if (cartStore.items.length === 0) {
    message.warning('购物车为空')
    return
  }
  submitting.value = true
  try {
    const orderData = {
      address: address.value,
      items: cartStore.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity
      })),
      coupon_code: selectedCoupon.value?.code
    }
    const order = await createOrder(orderData) as unknown as { id: number }
    await cartStore.clearCart()
    message.success('订单创建成功')
    router.push(`/pay/${order.id}`)
  } catch (error: any) {
    message.error(error.message || '订单创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loading.value = true
  Promise.all([
    cartStore.fetchCart(),
    fetchCoupons()
  ]).finally(() => {
    loading.value = false
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

.section-card {
  margin-bottom: 0;
}

.order-summary {
  position: sticky;
  top: 84px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.summary-item.total {
  font-size: 18px;
  font-weight: bold;
}

.final-amount {
  color: #ff4d4f;
  font-size: 24px;
}
</style>
