<template>
  <div class="empty-state">
    <a-empty :image="emptyImage">
      <template #description>
        <p class="empty-title">{{ title }}</p>
        <p v-if="description" class="empty-description">{{ description }}</p>
      </template>
      <a-button v-if="actionText" type="primary" @click="handleAction">
        {{ actionText }}
      </a-button>
    </a-empty>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Empty } from 'ant-design-vue'

interface Props {
  entityName?: string
  title?: string
  description?: string
  actionText?: string
}

interface Emits {
  (e: 'action'): void
}

const props = withDefaults(defineProps<Props>(), {
  entityName: '数据',
  title: '',
  description: '',
  actionText: ''
})

const emit = defineEmits<Emits>()

const title = computed(() => props.title || `暂无${props.entityName}数据`)
const description = computed(() => props.description || `还没有添加任何${props.entityName}`)

// Use simple SVG placeholder instead of built-in Empty.PRESENTED_IMAGE_SIMPLE
// to avoid default Ant Design illustration
const emptyImage = computed(() => Empty.PRESENTED_IMAGE_SIMPLE)

function handleAction() {
  emit('action')
}
</script>

<style scoped>
.empty-state {
  padding: 48px 0;
  text-align: center;
}

.empty-title {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 16px;
}
</style>
