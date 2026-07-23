<template>
  <div style="max-width: 500px">
    <a-spin :spinning="loading">
      <a-form layout="vertical">
        <a-form-item label="L1 渠道商佣金比例">
          <a-input-number
            v-model:value="l1Value"
            :min="0"
            :max="100"
            :precision="2"
            style="width: 100%"
          />
          <div style="margin-top: 8px; color: #999">
            <a-slider v-model:value="l1Value" :min="0" :max="100" :step="0.1" />
            <span>{{ l1Value }}%</span>
          </div>
        </a-form-item>

        <a-form-item label="L2 渠道商佣金比例">
          <a-input-number
            v-model:value="l2Value"
            :min="0"
            :max="100"
            :precision="2"
            style="width: 100%"
          />
          <div style="margin-top: 8px; color: #999">
            <a-slider v-model:value="l2Value" :min="0" :max="100" :step="0.1" />
            <span>{{ l2Value }}%</span>
          </div>
        </a-form-item>

        <a-form-item>
          <a-button type="primary" @click="handleSave" :loading="saving">
            保存设置
          </a-button>
        </a-form-item>
      </a-form>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getChannelSetting, updateChannelSetting } from '../../api/channel'

const loading = ref(false)
const saving = ref(false)
const l1Value = ref(10)
const l2Value = ref(5)

onMounted(async () => {
  loading.value = true
  try {
    const data = await getChannelSetting()
    l1Value.value = parseFloat(data.l1_rate) * 100
    l2Value.value = parseFloat(data.l2_rate) * 100
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
})

const handleSave = async () => {
  saving.value = true
  try {
    await updateChannelSetting(
      (l1Value.value / 100).toFixed(4),
      (l2Value.value / 100).toFixed(4)
    )
    message.success('保存成功')
  } catch (error: any) {
    message.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>
