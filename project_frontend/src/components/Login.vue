<template>
  <div class="login-page-bg">
    <div class="login-center">
      <div class="login-box">
        <h2>LOGIN</h2>
        <input type="text" placeholder="USER NAME" v-model="username" />
        <input type="password" placeholder="PASSWORD" v-model="password" />
        <button class="login-btn" @click="login">Log In</button>
        <a href="#" class="join">회원가입</a>
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