<template>
  <div>
    <ErrorBoundary @retry="loadApplications">
      <TableSkeleton v-if="loading" :columns="columns" :rows="10" />
      <EmptyState v-else-if="!loading && applications.length === 0" entity-name="申请记录" @action="loadApplications" />
      <a-table
        v-else
        :columns="columns"
        :data-source="applications"
        :pagination="{ pageSize: 20, current: currentPage, total }"
        row-key="id"
        @change="onTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="statusColor(record.status)">
              {{ statusText(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space v-if="record.status === 'pending'">
              <a-button type="link" size="small" @click="handleApprove(record)">
                通过
              </a-button>
              <a-button type="link" size="small" danger @click="handleReject(record)">
                拒绝
              </a-button>
            </a-space>
            <span v-else-if="record.status === 'rejected'" style="color: #999">
              {{ record.reject_reason || '-' }}
            </span>
          </template>
        </template>
      </a-table>
    </ErrorBoundary>

    <a-modal
      v-model:open="rejectModalVisible"
      title="拒绝申请"
      @ok="handleRejectSubmit"
      @cancel="rejectModalVisible = false"
      :confirm-loading="rejectLoading"
    >
      <a-form :model="rejectForm" :label-col="{ span: 6 }" layout="vertical">
        <a-form-item label="拒绝原因" required>
          <a-input v-model:value="rejectForm.reason" placeholder="请输入拒绝原因" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'
import type { TableProps } from 'ant-design-vue'
import {
  getChannelApplications,
  reviewChannelApplication,
  type ChannelApplicationItem
} from '../../api/channel'
import ErrorBoundary from '../../components/ui/ErrorBoundary.vue'
import TableSkeleton from '../../components/ui/TableSkeleton.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const columns = [
  { title: '用户ID', dataIndex: 'id', key: 'id', width: 100 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '申请时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '状态', key: 'status', width: 120 },
  { title: '操作', key: 'action', width: 160 }
]

const PAGE_SIZE = 20

const applications = ref<ChannelApplicationItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const rejectModalVisible = ref(false)
const rejectLoading = ref(false)
const currentRecord = ref<ChannelApplicationItem | null>(null)

const rejectForm = reactive({ reason: '' })

const statusColor = (status: string) => {
  if (status === 'approved') return 'green'
  if (status === 'rejected') return 'red'
  return 'orange'
}

const statusText = (status: string) => {
  if (status === 'approved') return '已通过'
  if (status === 'rejected') return '已拒绝'
  return '待审核'
}

const loadApplications = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * PAGE_SIZE
    const res = await getChannelApplications(undefined, skip, PAGE_SIZE)
    applications.value = res.data
    total.value = res.total
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const onTableChange: TableProps['onChange'] = (pagination) => {
  currentPage.value = pagination.current || 1
  loadApplications()
}

const handleApprove = async (record: ChannelApplicationItem) => {
  try {
    await reviewChannelApplication(record.id, 'approved')
    message.success('已通过')
    loadApplications()
  } catch (error: any) {
    message.error(error.message || '操作失败')
  }
}

const handleReject = (record: ChannelApplicationItem) => {
  currentRecord.value = record
  rejectForm.reason = ''
  rejectModalVisible.value = true
}

const handleRejectSubmit = async () => {
  if (!rejectForm.reason) {
    message.error('请输入拒绝原因')
    return
  }
  if (!currentRecord.value) return
  rejectLoading.value = true
  try {
    await reviewChannelApplication(currentRecord.value.id, 'rejected', rejectForm.reason)
    message.success('已拒绝')
    rejectModalVisible.value = false
    loadApplications()
  } catch (error: any) {
    message.error(error.message || '操作失败')
  } finally {
    rejectLoading.value = false
  }
}

loadApplications()
</script>
