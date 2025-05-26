<template>
  <div class="stock-voice-container">
    <div class="search-section">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="회사명을 입력하세요"
          @keyup.enter="searchStock"
        />
        <button @click="searchStock" :disabled="isLoading">
          {{ isLoading ? '분석 중...' : '분석' }}
        </button>
      </div>
    </div>

    <div v-if="stockData" class="stock-info-section">
      <div class="stock-header">
        <h2>{{ stockData.company_name }}</h2>
        <p class="stock-code">{{ stockData.stock_code }}</p>
      </div>

      <div v-if="stockData.price_info" class="price-info">
        <div class="price-item">
          <span class="label">현재가</span>
          <span class="value">{{ stockData.price_info.current_price }}</span>
        </div>
        <div class="price-item">
          <span class="label">등락률</span>
          <span class="value" :class="getChangeRateClass(stockData.price_info.change_rate)">
            {{ stockData.price_info.change_rate }}
          </span>
        </div>
        <div class="price-item">
          <span class="label">거래량</span>
          <span class="value">{{ stockData.price_info.volume }}</span>
        </div>
      </div>

      <div class="analysis-section">
        <h3>ChatGPT 분석</h3>
        <p>{{ stockData.chatgpt_response }}</p>
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
    </div>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const searchQuery = ref('')
const stockData = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

const searchStock = async () => {
  if (!searchQuery.value.trim()) {
    errorMessage.value = '회사명을 입력해주세요.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await axios.post('http://localhost:8000/crawlings/', {
      company_name: searchQuery.value
    })

    if (response.data.error_message) {
      errorMessage.value = response.data.error_message
    } else {
      stockData.value = {
        company_name: response.data.company_name,
        stock_code: response.data.stock_code,
        comments: response.data.comments,
        chatgpt_response: response.data.chatgpt_response,
        price_info: response.data.price_info
      }
    }
  } catch (error) {
    errorMessage.value = '분석 중 오류가 발생했습니다.'
    console.error('Error:', error)
  } finally {
    isLoading.value = false
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
      stockData.value = {
        company_name: response.data.company_name,
        stock_code: response.data.stock_code,
        comments: response.data.comments,
        chatgpt_response: response.data.chatgpt_response,
        price_info: response.data.price_info
      }
    }
  } catch (error) {
    errorMessage.value = '댓글 삭제 중 오류가 발생했습니다.'
    console.error('Error:', error)
  }
}

const getChangeRateClass = (changeRate) => {
  if (!changeRate) return ''
  const rate = parseFloat(changeRate.replace('%', ''))
  if (rate > 0) return 'positive'
  if (rate < 0) return 'negative'
  return ''
}
</script>

<style scoped>
.stock-voice-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.search-section {
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-box input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-box button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-box button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.stock-info-section {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stock-header {
  margin-bottom: 20px;
}

.stock-header h2 {
  margin: 0;
  color: #333;
}

.stock-code {
  color: #666;
  margin: 5px 0;
}

.price-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.price-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.price-item .label {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
}

.price-item .value {
  font-size: 1.2em;
  font-weight: bold;
}

.price-item .value.positive {
  color: #4CAF50;
}

.price-item .value.negative {
  color: #f44336;
}

.analysis-section {
  margin-bottom: 30px;
}

.analysis-section h3 {
  color: #333;
  margin-bottom: 10px;
}

.comments-section {
  margin-top: 30px;
}

.comments-section h3 {
  color: #333;
  margin-bottom: 15px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.comment-item p {
  margin: 0;
  flex: 1;
}

.delete-btn {
  padding: 5px 10px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

.error-message {
  color: #f44336;
  text-align: center;
  margin-top: 20px;
}
</style> 