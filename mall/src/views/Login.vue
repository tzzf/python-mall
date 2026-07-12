<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Left: Branding -->
      <div class="login-branding">
        <div class="branding-content">
          <div class="brand-logo">🛍️</div>
          <h1 class="brand-title">欢迎回来</h1>
          <p class="brand-subtitle">登录轻氧商城，发现更多品质好物</p>
          <div class="brand-features">
            <div class="feature-item">
              <span class="feature-icon">✨</span>
              <span>精选好物</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🚚</span>
              <span>快速配送</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">💎</span>
              <span>品质保障</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Login Form -->
      <div class="login-form-wrapper">
        <a-card class="login-card" :bordered="false">
          <div class="card-header">
            <h2>用户登录</h2>
            <p>还没有账号？<RouterLink to="/register" class="link">立即注册</RouterLink></p>
          </div>

          <a-form
            :model="formState"
            @finish="handleSubmit"
            class="login-form"
          >
            <a-form-item
              name="username"
              :rules="[{ required: true, message: '请输入用户名' }]"
            >
              <a-input
                v-model:value="formState.username"
                placeholder="用户名"
                size="large"
                allow-clear
              >
                <template #prefix>
                  <UserOutlined class="input-icon" />
                </template>
              </a-input>
            </a-form-item>

            <a-form-item
              name="password"
              :rules="[{ required: true, message: '请输入密码' }]"
            >
              <a-input-password
                v-model:value="formState.password"
                placeholder="密码"
                size="large"
              >
                <template #prefix>
                  <LockOutlined class="input-icon" />
                </template>
              </a-input-password>
            </a-form-item>

            <div class="form-extras">
              <a-checkbox>记住我</a-checkbox>
            </div>

            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                block
                :loading="loading"
                size="large"
                class="submit-btn"
              >
                登录
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formState = reactive({
  username: '',
  password: ''
})
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    await authStore.login(formState)
    message.success('登录成功')
    router.push('/')
  } catch (error: any) {
    message.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-bg-base) 0%, var(--color-primary-light) 100%);
  padding: var(--space-6);
}

.login-container {
  display: flex;
  max-width: 900px;
  width: 100%;
  background: var(--color-bg-white);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-xl);
}

/* ---- Branding Panel ---- */
.login-branding {
  flex: 1;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-active) 100%);
  padding: var(--space-10);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.branding-content {
  text-align: center;
}

.brand-logo {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.brand-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
  color: white;
}

.brand-subtitle {
  opacity: 0.9;
  margin-bottom: var(--space-8);
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  justify-content: center;
  font-size: var(--text-sm);
  opacity: 0.9;
}

.feature-icon {
  font-size: 18px;
}

/* ---- Form Panel ---- */
.login-form-wrapper {
  flex: 1;
  padding: var(--space-10);
  display: flex;
  align-items: center;
}

.login-card {
  width: 100%;
  box-shadow: none;
}

.card-header {
  margin-bottom: var(--space-8);
}

.card-header h2 {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
}

.card-header p {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

.login-form {
  margin-bottom: var(--space-4);
}

.input-icon {
  color: var(--color-text-muted);
}

.form-extras {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.submit-btn {
  height: 48px;
  font-size: var(--text-base);
  font-weight: 600;
  border-radius: var(--radius-md);
}

.divider {
  text-align: center;
  margin: var(--space-6) 0;
  position: relative;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: calc(50% - 30px);
  height: 1px;
  background: var(--color-border);
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.social-login {
  display: flex;
  justify-content: center;
}

.social-btn {
  width: 100%;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .login-branding {
    display: none;
  }

  .login-container {
    max-width: 420px;
  }
}
</style>
