<template>
  <div class="calendar-container">
    <div class="calendar-section">
      <div class="calendar-header">
        <button class="nav-btn" @click="previousMonth">&lt;</button>
        <h2>{{ currentYear }}년 {{ currentMonth + 1 }}월</h2>
        <button class="nav-btn" @click="nextMonth">&gt;</button>
        <button class="today-btn" @click="goToToday">오늘</button>
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
          <div class="event-dots" v-if="hasEvents(day.date)">
            <span class="event-dot" 
                  v-for="(event, i) in getEvents(day.date)" 
                  :key="i"
                  :style="{ backgroundColor: event.color || '#2a388f' }"
                  :title="event.title">
            </span>
          </div>
          <!-- IPO 이벤트 텍스트 표시 -->
          <div v-for="(event, i) in getEvents(day.date)" :key="'ipo-'+i" v-if="event.isIpo" class="ipo-event-text">
            {{ event.title }}
          </div>
        </div>
      </div>
    </div>

    <!-- 선택된 날짜 정보 -->
    <div class="selected-date-info" v-if="selectedDate">
      <h3>{{ formatDate(selectedDate) }}</h3>
      <div v-if="getEvents(selectedDate).length === 0" class="no-events">
        일정이 없습니다.
      </div>
      <div 
        v-for="(event, index) in getEvents(selectedDate)" 
        :key="index"
        class="event-item"
      >
        <div class="event-color" :style="{ backgroundColor: event.color || '#2a388f' }"></div>
        <div class="event-info">
          <div class="event-title">{{ event.title }}</div>
          <div class="event-time" v-if="event.time">{{ event.time }}</div>
          <div v-if="event.isIpo" class="ipo-info-text">IPO 이벤트 정보입니다.</div>
        </div>
      </div>
      <button class="add-event-btn" @click="showAddEventModal">일정 추가</button>
    </div>

    <!-- 일정 추가/수정 모달 -->
    <div v-if="showEventModal" class="modal">
      <div class="modal-content">
        <h3>{{ editingEvent ? '일정 수정' : '새 일정 추가' }}</h3>
        <form @submit.prevent="saveEvent">
          <div class="form-group">
            <label>제목</label>
            <input 
              type="text" 
              v-model="eventForm.title" 
              required 
              placeholder="일정 제목"
            >
          </div>
          <div class="form-group">
            <label>날짜</label>
            <input 
              type="date" 
              v-model="eventForm.date" 
              required
            >
          </div>
          <div class="form-group">
            <label>시간</label>
            <input 
              type="time" 
              v-model="eventForm.time"
            >
          </div>
          <div class="form-group">
            <label>설명</label>
            <textarea 
              v-model="eventForm.description" 
              placeholder="일정 설명"
            ></textarea>
          </div>
          <div class="form-group">
            <label>색상</label>
            <input 
              type="color" 
              v-model="eventForm.color"
            >
          </div>
          <div class="modal-buttons">
            <button type="submit" class="save-btn">저장</button>
            <button type="button" @click="closeModal" class="cancel-btn">취소</button>
            <button 
              v-if="editingEvent" 
              type="button" 
              @click="deleteEvent" 
              class="delete-btn"
            >삭제</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 기본 데이터
const weekDays = ['일', '월', '화', '수', '목', '금', '토']
const currentDate = ref(new Date())
const selectedDate = ref(null)
const showEventModal = ref(false)
const editingEvent = ref(null)
const events = ref([])
const ipoCalendar = ref([])

// 현재 연도와 월을 직접 ref로 관리
const displayYear = ref(new Date().getFullYear())
const displayMonth = ref(new Date().getMonth())

// 현재 연도와 월 computed 속성 제거하고 ref 사용
const updateDisplayDate = (year, month) => {
  displayYear.value = year
  displayMonth.value = month
  currentDate.value = new Date(year, month, 1)
}

// 달력 날짜 계산
const calendarDays = computed(() => {
  const days = []
  const year = displayYear.value
  const month = displayMonth.value

  // 해당 월의 첫 날과 마지막 날
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  // 이전 달의 날짜들
  const prevMonthLastDate = new Date(year, month, 0)
  for (let i = firstDay.getDay(); i > 0; i--) {
    const date = new Date(year, month - 1, prevMonthLastDate.getDate() - i + 1)
    days.push({
      date,
      dayNumber: date.getDate(),
      currentMonth: false
    })
  }

  // 현재 달의 날짜들
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    days.push({
      date,
      dayNumber: i,
      currentMonth: true
    })
  }

  // 다음 달의 날짜들
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const date = new Date(year, month + 1, i)
    days.push({
      date,
      dayNumber: i,
      currentMonth: false
    })
  }

  return days
})

// 날짜 선택
const selectDate = (date) => {
  selectedDate.value = new Date(date)
  console.log('Selected date:', selectedDate.value.toISOString())
}

// 이전 달로 이동
const previousMonth = () => {
  let newYear = displayYear.value
  let newMonth = displayMonth.value - 1
  
  if (newMonth < 0) {
    newMonth = 11
    newYear--
  }
  
  updateDisplayDate(newYear, newMonth)
  console.log('Previous month:', `${newYear}-${newMonth + 1}`)
}

// 다음 달로 이동
const nextMonth = () => {
  let newYear = displayYear.value
  let newMonth = displayMonth.value + 1
  
  if (newMonth > 11) {
    newMonth = 0
    newYear++
  }
  
  updateDisplayDate(newYear, newMonth)
  console.log('Next month:', `${newYear}-${newMonth + 1}`)
}

// 오늘 날짜로 이동
const goToToday = () => {
  const today = new Date()
  updateDisplayDate(today.getFullYear(), today.getMonth())
  selectedDate.value = today
  console.log('Today:', today.toISOString())
}

// 오늘 날짜 확인
const isToday = (date) => {
  const today = new Date()
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
}

// 선택된 날짜 확인
const isSelected = (date) => {
  if (!selectedDate.value) return false
  return date.getDate() === selectedDate.value.getDate() &&
         date.getMonth() === selectedDate.value.getMonth() &&
         date.getFullYear() === selectedDate.value.getFullYear()
}

// 날짜 포맷팅
const formatDate = (date) => {
  if (!date) return ''
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

// 토요일 확인
const isSaturday = (date) => {
  return date.getDay() === 6
}

// 일요일 확인
const isSunday = (date) => {
  return date.getDay() === 0
}

// 일정 관련 함수들
const hasEvents = (date) => {
  return getEvents(date).length > 0
}

const fetchIpoCalendar = async () => {
  try {
    const res = await axios.get('http://localhost:8000/ipo_calendar/')
    ipoCalendar.value = res.data.calendar || []
  } catch (e) {
    console.error('IPO 캘린더 불러오기 실패:', e)
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
  // 사용자 일정
  const userEvents = events.value.filter(event => {
    const eventDate = new Date(event.date)
    return eventDate.getDate() === date.getDate() &&
           eventDate.getMonth() === date.getMonth() &&
           eventDate.getFullYear() === date.getFullYear()
  })
  // IPO 이벤트
  const dateStr = date.toISOString().split('T')[0]
  const ipoDay = ipoCalendar.value.find(d => d.date === dateStr)
  const ipoEvents = ipoDay
    ? ipoDay.events.map(ev => ({
        title: `[IPO] ${ev.company} (${ev.type})`,
        color: ipoTypeColor(ev.type),
        isIpo: true
      }))
    : []
  return [...userEvents, ...ipoEvents]
}

const showAddEventModal = () => {
  if (!selectedDate.value) {
    alert('날짜를 선택해주세요.')
    return
  }

  editingEvent.value = null
  const formattedDate = selectedDate.value.toISOString().split('T')[0]
  eventForm.value = {
    title: '',
    date: formattedDate,
    time: '',
    description: '',
    color: '#2a388f'
  }
  showEventModal.value = true
}

const editEvent = (event) => {
  editingEvent.value = event
  eventForm.value = {
    ...event,
    date: new Date(event.date).toISOString().split('T')[0]
  }
  showEventModal.value = true
}

const saveEvent = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      alert('로그인이 필요합니다.')
      return
    }

    const eventData = {
      ...eventForm.value,
      date: eventForm.value.date
    }

    if (editingEvent.value) {
      await axios.put(`http://localhost:8000/events/${editingEvent.value.id}/`, 
        eventData,
        { headers: { Authorization: `Token ${token}` } }
      )
      const index = events.value.findIndex(e => e.id === editingEvent.value.id)
      events.value[index] = { ...eventData, id: editingEvent.value.id }
    } else {
      const response = await axios.post('http://localhost:8000/events/',
        eventData,
        { headers: { Authorization: `Token ${token}` } }
      )
      events.value.push(response.data)
    }

    showEventModal.value = false
    editingEvent.value = null
    await fetchEvents()
  } catch (error) {
    console.error('Failed to save event:', error)
    alert('일정 저장에 실패했습니다.')
  }
}

const deleteEvent = async () => {
  if (!editingEvent.value) return

  if (confirm('정말로 이 일정을 삭제하시겠습니까?')) {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('로그인이 필요합니다.')
        return
      }

      await axios.delete(`http://localhost:8000/events/${editingEvent.value.id}/`,
        { headers: { Authorization: `Token ${token}` } }
      )
      events.value = events.value.filter(e => e.id !== editingEvent.value.id)
      showEventModal.value = false
      editingEvent.value = null
    } catch (error) {
      console.error('Failed to delete event:', error)
      alert('일정 삭제에 실패했습니다.')
    }
  }
}

const closeModal = () => {
  showEventModal.value = false
  editingEvent.value = null
}

// 일정 데이터 가져오기
const fetchEvents = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      console.log('Token not found')
      return
    }

    const response = await axios.get('http://localhost:8000/events/',
      { headers: { Authorization: `Token ${token}` } }
    )
    events.value = response.data
  } catch (error) {
    console.error('Failed to fetch events:', error)
  }
}

// 템플릿에서 사용할 computed 속성
const currentYear = computed(() => displayYear.value)
const currentMonth = computed(() => displayMonth.value)

onMounted(() => {
  goToToday()
  fetchEvents()
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
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.today-btn:hover {
  background-color: #45a049;
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
</style> 