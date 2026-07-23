<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <a-spin :spinning="loading">
          <!-- 渠道商申请卡片 -->
          <a-card v-if="!isChannel" style="margin-bottom: 16px; background: #fff3e0">
            <div style="display: flex; align-items: center; justify-content: space-between">
              <div>
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 4px">成为渠道商</div>
                <div style="color: #999; font-size: 12px">推广好友下单，赚取佣金收益</div>
              </div>
              <a-button
                type="primary"
                :loading="applying"
                :disabled="channelStatus === 'pending'"
                @click="handleApplyChannel"
              >
                {{ channelStatus === 'pending' ? '申请审核中' : '立即申请' }}
              </a-button>
            </div>
          </a-card>

          <!-- 渠道商快捷入口 -->
          <a-card v-if="isChannel" style="margin-bottom: 16px">
            <template #title>渠道商中心</template>
            <a-row :gutter="16">
              <a-col :span="8">
                <a-statistic title="可提现佣金" :value="profile.commission_summary?.total_available || '0.00'" prefix="¥" :value-style="{ color: '#52c41a' }" />
              </a-col>
              <a-col :span="8">
                <a-statistic title="冻结中佣金" :value="profile.commission_summary?.total_frozen || '0.00'" prefix="¥" :value-style="{ color: '#faad14' }" />
              </a-col>
              <a-col :span="8">
                <a-statistic title="已提现佣金" :value="profile.commission_summary?.total_withdrawn || '0.00'" prefix="¥" />
              </a-col>
            </a-row>
            <div style="margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap">
              <router-link to="/commission">
                <a-button size="small">我的佣金</a-button>
              </router-link>
              <router-link to="/withdraw">
                <a-button size="small">申请提现</a-button>
              </router-link>
              <router-link to="/referrals">
                <a-button size="small">我的下级</a-button>
              </router-link>
              <router-link to="/invite">
                <a-button size="small">邀请码</a-button>
              </router-link>
              <router-link to="/bank">
                <a-button size="small">银行卡</a-button>
              </router-link>
            </div>
          </a-card>

          <!-- 个人信息卡片 -->
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/format'
import { getChannelProfile, applyChannel } from '@/api/channel'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const applying = ref(false)

const profile = ref({
  commission_summary: {
    total_frozen: '0.00',
    total_available: '0.00',
    total_withdrawn: '0.00'
  }
})

const isChannel = computed(() => authStore.currentUser?.is_channel === true)
const channelStatus = computed(() => authStore.currentUser?.channel_status || '')

const handleLogout = () => {
  authStore.logout()
  message.success('已退出登录')
  router.push('/')
}

const handleApplyChannel = async () => {
  applying.value = true
  try {
    await applyChannel()
    message.success('申请已提交，请等待管理员审核')
    await authStore.fetchCurrentUser()
  } catch (error: any) {
    message.error(error.message || '申请失败')
  } finally {
    applying.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await authStore.fetchCurrentUser()
    if (authStore.currentUser?.is_channel) {
      const data = await getChannelProfile()
      profile.value = data
    }
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
