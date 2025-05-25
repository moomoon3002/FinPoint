import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '../components/Main.vue'
import Login from '../components/Login.vue'
import SignUp from '../components/signup.vue'
import MyPage from '../components/MyPage.vue'
import DepositCompare from '../components/depositcompare.vue'

const routes = [
  { path: '/', name: 'Main', component: MainPage },
  { path: '/login', component: Login },
  { path: '/signup', component: SignUp },
  { path: '/mypage', component: MyPage },
  { path: '/deposit', name: 'Deposit', component: DepositCompare }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 로그인이 필요한 페이지에 대한 네비게이션 가드
router.beforeEach((to, from, next) => {
  const publicPages = ['/', '/login', '/signup', '/deposit']
  const authRequired = !publicPages.includes(to.path)
  const token = localStorage.getItem('token')

  if (authRequired && !token) {
    alert('로그인이 필요한 서비스입니다.')
    next('/login')
  } else {
    next()
  }
})

export default router
