<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <!-- Page Header -->
        <div class="page-header">
          <div class="header-content">
            <div class="header-icon">🎉</div>
            <div>
              <h1>我的邀请码</h1>
              <p>分享给好友，好友注册时填写邀请码，即可成为您的下级</p>
            </div>
          </div>
        </div>

        <a-row :gutter="24">
          <a-col :xs="24" :lg="10">
            <!-- Invite Code Card -->
            <a-card class="invite-card" :bordered="false">
              <a-spin v-if="loading" class="loading-spin" />
              <div v-else class="invite-content">
                <div class="invite-label">我的邀请码</div>
                <div class="invite-code-box">
                  <span class="invite-code">{{ inviteCode }}</span>
                  <a-button type="primary" @click="handleCopy" class="copy-btn">
                    <template #icon><CopyOutlined /></template>
                    复制
                  </a-button>
                </div>
                <div class="invite-tips">
                  <div class="tip-item">
                    <CheckCircleOutlined class="tip-icon" />
                    <span>好友下单您可获得佣金奖励</span>
                  </div>
                  <div class="tip-item">
                    <CheckCircleOutlined class="tip-icon" />
                    <span>下级用户终身归属您</span>
                  </div>
                  <div class="tip-item">
                    <CheckCircleOutlined class="tip-icon" />
                    <span>邀请人数无上限</span>
                  </div>
                </div>
              </div>
            </a-card>
          </a-col>

          <a-col :xs="24" :lg="14">
            <!-- Custom Code Card -->
            <a-card class="custom-card" :bordered="false">
              <div class="custom-header">
                <div class="custom-icon"><EditOutlined /></div>
                <div>
                  <h3>自定义邀请码</h3>
                  <p>设置专属于您的邀请码，更容易让好友记住</p>
                </div>
              </div>

              <a-form layout="vertical" class="custom-form">
                <a-form-item>
                  <a-input
                    v-model:value="customCode"
                    placeholder="4-20位字母或数字组合"
                    :maxlength="20"
                    size="large"
                    class="custom-input"
                  >
                    <template #prefix><LinkOutlined /></template>
                  </a-input>
                </a-form-item>
                <a-form-item>
                  <a-button
                    type="primary"
                    @click="handleSave"
                    :loading="saving"
                    :disabled="!customCode || customCode.length < 4"
                    class="save-btn"
                  >
                    保存自定义邀请码
                  </a-button>
                </a-form-item>
              </a-form>
            </a-card>
          </a-col>
        </a-row>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { getMyInviteCode, setCustomInviteCode } from '@/api/channel'
import { CopyOutlined, CheckCircleOutlined, EditOutlined, LinkOutlined } from '@ant-design/icons-vue'

const loading = ref(false)
const saving = ref(false)
const inviteCode = ref('')
const customCode = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const data = await getMyInviteCode()
    inviteCode.value = data.invite_code
    customCode.value = data.is_custom ? data.invite_code : ''
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
})

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(inviteCode.value)
    message.success('已复制到剪贴板')
  } catch {
    message.error('复制失败')
  }
}

const handleSave = async () => {
  if (customCode.value.length < 4) {
    message.error('邀请码长度需在4-20位之间')
    return
  }
  saving.value = true
  try {
    const data = await setCustomInviteCode(customCode.value)
    inviteCode.value = data.invite_code
    message.success('保存成功')
  } catch (error: any) {
    message.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.main-content {
  background: var(--color-bg-base);
  min-height: calc(100vh - 64px);
  padding: var(--space-8) 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

/* ---- Page Header ---- */
.page-header {
  margin-bottom: var(--space-6);
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  background: var(--color-bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.header-icon {
  font-size: 40px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent-light);
  border-radius: var(--radius-lg);
}

.header-content h1 {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  margin-bottom: var(--space-1);
}

.header-content p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ---- Card Base ---- */
.invite-card,
.custom-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}

.loading-spin {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}

/* ---- Invite Code Card ---- */
.invite-content {
  text-align: center;
}

.invite-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}

.invite-code-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--color-bg-gray);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-6);
}

.invite-code {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 2px;
}

.copy-btn {
  border-radius: var(--radius-md);
}

.invite-tips {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  text-align: left;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.tip-icon {
  color: var(--color-success);
}

/* ---- Custom Code Card ---- */
.custom-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.custom-icon {
  font-size: 24px;
  color: var(--color-primary);
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-light);
  border-radius: var(--radius-md);
}

.custom-header h3 {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.custom-header p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.custom-form :deep(.ant-input-affix-wrapper),
.custom-form :deep(.ant-input) {
  border-radius: var(--radius-md);
}

.save-btn {
  width: 100%;
  height: 48px;
  font-size: var(--text-base);
  font-weight: 600;
  border-radius: var(--radius-md);
}
</style>
