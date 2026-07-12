<template>
  <a-config-provider :theme="themeConfig">
    <Layout>
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </Layout>
  </a-config-provider>
</template>

<script setup lang="ts">
import { Layout } from 'ant-design-vue'
import { RouterView } from 'vue-router'

const themeConfig = {
  token: {
    colorPrimary: '#0d9488',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    colorInfo: '#3b82f6',
    borderRadius: 10,
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    boxShadow: '0 2px 8px rgb(0 0 0 / 0.06), 0 4px 24px rgb(0 0 0 / 0.04)',
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f8fafc',
    colorBorder: '#e2e8f0',
    colorText: '#0f172a',
    colorTextSecondary: '#475569',
    colorTextTertiary: '#94a3b8',
  },
  components: {
    Button: {
      borderRadius: 10,
      controlHeight: 40,
      primaryShadow: '0 2px 0 rgb(13 148 136 / 0.1)',
    },
    Card: {
      borderRadius: 16,
      paddingLG: 20,
    },
    Input: {
      borderRadius: 10,
      controlHeight: 42,
    },
    InputNumber: {
      borderRadius: 10,
      controlHeight: 42,
    },
    Select: {
      borderRadius: 10,
      controlHeight: 42,
    },
    Menu: {
      itemBorderRadius: 10,
      itemSelectedBg: '#ccfbf1',
      itemSelectedColor: '#0d9488',
      itemHoverBg: '#f1f5f9',
      itemHoverColor: '#0d9488',
    },
    Pagination: {
      itemActiveBg: '#ccfbf1',
    },
    Badge: {
      dotSize: 8,
    },
  },
}
</script>

<style>
.ant-layout {
  min-height: 100vh;
}
</style>
