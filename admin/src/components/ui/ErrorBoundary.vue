<template>
  <div class="error-boundary">
    <a-result
      v-if="error"
      status="error"
      :title="errorTitle"
    >
      <template #subTitle>
        <span class="error-message">{{ errorMessage }}</span>
      </template>
      <template #extra>
        <a-space>
          <a-button @click="handleRetry">
            重试
          </a-button>
          <a-button type="primary" @click="handleGoBack">
            返回列表
          </a-button>
        </a-space>
      </template>
    </a-result>
    <slot v-else />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  error?: Error | null
  title?: string
}

interface Emits {
  (e: 'retry'): void
  (e: 'goBack'): void
}

const props = withDefaults(defineProps<Props>(), {
  error: null,
  title: '加载失败'
})

const emit = defineEmits<Emits>()

const errorTitle = computed(() => props.title)
const errorMessage = computed(() => props.error?.message || '数据加载失败，请稍后重试')

function handleRetry() {
  emit('retry')
}

function handleGoBack() {
  emit('goBack')
}
</script>

<style scoped>
.error-boundary {
  width: 100%;
}

.error-message {
  color: rgba(0, 0, 0, 0.45);
}
</style>
