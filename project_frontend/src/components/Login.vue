<template>
  <div class="login-page-bg">
    <div class="login-center">
      <div class="login-box">
        <h2>LOGIN</h2>
        <input type="text" placeholder="USER NAME" v-model="username" />
        <input type="password" placeholder="PASSWORD" v-model="password" />
        <button class="login-btn" @click="login">Log In</button>

        <!-- 아이디/비밀번호 찾기 버튼 -->
        <div class="find-section">
          <button class="find-link" @click="showFindIdModal = true">아이디 찾기</button>
          <span class="find-divider">/</span>
          <button class="find-link" @click="showFindPwModal = true">비밀번호 변경</button>
        </div>

        <div class="signup-section">
          <p class="signup-text">회원이 아니신가요?</p>
          <router-link to="/signup" class="signup-link">회원가입</router-link>
        </div>
      </div>
    </div>

    <!-- 아이디 찾기 모달 -->
    <div v-if="showFindIdModal" class="modal-overlay" @click.self="closeModalId">
      <div class="modal-content">
        <h3>아이디 찾기</h3>
        <input
          type="email"
          v-model="findIdEmail"
          placeholder="가입한 이메일 입력"
        />
        <button class="login-btn" @click="findId">아이디 찾기</button>
        <div v-if="findIdResult" class="findid-result">{{ findIdResult }}</div>
        <button class="modal-close-btn" @click="closeModalId">닫기</button>
      </div>
    </div>

    <!-- 비밀번호 변경 모달 -->
    <div v-if="showFindPwModal" class="modal-overlay" @click.self="closeModalPw">
      <div class="modal-content">
        <h3>비밀번호 변경</h3>
        <input
          type="email"
          v-model="findPwEmail"
          placeholder="가입한 이메일 입력"
        />
        <input
          type="password"
          v-model="newPassword"
          placeholder="새 비밀번호 입력"
        />
        <button class="login-btn" @click="changePassword">비밀번호 변경</button>
        <div v-if="findPwResult" class="findid-result">{{ findPwResult }}</div>
        <button class="modal-close-btn" @click="closeModalPw">닫기</button>
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

// 아이디 찾기 모달 관련
const showFindIdModal = ref(false)
const findIdEmail = ref('')
const findIdResult = ref('')

// 비밀번호 변경 모달 관련
const showFindPwModal = ref(false)
const findPwEmail = ref('')
const newPassword = ref('')
const findPwResult = ref('')

function closeModalId() {
  showFindIdModal.value = false
  findIdEmail.value = ''
  findIdResult.value = ''
}

function closeModalPw() {
  showFindPwModal.value = false
  findPwEmail.value = ''
  newPassword.value = ''
  findPwResult.value = ''
}

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
    localStorage.setItem('token', response.data.key)
    alert('로그인 성공!')
    router.push({ name: 'Main' })
  } catch (error) {
    if (error.response) {
      alert(error.response.data.non_field_errors?.[0] || '로그인에 실패했습니다.')
    } else {
      alert('서버에 연결할 수 없습니다.')
    }
  }
}

async function findId() {
  if (!findIdEmail.value) {
    findIdResult.value = '이메일을 입력하세요.'
    return
  }
  try {
    // 실제 API 주소와 응답 형식에 맞게 수정하세요!
    const response = await axios.post('http://localhost:8000/accounts/find-id/', {
      email: findIdEmail.value
    })
    // 예시: { username: "찾은아이디" }
    findIdResult.value = `아이디: ${response.data.username}`
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail) {
      findIdResult.value = error.response.data.detail
    } else {
      findIdResult.value = '아이디를 찾을 수 없습니다.'
    }
  }
}

async function changePassword() {
  if (!findPwEmail.value || !newPassword.value) {
    findPwResult.value = '이메일과 새 비밀번호를 모두 입력하세요.'
    return
  }
  try {
    // 실제 API 주소와 응답 형식에 맞게 수정하세요!
    const response = await axios.post('http://localhost:8000/accounts/change-password/', {
      email: findPwEmail.value,
      new_password: newPassword.value
    })
    // 예시: { detail: "비밀번호가 변경되었습니다." }
    findPwResult.value = response.data.detail || '비밀번호가 변경되었습니다.'
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail) {
      findPwResult.value = error.response.data.detail
    } else {
      findPwResult.value = '비밀번호 변경에 실패했습니다.'
    }
  }
}
</script>

<style scoped>
/* 기존 모달 스타일 그대로 사용 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  border-radius: 12px;
  padding: 32px 24px 20px 24px;
  min-width: 320px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.modal-content h3 {
  margin-bottom: 18px;
  color: #2a388c;
  font-weight: bold;
  font-size: 1.3rem;
}
.modal-content input {
  width: 100%;
  padding: 12px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  font-size: 1rem;
  margin-bottom: 14px;
  background: #fafbfc;
}
.findid-result {
  margin: 10px 0;
  color: #2a388c;
  font-weight: 500;
  text-align: center;
}
.modal-close-btn {
  margin-top: 8px;
  background: #eee;
  color: #333;
  border: none;
  border-radius: 18px;
  padding: 7px 20px;
  cursor: pointer;
  font-size: 0.95rem;
}
.modal-close-btn:hover {
  background: #ddd;
}
</style>
