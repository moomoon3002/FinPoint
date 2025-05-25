<template>
  <div class="deposit-compare-wrapper">
    <div class="deposit-compare-container">
      <h2 class="deposit-compare-title">예금비교</h2>
      
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

      <!-- 예금 상품 목록 -->
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
            <span class="sub-text">{{ product.type }}</span>
          </div>
          <div class="col product">{{ product.name }}</div>
          <div class="col interest">
            <strong>{{ product.interestRate }}%</strong>
            <span class="sub-text">이자율</span>
          </div>
          <div class="col period">
            <strong>{{ product.period }}</strong>
            <span class="sub-text">개월수</span>
          </div>
          <div class="col action">
            <button @click="showDetail(product)" class="detail-btn">자세히보기</button>
          </div>
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

const products = ref([])
const selectedProduct = ref(null)
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
    const bankMatch = !filters.value.bank || product.bank === filters.value.bank
    const nameMatch = !filters.value.productName || 
      product.name.toLowerCase().includes(filters.value.productName.toLowerCase())
    const rateMatch = !filters.value.interestRate || 
      parseFloat(product.interestRate) >= parseFloat(filters.value.interestRate)
    const periodMatch = !filters.value.period || 
      product.period === parseInt(filters.value.period)
    
    return bankMatch && nameMatch && rateMatch && periodMatch
  })
})

// 상품 데이터 가져오기
const fetchProducts = async () => {
  try {
    console.log('Fetching products...')
    const response = await axios.get('http://localhost:8000/deposits/products/')
    console.log('API Response:', response.data)
    
    if (!response.data || response.data.length === 0) {
      console.warn('No products received from API')
      return
    }

    products.value = response.data.map(item => {
      const highestRate = Math.max(...(item.options?.map(opt => opt.intr_rate) || [0]))
      return {
        id: item.deposit_ID,
        bank: item.kor_co_nm,
        name: item.fin_prdt_nm,
        type: item.product_type,
        interestRate: highestRate,
        period: parseInt(item.options?.[0]?.save_trm) || 0,
        joinWay: item.join_way,
        specialCondition: item.spcl_cnd,
        joinLimit: item.join_deny,
        options: item.options
      }
    })
    console.log('Processed products:', products.value)
  } catch (error) {
    console.error('Failed to fetch products:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
    }
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

.deposit-compare-title {
  font-size: 2rem;
  color: #333;
  margin-bottom: 2rem;
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

.filter-select, .filter-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.deposit-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.deposit-header {
  display: flex;
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  font-weight: bold;
}

.deposit-item {
  display: flex;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.deposit-item:hover {
  background: #f8f9fa;
}

.col {
  flex: 1;
  padding: 0 0.5rem;
}

.col.bank { flex: 1.5; }
.col.product { flex: 2; }
.col.interest, .col.period { flex: 1; }
.col.action { flex: 0.8; }

.sub-text {
  display: block;
  font-size: 0.8rem;
  color: #666;
}

.detail-btn {
  padding: 0.5rem 1rem;
  background: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.detail-btn:hover {
  background: #1a287f;
}

/* 모달 스타일 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
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
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.info-row label {
  flex: 1;
  color: #666;
}

.info-row span {
  flex: 2;
}

.close-btn {
  width: 100%;
  padding: 0.8rem;
  background: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.close-btn:hover {
  background: #1a287f;
}
</style>
