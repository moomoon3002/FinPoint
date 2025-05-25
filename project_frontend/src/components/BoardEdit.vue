<template>
  <div class="edit-container">
    <h2>글 수정</h2>
    
    <form v-if="article" @submit.prevent="submitEdit" class="edit-form">
      <div class="form-group">
        <label for="title">제목</label>
        <input 
          type="text" 
          id="title" 
          v-model="article.title" 
          required 
          placeholder="제목을 입력하세요"
        >
      </div>

      <div class="form-group">
        <label for="content">내용</label>
        <textarea 
          id="content" 
          v-model="article.content" 
          required 
          placeholder="내용을 입력하세요"
          rows="10"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="image">이미지</label>
        <input 
          type="file" 
          id="image" 
          @change="handleImageChange" 
          accept="image/*"
        >
        <img 
          v-if="imagePreview || article.image" 
          :src="imagePreview || article.image" 
          class="image-preview" 
          alt="미리보기"
        >
      </div>

      <div class="form-actions">
        <button type="submit" class="submit-btn">수정하기</button>
        <router-link :to="'/board/' + article.id" class="cancel-btn">취소</router-link>
      </div>
    </form>

    <div v-else class="loading">
      로딩 중...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const article = ref(null)
const imagePreview = ref(null)
const newImage = ref(null)

const fetchArticle = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:8000/articles/${route.params.id}/`, {
      headers: { Authorization: `Token ${token}` }
    })
    article.value = response.data
  } catch (error) {
    console.error('Failed to fetch article:', error)
    router.push('/board')
  }
}

const handleImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    newImage.value = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

const submitEdit = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      alert('로그인이 필요합니다.')
      router.push('/login')
      return
    }

    const formData = new FormData()
    formData.append('title', article.value.title)
    formData.append('content', article.value.content)
    if (newImage.value) {
      formData.append('image', newImage.value)
    }

    await axios.put(`http://localhost:8000/articles/${article.value.id}/`, formData, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    router.push(`/board/${article.value.id}`)
  } catch (error) {
    console.error('Failed to update article:', error)
    alert('게시글 수정에 실패했습니다.')
  }
}

onMounted(() => {
  fetchArticle()
})
</script>

<style scoped>
.edit-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.edit-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input[type="text"],
textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

textarea {
  resize: vertical;
}

.image-preview {
  max-width: 100%;
  margin-top: 1rem;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.submit-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
}

.submit-btn {
  background-color: #2a388f;
  color: white;
  border: none;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.submit-btn:hover {
  background-color: #1a287f;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style> 