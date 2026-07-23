<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <h1>我的佣金</h1>

        <!-- 汇总卡片 -->
        <a-row :gutter="16" style="margin-bottom: 24px">
          <a-col :xs="24" :sm="8">
            <a-card hoverable>
              <a-statistic
                title="冻结中"
                :value="Number(summary.total_frozen)"
                :precision="2"
                prefix="¥"
                :value-style="{ color: '#f59e0b' }"
              />
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="8">
            <a-card hoverable>
              <a-statistic
                title="可提现"
                :value="Number(summary.total_available)"
                :precision="2"
                prefix="¥"
                :value-style="{ color: '#10b981' }"
              />
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="8">
            <a-card hoverable>
              <a-statistic
                title="已提现"
                :value="Number(summary.total_withdrawn)"
                :precision="2"
                prefix="¥"
              />
            </a-card>
          </a-col>
        </a-row>

        <!-- 标签页 -->
        <a-card>
          <a-tabs v-model:activeKey="activeTab" @change="onTabChange">
            <a-tab-pane key="frozen" tab="冻结中">
              <a-spin v-if="loading" />
              <a-table
                v-if="!loading"
                :columns="withdrawnAndFrozeColumns"
                :data-source="list"
                :pagination="{ pageSize: 10, current: currentPage, total }"
                row-key="id"
                @change="onTableChange"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'level'">
                    <a-tag :color="record.level === 1 ? 'blue' : 'purple'">
                      {{ record.level === 1 ? 'L1 直接' : 'L2 二级' }}
                    </a-tag>
                  </template>
                  <template v-else-if="column.key === 'amount'">
                    <span style="color: #f59e0b; font-weight: 600">¥{{ record.amount }}</span>
                  </template>
                  <template v-else-if="column.key === 'created_at'">
                    {{ formatDate(record.created_at) }}
                  </template>
                </template>
              </a-table>
              <div v-if="!loading && list.length === 0" class="empty-state">
                <div class="icon">💰</div>
                <p>暂无冻结佣金</p>
              </div>
            </a-tab-pane>

            <a-tab-pane key="available" tab="可提现">
              <a-spin v-if="loading" />
              <a-table
                v-if="!loading"
                :columns="columns"
                :data-source="list"
                :pagination="{ pageSize: 10, current: currentPage, total }"
                row-key="id"
                @change="onTableChange"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'level'">
                    <a-tag :color="record.level === 1 ? 'blue' : 'purple'">
                      {{ record.level === 1 ? 'L1 直接' : 'L2 二级' }}
                    </a-tag>
                  </template>
                  <template v-else-if="column.key === 'amount'">
                    <span style="color: #10b981; font-weight: 600">¥{{ record.amount }}</span>
                  </template>
                  <template v-else-if="column.key === 'balance'">
                    <span style="color: #10b981; font-weight: 600">¥{{ record.balance }}</span>
                  </template>
                  <template v-else-if="column.key === 'created_at'">
                    {{ formatDate(record.created_at) }}
                  </template>
                </template>
              </a-table>
              <div v-if="!loading && list.length === 0" class="empty-state">
                <div class="icon">💵</div>
                <p>暂无可提现佣金</p>
              </div>
            </a-tab-pane>

            <a-tab-pane key="withdrawn" tab="已提现">
              <a-spin v-if="loading" />
              <a-table
                v-if="!loading"
                :columns="withdrawnAndFrozeColumns"
                :data-source="list"
                :pagination="{ pageSize: 10, current: currentPage, total }"
                row-key="id"
                @change="onTableChange"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'level'">
                    <a-tag :color="record.level === 1 ? 'blue' : 'purple'">
                      {{ record.level === 1 ? 'L1 直接' : 'L2 二级' }}
                    </a-tag>
                  </template>
                  <template v-else-if="column.key === 'amount'">
                    <span style="color: #94a3b8; font-weight: 600">¥{{ record.amount }}</span>
                  </template>
                  <template v-else-if="column.key === 'created_at'">
                    {{ formatDate(record.created_at) }}
                  </template>
                </template>
              </a-table>
              <div v-if="!loading && list.length === 0" class="empty-state">
                <div class="icon">🏦</div>
                <p>暂无已提现记录</p>
              </div>
            </a-tab-pane>
          </a-tabs>
        </a-card>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import type { TableProps } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { getMyCommissions, getCommissionSummary, type ChannelCommission } from '@/api/channel'
import { formatDate } from '@/utils/format'

const columns = [
  { title: '订单号', dataIndex: 'order_id', key: 'order_id', width: 100 },
  { title: '来源', key: 'level', width: 100 },
  { title: '佣金金额', key: 'amount', width: 120 },
  { title: '还可提现金额', key: 'balance', width: 120 },
  { title: '时间', key: 'created_at', width: 180 }
]

const withdrawnAndFrozeColumns = [
  { title: '订单号', dataIndex: 'order_id', key: 'order_id', width: 100 },
  { title: '来源', key: 'level', width: 100 },
  { title: '佣金金额', key: 'amount', width: 120 },
  { title: '时间', key: 'created_at', width: 180 }
]

const PAGE_SIZE = 10

const activeTab = ref('frozen')
const loading = ref(false)
const list = ref<ChannelCommission[]>([])
const total = ref(0)
const currentPage = ref(1)
const summary = ref({ total_frozen: '0.00', total_available: '0.00', total_withdrawn: '0.00' })

const fetchList = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * PAGE_SIZE
    const res = await getMyCommissions(activeTab.value, skip, PAGE_SIZE)
    list.value = res.data
    total.value = res.total
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const onTabChange = () => {
  currentPage.value = 1
  fetchList()
}

const onTableChange: TableProps['onChange'] = (pagination) => {
  currentPage.value = pagination.current || 1
  fetchList()
}

onMounted(async () => {
  try {
    const sumData = await getCommissionSummary()
    summary.value = sumData
  } catch (error: any) {
    message.error(error.message || '加载失败')
  }
  fetchList()
})
</script>

<style scoped>
.main-content {
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
  padding: 20px 0;
}

h1 {
  margin-bottom: 24px;
}

.empty-state {
  text-align: center;
  padding: 48px 20px;
}

.empty-state .icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-state p {
  color: #94a3b8;
  font-size: 14px;
}
</style>
