<template>
  <div class="spot-compare">
    <div class="header">
      <h2>귀금속 현물 시세</h2>
      <div class="controls">
        <div class="metal-selector">
          <button 
            :class="{ active: selectedMetal === 'GOLD' }" 
            @click="changeMetal('GOLD')"
          >
            금(Gold)
          </button>
          <button 
            :class="{ active: selectedMetal === 'SILVER' }" 
            @click="changeMetal('SILVER')"
          >
            은(Silver)
          </button>
        </div>
      </div>
    </div>

    <div class="content" v-if="!loading">
      <!-- 현재 가격 정보 -->
      <div class="current-price" v-if="latestPrice">
        <div class="price-header">
          <h3>{{ selectedMetal === 'GOLD' ? '금' : '은' }} 현재가</h3>
          <span class="date">{{ formatDate(latestPrice.date) }}</span>
        </div>
        <div class="price-details">
          <div class="main-price">
            <span class="value">{{ formatPrice(latestPrice.close_price) }}</span>
            <span class="unit">USD/oz</span>
          </div>
          <div class="price-changes">
            <div class="change-item">
              <span class="label">전일대비</span>
              <span :class="['value', getDailyPriceChangeClass()]">
                {{ formatPriceChange(getDailyPriceChange()) }}
                ({{ formatPercentage(getDailyPriceChangePercent()) }})
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 가격 차트 -->
      <div class="chart-section">
        <div class="chart-header">
          <h3>가격 추이</h3>
          <div class="period-selector">
            <button 
              v-for="period in periods" 
              :key="period.value"
              :class="{ active: selectedPeriod === period.value }"
              @click="changePeriod(period.value)"
            >
              {{ period.label }}
            </button>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="priceChart"></canvas>
        </div>
      </div>

      <!-- 거래량 차트 -->
      <div class="volume-section">
        <h3>거래량</h3>
        <div class="chart-container">
          <canvas ref="volumeChart"></canvas>
        </div>
      </div>

      <!-- 상세 데이터 테이블 -->
      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>날짜</th>
              <th>시가</th>
              <th>고가</th>
              <th>저가</th>
              <th>종가</th>
              <th>거래량</th>
              <th>변동률</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in sortedData" :key="item.date">
              <td>{{ formatDate(item.date) }}</td>
              <td>{{ formatPrice(item.open_price) }}</td>
              <td>{{ formatPrice(item.high_price) }}</td>
              <td>{{ formatPrice(item.low_price) }}</td>
              <td>{{ formatPrice(item.close_price) }}</td>
              <td>{{ formatVolume(item.volume) }}</td>
              <td :class="getPriceChangeClass(item, index)">
                {{ formatPercentage(getPriceChangePercent(item, index)) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="loading">
      <div class="spinner"></div>
      <p>데이터를 불러오는 중...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

// 상태 관리
const selectedMetal = ref('GOLD')
const selectedPeriod = ref('1M')
const loading = ref(true)
const priceData = ref([])
const priceChart = ref(null)
const volumeChart = ref(null)
let priceChartInstance = null
let volumeChartInstance = null
let isChartInitialized = ref(false)

// 기간 옵션
const periods = [
  { label: '1개월', value: '1M' },
  { label: '3개월', value: '3M' },
  { label: '6개월', value: '6M' },
  { label: '1년', value: '1Y' }
]

// 계산된 속성
const sortedData = computed(() => {
  return [...priceData.value].sort((a, b) => new Date(b.date) - new Date(a.date))
})

const latestPrice = computed(() => {
  return sortedData.value[0] || null
})

// 메서드
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(date)
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price)
}

const formatVolume = (volume) => {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0
  }).format(volume)
}

const formatPriceChange = (change) => {
  const prefix = change > 0 ? '+' : ''
  return `${prefix}${formatPrice(change)}`
}

const formatPercentage = (value) => {
  const prefix = value > 0 ? '+' : ''
  return `${prefix}${value.toFixed(2)}%`
}

const getDailyPriceChange = () => {
  if (sortedData.value.length < 2) return 0
  return sortedData.value[0].close_price - sortedData.value[1].close_price
}

const getDailyPriceChangePercent = () => {
  if (sortedData.value.length < 2) return 0
  const change = getDailyPriceChange()
  const previousPrice = sortedData.value[1].close_price
  return (change / previousPrice) * 100
}

const getDailyPriceChangeClass = () => {
  const change = getDailyPriceChange()
  return {
    'price-up': change > 0,
    'price-down': change < 0,
    'price-neutral': change === 0
  }
}

const getPriceChangePercent = (item, index) => {
  if (index === sortedData.value.length - 1) return 0
  const previousPrice = sortedData.value[index + 1].close_price
  const change = item.close_price - previousPrice
  return (change / previousPrice) * 100
}

const getPriceChangeClass = (item, index) => {
  const change = getPriceChangePercent(item, index)
  return {
    'price-up': change > 0,
    'price-down': change < 0,
    'price-neutral': change === 0
  }
}

const changeMetal = async (metal) => {
  selectedMetal.value = metal
  await fetchData()
}

const changePeriod = async (period) => {
  selectedPeriod.value = period
  await fetchData()
}

const getPeriodDates = () => {
  const end = new Date()
  const start = new Date()
  
  switch (selectedPeriod.value) {
    case '1M':
      start.setMonth(start.getMonth() - 1)
      break
    case '3M':
      start.setMonth(start.getMonth() - 3)
      break
    case '6M':
      start.setMonth(start.getMonth() - 6)
      break
    case '1Y':
      start.setFullYear(start.getFullYear() - 1)
      break
  }
  
  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  }
}

const initializeCharts = async () => {
  try {
    // DOM 요소가 준비될 때까지 대기
    await nextTick()

    // canvas 요소 존재 확인
    if (!priceChart.value || !volumeChart.value) {
      console.warn('Chart elements not ready')
      return false
    }

    // 이전 차트 인스턴스 제거
    if (priceChartInstance) {
      priceChartInstance.destroy()
      priceChartInstance = null
    }
    if (volumeChartInstance) {
      volumeChartInstance.destroy()
      volumeChartInstance = null
    }

    return true
  } catch (error) {
    console.error('Error initializing charts:', error)
    return false
  }
}

const updateCharts = async () => {
  if (!sortedData.value.length) {
    console.warn('No data to display')
    return
  }

  try {
    // 차트 초기화 확인
    const isInitialized = await initializeCharts()
    if (!isInitialized) {
      console.warn('Charts not initialized')
      return
    }

    const dates = sortedData.value.map(item => formatDate(item.date)).reverse()
    const prices = sortedData.value.map(item => item.close_price).reverse()
    const volumes = sortedData.value.map(item => item.volume).reverse()

    // 가격 차트 생성
    priceChartInstance = new Chart(priceChart.value, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: selectedMetal.value === 'GOLD' ? '금 가격' : '은 가격',
          data: prices,
          borderColor: selectedMetal.value === 'GOLD' ? '#FFD700' : '#C0C0C0',
          backgroundColor: selectedMetal.value === 'GOLD' ? '#FFD700' : '#C0C0C0',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        scales: {
          y: {
            beginAtZero: false,
            ticks: {
              callback: value => `$${formatPrice(value)}`
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: context => `$${formatPrice(context.parsed.y)}`
            }
          }
        }
      }
    })

    // 거래량 차트 생성
    volumeChartInstance = new Chart(volumeChart.value, {
      type: 'bar',
      data: {
        labels: dates,
        datasets: [{
          label: '거래량',
          data: volumes,
          backgroundColor: selectedMetal.value === 'GOLD' ? '#FFD700' : '#C0C0C0'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: value => formatVolume(value)
            }
          }
        }
      }
    })

    isChartInitialized.value = true
  } catch (error) {
    console.error('Error updating charts:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/metals/prices/', {
      params: { metal_type: selectedMetal.value }
    })
    
    if (response.data && Array.isArray(response.data)) {
      priceData.value = response.data.map(item => ({
        ...item,
        open_price: parseFloat(item.open_price),
        high_price: parseFloat(item.high_price),
        low_price: parseFloat(item.low_price),
        close_price: parseFloat(item.close_price),
        volume: parseInt(item.volume)
      }))

      // DOM이 업데이트된 후 차트 업데이트
      await nextTick()
      await updateCharts()
    }
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    loading.value = false
  }
}

// 감시자
watch([selectedMetal, selectedPeriod], async () => {
  await fetchData()
})

// 컴포넌트 마운트 시 실행
onMounted(async () => {
  try {
    await nextTick()
    await fetchData()
  } catch (error) {
    console.error('Error in component mount:', error)
  }
})
</script>

<style scoped>
.spot-compare {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  margin-bottom: 2rem;
}

.header h2 {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 1rem;
}

.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.metal-selector {
  display: flex;
  gap: 0.5rem;
}

.metal-selector button {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.metal-selector button.active {
  background: #f8f9fa;
  border-color: #adb5bd;
  font-weight: bold;
}

.current-price {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.price-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.price-header h3 {
  font-size: 1.2rem;
  color: #333;
  margin: 0;
}

.price-header .date {
  color: #666;
}

.main-price {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.main-price .unit {
  font-size: 1rem;
  color: #666;
  margin-left: 0.5rem;
}

.price-changes {
  display: flex;
  gap: 2rem;
}

.change-item .label {
  color: #666;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.price-up {
  color: #dc3545;
}

.price-down {
  color: #198754;
}

.price-neutral {
  color: #666;
}

.chart-section, .volume-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  font-size: 1.2rem;
  color: #333;
  margin: 0;
}

.period-selector {
  display: flex;
  gap: 0.5rem;
}

.period-selector button {
  padding: 0.25rem 0.75rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.period-selector button.active {
  background: #f8f9fa;
  border-color: #adb5bd;
  font-weight: bold;
}

.chart-container {
  height: 400px;
  position: relative;
}

.data-table {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: right;
  border-bottom: 1px solid #eee;
}

th:first-child, td:first-child {
  text-align: left;
}

th {
  background: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 