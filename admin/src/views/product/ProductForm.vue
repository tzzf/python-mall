<template>
  <a-modal
    :open="visible"
    :title="isEdit ? '编辑商品' : '创建商品'"
    @ok="handleSubmit"
    @cancel="handleClose"
    :confirm-loading="loading"
  >
    <a-form
      :model="formState"
      :label-col="{ span: 6 }"
      layout="vertical"
    >
      <a-form-item label="名称" required>
        <a-input v-model:value="formState.name" placeholder="请输入商品名称" />
      </a-form-item>
      <a-form-item label="描述">
        <a-textarea v-model:value="formState.description" placeholder="请输入商品描述" :rows="3" />
      </a-form-item>
      <a-form-item label="价格" required>
        <a-input-number v-model:value="formState.price" :min="0" :precision="2" style="width: 100%" />
      </a-form-item>
      <a-form-item label="库存" required>
        <a-input-number v-model:value="formState.stock" :min="0" style="width: 100%" />
      </a-form-item>
      <a-form-item label="分类">
        <a-select v-model:value="formState.category_id" placeholder="请选择分类" allow-clear>
          <a-select-option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="状态">
        <a-switch v-model:checked="formState.is_active" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import type { ProductResponse, CategoryResponse } from '../../types'
import { createProduct, updateProduct, getCategories } from '../../api'

const props = defineProps<{
  visible: boolean
  product: ProductResponse | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

const loading = ref(false)
const categories = ref<CategoryResponse[]>([])

const formState = reactive({
  name: '',
  description: '',
  price: 0,
  stock: 0,
  is_active: true,
  category_id: null as number | null
})

const isEdit = computed(() => !!props.product)

watch(() => props.visible, async (val) => {
  if (val) {
    await loadCategories()
    if (props.product) {
      formState.name = props.product.name
      formState.description = props.product.description || ''
      formState.price = parseFloat(props.product.price)
      formState.stock = props.product.stock
      formState.is_active = props.product.is_active
      formState.category_id = props.product.category_id
    } else {
      formState.name = ''
      formState.description = ''
      formState.price = 0
      formState.stock = 0
      formState.is_active = true
      formState.category_id = null
    }
  }
})

const loadCategories = async () => {
  try {
    categories.value = await getCategories() as unknown as CategoryResponse[]
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

const handleSubmit = async () => {
  if (!formState.name) {
    message.error('请输入商品名称')
    return
  }
  loading.value = true
  try {
    const data = {
      name: formState.name,
      description: formState.description || null,
      price: formState.price.toString(),
      stock: formState.stock,
      is_active: formState.is_active,
      category_id: formState.category_id
    }
    if (isEdit.value && props.product) {
      await updateProduct(props.product.id, data)
      message.success('更新成功')
    } else {
      await createProduct(data)
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
