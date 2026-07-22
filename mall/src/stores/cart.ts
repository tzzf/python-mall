import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCart, addCartItem as apiAddItem, updateCartItem as apiUpdateItem, removeCartItem as apiRemoveItem, clearCart as apiClearCart } from '@/api'
import type { CartItemResponse } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItemResponse[]>([])
  const loading = ref(false)

  const totalCount = computed(() => items.value.reduce((sum, item) => sum + item.quantity, 0))

  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => {
      const price = parseFloat(item.price || '0')
      return sum + price * item.quantity
    }, 0).toFixed(2)
  })

  const fetchCart = async () => {
    loading.value = true
    try {
      const response = await getCart() as unknown as { items: CartItemResponse[] }
      items.value = response.items || []
    } catch (error) {
      console.error('Failed to fetch cart:', error)
      items.value = []
    } finally {
      loading.value = false
    }
  }

  const addItem = async (productId: number, quantity: number = 1, image: string = '') => {
    const existingItem = items.value.find(item => item.product_id === productId)
    if (existingItem) {
      existingItem.quantity += quantity
    } else {
      items.value.push({
        image,
        product_id: productId,
        quantity,
        product_name: null,
        price: null
      })
    }
    try {
      await apiAddItem(productId, quantity)
      await fetchCart()
    } catch (error) {
      await fetchCart()
      throw error
    }
  }

  const updateItem = async (productId: number, quantity: number) => {
    const item = items.value.find(i => i.product_id === productId)
    if (item) {
      item.quantity = quantity
    }
    try {
      await apiUpdateItem(productId, quantity)
    } catch (error) {
      await fetchCart()
      throw error
    }
  }

  const removeItem = async (productId: number) => {
    const index = items.value.findIndex(i => i.product_id === productId)
    if (index > -1) {
      items.value.splice(index, 1)
    }
    try {
      await apiRemoveItem(productId)
    } catch (error) {
      await fetchCart()
      throw error
    }
  }

  const clearCartItems = async () => {
    items.value = []
    try {
      await apiClearCart()
    } catch (error) {
      await fetchCart()
      throw error
    }
  }

  return {
    items,
    loading,
    totalCount,
    totalPrice,
    fetchCart,
    addItem,
    updateItem,
    removeItem,
    clearCart: clearCartItems
  }
})
