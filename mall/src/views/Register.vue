<template>
  <div class="register-page">
    <a-card class="register-card">
      <h1>注册</h1>
      <a-form
        :model="formState"
        @finish="handleSubmit"
      >
        <a-form-item
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input v-model:value="formState.username" placeholder="用户名" size="large" />
        </a-form-item>
        <a-form-item
          name="email"
          :rules="[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' }
          ]"
        >
          <a-input v-model:value="formState.email" placeholder="邮箱" size="large" />
        </a-form-item>
        <a-form-item
          name="password"
          :rules="[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码至少6位' }
          ]"
        >
          <a-input-password v-model:value="formState.password" placeholder="密码" size="large" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="loading" size="large">
            注册
          </a-button>
        </a-form-item>
        <div class="login-link">
          已有账号? <RouterLink to="/login">立即登录</RouterLink>
        </div>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formState = reactive({
  username: '',
  email: '',
  password: ''
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
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.register-card {
  width: 400px;
}

.register-card h1 {
  text-align: center;
  margin-bottom: 24px;
}

.login-link {
  text-align: center;
  margin-top: 16px;
}
</style>
