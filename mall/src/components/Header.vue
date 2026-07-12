<template>
  <a-layout-header class="header">
    <div class="header-content">
      <RouterLink to="/" class="logo">
        <span class="logo-icon">🛍️</span>
        <span class="logo-text">轻氧商城</span>
      </RouterLink>

      <nav class="nav-links">
        <RouterLink to="/" class="nav-item" active-class="active">
          <span>首页</span>
        </RouterLink>
        <RouterLink to="/cart" class="nav-item" active-class="active">
          <span>购物车</span>
          <a-badge
            v-if="cartStore.totalCount > 0"
            :count="cartStore.totalCount"
            :offset="[6, -2]"
            class="cart-badge"
          />
        </RouterLink>
        <RouterLink to="/orders" class="nav-item" active-class="active">
          <span>我的订单</span>
        </RouterLink>
        <RouterLink to="/user" class="nav-item" active-class="active">
          <span>个人中心</span>
        </RouterLink>
      </nav>

      <div class="auth-section">
        <template v-if="authStore.isAuthenticated">
          <a-dropdown>
            <div class="user-info">
              <a-avatar :size="32" class="user-avatar">
                {{ authStore.currentUser?.username?.charAt(0).toUpperCase() }}
              </a-avatar>
              <span class="username">{{ authStore.currentUser?.username }}</span>
              <DownOutlined class="dropdown-icon" />
            </div>
            <template #overlay>
              <a-menu>
                <a-menu-item key="profile" @click="handleCenter">
                  <UserOutlined /> 个人中心
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout" danger @click="handleLogout">
                  <LogoutOutlined /> 退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </template>
        <template v-else>
          <RouterLink to="/login" class="auth-btn login-btn">登录</RouterLink>
          <RouterLink to="/register" class="auth-btn register-btn">注册</RouterLink>
        </template>
      </div>
    </div>
  </a-layout-header>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { DownOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { watch } from 'vue'

const authStore = useAuthStore()
const cartStore = useCartStore()
const router = useRouter()

watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    cartStore.fetchCart()
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const handleCenter = () => {
  router.push('/user')
}
</script>

<style scoped>
.header {
  background: var(--color-bg-white);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0;
  border-bottom: 1px solid var(--color-border-light);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 var(--space-6);
  gap: var(--space-8);
}

/* ---- Logo ---- */
.logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 24px;
  line-height: 1;
}

.logo-text {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ---- Nav Links ---- */
.nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex: 1;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-item:hover {
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.nav-item.active {
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: var(--color-primary);
  border-radius: var(--radius-full);
}

.cart-badge :deep(.ant-badge-count) {
  background: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-bg-white);
}

/* ---- Auth Section ---- */
.auth-section {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.auth-btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: var(--text-sm);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.login-btn {
  color: var(--color-primary);
  background: transparent;
}

.login-btn:hover {
  background: var(--color-primary-light);
}

.register-btn {
  color: var(--color-bg-white);
  background: var(--color-primary);
}

.register-btn:hover {
  background: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* ---- User Info ---- */
.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: var(--color-bg-gray);
}

.user-avatar {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  font-weight: 600;
}

.username {
  font-weight: 500;
  color: var(--color-text-primary);
  font-size: var(--text-sm);
}

.dropdown-icon {
  font-size: 10px;
  color: var(--color-text-muted);
}
</style>
