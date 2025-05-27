<template>
  <div class="bank-finder">
    <h2>은행 찾기</h2>
    <!-- <div class="highlight-bar">가까운 은행을 찾아보세요</div> -->

    <div class="search-container">
      <div class="filter-section">
        <select v-model="selectedCity" class="filter-select">
          <option value="">시/도 선택</option>
          <option v-for="city in cityList" :key="city">{{ city }}</option>
        </select>

        <select v-model="selectedDistrict" class="filter-select">
          <option value="">구/군 선택</option>
          <option v-for="district in districtList" :key="district">{{ district }}</option>
        </select>

        <select v-model="selectedBankType" class="filter-select">
          <option value="">은행 선택</option>
          <option v-for="bank in bankList" :key="bank">{{ bank }}</option>
        </select>
      </div>

      <div class="search-section">
        <button @click="searchBanks" class="search-button">
          <i class="fas fa-search"></i>
        </button>
        <button @click="findNearbyBanks" class="nearby-button">주변 검색</button>
      </div>
    </div>

    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    
    <div class="content-container">
      <div id="map" class="map-container"></div>

      <div class="bank-list-container">
        <div v-if="banks.length" class="bank-list">
          <div class="bank-list-header">검색 결과 ({{ banks.length }})</div>
          <div class="bank-list-scroll">
            <div v-for="bank in banks" 
                 :key="bank.id" 
                 class="bank-item" 
                 @click="selectBank(bank)"
                 :class="{ 'active': selectedBankId === bank.id }">
              <h4>{{ bank.place_name }}</h4>
              <p class="address">{{ bank.address_name }}</p>
              <p class="phone">{{ bank.phone || '전화번호 없음' }}</p>
              <span class="bank-distance" v-if="bank.distance">
                {{ formatDistance(bank.distance) }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="no-results">
          검색 결과가 없습니다
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

// 상태 관리
const map = ref(null)
const markers = ref([])
const infowindow = ref(null)
const ps = ref(null)
const banks = ref([])
const errorMessage = ref('')

// 필터 상태
const selectedCity = ref('')
const selectedDistrict = ref('')
const selectedBankType = ref('')

// 선택된 은행 ID 상태 추가
const selectedBankId = ref(null)

// 현재 위치 마커와 반경 원 참조 추가
const currentLocationMarker = ref(null)
const currentLocationCircle = ref(null)

// 반경 설정 (미터 단위)
const searchRadius = ref(1000) // 기본 1km

// 도시 및 은행 데이터
const cityList = [
  '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시',
  '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
  '충청북도', '충청남도', '전라북도', '전라남도', '경상북도',
  '경상남도', '제주특별자치도'
]

const districtMap = {
  '서울특별시': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
              '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
              '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
  '부산광역시': ['강서구', '금정구', '기장군', '남구', '동구', '동래구', '부산진구', '북구',
              '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구'],
  '대구광역시': ['남구', '달서구', '달성군', '동구', '북구', '서구', '수성구', '중구'],
  '인천광역시': ['강화군', '계양구', '남구', '남동구', '동구', '부평구', '서구', '연수구', '옹진군', '중구'],
  '광주광역시': ['광산구', '남구', '동구', '북구', '서구'],
  '대전광역시': ['대덕구', '동구', '서구', '유성구', '중구'],
  '울산광역시': ['남구', '동구', '북구', '울주군', '중구'],
  '경기도': ['가평군', '고양시 덕양구', '고양시 일산동구', '고양시 일산서구', '과천시', '광명시', '광주시', '구리시', '군포시', '김포시',
           '남양주시', '동두천시', '부천시 소사구', '부천시 오정구', '부천시 원미구', '성남시 분당구', '성남시 수정구', '성남시 중원구',
           '수원시 권선구', '수원시 영통구', '수원시 장안구', '수원시 팔달구', '시흥시', '안산시 단원구', '안산시 상록구', '안성시',
           '안양시 동안구', '안양시 만안구', '양주시', '양평군', '여주군', '연천군', '오산시', '용인시 기흥구', '용인시 수지구',
           '용인시 처인구', '의왕시', '의정부시', '이천시', '파주시', '평택시', '포천시', '하남시', '화성시'],
  '강원도': ['강릉시', '고성군', '동해시', '삼척시', '속초시', '양구군', '양양군', '영월군', '원주시', '인제군',
          '정선군', '철원군', '춘천시', '태백시', '평창군', '홍천군', '화천군', '횡성군'],
  '충청북도': ['괴산군', '단양군', '보은군', '영동군', '옥천군', '음성군', '제천시', '증평군', '진천군',
            '청원군', '청주시 상당구', '청주시 흥덕구', '충주시'],
  '충청남도': ['계룡시', '공주시', '금산군', '논산시', '당진시', '보령시', '부여군', '서산시', '서천군', '아산시',
            '연기군', '예산군', '천안시 동남구', '천안시 서북구', '청양군', '태안군', '홍성군'],
  '전라북도': ['고창군', '군산시', '김제시', '남원시', '무주군', '부안군', '순창군', '완주군',
            '익산시', '임실군', '장수군', '전주시 덕진구', '전주시 완산구', '정읍시', '진안군'],
  '전라남도': ['강진군', '고흥군', '곡성군', '광양시', '구례군', '나주시', '담양군', '목포시',
            '무안군', '보성군', '순천시', '신안군', '여수시', '영광군', '영암군', '완도군',
            '장성군', '장흥군', '진도군', '함평군', '해남군', '화순군'],
  '경상북도': ['경산시', '경주시', '고령군', '구미시', '군위군', '김천시', '문경시', '봉화군',
            '상주시', '성주군', '안동시', '영덕군', '영양군', '영주시', '영천시', '예천군',
            '울릉군', '울진군', '의성군', '청도군', '청송군', '칠곡군', '포항시 남구', '포항시 북구'],
  '경상남도': ['거제시', '거창군', '고성군', '김해시', '남해군', '밀양시', '사천시', '산청군',
            '양산시', '의령군', '진주시', '창녕군', '창원시 마산합포구', '창원시 마산회원구',
            '창원시 성산구', '창원시 의창구', '창원시 진해구', '통영시', '하동군', '함안군',
            '함양군', '합천군'],
  '제주특별자치도': ['서귀포시', '제주시'],
  '세종특별자치시': ['세종시']
}

const bankList = [
  "국민은행", "신한은행", "우리은행", "하나은행", "산업은행", "농협", "새마을금고", "신협", "우체국",
        "기업은행", "부산은행", "대구은행", "광주은행", "경남은행", "전북은행", "제주은행", "수협"
]

// computed 속성
const districtList = computed(() => {
  return districtMap[selectedCity.value] || []
})

// 거리 계산 함수 추가
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // 지구의 반경 (km)
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distance = R * c;
  return Math.round(distance * 1000); // 미터 단위로 반환
}

// Kakao Maps SDK 로딩
function loadKakaoMap() {
  return new Promise((resolve, reject) => {
    try {
      console.log('🔄 카카오맵 SDK 로딩 시작')
      const apiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY
      
      // 환경 정보 로깅
      console.log('현재 환경 정보:')
      console.log('- 프로토콜:', window.location.protocol)
      console.log('- 호스트:', window.location.host)
      console.log('- API 키 상태:', apiKey ? '설정됨' : '미설정')
      
      if (!apiKey) {
        throw new Error('카카오맵 API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.')
      }

      // 이미 로드된 경우
      if (window.kakao && window.kakao.maps) {
        console.log('✅ 카카오맵 SDK 이미 로드됨')
        return resolve(window.kakao)
      }

      // 스크립트가 이미 추가된 경우
      const existingScript = document.getElementById('kakao-map-script')
      if (existingScript) {
        document.head.removeChild(existingScript)
        console.log('🔄 기존 스크립트 제거됨')
      }

      // 새로운 스크립트 추가
      const script = document.createElement('script')
      script.id = 'kakao-map-script'
      script.type = 'text/javascript'
      script.async = true
      
      const protocol = window.location.protocol
      script.src = `${protocol}//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services&autoload=false`
      
      console.log('🔄 스크립트 URL:', script.src)

      script.onload = () => {
        console.log('📥 스크립트 로드됨, 지도 API 초기화 중...')
        window.kakao.maps.load(() => {
          console.log('✅ 카카오맵 API 초기화 완료')
          resolve(window.kakao)
        })
      }

      script.onerror = (error) => {
        console.error('❌ 카카오맵 스크립트 로드 실패:', error)
        reject(new Error('카카오맵 SDK 로드 실패'))
      }

      document.head.appendChild(script)
      console.log('📤 카카오맵 스크립트 추가됨')

    } catch (error) {
      console.error('❌ 초기화 중 예외 발생:', error)
      reject(error)
    }
  })
}

// 마커 생성 및 관리
function createMarker(place) {
  const position = new window.kakao.maps.LatLng(place.y, place.x)
  
  // 마커 이미지 설정
  const imageSize = new window.kakao.maps.Size(24, 24)
  const imageOption = { offset: new window.kakao.maps.Point(12, 12) }
  
  const markerImage = new window.kakao.maps.MarkerImage(
    'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#28a745">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
    `),
    imageSize,
    imageOption
  )

  const marker = new window.kakao.maps.Marker({ 
    position,
    map: map.value,
    image: markerImage,
    zIndex: 1
  })

  // 인포윈도우 내용 개선
  const content = `
    <div style="padding: 10px; min-width: 200px;">
      <strong style="font-size: 14px; color: #333;">${place.place_name}</strong>
      <p style="margin: 5px 0; font-size: 12px; color: #666;">${place.address_name}</p>
      <p style="margin: 5px 0; font-size: 12px; color: #28a745;">
        ${place.phone || '전화번호 없음'}
      </p>
      ${place.distance ? 
        `<p style="margin: 5px 0; font-size: 12px; color: #007bff;">
          현재 위치에서 ${formatDistance(place.distance)} 거리
        </p>` : ''
      }
    </div>
  `

  const infowindow = new window.kakao.maps.InfoWindow({
    content: content,
    removable: true
  })

  window.kakao.maps.event.addListener(marker, 'click', () => {
    // 이전 인포윈도우 닫기
    if (infowindow.value) {
      infowindow.value.close()
    }
    infowindow.open(map.value, marker)
    infowindow.value = infowindow
  })

  return marker
}

// 마커 초기화
function clearMarkers() {
  markers.value.forEach(marker => marker.setMap(null))
  markers.value = []
  if (infowindow.value) {
    infowindow.value.close()
    infowindow.value = null
  }
}

// 거리 포맷팅
function formatDistance(distance) {
  return distance < 1000 ? `${distance}m` : `${(distance/1000).toFixed(1)}km`
}

// 은행 검색
async function searchBanks() {
  if (!map.value || !ps.value) {
    errorMessage.value = '지도가 아직 초기화되지 않았습니다.'
    return
  }

  const keyword = [
    selectedCity.value,
    selectedDistrict.value,
    selectedBankType.value
  ].filter(Boolean).join(' ')

  if (!keyword) {
    errorMessage.value = '검색어를 입력해주세요.'
    return
  }

  clearMarkers()
  errorMessage.value = ''

  ps.value.keywordSearch(keyword, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      const bounds = new window.kakao.maps.LatLngBounds()
      banks.value = data

      data.forEach(place => {
        const marker = createMarker(place)
        markers.value.push(marker)
        bounds.extend(new window.kakao.maps.LatLng(place.y, place.x))
      })

      map.value.setBounds(bounds)
    } else {
      errorMessage.value = '검색 결과가 없습니다.'
      banks.value = []
    }
  })
}

// 현재 위치 마커 이미지 설정
function createCurrentLocationMarker(position) {
  // 기존 현재 위치 마커와 반경 원 제거
  if (currentLocationMarker.value) {
    currentLocationMarker.value.setMap(null)
  }
  if (currentLocationCircle.value) {
    currentLocationCircle.value.setMap(null)
  }

  // 현재 위치 마커 생성
  const imageSize = new window.kakao.maps.Size(24, 24)
  const imageOption = { offset: new window.kakao.maps.Point(12, 12) }
  
  const markerImage = new window.kakao.maps.MarkerImage(
    'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#007bff">
        <circle cx="12" cy="12" r="8" fill="#007bff"/>
        <circle cx="12" cy="12" r="3" fill="white"/>
      </svg>
    `),
    imageSize,
    imageOption
  )

  currentLocationMarker.value = new window.kakao.maps.Marker({
    position: position,
    map: map.value,
    image: markerImage,
    zIndex: 2
  })

  // 반경 원 생성
  currentLocationCircle.value = new window.kakao.maps.Circle({
    center: position,
    radius: searchRadius.value,
    strokeWeight: 1,
    strokeColor: '#007bff',
    strokeOpacity: 0.2,
    strokeStyle: 'solid',
    fillColor: '#007bff',
    fillOpacity: 0.1,
    map: map.value
  })
}

// 주변 은행 검색
async function findNearbyBanks() {
  try {
    errorMessage.value = ''
    
    if (!navigator.geolocation) {
      throw new Error('브라우저가 위치 정보를 지원하지 않습니다.')
    }

    console.log('🔄 현재 위치 검색 시작...')
    
    // 위치 권한 요청
    const position = await new Promise((resolve, reject) => {
      const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }

      const successCallback = (pos) => {
        console.log('✅ 현재 위치 찾음:', pos.coords)
        resolve(pos)
      }

      const errorCallback = (err) => {
        console.error('❌ 위치 검색 실패:', err)
        let errorMessage = '위치를 찾을 수 없습니다.'
        
        switch (err.code) {
          case err.PERMISSION_DENIED:
            errorMessage = '위치 정보 접근이 거부되었습니다. 브라우저 설정에서 위치 접근을 허용해주세요.'
            break
          case err.POSITION_UNAVAILABLE:
            errorMessage = '위치 정보를 사용할 수 없습니다. 잠시 후 다시 시도해주세요.'
            break
          case err.TIMEOUT:
            errorMessage = '위치 검색 시간이 초과되었습니다. 다시 시도해주세요.'
            break
        }
        
        reject(new Error(errorMessage))
      }

      navigator.geolocation.getCurrentPosition(
        successCallback,
        errorCallback,
        options
      )
    })

    const latitude = position.coords.latitude
    const longitude = position.coords.longitude
    const currentLocation = new window.kakao.maps.LatLng(latitude, longitude)

    console.log('📍 현재 위치 좌표:', { latitude, longitude })

    // 현재 위치 마커 생성
    createCurrentLocationMarker(currentLocation)

    // 지도 중심 이동
    map.value.setCenter(currentLocation)
    map.value.setLevel(4)

    // 기존 마커들 제거
    clearMarkers()
    banks.value = []

    console.log('🔄 주변 은행 검색 시작...')

    // 주변 은행 검색
    const searchResult = await new Promise((resolve, reject) => {
      ps.value.categorySearch(
        'BK9',
        (data, status, pagination) => {
          if (status === window.kakao.maps.services.Status.OK) {
            console.log('✅ 주변 은행 검색 완료:', data.length + '개 발견')
            resolve({ data, pagination })
          } else {
            console.error('❌ 주변 은행 검색 실패:', status)
            reject(new Error('주변 은행을 찾을 수 없습니다.'))
          }
        },
        {
          location: currentLocation,
          radius: searchRadius.value,
          sort: window.kakao.maps.services.SortBy.DISTANCE
        }
      )
    })

    // 검색 결과 처리
    const { data } = searchResult
    banks.value = data.map(bank => {
      // 직선 거리 계산
      const distance = calculateDistance(
        latitude,
        longitude,
        parseFloat(bank.y),
        parseFloat(bank.x)
      )
      return { ...bank, distance }
    })

    console.log('✅ 검색 결과 처리 완료')

    // 마커 생성
    banks.value.forEach(bank => {
      const marker = createMarker(bank)
      markers.value.push(marker)
    })

  } catch (error) {
    console.error('❌ 주변 검색 실패:', error)
    errorMessage.value = error.message || '주변 은행 검색 중 오류가 발생했습니다.'
  }
}

// 특정 은행 선택
function selectBank(bank) {
  selectedBankId.value = bank.id
  const position = new window.kakao.maps.LatLng(bank.y, bank.x)
  map.value.setCenter(position)
  map.value.setLevel(2)
  
  markers.value.forEach(marker => {
    if (marker.getPosition().equals(position)) {
      window.kakao.maps.event.trigger(marker, 'click')
    }
  })
}

// 컴포넌트 마운트
onMounted(async () => {
  console.log('🚀 BankFinder 컴포넌트 마운트 시작')
  try {
    // 이전 에러 메시지 초기화
    errorMessage.value = ''
    
    // SDK 로드
    console.log('🔄 카카오맵 SDK 로드 시작')
    await loadKakaoMap()
    
    // DOM 요소 확인
    const container = document.getElementById('map')
    if (!container) {
      throw new Error('지도를 표시할 DOM 요소를 찾을 수 없습니다')
    }
    
    console.log('🔄 지도 인스턴스 생성 중...')
    const options = {
      center: new window.kakao.maps.LatLng(37.5665, 126.9780), // 서울 시청
      level: 5
    }

    // 지도 인스턴스 생성
    map.value = new window.kakao.maps.Map(container, options)
    
    // 지도 로드 완료 이벤트
    window.kakao.maps.event.addListener(map.value, 'tilesloaded', () => {
      console.log('✅ 지도 타일 로드 완료')
      if (!infowindow.value) {
        infowindow.value = new window.kakao.maps.InfoWindow({ zIndex: 1 })
        ps.value = new window.kakao.maps.services.Places()
        console.log('✅ 지도 서비스 초기화 완료')
      }
    })

    console.log('✅ 지도 초기화 완료')

    // 마지막 검색 복원
    const lastSearch = localStorage.getItem('lastBankSearch')
    if (lastSearch) {
      console.log('🔄 마지막 검색 복원 중:', lastSearch)
      const [city, district, bank] = lastSearch.split(' ')
      selectedCity.value = city
      selectedDistrict.value = district
      selectedBankType.value = bank
      setTimeout(searchBanks, 1000) // 지도 로드 후 검색하도록 대기 시간 증가
    }

  } catch (error) {
    console.error('❌ 지도 초기화 실패:', error)
    errorMessage.value = `지도 초기화 실패: ${error.message}`
  }
})
</script>

<style scoped>
.bank-finder {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f8fe;
}

h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.search-container {
  display: flex;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto 20px auto;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  align-items: flex-start;
  justify-content: flex-start;
  flex-wrap: nowrap;
  box-sizing: border-box;
  gap: 0;
}

.filter-section {
  display: flex;
  gap: 0;
  flex: 1;
  align-items: center;
}

.filter-select {
  flex: 1;
  height: 44px;
  font-size: 1rem;
  line-height: 44px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
  box-sizing: border-box;
  vertical-align: middle;
  margin-right: 8px;
}

.filter-section .filter-select:last-child {
  margin-right: 0;
}

.search-section {
  display: flex;
  gap: 0;
  align-items: flex-start;
  margin-left: 12px;
  flex-shrink: 0;
}

.search-button,
.nearby-button {
  height: 44px;
  min-width: 44px;
  padding: 0 16px;
  font-size: 1rem;
  line-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  transition: background-color 0.2s;
}

.search-button {
  background-color: #2A388F;
  color: white;
  margin-left: 4px;
}

.search-button:hover {
  background-color: #2A388F;
  color: white;
}

.nearby-button {
  margin-left: 4px;
}

.search-button i {
  font-size: 1.1rem;
}

.search-button:hover {
  background-color: #2A388F;
  color: white;
}

.nearby-button:hover {
  background-color: #2A388F;
  color: white;
}

.content-container {
  display: flex;
  gap: 24px;
  flex: 1;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 0;
  align-items: stretch;
}

.map-container,
.bank-list-container {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.map-container {
  flex: 1 1 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 600px;
  min-height: 600px;
  max-width: 1050px;
}

.bank-list-container {
  width: 350px;
  min-width: 300px;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 600px;
  min-height: 600px;
  overflow-y: auto;
}

.bank-list {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.bank-list-header {
  padding: 15px;
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.bank-list-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.bank-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bank-item:hover {
  background-color: #f8f9fa;
  transform: translateX(5px);
}

.bank-item.active {
  background-color: #e8f4ff;
  border-left: 4px solid #007bff;
}

.bank-item h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 16px;
}

.bank-item .address {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

.bank-item .phone {
  margin: 5px 0;
  color: #666;
  font-size: 13px;
}

.bank-distance {
  color: #28a745;
  font-size: 0.9em;
  font-weight: bold;
  display: inline-block;
  margin-top: 5px;
  background-color: #e8f5e9;
  padding: 4px 10px;
  border-radius: 12px;
}

.no-results {
  padding: 20px;
  text-align: center;
  color: #666;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  text-align: center;
}

@media (max-width: 768px) {
  .content-container {
    flex-direction: column;
  }
  
  .bank-list-container {
    width: 100%;
    max-height: 300px;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .search-section {
    justify-content: stretch;
  }
  
  .search-button,
  .nearby-button {
    flex: 1;
  }
}
</style>
