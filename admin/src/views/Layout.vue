<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible>
      <div class="logo" style="height: 32px; margin: 16px; background: rgba(255,255,255,0.2); border-radius: 4px;" />
      <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline" @click="handleMenuClick">
        <a-menu-item key="/products">
          <span>商品管理</span>
        </a-menu-item>
        <a-menu-item key="/categories">
          <span>分类管理</span>
        </a-menu-item>
        <a-menu-item key="/orders">
          <span>订单管理</span>
        </a-menu-item>
        <a-menu-item key="/coupons">
          <span>优惠券管理</span>
        </a-menu-item>
        <a-menu-item key="/users">
          <span>用户管理</span>
        </a-menu-item>
        <a-sub-menu key="channel">
          <template #title>渠道商管理</template>
          <a-menu-item key="/channel/applications">申请审核</a-menu-item>
          <a-menu-item key="/channel/list">渠道商列表</a-menu-item>
          <a-menu-item key="/channel/setting">佣金设置</a-menu-item>
          <a-menu-item key="/channel/withdrawals">提现审核</a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: flex-end;">
        <a-button type="link" @click="handleLogout">退出登录</a-button>
      </a-layout-header>
      <a-layout-content style="margin: 24px 16px; padding: 24px; background: #fff; min-height: 280px;">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const collapsed = ref(false)
const selectedKeys = ref<string[]>([route.path])

watch(() => route.path, (path) => {
  selectedKeys.value = [path]
})

const handleMenuClick = ({ key }: { key: string }) => {
  router.push(key)
}

const handleLogout = () => {
  authStore.logout()
  message.success('已退出登录')
  router.push('/login')
}
</script>
