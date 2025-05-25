<template>
  <div class="stock-voice">
    <h2>주식의 소리</h2>
    
    <div class="search-section">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="searchStock"
          placeholder="주식 종목명을 입력하세요"
        >
        <button @click="searchStock" :disabled="loading">검색</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>데이터를 분석중입니다...</p>
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="stockData" class="stock-info">
      <div class="stock-header">
        <h3>{{ stockData.name }}</h3>
        <span class="stock-code">{{ stockData.code }}</span>
      </div>

      <div class="price-info">
        <div class="current-price">
          <span class="price">{{ formatPrice(stockData.currentPrice) }}원</span>
          <span :class="['change', stockData.changeDirection]">
            {{ stockData.changeDirection === 'up' ? '▲' : '▼' }}
            {{ formatPrice(Math.abs(stockData.priceChange)) }}원
            ({{ stockData.changePercent }}%)
          </span>
        </div>
      </div>

      <div class="market-summary">
        <h4>시장 분위기</h4>
        <p>{{ stockData.aiAnalysis }}</p>
      </div>

      <div class="comments-section">
        <h4>투자자 댓글</h4>
        <div class="comments-list">
          <div v-for="comment in stockData.comments" :key="comment.id" class="comment">
            <p class="comment-text">{{ comment.text }}</p>
            <span class="comment-time">{{ comment.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY || '',
  dangerouslyAllowBrowser: true
})

// 상태 관리
const searchQuery = ref('')
const loading = ref(false)
const error = ref(null)
const stockData = ref(null)
const isApiKeyMissing = ref(!import.meta.env.VITE_OPENAI_API_KEY)

// 가격 포맷팅
const formatPrice = (price) => {
  return new Intl.NumberFormat('ko-KR').format(price)
}

// 주식 검색 및 데이터 수집
const searchStock = async () => {
  if (!searchQuery.value.trim()) {
    error.value = '종목명을 입력해주세요.'
    return
  }

  loading.value = true
  error.value = null
  stockData.value = null

  try {
    // 백엔드 API를 통해 토스증권 데이터 가져오기
    const response = await axios.get(`http://localhost:8000/api/stock/info`, {
      params: {
        query: searchQuery.value
      }
    })

    if (!response.data) {
      throw new Error('종목을 찾을 수 없습니다.')
    }

    const { stockInfo, comments } = response.data

    // AI 분석 수행
    const aiAnalysis = await analyzeMarketSentiment(stockInfo, comments)

    stockData.value = {
      name: stockInfo.name,
      code: stockInfo.code,
      currentPrice: stockInfo.price,
      priceChange: stockInfo.change,
      changePercent: stockInfo.changePercent,
      changeDirection: stockInfo.change > 0 ? 'up' : 'down',
      comments: comments,
      aiAnalysis
    }
  } catch (err) {
    console.error('Error fetching stock data:', err)
    error.value = err.message || '데이터를 가져오는 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

// AI 분석
const analyzeMarketSentiment = async (stockInfo, comments) => {
  if (isApiKeyMissing.value) {
    return '⚠️ OpenAI API 키가 설정되지 않아 시장 분위기 분석을 할 수 없습니다.'
  }

  try {
    const prompt = `
      주식 종목: ${stockInfo.name}
      현재가: ${stockInfo.price}원
      전일대비: ${stockInfo.change}원 (${stockInfo.changePercent}%)
      
      최근 댓글들:
      ${comments.map(c => c.text).join('\n')}
      
      위 정보를 바탕으로 현재 시장 분위기를 한 줄로 분석해주세요.
    `

    const completion = await openai.chat.completions.create({
      messages: [{ role: "user", content: prompt }],
      model: "gpt-3.5-turbo",
    })

    return completion.choices[0].message.content
  } catch (error) {
    console.error('Error analyzing with AI:', error)
    return '시장 분위기 분석을 실패했습니다.'
  }
}
</script>

<style scoped>
.stock-voice {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.search-section {
  margin-bottom: 2rem;
}

.search-box {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.search-box input {
  width: 300px;
  padding: 0.5rem 1rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.search-box button {
  padding: 0.5rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.search-box button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
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
  background-color: #f8d7da;
  border-radius: 4px;
  margin: 1rem 0;
}

.stock-info {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stock-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stock-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.stock-code {
  color: #666;
  font-size: 1rem;
}

.price-info {
  margin-bottom: 2rem;
}

.current-price {
  font-size: 2rem;
  font-weight: bold;
}

.change {
  font-size: 1.2rem;
  margin-left: 1rem;
}

.change.up {
  color: #dc3545;
}

.change.down {
  color: #198754;
}

.market-summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 2rem;
}

.market-summary h4 {
  margin: 0 0 0.5rem;
  color: #333;
}

.comments-section {
  margin-top: 2rem;
}

.comments-section h4 {
  margin-bottom: 1rem;
}

.comment {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.comment:last-child {
  border-bottom: none;
}

.comment-text {
  margin: 0 0 0.5rem;
}

.comment-time {
  color: #666;
  font-size: 0.9rem;
}
</style> 