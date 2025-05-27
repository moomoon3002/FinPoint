import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '../components/Main.vue'
import Login from '../components/Login.vue'
import SignUp from '../components/signup.vue'
import MyPage from '../components/MyPage.vue'
import DepositCompare from '../components/depositcompare.vue'
import SpotCompare from '../components/SpotCompare.vue'
import StockVoiceAnalysis from '../components/StockVoiceAnalysis.vue'
import Board from '../components/Board.vue'
import BoardDetail from '../components/BoardDetail.vue'
import BoardWrite from '../components/BoardWrite.vue'
import BoardEdit from '../components/BoardEdit.vue'
import BankFinder from '../components/BankFinder.vue'
import Calendar from '../components/Calendar.vue'

const routes = [
  { path: '/', name: 'Main', component: MainPage },
  { path: '/login', component: Login },
  { path: '/signup', component: SignUp },
  { path: '/mypage', component: MyPage },
  { path: '/deposit', name: 'Deposit', component: DepositCompare },
  { path: '/spot', name: 'Spot', component: SpotCompare },
  { path: '/stock-voice', name: 'StockVoice', component: StockVoiceAnalysis },
  { path: '/bank-finder', name: 'BankFinder', component: BankFinder },
  { path: '/board', name: 'Board', component: Board },
  { path: '/board/:id', name: 'BoardDetail', component: BoardDetail },
  { path: '/board/write', name: 'BoardWrite', component: BoardWrite },
  { path: '/board/edit/:id', name: 'BoardEdit', component: BoardEdit },
  { path: '/calendar', name: 'Calendar', component: Calendar }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 로그인이 필요한 페이지에 대한 네비게이션 가드
router.beforeEach((to, from, next) => {
  const publicPages = ['/', '/login', '/signup', '/deposit', '/spot', '/stock-voice', '/bank-finder', '/board']
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
