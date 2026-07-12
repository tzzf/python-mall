<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <a-spin :spinning="loading">
          <a-row :gutter="40" v-if="product">
            <a-col :span="10">
              <div class="product-image">
                <img src="https://via.placeholder.com/400x300?text=Product" :alt="product.name" />
              </div>
            </a-col>
            <a-col :span="14">
              <div class="product-info">
                <h1>{{ product.name }}</h1>
                <div class="price">¥{{ product.price }}</div>
                <div class="stock">库存: {{ product.stock }}</div>
                <div class="description" v-if="product.description">
                  {{ product.description }}
                </div>
                <div class="actions">
                  <a-input-number
                    v-model:value="quantity"
                    :min="1"
                    :max="product.stock"
                    size="large"
                  />
                  <a-button type="primary" size="large" @click="handleAddToCart" :loading="adding">
                    加入购物车
                  </a-button>
                </div>
                <a-button @click="$router.push('/')" style="margin-top: 16px">
                  返回列表
                </a-button>
              </div>
            </a-col>
          </a-row>
        </a-spin>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { getProduct } from '@/api'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import type { ProductResponse } from '@/types'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const product = ref<ProductResponse | null>(null)
const loading = ref(false)
const adding = ref(false)
const quantity = ref(1)

const fetchProduct = async () => {
  loading.value = true
  try {
    const response = await getProduct(Number(route.params.id))
    product.value = response as unknown as ProductResponse
  } catch (error: any) {
    message.error(error.message || '获取商品详情失败')
  } finally {
    loading.value = false
  }
}

const handleAddToCart = async () => {
  if (!authStore.isAuthenticated) {
    message.warning('请先登录')
    router.push('/login')
    return
  }
  adding.value = true
  try {
    await cartStore.addItem(product.value!.id, quantity.value)
    message.success('添加成功')
  } catch (error: any) {
    message.error(error.message || '添加失败')
  } finally {
    adding.value = false
  }
}

onMounted(() => {
  fetchProduct()
})
</script>

<style scoped>
.main-content {
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
  padding: 20px 0;
}

.product-image img {
  width: 100%;
  border-radius: 8px;
}

.product-info h1 {
  font-size: 24px;
  margin-bottom: 16px;
}

.price {
  font-size: 32px;
  color: #ff4d4f;
  font-weight: bold;
  margin: 16px 0;
}

.stock {
  color: #666;
  margin-bottom: 16px;
}

.description {
  color: #333;
  line-height: 1.6;
  margin-bottom: 24px;
}

.actions {
  display: flex;
  gap: 16px;
  align-items: center;
}
</style>
