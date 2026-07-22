<template>
  <a-card hoverable class="product-card" @click="$router.push(`/product/${product.id}`)">
    <template #cover>
      <div class="product-image-wrapper">
        <img
          :src="getImageUrl(product.image)"
          :alt="product.name"
          class="product-image"
          loading="lazy"
          @error="handleImageError"
        />
        <div class="product-badge" v-if="product.stock < 10">仅剩 {{ product.stock }} 件</div>
      </div>
    </template>

    <div class="product-content">
      <h3 class="product-name">{{ product.name }}</h3>
      <p class="product-description" v-if="product.description">
        {{ product.description }}
      </p>

      <div class="product-meta">
        <div class="price-section">
          <span class="price">{{ formatPrice(product.price) }}</span>
          <span class="original-price" v-if="product.original_price">
            {{ formatPrice(product.original_price) }}
          </span>
        </div>
        <div class="stock-info">
          <span :class="['stock-dot', { low: product.stock < 10 }]"></span>
          {{ product.stock > 0 ? '有货' : '缺货' }}
        </div>
      </div>
    </div>

    <template #actions>
      <a-button
        type="primary"
        class="add-cart-btn"
        @click.stop="handleAddToCart"
        :disabled="product.stock === 0"
      >
        <ShoppingCartOutlined />
        加入购物车
      </a-button>
    </template>
  </a-card>
</template>

<script setup lang="ts">
import { ShoppingCartOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { formatPrice } from '@/utils/format'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import type { ProductResponse } from '@/types'

const props = defineProps<{
  product: ProductResponse
}>()

const cartStore = useCartStore()
const authStore = useAuthStore()
const router = useRouter()

const handleAddToCart = async () => {
  if (!authStore.isAuthenticated) {
    message.warning('请先登录')
    router.push('/login')
    return
  }
  try {
    await cartStore.addItem(props.product.id, 1, props.product.image)
    message.success('已加入购物车')
  } catch (error: any) {
    message.error(error.message || '添加失败')
  }
}

const getImageUrl = (image: string | undefined) => {
  if (!image) return 'https://via.placeholder.com/300x200?text=Product'
  if (image.startsWith('http')) return image
  return `/static/${image}`
}

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src = 'https://via.placeholder.com/300x200?text=Product'
}
</script>

<style scoped>
.product-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.product-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-card-hover);
}

.product-image-wrapper {
  position: relative;
  height: 200px;
  overflow: hidden;
  background: var(--color-bg-gray);
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.product-badge {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  padding: var(--space-1) var(--space-2);
  background: var(--color-accent);
  color: white;
  font-size: var(--text-xs);
  font-weight: 600;
  border-radius: var(--radius-sm);
}

.product-content {
  padding: var(--space-4);
}

.product-name {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-description {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-light);
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
}

.price {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-accent);
}

.original-price {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-decoration: line-through;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.stock-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-success);
}

.stock-dot.low {
  background: var(--color-warning);
}

/* ---- Action Button ---- */
.add-cart-btn {
  width: 100%;
  height: 40px;
  border-radius: var(--radius-md);
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}
</style>
