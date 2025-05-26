<template>
  <div class="stock-voice-analysis">
    <div class="search-container">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="회사명을 입력하세요"
          @keyup.enter="searchStock"
          class="search-input"
        />
        <button @click="searchStock" :disabled="isLoading" class="search-button">
          {{ isLoading ? '분석 중...' : '분석' }}
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div v-if="stockData" class="stock-info-container">
      <div class="stock-header">
        <h2>{{ stockData.company_name }}</h2>
        <p class="stock-code">{{ stockData.stock_code }}</p>
      </div>

      <div class="price-info" v-if="stockData.price_info">
        <div class="current-price">
          <div class="price-main">
            <p class="price-value">{{ formatPrice(stockData.price_info.current_price) }}원</p>
            <p class="price-usd">${{ formatUSD(stockData.price_info.current_price) }}</p>
          </div>
          <div class="price-change-info">
            <p class="date-reference">{{ stockData.price_info.previous_date }}보다</p>
            <div class="change-details" :class="getPriceChangeClass(stockData.price_info.change_text)">
              <p>{{ stockData.price_info.change_text }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="analysis-section">
        <h3>AI 분석</h3>
        <div class="analysis-content">
          {{ stockData.chatgpt_response }}
        </div>
      </div>

      <div class="comments-section">
        <h3>실시간 댓글</h3>
        <div v-if="stockData.comments && stockData.comments.length > 0" class="comments-list">
          <div v-for="(comment, index) in stockData.comments" :key="index" class="comment-item">
            <p>{{ comment }}</p>
            <button @click="deleteComment(index)" class="delete-btn">삭제</button>
          </div>
        </div>
        <p v-else>댓글이 없습니다.</p>
      </div>

      <div v-if="youtubeVideos.length" class="youtube-section">
        <h3>관련 유튜브 영상</h3>
        <div class="youtube-list">
          <div v-for="video in youtubeVideos" :key="video.id.videoId" class="youtube-item">
            <iframe
              width="320"
              height="180"
              :src="`https://www.youtube.com/embed/${video.id.videoId}`"
              frameborder="0"
              allowfullscreen
            ></iframe>
            <div class="video-title">{{ video.snippet.title }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

// 상태 관리
const searchQuery = ref('')
const stockData = ref(null)
const youtubeVideos = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

// 유틸리티 함수
const formatPrice = (price) => {
  return new Intl.NumberFormat('ko-KR').format(price)
}

const formatUSD = (krwPrice) => {
  if (!krwPrice) return '0.00'
  // 환율은 실제로는 API를 통해 가져와야 하지만, 여기서는 예시로 1300원으로 고정
  const exchangeRate = 1300
  const usdPrice = krwPrice / exchangeRate
  return usdPrice.toFixed(2)
}

const getPriceChangeClass = (changeText) => {
  if (!changeText) return ''
  return {
    'price-up': !changeText.includes('-'),
    'price-down': changeText.includes('-'),
    'price-neutral': changeText.includes('0원')
  }
}

const formatPriceChange = (change) => {
  const prefix = change > 0 ? '+' : '';
  return `${prefix}${formatPrice(Math.abs(change))}`;
}

// API 호출
const searchStock = async () => {
  if (!searchQuery.value.trim()) {
    errorMessage.value = '회사명을 입력해주세요.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  stockData.value = null

  try {
    const response = await axios.post('http://localhost:8000/crawlings/', {
      company_name: searchQuery.value
    })

    if (response.data.error_message) {
      errorMessage.value = response.data.error_message
    } else {
      stockData.value = response.data
      await searchYoutubeVideos(searchQuery.value)
    }
  } catch (error) {
    errorMessage.value = '분석 중 오류가 발생했습니다.'
    console.error('Error:', error)
  } finally {
    isLoading.value = false
  }
}

const searchYoutubeVideos = async (query) => {
  youtubeVideos.value = []
  if (!query) return
  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY
  const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=3&q=${encodeURIComponent(query + ' 주식')}+분석&key=${apiKey}`

  try {
    const res = await axios.get(url)
    youtubeVideos.value = res.data.items
  } catch (e) {
    console.error('유튜브 API 오류:', e)
  }
}

const deleteComment = async (index) => {
  if (!stockData.value) return

  try {
    const response = await axios.post('http://localhost:8000/crawlings/delete-comment/', {
      stock_code: stockData.value.stock_code,
      comment_index: index
    })

    if (response.data.error_message) {
      errorMessage.value = response.data.error_message
    } else {
      stockData.value = response.data
    }
  } catch (error) {
    errorMessage.value = '댓글 삭제 중 오류가 발생했습니다.'
    console.error('Error:', error)
  }
}
</script>

<style scoped>
.stock-voice-analysis {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-container {
  margin-bottom: 2rem;
}

.search-box {
  display: flex;
  gap: 1rem;
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

.search-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  text-align: center;
  padding: 1rem;
}

.stock-info-container {
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

.stock-code {
  color: #666;
  margin: 0.5rem 0 0;
}

.price-info {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.current-price {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
}

.price-main {
  margin-bottom: 1rem;
}

.price-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.price-usd {
  font-size: 1.2rem;
  color: #666;
  margin: 0.5rem 0 0 0;
}

.price-change-info {
  border-top: 1px solid #eee;
  padding-top: 1rem;
  margin-top: 1rem;
}

.date-reference {
  color: #666;
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.change-details {
  font-size: 1.2rem;
  font-weight: 500;
}

.change-details p {
  margin: 0;
}

.price-up {
  color: #dc3545;
}

.price-down {
  color: #28a745;
}

.price-neutral {
  color: #6c757d;
}

.analysis-section,
.comments-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.analysis-section h3,
.comments-section h3 {
  margin: 0 0 1rem;
  color: #333;
}

.analysis-content {
  line-height: 1.6;
  white-space: pre-line;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.comment-item p {
  margin: 0;
  flex: 1;
}

.delete-btn {
  padding: 0.25rem 0.75rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #c82333;
}

.youtube-section {
  margin-top: 2rem;
}

.youtube-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.youtube-item {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.video-title {
  padding: 0.75rem;
  font-size: 0.9rem;
  color: #333;
}
</style> 