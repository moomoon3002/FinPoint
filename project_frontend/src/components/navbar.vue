<template>
  <!-- 첫 번째 줄: 로고만 -->
  <div class="navbar-row logo-row">
    <router-link to="/" class="logo-link">
      <div class="logo">FINPOINT</div>
    </router-link>
  </div>
  <!-- 두 번째 줄: 메뉴와 인증 -->
  <nav class="navbar-row menu-row">
    <ul class="nav-links">
      <li><router-link to="/deposit">예금비교</router-link></li>
      <li><router-link to="/spot">현물비교</router-link></li>
      <li><router-link to="/stock-voice">주식의 소리</router-link></li>
      <li><router-link to="/calendar">캘린더</router-link></li>
      <li><router-link to="/community">은행찾기</router-link></li>
      <li><router-link to="/board">게시판</router-link></li>
    </ul>
    <div class="auth-links">
      <!-- 로그인 상태일 때 -->
      <template v-if="isLoggedIn">
        <span class="welcome-text">{{ userNickname }}님 환영합니다</span>
        <router-link to="/mypage" class="nav-button">마이페이지</router-link>
        <button @click="handleLogout" class="nav-button logout-btn">로그아웃</button>
      </template>
      <!-- 로그아웃 상태일 때 -->
      <template v-else>
        <router-link to="/login" class="nav-button">로그인</router-link>
        <router-link to="/signup" class="nav-button">회원가입</router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const isLoggedIn = ref(false)
const userNickname = ref('')

// 로그인 상태 확인
const checkLoginStatus = async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const response = await axios.get('http://localhost:8000/accounts/user/', {
        headers: {
          Authorization: `Token ${token}`
        }
      })
      isLoggedIn.value = true
      userNickname.value = response.data.nickname
    } catch (error) {
      console.error('Failed to get user info:', error)
      handleLogout()
    }
  } else {
    isLoggedIn.value = false
    userNickname.value = ''
  }
}

// 로그아웃 처리
const handleLogout = async () => {
  try {
    const token = localStorage.getItem('token')
    if (token) {
      await axios.post('http://localhost:8000/accounts/logout/', null, {
        headers: {
          Authorization: `Token ${token}`
        }
      })
    }
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    localStorage.removeItem('token')
    isLoggedIn.value = false
    userNickname.value = ''
    router.push('/login')
  }
}

// 컴포넌트 마운트 시 로그인 상태 확인
onMounted(() => {
  checkLoginStatus()
})
</script>

<style scoped>
.navbar-row {
  padding: 1rem 2rem;
  background-color: white;
}

.logo-row {
  text-align: center;
  border-bottom: 1px solid #eee;
}

.menu-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.logo {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.logo-link {
  text-decoration: none;
}

.nav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 2rem;
}

.nav-links a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
}

.auth-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-text {
  color: #333;
  margin-right: 1rem;
}

.nav-button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
  background-color: #f0f0f0;
  transition: background-color 0.2s;
}

.nav-button:hover {
  background-color: #e0e0e0;
}

.logout-btn {
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.logout-btn:hover {
  background-color: #ff4444;
  color: white;
}
</style>
