<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <!-- Page Header -->
        <div class="page-header">
          <div class="header-content">
            <div class="header-icon">💰</div>
            <div>
              <h1>申请提现</h1>
              <p>佣金到账后即可申请提现，审核通过后自动打款</p>
            </div>
          </div>
        </div>

        <!-- Summary Card -->
        <a-row :gutter="24">
          <a-col :xs="24" :md="8">
            <a-card class="summary-card balance-card" :bordered="false">
              <div class="summary-icon">
                <WalletOutlined />
              </div>
              <div class="summary-content">
                <div class="summary-label">可提现余额</div>
                <div class="summary-value">¥ {{ Number(summary.total_available).toFixed(2) }}</div>
              </div>
            </a-card>
          </a-col>
          <a-col :xs="24" :md="8">
            <a-card class="summary-card pending-card" :bordered="false">
              <div class="summary-icon">
                <ClockCircleOutlined />
              </div>
              <div class="summary-content">
                <div class="summary-label">已冻结</div>
                <div class="summary-value">¥ {{ Number(summary.total_frozen).toFixed(2) }}</div>
              </div>
            </a-card>
          </a-col>
          <a-col :xs="24" :md="8">
            <a-card class="summary-card total-card" :bordered="false">
              <div class="summary-icon">
                <BankOutlined />
              </div>
              <div class="summary-content">
                <div class="summary-label">累计已提现</div>
                <div class="summary-value">¥ {{ Number(summary.total_withdrawn).toFixed(2) }}</div>
              </div>
            </a-card>
          </a-col>
        </a-row>

        <!-- Withdraw Form -->
        <a-row :gutter="24" class="form-row">
          <a-col :xs="24" :lg="24" :lg-offset="24">
            <a-card class="form-card" :bordered="false">
              <div class="form-header">
                <h3>提现金额</h3>
                <p>最低提现金额为 ¥1.00</p>
              </div>

              <a-spin v-if="loading" class="loading-spin" />
              <a-form v-else layout="vertical" class="withdraw-form">
                <a-form-item>
                  <div class="amount-input-wrapper">
                    <span class="currency-symbol">¥</span>
                    <a-input-number
                      v-model:value="amount"
                      :min="1"
                      :precision="2"
                      :controls="false"
                      placeholder="0.00"
                      class="amount-input"
                    />
                  </div>
                  <div class="quick-amount">
                    <a-tag
                      v-for="val in quickAmounts"
                      :key="val"
                      :class="['quick-tag', { active: amount === val }]"
                      @click="amount = val"
                    >
                      ¥{{ val }}
                    </a-tag>
                    <a-tag
                      class="quick-tag"
                      :class="['quick-tag', { active: amount === Number(summary.total_available) }]"
                      @click="amount = Number(summary.total_available)"
                    >
                      全部
                    </a-tag>
                  </div>
                </a-form-item>

                <a-divider />

                <a-form-item>
                  <a-button
                    type="primary"
                    block
                    size="large"
                    @click="handleSubmit"
                    :loading="submitting"
                    :disabled="!amount || amount <= 0"
                    class="submit-btn"
                  >
                    提交申请
                  </a-button>
                </a-form-item>

                <div class="withdraw-tips">
                  <div class="tips-title">
                    <ExclamationCircleOutlined /> 提现须知
                  </div>
                  <ul>
                    <li>提现申请审核通过后，1-3个工作日内到账</li>
                    <li>单笔提现金额不低于 ¥1.00</li>
                    <li>如有疑问，请联系客服</li>
                  </ul>
                </div>
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
import { getCommissionSummary, applyWithdrawal } from '@/api/channel'
import {
  WalletOutlined,
  ClockCircleOutlined,
  BankOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons-vue'

const amount = ref<number | null>(null)
const submitting = ref(false)
const loading = ref(false)
const summary = ref({
  total_available: '0.00',
  total_frozen: '0.00',
  total_withdrawn: '0.00'
})

const quickAmounts = [10, 50, 100, 500]

onMounted(async () => {
  loading.value = true
  try {
    const data = await getCommissionSummary()
    summary.value = data
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
})

const handleSubmit = async () => {
  if (!amount.value || amount.value <= 0) {
    message.error('请输入正确的提现金额')
    return
  }
  submitting.value = true
  try {
    await applyWithdrawal(amount.value.toString())
    message.success('提现申请已提交')
    amount.value = null
    // Refresh summary
    const data = await getCommissionSummary()
    summary.value = data
  } catch (error: any) {
    message.error(error.message || '申请失败')
  } finally {
    submitting.value = false
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
  background: var(--color-primary-light);
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

/* ---- Summary Cards ---- */
.summary-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
}

.summary-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.balance-card .summary-icon {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.pending-card .summary-icon {
  background: var(--color-accent-light);
  color: var(--color-accent);
}

.total-card .summary-icon {
  background: #dbeafe;
  color: #3b82f6;
}

.summary-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-1);
}

.summary-value {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

/* ---- Form Row ---- */
.form-row {
  margin-top: var(--space-2);
}

/* ---- Form Card ---- */
.form-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-6);
}

.loading-spin {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}

.form-header {
  margin-bottom: var(--space-6);
}

.form-header h3 {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.form-header p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ---- Amount Input ---- */
.amount-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg-gray);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.currency-symbol {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.amount-input {
  flex: 1;
  border: none;
  background: transparent;
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
}

.amount-input :deep(.ant-input-number-input) {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  text-align: left;
}

.quick-amount {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.quick-tag {
  cursor: pointer;
  border-radius: var(--radius-md);
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-border);
  background: var(--color-bg-white);
  transition: all var(--transition-fast);
}

.quick-tag:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.quick-tag.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  color: var(--color-primary);
}

/* ---- Submit Button ---- */
.submit-btn {
  height: 52px;
  font-size: var(--text-base);
  font-weight: 600;
  border-radius: var(--radius-md);
}

/* ---- Tips ---- */
.withdraw-tips {
  margin-top: var(--space-6);
  padding: var(--space-4);
  background: var(--color-bg-gray);
  border-radius: var(--radius-md);
}

.tips-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
}

.tips-title :deep(.anticon) {
  margin-right: var(--space-2);
  color: var(--color-warning);
}

.withdraw-tips ul {
  margin: 0;
  padding-left: var(--space-5);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  line-height: 1.8;
}
</style>
