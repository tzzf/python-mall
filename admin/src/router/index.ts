import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('../views/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/products'
        },
        {
          path: '/products',
          name: 'ProductList',
          component: () => import('../views/product/ProductList.vue')
        },
        {
          path: '/categories',
          name: 'CategoryList',
          component: () => import('../views/product/CategoryList.vue')
        },
        {
          path: '/orders',
          name: 'OrderList',
          component: () => import('../views/order/OrderList.vue')
        },
        {
          path: '/coupons',
          name: 'CouponList',
          component: () => import('../views/coupon/CouponList.vue')
        },
        {
          path: '/users',
          name: 'UserList',
          component: () => import('../views/user/UserList.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
