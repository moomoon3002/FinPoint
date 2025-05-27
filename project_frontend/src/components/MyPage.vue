<template>
  <div class="mypage-container">
    <h2>마이페이지</h2>
    <div class="profile-section" v-if="userData">
      <div class="profile-left">
        <div class="profile-image-container">
          <img :src="profileImageUrl" alt="프로필 이미지" class="profile-img-large" />
        </div>
      </div>
      <div class="profile-right">
        <div class="profile-nickname">{{ userData.nickname }}</div>
        <div class="profile-info-list">
          <div class="info-row"><label>이메일</label><span>{{ userData.email }}</span></div>
          <div class="info-row"><label>이름</label><span>{{ userData.username }}</span></div>
          <div class="info-row"><label>나이</label><span>{{ userData.age }}세</span></div>
          <div class="info-row"><label>연봉</label><span>{{ userData.salary ? userData.salary.toLocaleString() + '원' : '미입력' }}</span></div>
        </div>
        <div class="profile-actions">
          <button @click="openEditModal" class="edit-btn">프로필/사진 수정</button>
        </div>
      </div>
    </div>

    <!-- 프로필/사진 통합 수정 모달 -->
    <div v-if="showEditModal" class="modal-bg" @click.self="showEditModal = false">
      <div class="modal-box">
        <h3 class="modal-title">프로필 수정</h3>
        <form @submit.prevent="updateProfile">
          <div class="profile-edit-img-section">
            <img :src="editPreviewImageUrl" alt="프로필 미리보기" class="profile-img-large" />
            <input type="file" @change="handleEditImageChange" accept="image/*" />
          </div>
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
          <div class="modal-btns">
            <button type="submit" class="modal-btn main">저장</button>
            <button type="button" @click="showEditModal = false" class="modal-btn">취소</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 관심상품 섹션 -->
    <div class="favorites-section">
      <h3>관심상품</h3>
      <div v-if="favoriteProducts.length > 0" class="favorites-list">
        <div v-for="product in favoriteProducts" :key="product.id" class="favorite-item">
          <div class="product-info">
            <div class="title-row">
              <h4>{{ product.name }}</h4>
              <div class="button-group">
                <button @click="showDetail(product)" class="detail-btn">
                  <i class="fas fa-search"></i>
                </button>
                <button @click="removeFavorite(product.id)" class="remove-btn">
                  <i class="fas fa-heart"></i>
                </button>
              </div>
            </div>
            <p class="bank-name">{{ product.bank }}</p>
            <p class="product-type">{{ product.type }}</p>
            <p class="interest-rate">기본 금리: {{ product.interestRate }}%</p>
            <p class="period">가입 기간: {{ product.period }}개월</p>
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

    <div class="ai-recommend-section">
      <button @click="showPeriodModal = true" :disabled="aiLoading" class="ai-recommend-btn">
        AI 예적금 추천 받기
      </button>
      <div v-if="aiLoading" class="loading-spinner-wrapper">
        <div class="loading-spinner"></div>
        <div class="loading-text">추천 분석 중...</div>
      </div>
      <div v-if="aiRecommendResult" class="ai-recommend-result">
        <h4>AI 추천 상품</h4>
        <ul>
          <li v-for="(item, idx) in aiRecommendResult" :key="idx">
            {{ item.name }} ({{ item.bank }}) - {{ item.interestRate }}%, {{ item.period }}개월
          </li>
        </ul>
      </div>
    </div>

    <!-- 개월수 입력 모달 -->
    <div v-if="showPeriodModal" class="modal-bg" @click.self="showPeriodModal = false">
      <div class="modal-box">
        <h3 class="modal-title">가입 기간 선택</h3>
        <div class="period-input-section">
          <input 
            type="number" 
            v-model="selectedPeriod" 
            min="1" 
            max="60" 
            placeholder="가입 기간(개월)"
            class="period-input"
          >
          <p class="period-hint">1~60개월 사이의 기간을 입력해주세요</p>
        </div>
        <div class="modal-btns">
          <button @click="getAiRecommendation" class="modal-btn main" :disabled="!selectedPeriod">추천받기</button>
          <button @click="showPeriodModal = false" class="modal-btn">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const userData = ref(null)
const showEditModal = ref(false)
const editPreviewImageUrl = ref('')
const editImageFile = ref(null)
const editForm = ref({
  nickname: '',
  age: 0,
  salary: 0
})
const favoriteProducts = ref([])
const selectedProduct = ref(null)
const aiLoading = ref(false)
const aiRecommendResult = ref(null)
const showPeriodModal = ref(false)
const selectedPeriod = ref(null)

const profileImageUrl = computed(() => {
  if (userData.value?.profile_image) {
    if (!userData.value.profile_image.startsWith('http')) {
      return `http://localhost:8000${userData.value.profile_image}`
    }
    return userData.value.profile_image
  }
  return '/default-profile.png'
})

const openEditModal = () => {
  showEditModal.value = true
  editPreviewImageUrl.value = profileImageUrl.value
  editImageFile.value = null
}

const handleEditImageChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  editImageFile.value = file
  editPreviewImageUrl.value = URL.createObjectURL(file)
}

const updateProfile = async () => {
  try {
    const token = localStorage.getItem('token')
    // 1. 프로필 정보 업데이트
    await axios.patch('http://localhost:8000/accounts/user/', editForm.value, {
      headers: { Authorization: `Token ${token}` }
    })
    // 2. 이미지가 있으면 이미지도 업로드
    if (editImageFile.value) {
      const formData = new FormData()
      formData.append('profile_image', editImageFile.value)
      await axios.patch('http://localhost:8000/accounts/user/', formData, {
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      })
    }
    await fetchUserData()
    showEditModal.value = false
    alert('프로필이 업데이트되었습니다.')
  } catch (error) {
    alert('프로필 업데이트에 실패했습니다.')
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

const getAiRecommendation = async () => {
  if (!selectedPeriod.value) return
  
  aiLoading.value = true
  aiRecommendResult.value = null
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post('http://localhost:8000/deposits/ai-recommend/', {
      age: userData.value.age,
      salary: userData.value.salary,
      period: selectedPeriod.value
    }, {
      headers: { Authorization: `Token ${token}` }
    })
    aiRecommendResult.value = response.data.recommendations
    showPeriodModal.value = false
  } catch (e) {
    aiRecommendResult.value = [{ name: '추천 실패', bank: '', interestRate: '', period: '' }]
  } finally {
    aiLoading.value = false
  }
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
  display: flex;
  gap: 2.5rem;
  align-items: flex-start;
  margin-top: 2rem;
}

.profile-left {
  flex: 0 0 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-image-container {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 1rem;
}

.profile-img-large {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 3px solid #eee;
}

.profile-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

.profile-nickname {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
}

.profile-info-list {
  margin-bottom: 2.5rem;
}

.info-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 0.7rem;
  font-size: 1.1rem;
}

.info-row label {
  width: 70px;
  color: #666;
  font-weight: 500;
}

.profile-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  position: absolute;
  right: 0;
  bottom: 0;
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
  flex-direction: column;
  justify-content: space-between;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #eee;
  position: relative;
}

.product-info {
  position: relative;
  flex: 1;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.title-row h4 {
  margin: 0;
  color: #2a388f;
}

.button-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.detail-btn, .remove-btn {
  background: none;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.detail-btn {
  color: #333;
}

.remove-btn {
  color: #ff4d4d;
}

.detail-btn:hover {
  background: none;
  color: #333;
}

.remove-btn:hover {
  color: #ff0000;
}

.detail-btn i {
  font-size: 1.1rem;
}

.remove-btn i {
  font-size: 1.3rem;
}

.product-info p {
  margin: 0.25rem 0;
  color: #666;
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
  background-color: #E0E0E0;
  color: black;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-btn:hover {
  background-color: #5a6268;
}

.ai-recommend-section {
  margin-top: 2rem;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  text-align: center;
}
.ai-recommend-btn {
  padding: 0.7rem 2rem;
  background-color: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  cursor: pointer;
  margin-bottom: 1rem;
}
.ai-recommend-btn:disabled {
  background-color: #bdbdbd;
  cursor: not-allowed;
}
.ai-recommend-result {
  margin-top: 1rem;
  text-align: left;
}
.loading-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  width: 100%;
}
.loading-spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #2a388f;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
.loading-text {
  font-size: 1.1rem;
  color: #2a388f;
}
.modal-bg {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  padding: 2.5rem 2rem;
  min-width: 350px;
  max-width: 90vw;
  text-align: center;
}
.modal-title {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
}
.modal-btns {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: center;
}
.modal-btn {
  padding: 0.6rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  background: #e0e0e0;
  color: #333;
  cursor: pointer;
  transition: background 0.2s;
}
.modal-btn.main {
  background: #2a388f;
  color: #fff;
}
.modal-btn:hover {
  background: #bdbdbd;
}
.modal-btn.main:hover {
  background: #1a287f;
}
.profile-edit-img-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
}
.profile-edit-img-section img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #eee;
  margin-bottom: 0.7rem;
}
.period-input-section {
  margin: 1.5rem 0;
  text-align: center;
}

.period-input {
  width: 200px;
  padding: 0.8rem;
  font-size: 1.1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
}

.period-hint {
  margin-top: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.modal-btn:disabled {
  background-color: #bdbdbd;
  cursor: not-allowed;
}
</style> 