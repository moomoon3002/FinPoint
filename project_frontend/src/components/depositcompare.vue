<template>
  
  <div class="deposit-compare-wrapper">
    <div class="deposit-compare-container">
      <h2 class="deposit-compare-title">예금비교</h2>
      <!-- 필터 영역 -->
      <div class="deposit-filter-row">
        <select v-model="filters.bank">
          <option value="">전체은행</option>
          <option v-for="bank in bankOptions" :key="bank" :value="bank">{{ bank }}</option>
        </select>
        <input type="text" v-model="filters.productName" placeholder="상품명 검색" />
        <select v-model="filters.interestRate">
          <option value="">전체이자율</option>
          <option v-for="rate in interestRateOptions" :key="rate" :value="rate">{{ rate }}</option>
        </select>
        <select v-model="filters.months">
          <option value="">전체기간</option>
          <option v-for="month in monthsOptions" :key="month" :value="month">{{ month }}개월</option>
        </select>
      </div>

      <!-- 예금 테이블 -->
      <div class="deposit-table">
        <div class="deposit-table-header">
          <span>은행</span>
          <span>상품명</span>
          <span>이자율</span>
          <span>개월수</span>
          <span></span>
        </div>
        <div
          class="deposit-table-row"
          v-for="(item, idx) in filteredDeposits"
          :key="idx"
        >
          <span>
            <b>{{ item.bank }}</b><br />
            <span class="sub">{{ item.product }}</span>
          </span>
          <span>
            <b>{{ item.productName }}</b>
          </span>
          <span>
            <b>{{ item.interestRate }}</b><br />
            <span class="sub">이자율</span>
          </span>
          <span>
            <b>{{ item.months }}</b><br />
            <span class="sub">개월수</span>
          </span>
          <span>
            <button class="detail-btn">자세히보기</button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

function goLogin() {
  router.push('/login')
}

const depositList = [
  { bank: '신한은행', product: '정기예금', productName: '스마트예금', interestRate: '3.0%', months: '12' },
  { bank: '국민은행', product: '정기예금', productName: '국민플러스', interestRate: '3.2%', months: '24' },
  { bank: '우리은행', product: '자유적금', productName: '우리드림', interestRate: '2.8%', months: '12' },
  { bank: '하나은행', product: '정기예금', productName: '하나행복', interestRate: '3.0%', months: '36' },
]

const filters = ref({
  bank: '',
  productName: '',
  interestRate: '',
  months: ''
})

const bankOptions = [...new Set(depositList.map(d => d.bank))]
const interestRateOptions = [...new Set(depositList.map(d => d.interestRate))]
const monthsOptions = [...new Set(depositList.map(d => d.months))]

const filteredDeposits = computed(() => {
  return depositList.filter(item => {
    const bankMatch = !filters.value.bank || item.bank === filters.value.bank
    const productNameMatch = !filters.value.productName || item.productName.includes(filters.value.productName)
    const interestRateMatch = !filters.value.interestRate || item.interestRate === filters.value.interestRate
    const monthsMatch = !filters.value.months || item.months === filters.value.months
    return bankMatch && productNameMatch && interestRateMatch && monthsMatch
  })
})
</script>
