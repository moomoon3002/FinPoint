<template>
  <div class="stock-analysis">
    <div class="search-section">
      <input 
        v-model="symbol"
        @keyup.enter="fetchStockData"
        placeholder="주식 심볼을 입력하세요 (예: 005930)"
        class="search-input"
      />
      <button @click="fetchStockData" class="search-button">검색</button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>데이터를 불러오는 중...</p>
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="stockData" class="stock-data">
      <div class="stock-header">
        <h2>{{ stockData.name }}</h2>
        <p class="symbol">{{ stockData.symbol }}</p>
      </div>

      <div class="price-section">
        <div class="current-price">
          <h3>현재가</h3>
          <p>{{ formatPrice(stockData.current_price) }}원</p>
        </div>
        <div class="price-change" :class="getPriceChangeClass">
          <p>{{ formatChange(stockData.change) }}원</p>
          <p>({{ formatChangeRate(stockData.change_rate) }}%)</p>
        </div>
      </div>

      <div class="volume-section">
        <h3>거래량</h3>
        <p>{{ formatVolume(stockData.volume) }}</p>
      </div>

      <div class="ai-analysis">
        <h3>AI 분석</h3>
        <div class="analysis-content">
          {{ stockData.ai_analysis }}
        </div>
      </div>

      <div class="timestamp">
        <p>최종 업데이트: {{ formatTimestamp(stockData.timestamp) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const symbol = ref('')
const stockData = ref(null)
const loading = ref(false)
const error = ref(null)

const getPriceChangeClass = computed(() => {
  if (!stockData.value) return ''
  return stockData.value.change > 0 ? 'positive' : stockData.value.change < 0 ? 'negative' : ''
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ko-KR').format(price)
}

const formatChange = (change) => {
  const prefix = change > 0 ? '+' : ''
  return `${prefix}${formatPrice(change)}`
}

const formatChangeRate = (rate) => {
  const prefix = rate > 0 ? '+' : ''
  return `${prefix}${rate.toFixed(2)}`
}

const formatVolume = (volume) => {
  return new Intl.NumberFormat('ko-KR').format(volume)
}

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString('ko-KR')
}

const fetchStockData = async () => {
  if (!symbol.value) {
    error.value = '주식 심볼을 입력해주세요.'
    return
  }

  loading.value = true
  error.value = null
  stockData.value = null

  try {
    const response = await axios.get(`http://localhost:8000/api/stocks/`, {
      params: { symbol: symbol.value }
    })
    stockData.value = response.data
  } catch (e) {
    error.value = e.response?.data?.error || '데이터를 불러오는데 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.stock-analysis {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
}

.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input {
  flex: 1;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-button {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-button:hover {
  background-color: #0056b3;
}

.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #dc3545;
  text-align: center;
  padding: 1rem;
}

.stock-data {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.stock-header {
  margin-bottom: 1.5rem;
}

.stock-header h2 {
  margin: 0;
  font-size: 1.8rem;
}

.symbol {
  color: #666;
  margin: 0.5rem 0 0;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.current-price h3 {
  margin: 0;
  font-size: 1rem;
  color: #666;
}

.current-price p {
  margin: 0.25rem 0 0;
  font-size: 2rem;
  font-weight: bold;
}

.price-change {
  font-size: 1.2rem;
}

.price-change.positive {
  color: #dc3545;
}

.price-change.negative {
  color: #28a745;
}

.volume-section {
  margin-bottom: 1.5rem;
}

.volume-section h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: #666;
}

.volume-section p {
  margin: 0;
  font-size: 1.2rem;
}

.ai-analysis {
  background-color: #f8f9fa;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.ai-analysis h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: #666;
}

.analysis-content {
  white-space: pre-line;
  line-height: 1.5;
}

.timestamp {
  color: #666;
  font-size: 0.9rem;
  text-align: right;
}
</style> 