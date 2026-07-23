<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-button type="primary" @click="handleCreate">新增分类</a-button>
    </div>

    <ErrorBoundary @retry="loadCategories">
      <!-- Loading state: show skeleton -->
      <TableSkeleton v-if="isLoading" :columns="columns" :rows="5" />

      <!-- Empty state -->
      <EmptyState
        v-else-if="isEmpty"
        entity-name="分类"
        action-text="创建分类"
        @action="handleCreate"
      />

      <!-- Data table -->
      <a-table
        v-else
        :columns="columns"
        :data-source="categories"
        :pagination="{ pageSize: pageSize, total, current }"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'parent_id'">
            {{ getParentName(record.parent_id) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
              <a-popconfirm
                title="确定删除该分类吗?"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.id)"
              >
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </ErrorBoundary>

    <CategoryForm
      v-model:visible="formVisible"
      :category="currentCategory"
      :categories="categories"
      @success="loadCategories"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import type { CategoryResponse } from '../../types'
import { getCategories, deleteCategory } from '../../api'
import { useAsyncState } from '../../composables/useAsyncState'
import ErrorBoundary from '../../components/ui/ErrorBoundary.vue'
import TableSkeleton from '../../components/ui/TableSkeleton.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import CategoryForm from './CategoryForm.vue'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '分类名称', dataIndex: 'name', key: 'name' },
  { title: '操作', key: 'action', width: 150 }
]

const categories = ref<CategoryResponse[]>([])
const formVisible = ref(false)
const currentCategory = ref<CategoryResponse | null>(null)
const total = ref(0)
const current = ref(1)
const pageSize = ref(10)

const { isLoading, isEmpty, execute } = useAsyncState<CategoryResponse[]>()

const getParentName = (parentId: number | null) => {
  if (!parentId) return '无'
  const parent = categories.value.find(c => c.id === parentId)
  return parent?.name || '无'
}

const loadCategories = async () => {
  try {
    const result = await execute(async () => {
      const data = await getCategories({
        skip: (current.value - 1) * pageSize.value,
        limit: pageSize.value
      })
      return data as unknown as CategoryResponse[]
    })

    if (result) {
      total.value = (result as any).total || 0
      pageSize.value = (result as any).limit || 0
      categories.value = (result as any).data
    }
  } catch (error: any) {
    message.error(error.message || '加载分类失败')
  }
}

const handleCreate = () => {
  currentCategory.value = null
  formVisible.value = true
}

const handleEdit = (category: CategoryResponse) => {
  currentCategory.value = category
  formVisible.value = true
}

const handleTableChange = (e: any) => {
  current.value = e.current
  loadCategories()
}

const handleDelete = async (id: number) => {
  try {
    await deleteCategory(id)
    message.success('删除成功')
    loadCategories()
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

loadCategories()
</script>
