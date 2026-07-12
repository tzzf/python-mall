<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <h1>购物车</h1>
        <a-spin :spinning="loading">
          <a-table
            :dataSource="cartStore.items"
            :columns="columns"
            row-key="product_id"
            :pagination="false"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'image'">
                <img class="product-thumb" src="https://via.placeholder.com/60x60?text=P" />
              </template>
              <template v-else-if="column.key === 'name'">
                {{ record.product_name || `商品 #${record.product_id}` }}
              </template>
              <template v-else-if="column.key === 'price'">
                ¥{{ record.price || '0.00' }}
              </template>
              <template v-else-if="column.key === 'quantity'">
                <a-input-number
                  :value="record.quantity"
                  :min="1"
                  @change="(val: number) => handleUpdateQuantity(record.product_id, val)"
                />
              </template>
              <template v-else-if="column.key === 'subtotal'">
                ¥{{ ((parseFloat(record.price || '0') * record.quantity)).toFixed(2) }}
              </template>
              <template v-else-if="column.key === 'action'">
                <a-button type="link" danger @click="handleRemove(record.product_id)">
                  删除
                </a-button>
              </template>
            </template>
          </a-table>
          <div class="cart-footer" v-if="cartStore.items.length > 0">
            <div class="total">
              总计: <span class="total-price">¥{{ cartStore.totalPrice }}</span>
            </div>
            <a-button type="primary" size="large" @click="handleCheckout">
              去结算
            </a-button>
          </div>
          <div v-else class="empty-state">
            <div class="icon">🛒</div>
            <p>购物车是空的</p>
            <a-button type="primary" @click="$router.push('/')">去购物</a-button>
          </div>
        </a-spin>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()
const loading = ref(false)

const columns = [
  { title: '商品', key: 'image', width: 100 },
  { title: '商品名称', key: 'name' },
  { title: '单价', key: 'price', width: 120 },
  { title: '数量', key: 'quantity', width: 150 },
  { title: '小计', key: 'subtotal', width: 120 },
  { title: '操作', key: 'action', width: 100 }
]

const handleUpdateQuantity = async (productId: number, quantity: number) => {
  try {
    await cartStore.updateItem(productId, quantity)
  } catch (error: any) {
    message.error(error.message || '更新失败')
  }
}

const handleRemove = async (productId: number) => {
  try {
    await cartStore.removeItem(productId)
    message.success('删除成功')
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

const handleCheckout = () => {
  router.push('/checkout')
}

onMounted(() => {
  loading.value = true
  cartStore.fetchCart().finally(() => {
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

.product-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.cart-footer {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 24px;
}

.total {
  font-size: 18px;
}

.total-price {
  font-size: 24px;
  color: #ff4d4f;
  font-weight: bold;
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
