<template>
  <div class="login-page-bg">
    <div class="login-center">
      <div class="login-box">
        <h2>LOGIN</h2>
        <input type="text" placeholder="USER NAME" v-model="username" />
        <input type="password" placeholder="PASSWORD" v-model="password" />
        <button class="login-btn" @click="login">Log In</button>
        <div class="signup-section">
          <p class="signup-text">회원이 아니신가요?</p>
          <router-link to="/signup" class="signup-link">회원가입</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const password = ref('')
const router = useRouter()

async function login() {
  if (!username.value || !password.value) {
    alert('아이디와 비밀번호를 입력하세요.')
    return
  }

  try {
    const response = await axios.post('http://localhost:8000/accounts/login/', {
      username: username.value,
      password: password.value
    })

    // 토큰 저장
    localStorage.setItem('token', response.data.key)
    
    // 로그인 성공 후 메인 페이지로 이동
    router.push('/')
    
    // 페이지 새로고침하여 네비게이션 바 상태 업데이트
    window.location.reload()
  } catch (error) {
    if (error.response) {
      alert(error.response.data.non_field_errors?.[0] || '로그인에 실패했습니다.')
    } else {
      alert('서버에 연결할 수 없습니다.')
    }
  }
}
</script>

<style scoped>
.login-page-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f8fe;
}

.login-center {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

input {
  width: 100%;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #2a388f;
}

.login-btn {
  width: 100%;
  padding: 0.8rem;
  background: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 1rem;
}

.login-btn:hover {
  background: #1a287f;
}

.signup-section {
  text-align: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.signup-text {
  color: #666;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.signup-link {
  color: #2a388f;
  text-decoration: none;
  font-weight: 500;
}

.signup-link:hover {
  text-decoration: underline;
}
</style>