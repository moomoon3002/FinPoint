<template>
  <div class="article-container">
    <div v-if="article" class="article-content">
      <div class="article-header">
        <h2>{{ article.title }}</h2>
        <div class="article-meta">
          <span class="author">
            <img 
              :src="getImageUrl(article.author_image)" 
              class="author-image" 
              alt="프로필 이미지"
            >
            {{ article.author }}
          </span>
          <span class="date">{{ formatDate(article.created_at) }}</span>
        </div>
      </div>

      <div class="article-body">
        <img v-if="article.image" :src="getImageUrl(article.image)" class="article-image" alt="게시글 이미지">
        <div class="article-text">
          {{ article.content }}
        </div>
      </div>

      <!-- 게시글 작성자만 볼 수 있는 수정/삭제 버튼 -->
      <div v-if="isArticleAuthor" class="article-actions">
        <router-link :to="'/board/edit/' + article.id" class="edit-btn">수정하기</router-link>
        <button @click="handleDelete" class="delete-btn">삭제하기</button>
      </div>

      <!-- 댓글 섹션 -->
      <div class="comments-section">
        <h3>댓글</h3>
        
        <!-- 댓글 작성 폼 -->
        <div v-if="isLoggedIn" class="comment-form">
          <textarea 
            v-model="newComment" 
            placeholder="댓글을 입력하세요"
            rows="3"
          ></textarea>
          <button @click="submitComment" class="submit-comment-btn">댓글 작성</button>
        </div>
        <div v-else class="login-message">
          <router-link to="/login">로그인</router-link>하고 댓글을 작성하세요.
        </div>

        <!-- 댓글 목록 -->
        <div class="comments-list">
          <div v-for="comment in article.comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <div class="comment-author">
                <img 
                  :src="getImageUrl(comment.user?.profile_image)" 
                  class="comment-author-image" 
                  alt="프로필 이미지"
                >
                <span>{{ comment.user?.nickname || '알 수 없음' }}</span>
              </div>
              <div class="comment-meta">
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                <!-- 댓글 작성자만 볼 수 있는 수정/삭제 버튼 -->
                <div v-if="currentUser && currentUser.id && comment.user && comment.user.id && currentUser.id === comment.user.id" class="comment-actions">
                  <button @click="editComment(comment)" class="edit-comment-btn">수정</button>
                  <button @click="deleteComment(comment.id)" class="delete-comment-btn">삭제</button>
                </div>
              </div>
            </div>
            <!-- 댓글 수정 폼 -->
            <div v-if="editingCommentId === comment.id" class="comment-edit-form">
              <textarea 
                v-model="editingCommentContent" 
                class="comment-edit-textarea"
                rows="3"
              ></textarea>
              <div class="comment-edit-actions">
                <button @click="updateComment(comment.id)" class="save-comment-btn">저장</button>
                <button @click="cancelEdit" class="cancel-comment-btn">취소</button>
              </div>
            </div>
            <!-- 일반 댓글 내용 -->
            <div v-else class="comment-content">
              {{ comment.content }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="loading">
      로딩 중...
    </div>

    <div class="article-navigation">
      <router-link to="/board" class="back-btn">목록으로</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const article = ref(null)
const currentUser = ref(null)
const newComment = ref('')
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

// 댓글 수정 관련 상태
const editingCommentId = ref(null)
const editingCommentContent = ref('')

// 게시글 작성자 확인
const isArticleAuthor = computed(() => {
  console.log('[Debug] Checking article author:', {
    currentUser: currentUser.value,
    currentUserId: currentUser.value?.id,
    article: article.value,
    articleAuthorId: article.value?.author_id
  });
  return currentUser.value && 
         currentUser.value.id && 
         article.value && 
         article.value.author_id && 
         currentUser.value.id === article.value.author_id;
});

// 이미지 URL 처리
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return '/default-profile.png'
  if (imageUrl.startsWith('/media/')) {
    return `http://localhost:8000${imageUrl}`
  }
  if (!imageUrl.startsWith('http')) {
    return `http://localhost:8000${imageUrl}`
  }
  return imageUrl
}

// 게시글 정보 가져오기
const fetchArticle = async () => {
  try {
    const token = localStorage.getItem('token')
    const headers = token ? { Authorization: `Token ${token}` } : {}
    console.log('[Debug] Fetching article with ID:', route.params.id)
    const response = await axios.get(`http://localhost:8000/articles/${route.params.id}/`, { headers })
    console.log('[Debug] Article API response:', response.data)
    
    if (!response.data) {
      throw new Error('No data received')
    }
    
    article.value = {
      ...response.data,
      comments: (response.data.comments || []).map(comment => ({
        ...comment,
        user: comment.user || null
      }))
    }
    
    console.log('[Debug] Processed article:', article.value)
    console.log('[Debug] Article author check:', {
      authorId: article.value.author_id,
      currentUserId: currentUser.value?.id,
      isAuthor: currentUser.value?.id === article.value.author_id
    })
  } catch (error) {
    console.error('[Debug] Failed to fetch article:', error.response || error)
    alert('게시글을 불러오는데 실패했습니다.')
    router.push('/board')
  }
}

// 게시글 삭제 처리
const handleDelete = async () => {
  if (!confirm('정말로 이 게시글을 삭제하시겠습니까?')) {
    return
  }

  try {
    const token = localStorage.getItem('token')
    await axios.delete(`http://localhost:8000/articles/${article.value.id}/`, {
      headers: { Authorization: `Token ${token}` }
    })
    alert('게시글이 삭제되었습니다.')
    router.push('/board')
  } catch (error) {
    console.error('Failed to delete article:', error)
    alert('게시글 삭제에 실패했습니다.')
  }
}

// 댓글 작성
const submitComment = async () => {
  if (!newComment.value.trim()) return

  try {
    const token = localStorage.getItem('token')
    await axios.post(
      `http://localhost:8000/articles/${article.value.id}/comments/`,
      { content: newComment.value },
      { headers: { Authorization: `Token ${token}` } }
    )
    newComment.value = ''
    await fetchArticle()
  } catch (error) {
    console.error('Failed to submit comment:', error)
    alert('댓글 작성에 실패했습니다.')
  }
}

// 댓글 수정 시작
const editComment = (comment) => {
  editingCommentId.value = comment.id;
  editingCommentContent.value = comment.content;
};

// 댓글 수정 취소
const cancelEdit = () => {
  editingCommentId.value = null;
  editingCommentContent.value = '';
};

// 댓글 수정 저장
const updateComment = async (commentId) => {
  if (!editingCommentContent.value.trim()) {
    alert('댓글 내용을 입력해주세요.');
    return;
  }

  try {
    const token = localStorage.getItem('token');
    await axios.put(
      `http://localhost:8000/articles/${article.value.id}/comments/${commentId}/`,
      { content: editingCommentContent.value },
      { headers: { Authorization: `Token ${token}` } }
    );
    await fetchArticle(); // 댓글 목록 새로고침
    cancelEdit(); // 수정 모드 종료
    alert('댓글이 수정되었습니다.');
  } catch (error) {
    console.error('Failed to update comment:', error);
    alert('댓글 수정에 실패했습니다.');
  }
};

// 댓글 삭제
const deleteComment = async (commentId) => {
  if (!confirm('정말로 이 댓글을 삭제하시겠습니까?')) {
    return;
  }

  try {
    const token = localStorage.getItem('token');
    await axios.delete(
      `http://localhost:8000/articles/${article.value.id}/comments/${commentId}/`,
      { headers: { Authorization: `Token ${token}` } }
    );
    await fetchArticle(); // 댓글 목록 새로고침
    alert('댓글이 삭제되었습니다.');
  } catch (error) {
    console.error('Failed to delete comment:', error);
    alert('댓글 삭제에 실패했습니다.');
  }
};

// 댓글 작성자 확인 함수 (디버깅용으로만 사용)
const isCommentAuthor = (comment) => {
  console.log('[Debug] Checking comment author:', {
    comment,
    commentUserId: comment.user?.id,
    currentUser: currentUser.value,
    currentUserId: currentUser.value?.id,
    isAuthor: currentUser.value && 
              currentUser.value.id && 
              comment.user && 
              comment.user.id && 
              currentUser.value.id === comment.user.id
  })
  return currentUser.value && 
         currentUser.value.id && 
         comment.user && 
         comment.user.id && 
         currentUser.value.id === comment.user.id
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 현재 로그인한 사용자 정보 가져오기
const fetchCurrentUser = async () => {
  const token = localStorage.getItem('token')
  console.log('[Debug] Fetching current user with token:', token)
  if (token) {
    try {
      const response = await axios.get('http://localhost:8000/accounts/user/', {
        headers: { Authorization: `Token ${token}` }
      })
      console.log('[Debug] Current user API response:', response.data)
      currentUser.value = response.data
      console.log('[Debug] Set currentUser to:', currentUser.value)
    } catch (error) {
      console.error('[Debug] Failed to fetch user info:', error.response || error)
      currentUser.value = null
    }
  } else {
    console.log('[Debug] No token found')
    currentUser.value = null
  }
}

onMounted(async () => {
  console.log('[Debug] Component mounted')
  try {
    await fetchCurrentUser()
    console.log('[Debug] After fetchCurrentUser:', currentUser.value)
    await fetchArticle()
    console.log('[Debug] After fetchArticle:', article.value)
    console.log('[Debug] Final author check:', {
      currentUser: currentUser.value,
      article: article.value,
      isAuthor: isArticleAuthor.value
    })
  } catch (error) {
    console.error('[Debug] Error in onMounted:', error)
  }
})
</script>

<style scoped>
.article-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.article-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.article-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #666;
  margin-top: 1rem;
}

.author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-image, .comment-author-image {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
  background-color: #f8f8f8;
}

.article-body {
  margin-bottom: 2rem;
}

.article-image {
  max-width: 100%;
  margin-bottom: 1rem;
  border-radius: 4px;
}

.article-text {
  line-height: 1.6;
  white-space: pre-wrap;
}

.article-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.edit-btn, 
.delete-btn {
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-btn {
  background-color: #2a388f;
  color: white;
  text-decoration: none;
}

.edit-btn:hover {
  background-color: #1a287f;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
}

.delete-btn:hover {
  background-color: #c82333;
}

.comments-section {
  margin-top: 3rem;
  border-top: 1px solid #eee;
  padding-top: 2rem;
}

.comment-form {
  margin-bottom: 2rem;
}

.comment-form textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  margin-bottom: 1rem;
}

.submit-comment-btn {
  padding: 0.5rem 1rem;
  background-color: #2a388f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-message {
  margin-bottom: 2rem;
  color: #666;
}

.login-message a {
  color: #2a388f;
  text-decoration: none;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-item {
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 4px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.comment-date {
  color: #666;
  font-size: 0.9rem;
}

.comment-content {
  line-height: 1.4;
  margin: 0.5rem 0;
}

.comment-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-comment-btn,
.delete-comment-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-comment-btn {
  background-color: #2a388f;
  color: white;
}

.edit-comment-btn:hover {
  background-color: #1a287f;
}

.delete-comment-btn {
  background-color: #dc3545;
  color: white;
}

.delete-comment-btn:hover {
  background-color: #c82333;
}

.comment-edit-form {
  margin-top: 0.5rem;
}

.comment-edit-textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  margin-bottom: 0.5rem;
}

.comment-edit-actions {
  display: flex;
  gap: 0.5rem;
}

.save-comment-btn,
.cancel-comment-btn {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.save-comment-btn {
  background-color: #28a745;
  color: white;
}

.save-comment-btn:hover {
  background-color: #218838;
}

.cancel-comment-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-comment-btn:hover {
  background-color: #5a6268;
}

.article-navigation {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

.back-btn {
  padding: 0.5rem 1.5rem;
  background-color: #6c757d;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background-color: #5a6268;
}
</style> 