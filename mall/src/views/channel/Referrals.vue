<template>
  <a-layout>
    <Header />
    <a-layout-content class="main-content">
      <div class="container">
        <h1>我的下级</h1>

        <a-card>
          <a-tabs v-model:activeKey="activeTab">
            <a-tab-pane key="l1" tab="直接下级">
              <a-spin v-if="loading" />
              <a-table
                v-if="!loading"
                :columns="columns"
                :data-source="l1List"
                :pagination="{ pageSize: 10 }"
                row-key="id"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'created_at'">
                    {{ formatDate(record.created_at) }}
                  </template>
                </template>
              </a-table>
              <div v-if="!loading && l1List.length === 0" class="empty-state">
                <div class="icon">👥</div>
                <p>暂无直接下级</p>
              </div>
            </a-tab-pane>

            <a-tab-pane key="l2" tab="二级下级">
              <a-spin v-if="loading" />
              <a-table
                v-if="!loading"
                :columns="columns"
                :data-source="l2List"
                :pagination="{ pageSize: 10 }"
                row-key="id"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'created_at'">
                    {{ formatDate(record.created_at) }}
                  </template>
                </template>
              </a-table>
              <div v-if="!loading && l2List.length === 0" class="empty-state">
                <div class="icon">👥</div>
                <p>暂无二级下级</p>
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
import Header from '@/components/Header.vue'
import { getMyReferrals, type ReferralUser } from '@/api/channel'
import { formatDate } from '@/utils/format'

const columns = [
  { title: '用户ID', dataIndex: 'id', key: 'id', width: 100 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '注册时间', key: 'created_at', width: 180 }
]

const activeTab = ref('l1')
const loading = ref(false)
const l1List = ref<ReferralUser[]>([])
const l2List = ref<ReferralUser[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const data = await getMyReferrals()
    l1List.value = data.l1_referrals || []
    l2List.value = data.l2_referrals || []
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
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
