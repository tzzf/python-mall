<template>
  <a-modal
    :open="visible"
    :title="isEdit ? '编辑优惠券' : '创建优惠券'"
    @ok="handleSubmit"
    @cancel="handleClose"
    :confirm-loading="loading"
  >
    <a-form
      :model="formState"
      :label-col="{ span: 6 }"
      layout="vertical"
    >
      <a-form-item label="优惠券码" required>
        <a-input v-model:value="formState.code" placeholder="请输入优惠券码" />
      </a-form-item>
      <a-form-item label="名称" required>
        <a-input v-model:value="formState.name" placeholder="请输入优惠券名称" />
      </a-form-item>
      <a-form-item label="折扣类型" required>
        <a-select v-model:value="formState.discount_type" placeholder="请选择折扣类型">
          <a-select-option value="fixed">满减</a-select-option>
          <a-select-option value="percent">折扣</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="折扣值" required>
        <a-input-number
          v-model:value="formState.discount_value"
          :min="0"
          :precision="2"
          style="width: 100%"
        />
      </a-form-item>
      <a-form-item label="最低订单金额" required>
        <a-input-number
          v-model:value="formState.min_order_amount"
          :min="0"
          :precision="2"
          style="width: 100%"
        />
      </a-form-item>
      <a-form-item label="最高折扣金额">
        <a-input-number
          v-model:value="formState.max_discount_amount"
          :min="0"
          :precision="2"
          style="width: 100%"
          placeholder="不限制则留空"
        />
      </a-form-item>
      <a-form-item label="发放数量" required v-if="!isEdit">
        <a-input-number
          v-model:value="formState.total_count"
          :min="1"
          style="width: 100%"
        />
      </a-form-item>
      <a-form-item label="开始时间" required>
        <a-date-picker
          v-model:value="formState.start_time"
          show-time
          format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
        />
      </a-form-item>
      <a-form-item label="结束时间" required>
        <a-date-picker
          v-model:value="formState.end_time"
          show-time
          format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import type { CouponInfo } from '../../types'
import { createCoupon, updateCoupon } from '../../api'

const props = defineProps<{
  visible: boolean
  coupon: CouponInfo | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

const loading = ref(false)

const formState = reactive({
  code: '',
  name: '',
  discount_type: 'fixed' as 'fixed' | 'percent',
  discount_value: 0,
  min_order_amount: 0,
  max_discount_amount: null as number | null,
  total_count: 1,
  start_time: null as dayjs.Dayjs | null,
  end_time: null as dayjs.Dayjs | null
})

const isEdit = computed(() => !!props.coupon)

watch(() => props.visible, (val) => {
  if (val) {
    if (props.coupon) {
      formState.code = props.coupon.code
      formState.name = props.coupon.name
      formState.discount_type = props.coupon.discount_type as 'fixed' | 'percent'
      formState.discount_value = parseFloat(props.coupon.discount_value)
      formState.min_order_amount = parseFloat(props.coupon.min_order_amount)
      formState.max_discount_amount = props.coupon.max_discount_amount ? parseFloat(props.coupon.max_discount_amount) : null
      formState.total_count = props.coupon.remain_count
      formState.start_time = dayjs(props.coupon.start_time)
      formState.end_time = dayjs(props.coupon.end_time)
    } else {
      formState.code = ''
      formState.name = ''
      formState.discount_type = 'fixed'
      formState.discount_value = 0
      formState.min_order_amount = 0
      formState.max_discount_amount = null
      formState.total_count = 1
      formState.start_time = null
      formState.end_time = null
    }
  }
})

const handleSubmit = async () => {
  if (!formState.code || !formState.name) {
    message.error('请填写完整信息')
    return
  }
  if (!formState.start_time || !formState.end_time) {
    message.error('请选择时间范围')
    return
  }
  loading.value = true
  try {
    const data = {
      code: formState.code,
      name: formState.name,
      discount_type: formState.discount_type,
      discount_value: formState.discount_value.toString(),
      min_order_amount: formState.min_order_amount.toString(),
      max_discount_amount: formState.max_discount_amount?.toString() || null,
      remain_count: formState.total_count,
      total_count: formState.total_count,
      start_time: formState.start_time.format('YYYY-MM-DDTHH:mm:ss'),
      end_time: formState.end_time.format('YYYY-MM-DDTHH:mm:ss')
    }
    if (isEdit.value && props.coupon) {
      await updateCoupon(props.coupon.id, {
        ...data,
        remain_count: undefined
      })
      message.success('更新成功')
    } else {
      await createCoupon(data)
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
