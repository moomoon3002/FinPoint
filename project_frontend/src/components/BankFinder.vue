<template>
  <div class="bank-finder">
    <div class="search-container">
      <div class="filter-section">
        <select v-model="selectedBankType" class="filter-select">
          <option value="">은행 종류 선택</option>
          <option value="국민은행">국민은행</option>
          <option value="신한은행">신한은행</option>
          <option value="우리은행">우리은행</option>
          <option value="하나은행">하나은행</option>
          <option value="농협은행">농협은행</option>
          <option value="기업은행">기업은행</option>
          <option value="새마을금고">새마을금고</option>
          <option value="신협">신협</option>
        </select>
        <select v-model="selectedCity" class="filter-select">
          <option value="">시/도 선택</option>
          <option value="서울특별시">서울특별시</option>
          <option value="부산광역시">부산광역시</option>
          <option value="대구광역시">대구광역시</option>
          <option value="인천광역시">인천광역시</option>
          <option value="광주광역시">광주광역시</option>
          <option value="대전광역시">대전광역시</option>
          <option value="울산광역시">울산광역시</option>
          <option value="세종특별자치시">세종특별자치시</option>
          <option value="경기도">경기도</option>
          <option value="강원도">강원도</option>
          <option value="충청북도">충청북도</option>
          <option value="충청남도">충청남도</option>
          <option value="전라북도">전라북도</option>
          <option value="전라남도">전라남도</option>
          <option value="경상북도">경상북도</option>
          <option value="경상남도">경상남도</option>
          <option value="제주특별자치도">제주특별자치도</option>
        </select>
      </div>
      <div class="search-section">
        <input
          v-model="searchKeyword"
          @keyup.enter="searchBanks"
          placeholder="은행명을 입력하세요"
          class="search-input"
        />
        <button @click="searchBanks" class="search-button">검색</button>
        <button @click="findNearbyBanks" class="nearby-button">주변 검색</button>
      </div>
    </div>

    <div id="map" class="map-container"></div>

    <ul v-if="banks.length" class="bank-list">
      <li
        v-for="bank in banks"
        :key="bank.id"
        class="bank-item"
        @click="selectBank(bank)"
      >
        <h4>{{ bank.place_name }}</h4>
        <p>{{ bank.address_name }}</p>
        <p>{{ bank.phone || '전화번호 없음' }}</p>
        <span class="bank-distance" v-if="bank.distance">
          {{ formatDistance(bank.distance) }}
        </span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 상태 관리
const searchKeyword = ref('')
const selectedBankType = ref('')
const selectedCity = ref('')
const banks = ref([])
const map = ref(null)
const markers = ref([])
const infowindow = ref(null)
const ps = ref(null)
const isMapReady = ref(false)

// .env에서 VITE_ 접두사로 읽어 옵니다.
const mapApiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY

// Kakao SDK 동적 로드
function loadKakaoSDK() {
  return new Promise((resolve, reject) => {
    if (!mapApiKey) {
      return reject(new Error('카카오맵 JS 키가 없습니다. .env 파일을 확인하세요.'))
    }

    // 이미 로드된 경우
    if (window.kakao && window.kakao.maps) {
      return resolve()
    }

    console.log('🔑 Kakao JS Key:', mapApiKey)

    const script = document.createElement('script')
    // 반드시 https:// 를 명시해야 https 요청으로 보냅니다.
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${mapApiKey}&autoload=false&libraries=services`

    script.onload = () => {
      console.log('카카오맵 SDK 스크립트 로드 완료')
      resolve()
    }

    script.onerror = () => {
      reject(new Error('카카오맵 SDK 로드 실패 (401/403 확인 필요)'))
    }

    document.head.appendChild(script)
  })
}

// 지도 초기화
function initMap() {
  const el = document.getElementById('map')
  if (!el || !window.kakao || !window.kakao.maps) {
    throw new Error('지도 초기화 불가: SDK 준비 확인 필요')
  }

  map.value = new window.kakao.maps.Map(el, {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 5,
  })
  infowindow.value = new window.kakao.maps.InfoWindow({ zIndex: 1 })
  ps.value = new window.kakao.maps.services.Places()
  isMapReady.value = true

  console.log('지도 초기화 완료')
}

// 마커 생성 헬퍼
function createMarker(place) {
  if (!isMapReady.value) return null
  const pos = new window.kakao.maps.LatLng(place.y, place.x)
  const marker = new window.kakao.maps.Marker({ map: map.value, position: pos })
  window.kakao.maps.event.addListener(marker, 'click', () => {
    infowindow.value.setContent(
      `<div style="padding:5px;font-size:12px;">
         <strong>${place.place_name}</strong><br>
         ${place.address_name}
       </div>`
    )
    infowindow.value.open(map.value, marker)
  })
  return marker
}

// 기존 마커/윈도우 삭제
function clearMarkers() {
  markers.value.forEach(m => m.setMap(null))
  markers.value = []
  infowindow.value && infowindow.value.close()
}

// 거리 포맷
function formatDistance(d) {
  return d < 1000 ? `${d}m` : `${(d/1000).toFixed(1)}km`
}

// 키워드 검색
function searchBanks() {
  if (!isMapReady.value) return
  let keyword = selectedBankType.value || searchKeyword.value.trim() || '은행'
  if (selectedCity.value) keyword += ` ${selectedCity.value}`

  ps.value.keywordSearch(keyword, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      clearMarkers()
      banks.value = data
      if (data.length) {
        map.value.setCenter(new window.kakao.maps.LatLng(data[0].y, data[0].x))
        map.value.setLevel(4)
        data.forEach(p => {
          const mk = createMarker(p)
          if (mk) markers.value.push(mk)
        })
      }
    } else {
      alert('검색 오류: ' + status)
    }
  })
}

// 주변 은행 검색 (현재 위치 기반)
function findNearbyBanks() {
  if (!isMapReady.value || !navigator.geolocation) {
    alert('위치 권한이 필요합니다.')
    return
  }
  navigator.geolocation.getCurrentPosition(
    pos => {
      const loc = new window.kakao.maps.LatLng(pos.coords.latitude, pos.coords.longitude)
      map.value.setCenter(loc)
      map.value.setLevel(3)
      clearMarkers()
      banks.value = []

      ps.value.categorySearch(
        'BK9',
        (data, status) => {
          if (status === window.kakao.maps.services.Status.OK) {
            data.forEach(p => {
              const mk = createMarker(p)
              if (mk) markers.value.push(mk)
              banks.value.push(p)
            })
          } else {
            alert('주변 검색 실패: ' + status)
          }
        },
        { location: loc, radius: 5000, sort: window.kakao.maps.services.SortBy.DISTANCE }
      )
    },
    () => {
      alert('위치 정보를 가져올 수 없습니다.')
    }
  )
}

// 리스트 클릭 시 해당 마커 열기
function selectBank(bank) {
  const pos = new window.kakao.maps.LatLng(bank.y, bank.x)
  map.value.setCenter(pos)
  map.value.setLevel(2)
  markers.value.forEach(m => {
    if (m.getPosition().equals(pos)) {
      window.kakao.maps.event.trigger(m, 'click')
    }
  })
}

onMounted(async () => {
  try {
    console.log('카카오맵 초기화 시작...')
    await loadKakaoSDK()
    initMap()
  } catch (err) {
    console.error('카카오맵 초기화 실패:', err)
    alert(`카카오맵 초기화 실패: ${err.message}\n키와 도메인 설정을 확인해주세요.`)
  }
})

onUnmounted(() => {
  clearMarkers()
  isMapReady.value = false
})
</script>

<style scoped>
.bank-finder { padding: 20px; display: flex; flex-direction: column; height: 100vh; }
.search-container { display: flex; gap: 10px; margin-bottom: 10px; }
.filter-section { display: flex; gap: 10px; }
.filter-select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.search-section { display: flex; gap: 10px; }
.search-input { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.search-button,
.nearby-button { padding: 8px 12px; border: none; background: #007bff; color: white; border-radius: 4px; cursor: pointer; }
.nearby-button { background: #28a745; }
.map-container { flex: 1; margin-bottom: 10px; border-radius: 4px; overflow: hidden; }
.bank-list { max-height: 200px; overflow-y: auto; list-style: none; margin: 0; padding: 0; }
.bank-item { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
.bank-item:hover { background: #f9f9f9; }
.bank-distance { color: #28a745; margin-top: 4px; display: block; }
</style>
