from django.contrib import admin
from .models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_nickname', 'created_at', 'updated_at')

    def user_nickname(self, obj):
        return obj.user.nickname
    user_nickname.short_description = '작성자 닉네임'

admin.site.register(Article, ArticleAdmin)