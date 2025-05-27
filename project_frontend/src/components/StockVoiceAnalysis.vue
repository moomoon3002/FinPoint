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
      <font-awesome-icon icon="fa-solid fa-magnifying-glass" style="color: white;" />
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

    <div v-if="loading" class="loading-spinner-wrapper">
      <div class="loading-spinner"></div>
      <div class="loading-text">검색 중...</div>
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
const loading = ref(false)
const result = ref(null)
const searchTerm = ref('')

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
  loading.value = true
  result.value = null
  errorMessage.value = ''
  stockData.value = null

  try {
    const token = localStorage.getItem('token')
    if (!token) {
      errorMessage.value = '로그인이 필요합니다.'
      return
    }

    const response = await axios.post('http://localhost:8000/crawlings/', {
      company_name: searchQuery.value
    }, {
      headers: {
        Authorization: `Token ${token}`
      }
    })

    if (response.data.error_message) {
      errorMessage.value = response.data.error_message
    } else {
      stockData.value = response.data
      await searchYoutubeVideos(searchQuery.value)
    }
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value = '로그인이 필요합니다.'
    } else {
      errorMessage.value = '분석 중 오류가 발생했습니다.'
    }
    console.error('Error:', error)
  } finally {
    isLoading.value = false
    loading.value = false
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
.loading-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
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
.error-text {
  color: #d32f2f;
  margin-top: 1rem;
}
</style>
