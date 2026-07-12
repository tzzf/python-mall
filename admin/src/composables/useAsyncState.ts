import { ref, computed, type Ref, type ComputedRef } from 'vue'

export type AsyncStatus = 'idle' | 'loading' | 'success' | 'error' | 'empty'

export interface AsyncState<T> {
  status: Ref<AsyncStatus>
  data: Ref<T | null>
  error: Ref<Error | null>
  isLoading: ComputedRef<boolean>
  isError: ComputedRef<boolean>
  isEmpty: ComputedRef<boolean>
  isSuccess: ComputedRef<boolean>
  isIdle: ComputedRef<boolean>
  execute: (fn: () => Promise<T>) => Promise<T>
  reset: () => void
}

export function useAsyncState<T>(): AsyncState<T> {
  const status = ref<AsyncStatus>('idle') as Ref<AsyncStatus>
  const data = ref<T | null>(null) as Ref<T | null>
  const error = ref<Error | null>(null)

  const isLoading = computed(() => status.value === 'loading')
  const isError = computed(() => status.value === 'error')
  const isEmpty = computed(() => status.value === 'empty')
  const isSuccess = computed(() => status.value === 'success')
  const isIdle = computed(() => status.value === 'idle')

  async function execute(fn: () => Promise<T>): Promise<T> {
    status.value = 'loading'
    error.value = null

    try {
      const result = await fn()

      // Check if result is an empty array
      if (Array.isArray(result) && result.length === 0) {
        status.value = 'empty'
        data.value = null
      } else if (result === null || result === undefined) {
        status.value = 'empty'
        data.value = null
      } else {
        status.value = 'success'
        data.value = result
      }

      return result
    } catch (err) {
      status.value = 'error'
      error.value = err instanceof Error ? err : new Error(String(err))
      throw err
    }
  }

  function reset() {
    status.value = 'idle'
    data.value = null
    error.value = null
  }

  return {
    status,
    data,
    error,
    isLoading,
    isError,
    isEmpty,
    isSuccess,
    isIdle,
    execute,
    reset
  }
}
