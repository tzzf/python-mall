<template>
  <div class="table-skeleton">
    <!-- Table header -->
    <div class="skeleton-header">
      <div
        v-for="(col, index) in columns"
        :key="index"
        class="skeleton-cell header-cell"
        :style="{ width: col.width ? `${col.width}px` : 'auto', flex: col.width ? 'none' : 1 }"
      >
        <div class="skeleton-line short"></div>
      </div>
    </div>

    <!-- Table rows -->
    <div v-for="rowIndex in displayRows" :key="rowIndex" class="skeleton-row">
      <div
        v-for="(col, colIndex) in columns"
        :key="colIndex"
        class="skeleton-cell"
        :style="{ width: col.width ? `${col.width}px` : 'auto', flex: col.width ? 'none' : 1 }"
      >
        <div class="skeleton-line" :class="{ short: colIndex > 0 }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Column {
  title?: string
  dataIndex?: string
  key?: string
  width?: number | string
}

interface Props {
  columns: Column[]
  rows?: number
}

const props = withDefaults(defineProps<Props>(), {
  columns: () => [],
  rows: 5
})

const displayRows = computed(() => Math.min(Math.max(props.rows, 1), 10))
</script>

<style scoped>
.table-skeleton {
  background: #fff;
}

.skeleton-header {
  display: flex;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.skeleton-row {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

.skeleton-row:nth-child(odd) {
  animation-delay: 0.1s;
}

.skeleton-cell {
  padding: 0 8px;
}

.header-cell {
  opacity: 0.7;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e6e6e6 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-line.short {
  width: 60%;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
