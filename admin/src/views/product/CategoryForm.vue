<template>
  <a-modal
    :open="visible"
    :title="isEdit ? '编辑分类' : '新增分类'"
    @ok="handleSubmit"
    @cancel="handleClose"
    :confirm-loading="loading"
  >
    <a-form
      :model="formState"
      :label-col="{ span: 6 }"
      layout="vertical"
    >
      <a-form-item label="分类名称" required>
        <a-input v-model:value="formState.name" placeholder="请输入分类名称" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import type { CategoryResponse } from '../../types'
import { createCategory, updateCategory } from '../../api'

const props = defineProps<{
  visible: boolean
  category: CategoryResponse | null
  categories: CategoryResponse[]
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

const loading = ref(false)

const formState = reactive({
  name: '',
  parent_id: null as number | null
})

const isEdit = computed(() => !!props.category)

watch(() => props.visible, (val) => {
  if (val) {
    if (props.category) {
      formState.name = props.category.name
      formState.parent_id = props.category.parent_id
    } else {
      formState.name = ''
      formState.parent_id = null
    }
  }
})

const handleSubmit = async () => {
  if (!formState.name) {
    message.error('请输入分类名称')
    return
  }
  loading.value = true
  try {
    if (isEdit.value && props.category) {
      await updateCategory(props.category.id, {
        name: formState.name,
        parent_id: formState.parent_id
      })
      message.success('更新成功')
    } else {
      await createCategory({
        name: formState.name,
        parent_id: formState.parent_id
      })
      message.success('创建成功')
    }
    emit('success')
    handleClose()
  } catch (error: any) {
    message.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
}
</script>
