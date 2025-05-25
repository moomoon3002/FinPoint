<template>
  <div class="signup-page-bg">
    <!-- 회원가입 폼 -->
    <div class="signup-center">
      <div class="signup-box">
        <h2>SIGN UP</h2>
        <form @submit.prevent="signUp">
          <input 
            type="text" 
            placeholder="USER NAME (2자 이상)" 
            v-model="username"
            @input="validateUsername" 
          />
          <div v-if="usernameError" class="error-message">{{ usernameError }}</div>
          
          <div class="input-group">
            <input 
              type="text" 
              placeholder="NICKNAME" 
              v-model="nickname"
              @input="validateNickname"
            />
            <button 
              type="button" 
              class="check-btn" 
              @click="checkNickname"
              :disabled="!nickname || nicknameChecking"
            >
              {{ nicknameChecking ? '확인 중...' : '중복 확인' }}
            </button>
          </div>
          <div v-if="nicknameError" class="error-message">{{ nicknameError }}</div>
          <div v-if="nicknameAvailable" class="success-message">사용 가능한 닉네임입니다.</div>
          
          <input 
            type="email" 
            placeholder="EMAIL" 
            v-model="email"
            @input="validateEmail" 
          />
          <div v-if="emailError" class="error-message">{{ emailError }}</div>
          
          <input 
            type="password" 
            placeholder="PASSWORD (8자 이상)" 
            v-model="password1"
            @input="validatePassword" 
          />
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          
          <input 
            type="password" 
            placeholder="CONFIRM PASSWORD" 
            v-model="password2"
            @input="validatePasswordMatch" 
          />
          <div v-if="passwordMatchError" class="error-message">{{ passwordMatchError }}</div>
          
          <button class="signup-btn" type="submit" :disabled="!isFormValid">Sign Up</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const nickname = ref('')
const email = ref('')
const password1 = ref('')
const password2 = ref('')
const age = ref(0)
const router = useRouter()

// 닉네임 중복 확인 상태
const nicknameChecking = ref(false)
const nicknameAvailable = ref(false)

// 에러 메시지 상태
const usernameError = ref('')
const nicknameError = ref('')
const emailError = ref('')
const passwordError = ref('')
const passwordMatchError = ref('')

// 닉네임 중복 확인
async function checkNickname() {
  if (!nickname.value) {
    nicknameError.value = '닉네임을 입력해주세요.'
    return
  }

  nicknameChecking.value = true
  nicknameError.value = ''
  nicknameAvailable.value = false

  try {
    const response = await axios.post('http://localhost:8000/accounts/check-nickname/', {
      nickname: nickname.value
    })
    nicknameAvailable.value = true
    nicknameError.value = ''
  } catch (error) {
    if (error.response) {
      nicknameError.value = error.response.data.detail || '중복 확인 중 오류가 발생했습니다.'
      nicknameAvailable.value = false
    }
  } finally {
    nicknameChecking.value = false
  }
}

// 유효성 검사 함수들
const validateUsername = () => {
  if (username.value.length < 2) {
    usernameError.value = '사용자 이름은 2자 이상이어야 합니다.'
  } else {
    usernameError.value = ''
  }
}

const validateNickname = () => {
  if (!nickname.value) {
    nicknameError.value = '닉네임을 입력해주세요.'
  } else {
    nicknameError.value = ''
  }
  // 닉네임이 변경되면 중복 확인 상태 초기화
  nicknameAvailable.value = false
}

const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    emailError.value = '올바른 이메일 형식이 아닙니다.'
  } else {
    emailError.value = ''
  }
}

const validatePassword = () => {
  if (password1.value.length < 8) {
    passwordError.value = '비밀번호는 8자 이상이어야 합니다.'
  } else {
    passwordError.value = ''
  }
  validatePasswordMatch()
}

const validatePasswordMatch = () => {
  if (password1.value !== password2.value) {
    passwordMatchError.value = '비밀번호가 일치하지 않습니다.'
  } else {
    passwordMatchError.value = ''
  }
}

// 폼 전체 유효성 검사
const isFormValid = computed(() => {
  return username.value.length >= 2 &&
         nickname.value &&
         nicknameAvailable.value &&  // 닉네임 중복 확인 완료 여부 추가
         email.value &&
         password1.value.length >= 8 &&
         password1.value === password2.value &&
         !usernameError.value &&
         !nicknameError.value &&
         !emailError.value &&
         !passwordError.value &&
         !passwordMatchError.value
})

async function signUp() {
  if (!isFormValid.value) {
    alert('모든 필드를 올바르게 입력하고 닉네임 중복 확인을 완료해주세요.')
    return
  }

    try {
    const response = await axios.post('http://localhost:8000/accounts/registration/', {
        username: username.value,
      nickname: nickname.value,
        email: email.value,
      password1: password1.value,
      password2: password2.value,
      age: age.value,
      })

      alert('회원가입이 완료되었습니다!')
      router.push('/login')
    } catch (error) {
      if (error.response) {
      console.log('Error response:', error.response.data)
      const errorMessage = error.response.data.detail || 
                         Object.values(error.response.data).flat().join('\n')
      alert(`회원가입 실패: ${errorMessage}`)
      } else {
        alert('서버에 연결할 수 없습니다.')
      }
  }
}
</script>

<style scoped>
.input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.input-group input {
  flex: 1;
}

.check-btn {
  padding: 8px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  min-width: 80px;
}

.check-btn:hover {
  background-color: #45a049;
}

.check-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #ff4444;
  font-size: 0.8rem;
  margin-top: -10px;
  margin-bottom: 10px;
  text-align: left;
  padding-left: 10px;
}

.success-message {
  color: #4CAF50;
  font-size: 0.8rem;
  margin-top: -10px;
  margin-bottom: 10px;
  text-align: left;
  padding-left: 10px;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>

