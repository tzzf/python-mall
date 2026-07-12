<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <a-spin :spinning="loading">
          <a-card v-if="authStore.currentUser">
            <template #title>个人信息</template>
            <a-descriptions :column="1" bordered>
              <a-descriptions-item label="用户ID">{{ authStore.currentUser.id }}</a-descriptions-item>
              <a-descriptions-item label="用户名">{{ authStore.currentUser.username }}</a-descriptions-item>
              <a-descriptions-item label="邮箱">{{ authStore.currentUser.email }}</a-descriptions-item>
              <a-descriptions-item label="账号状态">
                <a-tag :color="authStore.currentUser.is_active ? 'green' : 'red'">
                  {{ authStore.currentUser.is_active ? '正常' : '禁用' }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="注册时间">{{ formatDate(authStore.currentUser.created_at) }}</a-descriptions-item>
            </a-descriptions>
            <div class="actions">
              <a-button type="primary" danger @click="handleLogout">退出登录</a-button>
            </div>
          </a-card>
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
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/format'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const handleLogout = () => {
  authStore.logout()
  message.success('已退出登录')
  router.push('/')
}

onMounted(async () => {
  loading.value = true
  try {
    await authStore.fetchCurrentUser()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.main-content {
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
  padding: 20px 0;
}

.actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
