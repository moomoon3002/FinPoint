<template>
  <div class="main-wrapper">

    <!-- 메인 랜딩 섹션 -->
    <section class="hero-section">
      <div class="hero-content">
        <!-- 떠다니는 은행 로고들 -->
        <div class="floating-logos">
          <div class="logo-card floating floating-1">
            <img src="/img/shinhan.png" alt="신한은행" class="bank-logo-img" />
          </div>
          <div class="logo-card floating floating-2">
            <img src="/img/kb.png" alt="국민은행" class="bank-logo-img" />
          </div>
          <div class="logo-card floating floating-3">
            <img src="/img/woori.png" alt="우리은행" class="bank-logo-img" />
          </div>
          <div class="logo-card floating floating-4">
            <img src="/img/hana.png" alt="하나은행" class="bank-logo-img" />
          </div>
          <div class="logo-card floating floating-5">
            <img src="/img/shbank.png" alt="수협은행" class="bank-logo-img" />
          </div>
        </div>

        <!-- START 버튼 -->
        <button class="start-button" @click="goToDeposit">
          START
          <span class="arrow">→</span>
        </button>
      </div>
    </section>

    <!-- 캘린더 영역 -->
    <section ref="calendar" style="min-height:100vh; padding:60px 0; background:#fff;">
      <div style="text-align:center; font-size:2rem; color:#2a388c;"></div>
      
    </section>

    <!-- 은행찾기 영역 -->
    <section ref="community" style="min-height:100vh; padding:60px 0; background:#f5f8fe;">
      <div style="text-align:center; font-size:2rem; color:#2a388c; margin-bottom:24px;">
      </div>
      <div class="bank-finder-area" style="display:flex; flex-direction:column; align-items:center;">
        <div class="map-container">
          <img
            src="/img/map-placeholder.png"
            alt="지도 이미지"
            class="map-img"
          />
          <img
            src="/img/red_location.png"
            alt="움직이는 마커"
            class="marker-animate"
            style="
              position:absolute;
              left:460px;
              top:345px;  
              width:100px;
              height:100px;
              z-index:2;
              pointer-events:none;
            "
          />
        </div>
        <button class="find-bank-btn" @click="goToBankFinder" style="margin-top:32px;">
          은행찾기
        </button>
      </div>
    </section>

    <!-- 게시판 영역 -->
    <section ref="board" style="min-height:100vh; padding:100px 0 60px 0; background:#fff;">
      <div class="board-main-wrap">
        <!-- 왼쪽 큰 이미지 + 아래 텍스트 -->
        <div class="board-main-left">
          <img src="/img/board-main-1.png" alt="대표 이미지" class="board-main-img-lg" />
          <div class="board-main-desc">
            <span class="board-main-title">고민부터<br />자산관리 꿀팁까지</span><br />
            <span class="board-main-sub">간편하게 공유</span>
          </div>
        </div>
        <!-- 가운데 작은 이미지 -->
        <div class="board-main-center">
          <img src="/img/board-main-2.png" alt="서브 이미지" class="board-main-img-sm" />
        </div>
        <!-- 오른쪽 설명 텍스트 -->
        <div class="board-main-right">
          <div class="board-main-text">
            <span class="board-main-title">
              자산관리 꿀팁을<br />
              공유하고
            </span><br />
            <span class="board-main-sub">
              궁금한 점을 쉽게<br />
              물어보세요!
            </span>
          </div>
        </div>
      </div>
        <button class="board-btn-area" @click="goToBoard">
          게시판 바로가기
        </button>
    </section>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const calendar = ref(null)
const community = ref(null)
const board = ref(null)

function scrollTo(section) {
  if (section === 'calendar' && calendar.value) calendar.value.scrollIntoView({ behavior: 'smooth' })
  if (section === 'community' && community.value) community.value.scrollIntoView({ behavior: 'smooth' })
  if (section === 'board' && board.value) board.value.scrollIntoView({ behavior: 'smooth' })
}

function goToDeposit() {
  router.push('/deposit')
}

function goToLogin() {
  router.push('/login')
}

// 게시판 바로가기 버튼 이동 함수
function goToBoard() {
  router.push('/board')
}
</script>
