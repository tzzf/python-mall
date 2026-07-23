<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <!-- Page Header -->
        <div class="page-header">
          <div class="header-content">
            <div class="header-icon">💳</div>
            <div>
              <h1>我的银行卡</h1>
              <p>用于提现收款，请确保信息真实有效</p>
            </div>
          </div>
        </div>

        <a-row :gutter="24">
          <a-col :xs="24" :sm="24" :sm-offset="24">
            <a-card class="form-card" :bordered="false">
              <a-spin v-if="loading" class="loading-spin" />
              <a-form v-else layout="vertical" class="bank-form">
                <a-form-item label="银行名称">
                  <a-select
                    v-model:value="form.bank_name"
                    placeholder="选择银行"
                    size="large"
                    show-search
                    :filter-option="filterBank"
                  >
                    <a-select-option v-for="bank in bankList" :key="bank" :value="bank">
                      {{ bank }}
                    </a-select-option>
                  </a-select>
                </a-form-item>

                <a-form-item label="银行卡号">
                  <a-input
                    v-model:value="form.bank_account"
                    placeholder="请输入银行卡号"
                    size="large"
                    :maxlength="19"
                  >
                    <template #prefix><CreditCardOutlined /></template>
                  </a-input>
                </a-form-item>

                <a-form-item label="开户人姓名">
                  <a-input
                    v-model:value="form.account_holder"
                    placeholder="请输入开户人姓名"
                    size="large"
                  >
                    <template #prefix><UserOutlined /></template>
                  </a-input>
                </a-form-item>

                <a-divider />

                <a-form-item>
                  <a-button
                    type="primary"
                    block
                    size="large"
                    @click="handleSave"
                    :loading="saving"
                    class="submit-btn"
                  >
                    <template #icon><SaveOutlined /></template>
                    保存银行卡信息
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
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { getMyBank, saveMyBank } from '@/api/channel'
import { CreditCardOutlined, UserOutlined, SaveOutlined } from '@ant-design/icons-vue'

const loading = ref(false)
const saving = ref(false)

const form = reactive({
  bank_name: '',
  bank_account: '',
  account_holder: ''
})

const bankList = [
  '中国工商银行', '中国建设银行', '中国农业银行', '中国银行',
  '招商银行', '交通银行', '浦发银行', '兴业银行',
  '民生银行', '平安银行', '光大银行', '华夏银行',
  '广发银行', '邮政储蓄银行', '农村商业银行'
]

const filterBank = (input: string, option: any) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

onMounted(async () => {
  loading.value = true
  try {
    const bank = await getMyBank()
    if (bank) {
      form.bank_name = bank.bank_name
      form.bank_account = bank.bank_account
      form.account_holder = bank.account_holder
    }
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
})

const handleSave = async () => {
  if (!form.bank_name || !form.bank_account || !form.account_holder) {
    message.error('请填写完整')
    return
  }
  saving.value = true
  try {
    await saveMyBank(form)
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

/* ---- Form Styles ---- */
.bank-form :deep(.ant-form-item-label > label) {
  font-weight: 500;
  color: var(--color-text-primary);
}

.bank-form :deep(.ant-input-affix-wrapper),
.bank-form :deep(.ant-input),
.bank-form :deep(.ant-select-selector) {
  border-radius: var(--radius-md);
}

.submit-btn {
  height: 48px;
  font-size: var(--text-base);
  font-weight: 600;
  border-radius: var(--radius-md);
  margin-top: var(--space-4);
}
</style>
