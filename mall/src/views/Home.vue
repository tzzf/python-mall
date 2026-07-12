<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="home-page">
        <!-- Hero Banner -->
        <div class="hero-banner">
          <div class="hero-content">
            <h1 class="hero-title">发现品质好物</h1>
            <p class="hero-subtitle">精选商品，优质服务，让购物更轻松</p>
          </div>
          <div class="hero-decoration"></div>
        </div>

        <!-- Main Content -->
        <div class="content-wrapper">
          <a-row :gutter="24">
            <!-- Category Sidebar -->
            <a-col :xs="24" :sm="24" :md="6">
              <div class="category-sidebar">
                <div class="sidebar-header">
                  <span class="sidebar-icon">📂</span>
                  <span>商品分类</span>
                </div>
                <a-menu
                  v-model:selectedKeys="selectedCategory"
                  mode="vertical"
                  @click="handleCategoryChange"
                >
                  <a-menu-item key="all" class="category-item">
                    <template #icon><AppstoreOutlined /></template>
                    全部分类
                  </a-menu-item>
                  <a-menu-item v-for="cat in categories" :key="cat.id" class="category-item">
                    <template #icon><CrownOutlined /></template>
                    {{ cat.name }}
                  </a-menu-item>
                </a-menu>
              </div>
            </a-col>

            <!-- Product Grid -->
            <a-col :xs="24" :sm="24" :md="18">
              <div class="products-section">
                <div class="section-header">
                  <div class="result-info">
                    <span class="result-count">共找到 <strong>{{ total }}</strong> 件商品</span>
                  </div>
                  <div class="view-toggle">
                    <a-segmented
                      v-model:value="viewMode"
                      :options="[
                        { label: '网格', value: 'grid' },
                        { label: '列表', value: 'list' }
                      ]"
                    />
                  </div>
                </div>

                <a-spin :spinning="loading">
                  <TransitionGroup
                    :name="viewMode === 'grid' ? 'grid' : 'list'"
                    tag="div"
                    :class="['product-container', viewMode]"
                  >
                    <ProductCard
                      v-for="product in products"
                      :key="product.id"
                      :product="product"
                    />
                  </TransitionGroup>

                  <div v-if="products.length === 0 && !loading" class="empty-state">
                    <div class="empty-illustration">🛍️</div>
                    <h3>暂无商品</h3>
                    <p>试试其他分类吧</p>
                  </div>
                </a-spin>

                <div class="pagination-wrapper" v-if="total > 0">
                  <a-pagination
                    v-model:current="page"
                    :total="total"
                    :page-size="pageSize"
                    @change="handlePageChange"
                    show-quick-jumper
                    show-total
                    :show-size-changer="false"
                  />
                </div>
              </div>
            </a-col>
          </a-row>
        </div>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { AppstoreOutlined, CrownOutlined } from '@ant-design/icons-vue'
import Header from '@/components/Header.vue'
import ProductCard from '@/components/ProductCard.vue'
import { getProducts } from '@/api'
import type { ProductResponse, CategoryResponse } from '@/types'

const products = ref<ProductResponse[]>([])
const categories = ref<CategoryResponse[]>([])
const loading = ref(false)
const selectedCategory = ref(['all'])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const viewMode = ref< 'grid' | 'list'>('grid')

const fetchProducts = async () => {
  loading.value = true
  try {
    const params: { skip: number; limit: number; category_id?: number } = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (selectedCategory.value[0] !== 'all') {
      params.category_id = Number(selectedCategory.value[0])
    }
    const response = await getProducts(params) as unknown as { data: ProductResponse[]; total: number }
    products.value = response?.data || []
    total.value = response?.total || 0
  } catch (error: any) {
    message.error(error.message || '获取商品失败')
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = () => {
  page.value = 1
  fetchProducts()
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  fetchProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.main-content {
  background: var(--color-bg-base);
  min-height: calc(100vh - 64px);
}

.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

/* ---- Hero Banner ---- */
.hero-banner {
  position: relative;
  margin: var(--space-6) 0;
  padding: var(--space-10) var(--space-8);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-active) 100%);
  border-radius: var(--radius-xl);
  overflow: hidden;
  color: white;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
  color: white;
}

.hero-subtitle {
  font-size: var(--text-base);
  opacity: 0.9;
}

.hero-decoration {
  position: absolute;
  right: -50px;
  top: -50px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.hero-decoration::after {
  content: '';
  position: absolute;
  right: 30px;
  bottom: -80px;
  width: 160px;
  height: 160px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
}

/* ---- Content Wrapper ---- */
.content-wrapper {
  background: var(--color-bg-white);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-8);
}

/* ---- Category Sidebar ---- */
.category-sidebar {
  background: var(--color-bg-gray);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  height: fit-content;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.sidebar-icon {
  font-size: 18px;
}

.category-item {
  border-radius: var(--radius-md) !important;
  margin-bottom: var(--space-1) !important;
}

/* ---- Products Section ---- */
.products-section {
  min-height: 400px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
}

.result-info {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.result-count strong {
  color: var(--color-primary);
  font-weight: 600;
}

/* ---- Product Container ---- */
.product-container {
  min-height: 200px;
}

.product-container.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-5);
}

.product-container.list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.product-container.list > * {
  width: 100%;
}

/* ---- Empty State ---- */
.empty-state {
  text-align: center;
  padding: var(--space-16) var(--space-4);
}

.empty-illustration {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.empty-state h3 {
  font-size: var(--text-lg);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-state p {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

/* ---- Pagination ---- */
.pagination-wrapper {
  margin-top: var(--space-8);
  display: flex;
  justify-content: center;
}

/* ---- Transitions ---- */
.grid-move,
.grid-enter-active,
.grid-leave-active {
  transition: all var(--transition-base);
}

.grid-enter-from,
.grid-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.grid-leave-active {
  position: absolute;
}

.list-enter-active,
.list-leave-active {
  transition: all var(--transition-base);
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
