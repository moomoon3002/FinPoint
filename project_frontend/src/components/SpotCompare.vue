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
        <!-- 템플릿 -->
        <div class="date-range-row">
        <div class="date-range-picker">
          <label>시작일:</label><input type="date" v-model="startDate">
          <label>종료일:</label><input type="date" v-model="endDate">
        </div>
        </div>

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
              <td :class="getPriceChangeClass(item.open_price, index > 0 ? sortedData[index-1].open_price : item.open_price)">
                {{ formatPrice(item.open_price) }}
              </td>
              <td :class="getPriceChangeClass(item.high_price, index > 0 ? sortedData[index-1].high_price : item.high_price)">
                {{ formatPrice(item.high_price) }}
              </td>
              <td :class="getPriceChangeClass(item.low_price, index > 0 ? sortedData[index-1].low_price : item.low_price)">
                {{ formatPrice(item.low_price) }}
              </td>
              <td :class="getPriceChangeClass(item.close_price, index > 0 ? sortedData[index-1].close_price : item.close_price)">
                {{ formatPrice(item.close_price) }}
              </td>
              <td>{{ formatVolume(item.volume) }}</td>
              <td :class="getPriceChangeClass(item.close_price, index > 0 ? sortedData[index-1].close_price : item.close_price)">
                {{ formatDailyChange(item.close_price, index > 0 ? sortedData[index-1].close_price : item.close_price) }}
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
const allData = ref([]) // 전체 데이터 저장
const stockData = ref(null)
const priceChart = ref(null)
const volumeChart = ref(null)
let priceChartInstance = null
let volumeChartInstance = null
let isChartInitialized = ref(false)

// 날짜 관리
const today = new Date().toISOString().split('T')[0]
const startDate = ref('')  // 초기값을 비워둠
const endDate = ref(today)

// 기간 옵션
const periods = [
  { label: '1일', value: '1D' },
  { label: '1주일', value: '1W' },
  { label: '1개월', value: '1M' },
  { label: '3개월', value: '3M' },
  { label: '1년', value: '1Y' }
]

// 기간 선택 처리
const changePeriod = (period) => {
  selectedPeriod.value = period
  
  // 시작일을 Date 객체로 변환
  let start
  if (!startDate.value) {
    // 시작일이 설정되지 않은 경우, 가장 오래된 데이터의 날짜 사용
    const dates = allData.value.map(item => new Date(item.date))
    start = new Date(Math.min(...dates))
  } else {
    start = new Date(startDate.value)
  }
  
  let end = new Date(start)
  
  switch (period) {
    case '1D':
      end.setDate(start.getDate() + 1)
      break
    case '1W':
      end.setDate(start.getDate() + 7)
      break
    case '1M':
      end.setMonth(start.getMonth() + 1)
      break
    case '3M':
      end.setMonth(start.getMonth() + 3)
      break
    case '1Y':
      end.setFullYear(start.getFullYear() + 1)
      break
  }
  
  // 종료일이 오늘을 넘지 않도록 조정
  const todayDate = new Date(today)
  if (end > todayDate) {
    end = todayDate
  }
  
  startDate.value = start.toISOString().split('T')[0]
  endDate.value = end.toISOString().split('T')[0]
  updateFilteredData()
}

// 날짜 변경 처리
const handleDateChange = () => {
  selectedPeriod.value = 'custom'
  
  // 시작일이 종료일보다 늦으면 종료일을 시작일로 설정
  if (startDate.value > endDate.value) {
    endDate.value = startDate.value
  }
  
  // 종료일이 오늘을 넘지 않도록 조정
  if (endDate.value > today) {
    endDate.value = today
  }
  
  updateFilteredData()
}

// 필터링된 데이터 업데이트
const updateFilteredData = () => {
  console.log('Filtering data for period:', {
    start: startDate.value,
    end: endDate.value,
    period: selectedPeriod.value
  })
  
  if (!startDate.value) {
    // 시작일이 설정되지 않은 경우 모든 데이터 표시
    priceData.value = [...allData.value]
    console.log('Showing all data:', priceData.value.length, 'items')
  } else {
    // 시작일이 설정된 경우 필터링
    const filtered = allData.value.filter(item => {
      const itemDate = new Date(item.date).toISOString().split('T')[0]
      return itemDate >= startDate.value && itemDate <= endDate.value
    })
    priceData.value = filtered
    console.log(`Filtered ${filtered.length} items from ${allData.value.length} total items`)
  }

  // nextTick을 사용하여 DOM 업데이트 후 차트 업데이트
  nextTick(() => {
    updateCharts()
  })
}

// 정렬된 데이터 computed 속성
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

const getPriceChangeClass = (currentPrice, previousPrice) => {
  if (currentPrice === previousPrice) return 'price-neutral'
  return currentPrice > previousPrice ? 'price-up' : 'price-down'
}

const formatDailyChange = (currentPrice, previousPrice) => {
  if (currentPrice === previousPrice) return '0.00%'
  const change = ((currentPrice - previousPrice) / previousPrice) * 100
  const prefix = change > 0 ? '+' : ''
  return `${prefix}${change.toFixed(2)}%`
}

const changeMetal = async (metal) => {
  console.log('Changing metal to:', metal)
  selectedMetal.value = metal
  allData.value = [] // 메탈이 변경되면 데이터 초기화
  await fetchData()
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

    const chartData = sortedData.value.slice().reverse()
    const dates = chartData.map(item => formatDate(item.date))
    const prices = chartData.map(item => item.close_price)
    const volumes = chartData.map(item => item.volume)

    console.log('Chart data prepared:', {
      dates: dates.length,
      prices: prices.length,
      volumes: volumes.length,
      samplePrice: prices[0],
      sampleDate: dates[0]
    })

    // 가격 차트 생성
    priceChartInstance = new Chart(priceChart.value, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: `${selectedMetal.value === 'GOLD' ? '금' : '은'} 가격 (USD/oz)`,
          data: prices,
          borderColor: selectedMetal.value === 'GOLD' ? '#FFD700' : '#C0C0C0',
          backgroundColor: 'rgba(255, 215, 0, 0.1)',
          borderWidth: 2,
          tension: 0.1,
          fill: true
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
          x: {
            grid: {
              display: false
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          },
          y: {
            beginAtZero: false,
            ticks: {
              callback: value => `$${formatPrice(value)}`
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
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
          backgroundColor: selectedMetal.value === 'GOLD' ? 'rgba(255, 215, 0, 0.6)' : 'rgba(192, 192, 192, 0.6)',
          borderColor: selectedMetal.value === 'GOLD' ? '#FFD700' : '#C0C0C0',
          borderWidth: 1
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
          x: {
            grid: {
              display: false
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: value => formatVolume(value)
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            callbacks: {
              label: context => formatVolume(context.parsed.y)
            }
          }
        }
      }
    })

    isChartInitialized.value = true
    console.log('Charts updated successfully')
  } catch (error) {
    console.error('Error updating charts:', error)
  }
}

// 데이터 로드 함수
const fetchData = async () => {
  loading.value = true
  try {
    let url = 'http://localhost:8000/metals/prices/'
    const params = { metal_type: selectedMetal.value }
    
    console.log('Fetching metal data from:', url, 'with params:', params)
    const response = await axios.get(url, { params })
    console.log('Received metal data:', response.data)
    
    if (response.data && Array.isArray(response.data)) {
      allData.value = response.data.map(item => ({
        date: item.date,
        open_price: parseFloat(item.open_price),
        high_price: parseFloat(item.high_price),
        low_price: parseFloat(item.low_price),
        close_price: parseFloat(item.close_price),
        volume: parseInt(item.volume || '0')
      }))

      // 데이터 로드 후 시작일을 가장 오래된 날짜로 설정
      if (allData.value.length > 0) {
        const dates = allData.value.map(item => item.date)
        const oldestDate = new Date(Math.min(...dates.map(date => new Date(date))))
        startDate.value = oldestDate.toISOString().split('T')[0]
      }

      console.log('Processed all data:', allData.value.length, 'items')
      console.log('Date range:', { start: startDate.value, end: endDate.value })
      updateFilteredData()
    } else {
      console.error('Invalid data format received:', response.data)
    }
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    loading.value = false
  }
}

// 컴포넌트 마운트 시 실행
onMounted(async () => {
  try {
    console.log('Component mounted, initializing...')
    await nextTick()
    await fetchData()
  } catch (error) {
    console.error('Error in component mount:', error)
  }
})

// 메탈 변경 시 데이터 다시 로드
watch(selectedMetal, async () => {
  allData.value = [] // 메탈이 변경되면 데이터 초기화
  await fetchData()
})

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
</script>
