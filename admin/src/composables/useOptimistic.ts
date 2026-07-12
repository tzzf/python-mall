import { ref, computed, type Ref, type ComputedRef } from 'vue'

export interface OptimisticOptions<T extends { id: number }> {
  initialData?: T[]
}

export interface OptimisticUpdateResult<T extends { id: number }> {
  isPending: ComputedRef<boolean>
  optimisticUpdate: (
    id: number,
    updateFn: (item: T) => T,
    serverFn: () => Promise<void>
  ) => Promise<void>
  optimisticRemove: (
    id: number,
    serverFn: () => Promise<void>
  ) => Promise<void>
  isItemPending: (id: number) => boolean
}

export function useOptimistic<T extends { id: number }>(
  options: OptimisticOptions<T> = {}
): OptimisticUpdateResult<T> {
  const { initialData = [] } = options

  const data = ref<T[]>([...initialData]) as Ref<T[]>
  const pendingIds = ref(new Set<number>())

  function isItemPending(id: number): boolean {
    return pendingIds.value.has(id)
  }

  async function optimisticUpdate(
    id: number,
    updateFn: (item: T) => T,
    serverFn: () => Promise<void>
  ): Promise<void> {
    const previousData = [...data.value]
    pendingIds.value.add(id)

    try {
      data.value = data.value.map(item =>
        item.id === id ? updateFn(item) : item
      )

      await serverFn()
    } catch (error) {
      data.value = previousData
      throw error
    } finally {
      pendingIds.value.delete(id)
    }
  }

  async function optimisticRemove(
    id: number,
    serverFn: () => Promise<void>
  ): Promise<void> {
    const previousData = [...data.value]
    pendingIds.value.add(id)

    try {
      data.value = data.value.filter(item => item.id !== id)
      await serverFn()
    } catch (error) {
      data.value = previousData
      throw error
    } finally {
      pendingIds.value.delete(id)
    }
  }

  const isPending = computed(() => pendingIds.value.size > 0)

  return {
    isPending,
    optimisticUpdate,
    optimisticRemove,
    isItemPending
  }
}
