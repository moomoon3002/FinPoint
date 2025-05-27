<template>
  <div class="deposit-compare-wrapper">
    <div class="deposit-compare-container">
      <h2 class="deposit-compare-title">금융상품 비교</h2>
      
      <!-- 상품 유형 탭 -->
      <div class="product-type-tabs">
        <button 
          :class="['tab-btn', { active: selectedType === 'deposit' }]"
          @click="selectedType = 'deposit'"
        >
          예금
        </button>
        <button 
          :class="['tab-btn', { active: selectedType === 'savings' }]"
          @click="selectedType = 'savings'"
        >
          적금
        </button>
      </div>

      <!-- 필터 영역 -->
      <div class="filter-section">
        <div class="filter-item">
          <select v-model="filters.bank" class="filter-select">
            <option value="">전체은행</option>
            <option v-for="bank in bankList" :key="bank" :value="bank">{{ bank }}</option>
          </select>
        </div>

        <div class="filter-item">
          <input 
            type="text" 
            v-model="filters.productName" 
            placeholder="상품명 검색" 
            class="filter-input"
          />
        </div>

        <div class="filter-item">
          <select v-model="filters.interestRate" class="filter-select">
            <option value="">전체이자율</option>
            <option value="2">2% 이상</option>
            <option value="3">3% 이상</option>
            <option value="4">4% 이상</option>
            <option value="5">5% 이상</option>
          </select>
        </div>

        <div class="filter-item">
          <select v-model="filters.period" class="filter-select">
            <option value="">전체기간</option>
            <option value="6">6개월</option>
            <option value="12">12개월</option>
            <option value="24">24개월</option>
            <option value="36">36개월</option>
          </select>
        </div>
      </div>

      <!-- 상품 목록 -->
      <div class="deposit-list">
        <div class="deposit-header">
          <span class="col bank">은행</span>
          <span class="col product">상품명</span>
          <span class="col interest">이자율</span>
          <span class="col period">개월수</span>
          <span class="col action">상세보기</span>
        </div>

        <div v-for="product in filteredProducts" :key="product.id" class="deposit-item">
          <div class="col bank">
            <strong>{{ product.bank }}</strong>
          </div>
          <div class="col product">{{ product.name }}</div>
          <div class="col interest">
            <strong>{{ product.interestRate }}%</strong><span class="sub-text">이자율</span>
          </div>
          <div class="col period">
            <spans style="font-size: medium; color: #666;">{{ product.period}}개월</spans>
          </div>
          <div class="col action">
            <button @click="showDetail(product)" class="detail-btn">자세히보기</button>
          </div>
        </div>

        <!-- 데이터가 없을 때 메시지 -->
        <div v-if="filteredProducts.length === 0" class="no-data">
          조건에 맞는 상품이 없습니다.
        </div>
      </div>
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
            <span>{{ selectedType === 'deposit' ? '예금' : '적금' }}</span>
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

const products = ref([])
const selectedProduct = ref(null)
const selectedType = ref('deposit') // 기본값은 예금

const filters = ref({
  bank: '',
  productName: '',
  interestRate: '',
  period: ''
})

// 은행 목록 계산
const bankList = computed(() => {
  return [...new Set(products.value.map(p => p.bank))]
})

// 필터링된 상품 목록
const filteredProducts = computed(() => {
  return products.value.filter(product => {
    // 상품 유형 필터
    const typeMatch = product.type === (selectedType.value === 'deposit' ? '예금' : '적금')
    
    // 기존 필터 조건
    const bankMatch = !filters.value.bank || product.bank === filters.value.bank
    const nameMatch = !filters.value.productName || 
      product.name.toLowerCase().includes(filters.value.productName.toLowerCase())
    const rateMatch = !filters.value.interestRate || 
      parseFloat(product.interestRate) >= parseFloat(filters.value.interestRate)
    const periodMatch = !filters.value.period || 
      product.period === parseInt(filters.value.period)
    
    return typeMatch && bankMatch && nameMatch && rateMatch && periodMatch
  })
})

// 상품 데이터 가져오기
const fetchProducts = async () => {
  try {
    const response = await axios.get('http://localhost:8000/deposits/products/')
    
    if (!response.data || response.data.length === 0) {
      console.warn('No products received from API')
      return
    }

    products.value = response.data.map(item => ({
      id: item.deposit_ID,
      bank: item.kor_co_nm,
      name: item.fin_prdt_nm,
      type: item.product_type, // '예금' 또는 '적금'
      interestRate: Math.max(...(item.options?.map(opt => opt.intr_rate) || [0])),
      period: parseInt(item.options?.[0]?.save_trm) || 0,
      joinWay: item.join_way,
      specialCondition: item.spcl_cnd,
      joinLimit: item.join_deny,
      options: item.options
    }))
  } catch (error) {
    console.error('Failed to fetch products:', error)
  }
}

// 상세 정보 표시
const showDetail = (product) => {
  selectedProduct.value = product
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.deposit-compare-wrapper {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.product-type-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.tab-btn {
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #f0f0f0;
  color: #666;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background-color: #2a388f;
  color: white;
}

.tab-btn:hover {
  background-color: #1a287f;
  color: white;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 1.1rem;
}

/* 기존 스타일 유지 */
.deposit-compare-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.filter-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-item {
  flex: 1;
  min-width: 200px;
}

.filter-select,
.filter-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.deposit-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.deposit-header {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr 1fr 1fr;
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  font-weight: bold;
}

.deposit-item {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.deposit-item:hover {
  background-color: #f8f9fa;
}

.col {
  padding: 0.5rem;
}

.sub-text {
  display: block;
  font-size: 0.8rem;
  color: #666;
}

.detail-btn {
  padding: 0.5rem 1rem;
  background-color: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.detail-btn:hover {
  background-color: #1a287f;
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
