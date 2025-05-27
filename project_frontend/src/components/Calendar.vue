<template>
  <div class="calendar-container">
    <div v-if="loading" class="loading-spinner-wrapper">
      <div class="loading-spinner"></div>
      <div class="loading-text">로딩 중...</div>
    </div>
    <template v-else>
      <div class="calendar-section">
        <div class="calendar-header">
          <button class="nav-btn" @click="previousMonth">&lt;</button>
          <h2>{{ currentYear }}년 {{ currentMonth + 1 }}월</h2>
          <button class="nav-btn" @click="nextMonth">&gt;</button>
          <button class="today-btn" @click="goToToday">TODAY</button>
        </div>

        <div class="calendar-grid">
          <!-- 요일 헤더 -->
          <div class="weekday-header" v-for="day in weekDays" :key="day">
            {{ day }}
          </div>

          <!-- 날짜 그리드 -->
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            :class="[
              'calendar-day',
              { 'current-month': day.currentMonth },
              { 'today': isToday(day.date) },
              { 'selected': isSelected(day.date) },
              { 'saturday': isSaturday(day.date) },
              { 'sunday': isSunday(day.date) }
            ]"
            @click="selectDate(day.date)"
          >
            <span class="date">{{ day.dayNumber }}</span>
            <div class="event-dots" v-if="getEvents(day.date).length">
              <span class="event-dot" 
                    v-for="(event, i) in getEvents(day.date)" 
                    :key="i"
                    :style="{ backgroundColor: event.color || '#2a388f' }"
                    :title="event.title">
              </span>
            </div>
            <!-- IPO 이벤트 텍스트 표시 -->
            <div v-for="(event, i) in getEvents(day.date)" :key="'ipo-'+i" v-if="event && event.isIpo" class="ipo-event-text">
              {{ event.title }}
            </div>
          </div>
        </div>
      </div>

      <!-- 상세 정보 영역 -->
      <div class="selected-date-info" v-if="selectedDate">
        <h3>{{ formatDate(selectedDate) }}</h3>
        <div v-if="getEvents(selectedDate).length === 0" class="no-events">
          IPO 이벤트가 없습니다.
        </div>
        <div 
          v-for="(event, index) in getEvents(selectedDate)" 
          :key="index"
          class="event-item"
        >
          <div class="event-color" :style="{ backgroundColor: event.color || '#2a388f' }"></div>
          <div class="event-info">
            <div class="event-title">{{ event.title }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const weekDays = ['일', '월', '화', '수', '목', '금', '토']
const currentDate = ref(new Date())
const selectedDate = ref(null)
const ipoCalendar = ref([])
const loading = ref(false)

const displayYear = ref(new Date().getFullYear())
const displayMonth = ref(new Date().getMonth())

const updateDisplayDate = (year, month) => {
  displayYear.value = year
  displayMonth.value = month
  currentDate.value = new Date(year, month, 1)
}

const calendarDays = computed(() => {
  const days = []
  const year = displayYear.value
  const month = displayMonth.value
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const prevMonthLastDate = new Date(year, month, 0)
  for (let i = firstDay.getDay(); i > 0; i--) {
    const date = new Date(year, month - 1, prevMonthLastDate.getDate() - i + 1)
    days.push({ date, dayNumber: date.getDate(), currentMonth: false })
  }
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    days.push({ date, dayNumber: i, currentMonth: true })
  }
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const date = new Date(year, month + 1, i)
    days.push({ date, dayNumber: i, currentMonth: false })
  }
  return days
})

const selectDate = (date) => {
  selectedDate.value = new Date(date)
}

const previousMonth = () => {
  let newYear = displayYear.value
  let newMonth = displayMonth.value - 1
  if (newMonth < 0) {
    newMonth = 11
    newYear--
  }
  updateDisplayDate(newYear, newMonth)
}

const nextMonth = () => {
  let newYear = displayYear.value
  let newMonth = displayMonth.value + 1
  if (newMonth > 11) {
    newMonth = 0
    newYear++
  }
  updateDisplayDate(newYear, newMonth)
}

const goToToday = () => {
  const today = new Date()
  updateDisplayDate(today.getFullYear(), today.getMonth())
  selectedDate.value = today
}

const isToday = (date) => {
  const today = new Date()
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
}

const isSelected = (date) => {
  if (!selectedDate.value) return false
  return date.getDate() === selectedDate.value.getDate() &&
         date.getMonth() === selectedDate.value.getMonth() &&
         date.getFullYear() === selectedDate.value.getFullYear()
}

const formatDate = (date) => {
  if (!date) return ''
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

const isSaturday = (date) => date.getDay() === 6
const isSunday = (date) => date.getDay() === 0

const fetchIpoCalendar = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8000/ipo-calendar/')
    ipoCalendar.value = res.data.calendar || []
  } catch (e) {
    console.error('IPO 캘린더 불러오기 실패:', e)
  } finally {
    loading.value = false
  }
}

function ipoTypeColor(type) {
  switch (type) {
    case '수요예측': return '#6ec6ff'
    case '청약': return '#ffb6c1'
    case '환불': return '#bdbdbd'
    case '상장': return '#90caf9'
    case '락업해제': return '#ffd700'
    default: return '#bdbdbd'
  }
}

const getEvents = (date) => {
  if (!date) return []
  const correctedDate = new Date(date)
  correctedDate.setDate(correctedDate.getDate() + 1)
  const dateStr = correctedDate.toISOString().split('T')[0]
  const ipoDay = ipoCalendar.value.find(d => d.date === dateStr)
  const ipoEvents = ipoDay
    ? ipoDay.events.filter(ev => !!ev).map(ev => ({
        title: `${ev.company} (${ev.type})`,
        color: ipoTypeColor(ev.type),
        isIpo: true
      }))
    : []
  return ipoEvents
}

const filteredIpoEvents = computed(() => {
  const year = displayYear.value
  const month = displayMonth.value + 1
  return ipoCalendar.value
    .filter(item => {
      const [y, m] = item.date.split('-')
      return Number(y) === year && Number(m) === month
    })
    .sort((a, b) => a.date.localeCompare(b.date))
})

const currentYear = computed(() => displayYear.value)
const currentMonth = computed(() => displayMonth.value)

onMounted(() => {
  goToToday()
  fetchIpoCalendar()
})
</script>

<style scoped>
.calendar-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  display: flex;
  gap: 2rem;
}

.calendar-section {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
  position: relative;
}

.calendar-header h2 {
  font-size: 1.5rem;
  margin: 0 1rem;
}

.nav-btn {
  padding: 0.5rem 1rem;
  background-color: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2rem;
}

.nav-btn:hover {
  background-color: #1a287f;
}

.today-btn {
  position: absolute;
  right: 0;
  padding: 0.5rem 1rem;
  background-color: white;
  color: #2a388f;
  border: 1px solid #2a388f;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: bold;
}

.today-btn:hover {
  background-color: #2a388f;
  color: white;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: #eee;
  border: 1px solid #eee;
}

.weekday-header {
  background-color: #f8f9fa;
  padding: 1rem;
  text-align: center;
  font-weight: bold;
  color: #2a388f;
}

.calendar-day {
  background-color: white;
  min-height: 100px;
  padding: 0.5rem;
  position: relative;
  cursor: pointer;
}

.calendar-day:hover {
  background-color: #f8f9fa;
}

.calendar-day .date {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  color: #666;
}

.calendar-day.current-month .date {
  color: #333;
}

.calendar-day.today {
  background-color: #e8f4ff;
}

.calendar-day.today .date {
  color: #2a388f;
  font-weight: bold;
}

.calendar-day.selected {
  background-color: #e3f2fd;
  border: 2px solid #2a388f;
}

.selected-date-info {
  width: 300px;
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.add-event-btn {
  width: 100%;
  padding: 0.5rem;
  background-color: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.add-event-btn:hover {
  background-color: #1a287f;
}

.calendar-day.saturday .date {
  color: #0066cc;
}

.calendar-day.sunday .date {
  color: #ff0000;
}

.event-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  margin-top: 2rem;
}

.event-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #2a388f;
}

.event-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.event-item:hover {
  background-color: #f8f9fa;
}

.event-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.event-info {
  flex: 1;
}

.event-title {
  font-weight: 500;
}

.event-time {
  font-size: 0.8rem;
  color: #666;
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
  max-width: 500px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.save-btn,
.cancel-btn,
.delete-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-btn {
  background-color: #2a388f;
  color: white;
}

.save-btn:hover {
  background-color: #1a287f;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
}

.no-events {
  text-align: center;
  color: #666;
  padding: 1rem;
}

.ipo-event-text {
  font-size: 0.8rem;
  color: #2a388f;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ipo-info-text {
  font-size: 0.8rem;
  color: #888;
  margin-top: 2px;
}

.ipo-list-section {
  width: 350px;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-left: 2rem;
  height: fit-content;
}
.ipo-list {
  list-style: none;
  padding: 0;
}
.ipo-list > li {
  margin-bottom: 1rem;
}
.ipo-list ul {
  margin: 0.2rem 0 0 1rem;
  padding: 0;
}
.loading-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  width: 100%;
}
.loading-spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #2a388f;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
.loading-text {
  font-size: 1.2rem;
  color: #2a388f;
}
</style> 