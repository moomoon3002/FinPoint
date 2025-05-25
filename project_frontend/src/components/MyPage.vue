<template>
  <div class="mypage-container">
    <h2>마이페이지</h2>
    <div class="profile-section" v-if="userData">
      <div class="profile-header">
        <div class="profile-image-container">
          <img 
            :src="profileImageUrl" 
            alt="프로필 이미지" 
            class="profile-img"
            @click="triggerFileInput"
          />
          <div class="image-overlay">
            <span>클릭하여 변경</span>
          </div>
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleImageChange" 
            accept="image/*" 
            style="display: none"
          />
        </div>
        <div class="profile-info">
          <h3>{{ userData.nickname }}</h3>
          <p>{{ userData.email }}</p>
        </div>
      </div>
      
      <div class="profile-details">
        <div class="info-group">
          <label>사용자 이름</label>
          <p>{{ userData.username }}</p>
        </div>
        <div class="info-group">
          <label>나이</label>
          <p>{{ userData.age }}세</p>
        </div>
        <div class="info-group">
          <label>연봉</label>
          <p>{{ userData.salary ? userData.salary.toLocaleString() + '원' : '미입력' }}</p>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="showEditForm = true" class="edit-btn">프로필 수정</button>
      </div>
    </div>

    <!-- 프로필 수정 폼 -->
    <div v-if="showEditForm" class="edit-form">
      <h3>프로필 수정</h3>
      <form @submit.prevent="updateProfile">
        <div class="form-group">
          <label>닉네임</label>
          <input type="text" v-model="editForm.nickname" required>
        </div>
        <div class="form-group">
          <label>나이</label>
          <input type="number" v-model="editForm.age" required>
        </div>
        <div class="form-group">
          <label>연봉</label>
          <input type="number" v-model="editForm.salary">
        </div>
        <div class="form-buttons">
          <button type="submit" class="save-btn">저장</button>
          <button type="button" @click="showEditForm = false" class="cancel-btn">취소</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const userData = ref(null)
const showEditForm = ref(false)
const fileInput = ref(null)
const editForm = ref({
  nickname: '',
  age: 0,
  salary: 0
})

const profileImageUrl = computed(() => {
  if (userData.value?.profile_image) {
    if (!userData.value.profile_image.startsWith('http')) {
      return `http://localhost:8000${userData.value.profile_image}`
    }
    return userData.value.profile_image
  }
  return '/default-profile.png'
})

// 파일 입력 트리거
const triggerFileInput = () => {
  fileInput.value.click()
}

// 이미지 변경 처리
const handleImageChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    alert('파일 크기는 5MB를 초과할 수 없습니다.')
    return
  }

  if (!file.type.startsWith('image/')) {
    alert('이미지 파일만 업로드할 수 있습니다.')
    return
  }

  const formData = new FormData()
  formData.append('profile_image', file)

  try {
    const token = localStorage.getItem('token')
    await axios.patch('http://localhost:8000/accounts/user/', formData, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })
    await fetchUserData()
    alert('프로필 이미지가 업데이트되었습니다.')
  } catch (error) {
    console.error('Failed to update profile image:', error)
    alert('프로필 이미지 업데이트에 실패했습니다.')
  }
}

// 사용자 정보 가져오기
const fetchUserData = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/accounts/user/', {
      headers: {
        Authorization: `Token ${token}`
      }
    })
    userData.value = response.data
    // 수정 폼 초기값 설정
    editForm.value = {
      nickname: response.data.nickname,
      age: response.data.age,
      salary: response.data.salary
    }
  } catch (error) {
    console.error('Failed to fetch user data:', error)
  }
}

// 프로필 업데이트
const updateProfile = async () => {
  try {
    const token = localStorage.getItem('token')
    await axios.patch('http://localhost:8000/accounts/user/', editForm.value, {
      headers: {
        Authorization: `Token ${token}`
      }
    })
    await fetchUserData()
    showEditForm.value = false
    alert('프로필이 업데이트되었습니다.')
  } catch (error) {
    console.error('Failed to update profile:', error)
    alert('프로필 업데이트에 실패했습니다.')
  }
}

onMounted(() => {
  fetchUserData()
})
</script>

<style scoped>
.mypage-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-section {
  margin-top: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}

.profile-image-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin-right: 2rem;
  cursor: pointer;
}

.profile-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-overlay span {
  color: white;
  font-size: 0.8rem;
  text-align: center;
}

.profile-image-container:hover .image-overlay {
  opacity: 1;
}

.profile-info h3 {
  margin: 0;
  font-size: 1.5rem;
}

.profile-info p {
  margin: 0.5rem 0;
  color: #666;
}

.profile-details {
  margin: 2rem 0;
}

.info-group {
  margin-bottom: 1rem;
}

.info-group label {
  display: block;
  color: #666;
  margin-bottom: 0.5rem;
}

.info-group p {
  margin: 0;
  font-size: 1.1rem;
}

.action-buttons {
  margin-top: 2rem;
}

.edit-btn {
  padding: 0.5rem 1.5rem;
  background-color: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.edit-btn:hover {
  background-color: #1a287f;
}

.edit-form {
  margin-top: 2rem;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-buttons {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
}

.save-btn, .cancel-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background-color: #2a388f;
  color: white;
}

.save-btn:hover {
  background-color: #1a287f;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}

.cancel-btn:hover {
  background-color: #da190b;
}
</style> 