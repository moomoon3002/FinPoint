<template>
  <div class="main-wrapper">

    <!-- 나머지 컨텐츠 ... -->


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

    <!-- 나머지 섹션 -->
    <section ref="calendar" style="min-height:100vh; padding:60px 0; background:#fff;">
      <div style="text-align:center; font-size:2rem; color:#2a388c;">캘린더 영역</div>
    </section>
    <section ref="community" style="min-height:100vh; padding:60px 0; background:#f5f8fe;">
      <div style="text-align:center; font-size:2rem; color:#2a388c;">커뮤니티 영역</div>
    </section>
    <section ref="board" style="min-height:100vh; padding:60px 0; background:#fff;">
      <div style="text-align:center; font-size:2rem; color:#2a388c;">게시판 영역</div>
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
</script>