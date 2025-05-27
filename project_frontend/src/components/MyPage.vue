<template>
  <div class="mypage-container">
    <h2>마이페이지</h2>
    <div class="profile-section" v-if="userData">
      <div class="profile-header">
        <div class="profile-image-section">
          <div class="profile-image-container">
            <img 
              :src="profileImageUrl" 
              alt="프로필 이미지" 
              class="profile-img"
            />
          </div>
          <button @click="triggerFileInput" class="image-edit-btn">
            프로필 사진 수정
          </button>
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

    <!-- 관심상품 섹션 -->
    <div class="favorites-section">
      <h3>관심상품</h3>
      <div v-if="favoriteProducts.length > 0" class="favorites-list">
        <div v-for="product in favoriteProducts" :key="product.id" class="favorite-item">
          <div class="product-info">
            <h4>{{ product.name }}</h4>
            <p class="bank-name">{{ product.bank }}</p>
            <p class="product-type">{{ product.type }}</p>
            <p class="interest-rate">기본 금리: {{ product.interestRate }}%</p>
            <p class="period">가입 기간: {{ product.period }}개월</p>
          </div>
          <div class="product-actions">
            <button @click="removeFavorite(product.id)" class="remove-btn">관심상품 해제</button>
            <button @click="showDetail(product)" class="detail-btn">상세보기</button>
          </div>
        </div>
      </div>
      <p v-else class="no-favorites">관심상품이 없습니다.</p>
    </div>

    <!-- 상세 정보 모달 -->
    <div v-if="selectedProduct" class="modal">
      <div class="modal-content">
        <h3>{{ selectedProduct.name }}</h3>
        <div class="detail-info">
          <div class="info-row">
            <label>은행명</label>
            <span>{{ selectedProduct.bank }}</span>
          </div>
          <div class="info-row">
            <label>상품 종류</label>
            <span>{{ selectedProduct.type }}</span>
          </div>
          <div class="info-row">
            <label>기본 금리</label>
            <span>{{ selectedProduct.interestRate }}%</span>
          </div>
          <div class="info-row">
            <label>가입 기간</label>
            <span>{{ selectedProduct.period }}개월</span>
          </div>
          <div class="info-row">
            <label>가입 방법</label>
            <span>{{ selectedProduct.joinWay }}</span>
          </div>
          <div class="info-row">
            <label>우대 조건</label>
            <span>{{ selectedProduct.specialCondition || '없음' }}</span>
          </div>
          <div class="info-row">
            <label>가입 제한</label>
            <span>{{ selectedProduct.joinLimit || '제한없음' }}</span>
          </div>
        </div>
        <button @click="selectedProduct = null" class="close-btn">닫기</button>
      </div>
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
const favoriteProducts = ref([])
const selectedProduct = ref(null)

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
    console.error('Error details:', error.response?.data || error.message)
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

// 관심상품 목록 가져오기
const fetchFavorites = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/deposits/favorites/', {
      headers: {
        Authorization: `Token ${token}`
      }
    })
    // 응답 데이터 구조에 맞게 변환
    favoriteProducts.value = response.data.map(item => ({
      id: item.deposit.deposit_ID,
      name: item.deposit.fin_prdt_nm,
      bank: item.deposit.kor_co_nm,
      type: item.deposit.product_type,
      interestRate: Math.max(...(item.deposit.options?.map(opt => opt.intr_rate) || [0])),
      period: parseInt(item.deposit.options?.[0]?.save_trm) || 0,
      joinWay: item.deposit.join_way,
      specialCondition: item.deposit.spcl_cnd,
      joinLimit: item.deposit.join_deny
    }))
  } catch (error) {
    console.error('Failed to fetch favorites:', error)
  }
}

// 관심상품 해제
const removeFavorite = async (productId) => {
  try {
    const token = localStorage.getItem('token')
    await axios.post(`http://localhost:8000/deposits/favorites/remove/${productId}/`, {}, {
      headers: {
        Authorization: `Token ${token}`
      }
    })
    // 목록에서 제거
    favoriteProducts.value = favoriteProducts.value.filter(p => p.id !== productId)
    alert('관심상품이 해제되었습니다.')
  } catch (error) {
    console.error('Failed to remove favorite:', error)
    alert('관심상품 해제 중 오류가 발생했습니다.')
  }
}

// 상세 정보 표시
const showDetail = (product) => {
  selectedProduct.value = product
}

onMounted(() => {
  fetchUserData()
  fetchFavorites()
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
  align-items: flex-start;
  margin-bottom: 2rem;
}

.profile-image-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-right: 2rem;
}

.profile-image-container {
  width: 120px;
  height: 120px;
}

.profile-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #eee;
}

.image-edit-btn {
  background-color: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 0.5rem;
}

.image-edit-btn:hover {
  background-color: #1a287f;
}

.profile-info {
  flex: 1;
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

.favorites-section {
  margin-top: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.favorites-list {
  display: grid;
  gap: 1rem;
}

.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #eee;
}

.product-info h4 {
  margin: 0 0 0.5rem 0;
  color: #2a388f;
}

.product-info p {
  margin: 0.25rem 0;
  color: #666;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
}

.remove-btn,
.detail-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.remove-btn {
  background-color: #ff6b6b;
  color: white;
}

.detail-btn {
  background-color: #2a388f;
  color: white;
}

.remove-btn:hover {
  background-color: #ff5252;
}

.detail-btn:hover {
  background-color: #1a287f;
}

.no-favorites {
  text-align: center;
  color: #666;
  padding: 2rem;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
}

.detail-info {
  margin: 1.5rem 0;
}

.info-row {
  display: flex;
  margin-bottom: 1rem;
}

.info-row label {
  width: 120px;
  font-weight: bold;
  color: #666;
}

.close-btn {
  width: 100%;
  padding: 0.8rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-btn:hover {
  background-color: #5a6268;
}
</style> 