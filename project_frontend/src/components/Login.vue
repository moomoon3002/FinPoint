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
    
    // 로그인 성공 메시지
    alert('로그인 성공!')
    
    // 메인 페이지로 이동 (라우터의 name 속성 사용)
    router.push({ name: 'Main' })
  } catch (error) {
    if (error.response) {
      alert(error.response.data.non_field_errors?.[0] || '로그인에 실패했습니다.')
    } else {
      alert('서버에 연결할 수 없습니다.')
    }
  }
}
</script>

