<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-button type="primary" @click="handleCreate">创建商品</a-button>
    </div>

    <ErrorBoundary @retry="loadProducts">
      <!-- Loading state: show skeleton -->
      <TableSkeleton v-if="isLoading" :columns="columns" :rows="10" />

      <!-- Empty state -->
      <EmptyState
        v-else-if="isEmpty"
        entity-name="商品"
        action-text="创建商品"
        @action="handleCreate"
      />

      <!-- Data table -->
      <a-table
        v-else
        :columns="columns"
        :data-source="products"
        row-key="id"
        :pagination="{ pageSize: pageSize, total, current }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'green' : 'red'">
              {{ record.is_active ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
              <a-button type="link" size="small" @click="handleRegenerateImage(record.id)">重新生成图片</a-button>
              <a-popconfirm
                title="确定删除该商品吗?"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.id)"
              >
                <a-button
                  type="link"
                  size="small"
                  danger
                  :loading="isItemPending(record.id)"
                >
                  {{ isItemPending(record.id) ? '删除中...' : '删除' }}
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </ErrorBoundary>

    <ProductForm
      v-model:visible="formVisible"
      :product="currentProduct"
      @success="loadProducts"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import type { ProductResponse } from '../../types'
import { getProducts, deleteProduct, regenerateProductImage } from '../../api'
import { useAsyncState } from '../../composables/useAsyncState'
import { useOptimistic } from '../../composables/useOptimistic'
import ErrorBoundary from '../../components/ui/ErrorBoundary.vue'
import TableSkeleton from '../../components/ui/TableSkeleton.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import ProductForm from './ProductForm.vue'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '价格', dataIndex: 'price', key: 'price' },
  { title: '库存', dataIndex: 'stock', key: 'stock', width: 100 },
  { title: '状态', key: 'is_active', width: 100 },
  { title: '操作', key: 'action', width: 150 }
]

const products = ref<ProductResponse[]>([])
const total = ref(0)
const current = ref(1)
const pageSize = ref(10)
const formVisible = ref(false)
const currentProduct = ref<ProductResponse | null>(null)

const { isLoading, isEmpty, execute } = useAsyncState<ProductResponse[]>()
const { optimisticRemove, isItemPending } = useOptimistic<ProductResponse>()

const loadProducts = async () => {
  try {
    const apiResponse = await execute(async () => {
      const data = await getProducts({
        skip: (current.value - 1) * pageSize.value,
        limit: pageSize.value
      })
      // Store total from API response
      total.value = (data as any).total || 0
      pageSize.value = (data as any).limit || 0
      return data?.data as unknown as ProductResponse[]
    })

    if (apiResponse) {
      products.value = apiResponse
    }
  } catch (error: any) {
    message.error(error.message || '加载商品失败')
  }
}

const handleCreate = () => {
  currentProduct.value = null
  formVisible.value = true
}

const handleEdit = (product: ProductResponse) => {
  currentProduct.value = product
  formVisible.value = true
}

const handleRegenerateImage = async (id: number) => {
  try {
    await regenerateProductImage(id)
    message.success('图片生成任务已受理，请稍后刷新查看')
  } catch (error: any) {
    message.error(error.message || '操作失败')
  }
}

const handleTableChange = (e: any) => {
  current.value = e.current
  loadProducts()
}

const handleDelete = async (id: number) => {
  try {
    await optimisticRemove(
      id,
      async () => {
        await deleteProduct(id)
      }
    )
    message.success('删除成功')
    // Reload to get fresh data
    loadProducts()
  } catch (error: any) {
    message.error(error.message || '删除失败，已恢复原状态')
  }
}

loadProducts()
</script>
