<template>
  <div class="board-container">
    <h2>게시판</h2>
    
    <!-- 글쓰기 버튼 -->
    <div class="board-header">
      <router-link to="/board/write" class="write-btn">글쓰기</router-link>
    </div>

    <!-- 게시글 목록 -->
    <div class="board-list">
      <div class="board-item header">
        <span class="col id">번호</span>
        <span class="col title">제목</span>
        <span class="col author">작성자</span>
        <span class="col date">작성일</span>
      </div>

      <div v-if="articles.length === 0" class="no-articles">
        게시글이 없습니다.
      </div>

      <router-link
        v-for="article in articles"
        :key="article.id"
        :to="'/board/' + article.id"
        class="board-item"
      >
        <span class="col id">{{ article.id }}</span>
        <span class="col title">{{ article.title }}</span>
        <span class="col author">{{ article.author }}</span>
        <span class="col date">{{ formatDate(article.created_at) }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const articles = ref([])

const fetchArticles = async () => {
  try {
    const response = await axios.get('http://localhost:8000/articles/')
    articles.value = response.data
  } catch (error) {
    console.error('Failed to fetch articles:', error)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR')
}

onMounted(() => {
  fetchArticles()
})
</script>