<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-button type="primary" @click="handleCreate">创建优惠券</a-button>
    </div>

    <ErrorBoundary @retry="loadCoupons">
      <!-- Loading state: show skeleton -->
      <TableSkeleton v-if="isLoading" :columns="columns" :rows="10" />

      <!-- Empty state -->
      <EmptyState
        v-else-if="isEmpty"
        entity-name="优惠券"
        action-text="创建优惠券"
        @action="handleCreate"
      />

      <!-- Data table -->
      <a-table
        v-else
        :columns="columns"
        :data-source="coupons"
        row-key="id"
        :pagination="{ pageSize: 10, total }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'discount_type'">
            <a-tag :color="record.discount_type === 'fixed' ? 'blue' : 'green'">
              {{ record.discount_type === 'fixed' ? '满减' : '折扣' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'discount_value'">
            {{ record.discount_type === 'fixed' ? `¥${record.discount_value}` : `${record.discount_value}%` }}
          </template>
          <template v-else-if="column.key === 'time_range'">
            {{ record.start_time }} ~ {{ record.end_time }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </ErrorBoundary>

    <CouponForm
      v-model:visible="formVisible"
      :coupon="currentCoupon"
      @success="loadCoupons"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import type { CouponInfo } from '../../types'
import { getCoupons } from '../../api'
import { useAsyncState } from '../../composables/useAsyncState'
import ErrorBoundary from '../../components/ui/ErrorBoundary.vue'
import TableSkeleton from '../../components/ui/TableSkeleton.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import CouponForm from './CouponForm.vue'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '优惠券码', dataIndex: 'code', key: 'code', width: 150 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '折扣类型', key: 'discount_type', width: 100 },
  { title: '折扣值', key: 'discount_value', width: 100 },
  { title: '剩余数量', dataIndex: 'remain_count', key: 'remain_count', width: 100 },
  { title: '有效期', key: 'time_range', width: 280 },
  { title: '操作', key: 'action', width: 100 }
]

const total = ref(0)
const current = ref(1)
const pageSize = ref(10)

const coupons = ref<CouponInfo[]>([])
const formVisible = ref(false)
const currentCoupon = ref<CouponInfo | null>(null)

const { isLoading, isEmpty, execute } = useAsyncState<CouponInfo[]>()

const loadCoupons = async () => {
  try {
    const apiResponse = await execute(async () => {
      const data = await getCoupons({
        skip: (current.value - 1) * pageSize.value,
        limit: pageSize.value
      })
      // Store total from API response
      total.value = (data as any).total || 0
      return data.data as unknown as CouponInfo[]
    })

    if (apiResponse) {
      coupons.value = apiResponse
    }
  } catch (error: any) {
    message.error(error.message || '加载优惠券失败')
  }
}

const handleTableChange = (e: any) => {
  current.value = e.current
  loadCoupons()
}

const handleCreate = () => {
  currentCoupon.value = null
  formVisible.value = true
}

const handleEdit = (coupon: CouponInfo) => {
  currentCoupon.value = coupon
  formVisible.value = true
}

loadCoupons()
</script>
