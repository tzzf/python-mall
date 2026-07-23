<template>
  <div class="register-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-icon">🎁</div>
        <h1>加入我们</h1>
        <p>注册即享专属优惠，开启品质购物之旅</p>
      </div>
      <div class="hero-decoration"></div>
    </div>

    <!-- Form Card -->
    <div class="form-section">
      <a-card class="register-card" :bordered="false">
        <div class="card-header">
          <h2>创建账号</h2>
          <p>已有账号? <RouterLink to="/login">立即登录</RouterLink></p>
        </div>

        <a-form
          :model="formState"
          @finish="handleSubmit"
          layout="vertical"
          class="register-form"
        >
          <a-form-item
            name="username"
            :rules="[{ required: true, message: '请输入用户名' }]"
          >
            <a-input v-model:value="formState.username" placeholder="用户名" size="large">
              <template #prefix><UserOutlined /></template>
            </a-input>
          </a-form-item>
          <a-form-item
            name="email"
            :rules="[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]"
          >
            <a-input v-model:value="formState.email" placeholder="邮箱" size="large">
              <template #prefix><MailOutlined /></template>
            </a-input>
          </a-form-item>
          <a-form-item
            name="password"
            :rules="[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6位' }
            ]"
          >
            <a-input-password v-model:value="formState.password" placeholder="密码" size="large">
              <template #prefix><LockOutlined /></template>
            </a-input-password>
          </a-form-item>
          <a-form-item name="invite_code">
            <a-input
              v-model:value="formState.invite_code"
              placeholder="邀请码（选填）"
              size="large"
            >
              <template #prefix><GiftOutlined /></template>
            </a-input>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" html-type="submit" block :loading="loading" size="large" class="submit-btn">
              立即注册
            </a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { UserOutlined, MailOutlined, LockOutlined, GiftOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const formState = reactive({
  username: '',
  email: '',
  password: '',
  invite_code: ''
})
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    await authStore.register(formState)
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (error: any) {
    message.error(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: var(--color-bg-base);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-8) var(--space-4);
}

/* ---- Hero Section ---- */
.hero-section {
  position: relative;
  text-align: center;
  margin-bottom: var(--space-8);
  padding: var(--space-10) var(--space-8);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-active) 100%);
  border-radius: var(--radius-xl);
  color: white;
  overflow: hidden;
  max-width: 480px;
  width: 100%;
}

.hero-icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
}

.hero-section h1 {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: white;
  margin-bottom: var(--space-2);
}

.hero-section p {
  font-size: var(--text-sm);
  opacity: 0.9;
}

.hero-decoration {
  position: absolute;
  right: -30px;
  bottom: -30px;
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

/* ---- Form Section ---- */
.form-section {
  width: 100%;
  max-width: 420px;
}

.register-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-6);
}

.card-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.card-header h2 {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
}

.card-header p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.card-header a {
  color: var(--color-primary);
  font-weight: 500;
}

.register-form :deep(.ant-input-affix-wrapper),
.register-form :deep(.ant-input) {
  border-radius: var(--radius-md);
}

.submit-btn {
  height: 48px;
  font-size: var(--text-base);
  font-weight: 600;
  border-radius: var(--radius-md);
  margin-top: var(--space-2);
}
</style>
