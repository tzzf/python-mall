<template>
  <div>
    <ErrorBoundary @retry="loadUsers">
      <!-- Loading state: show skeleton -->
      <TableSkeleton v-if="isLoading" :columns="columns" :rows="10" />

      <!-- Empty state -->
      <EmptyState
        v-else-if="isEmpty"
        entity-name="用户"
        @action="loadUsers"
      />

      <!-- Data table -->
      <a-table
        v-else
        :columns="columns"
        :data-source="users"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'green' : 'red'">
              {{ record.is_active ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="handleToggleStatus(record)"
              >
                {{ record.is_active ? '禁用' : '启用' }}
              </a-button>
              <a-button type="link" size="small" @click="handleChangePassword(record)">
                修改密码
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </ErrorBoundary>

    <a-modal
      v-model:open="passwordModalVisible"
      title="修改密码"
      @ok="handlePasswordSubmit"
      @cancel="passwordModalVisible = false"
      :confirm-loading="passwordLoading"
    >
      <a-form
        :model="passwordForm"
        :label-col="{ span: 6 }"
        layout="vertical"
      >
        <a-form-item label="旧密码" required>
          <a-input-password v-model:value="passwordForm.old_password" />
        </a-form-item>
        <a-form-item label="新密码" required>
          <a-input-password v-model:value="passwordForm.new_password" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'
import type { AdminUserResponse } from '../../types'
import { getUsers, updateUser, changePassword } from '../../api'
import { useAsyncState } from '../../composables/useAsyncState'
import ErrorBoundary from '../../components/ui/ErrorBoundary.vue'
import TableSkeleton from '../../components/ui/TableSkeleton.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '状态', key: 'is_active', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 180 }
]

const users = ref<AdminUserResponse[]>([])
const passwordModalVisible = ref(false)
const passwordLoading = ref(false)
const currentUserId = ref<number | null>(null)

const passwordForm = reactive({
  old_password: '',
  new_password: ''
})

const { isLoading, isEmpty, execute } = useAsyncState<AdminUserResponse[]>()

const loadUsers = async () => {
  try {
    const result = await execute(async () => {
      const data = await getUsers()
      return data as unknown as AdminUserResponse[]
    })

    if (result) {
      users.value = result
    }
  } catch (error: any) {
    message.error(error.message || '加载用户失败')
  }
}

const handleToggleStatus = async (user: AdminUserResponse) => {
  try {
    await updateUser(user.id, { is_active: !user.is_active })
    message.success('更新成功')
    loadUsers()
  } catch (error: any) {
    message.error(error.message || '更新失败')
  }
}

const handleChangePassword = (user: AdminUserResponse) => {
  currentUserId.value = user.id
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordModalVisible.value = true
}

const handlePasswordSubmit = async () => {
  if (!passwordForm.old_password || !passwordForm.new_password) {
    message.error('请填写完整')
    return
  }
  if (!currentUserId.value) return
  passwordLoading.value = true
  try {
    await changePassword(currentUserId.value, passwordForm.old_password, passwordForm.new_password)
    message.success('密码修改成功')
    passwordModalVisible.value = false
  } catch (error: any) {
    message.error(error.message || '修改失败')
  } finally {
    passwordLoading.value = false
  }
}

loadUsers()
</script>
