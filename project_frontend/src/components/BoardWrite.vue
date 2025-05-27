<template>
  <div class="write-container">
    <h2>글쓰기</h2>
    
    <form @submit.prevent="submitArticle" class="write-form">
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
        <img v-if="imagePreview" :src="imagePreview" class="image-preview" alt="미리보기">
      </div>

      <div class="form-actions">
        <button type="submit" class="submit-btn">작성하기</button>
        <router-link to="/board" class="cancel-btn">취소</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const article = ref({
  title: '',
  content: '',
  image: null
})
const imagePreview = ref(null)

const handleImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    article.value.image = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

const submitArticle = async () => {
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
    if (article.value.image) {
      formData.append('image', article.value.image)
    }

    await axios.post('http://localhost:8000/articles/', formData, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    router.push('/board')
  } catch (error) {
    console.error('Failed to create article:', error)
    alert('게시글 작성에 실패했습니다.')
  }
}
</script>

<style scoped>
.write-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.write-form {
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
  justify-content: flex-end;
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
</style> 