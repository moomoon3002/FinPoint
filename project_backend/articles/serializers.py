from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Article, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'nickname', 'profile_image', 'age', 'salary')


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('article', 'user',)


class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Article
        fields = ('id', 'title', 'author', 'created_at')

    def get_author(self, obj):
        return obj.user.nickname


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    author_id = serializers.SerializerMethodField(read_only=True)
    author_image = serializers.SerializerMethodField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'content', 'image', 
            'author', 'author_id', 'author_image',
            'created_at', 'comments'
        )
        read_only_fields = ('user', 'created_at')

    def get_author(self, obj):
        return obj.user.nickname

    def get_author_id(self, obj):
        return obj.user.id

    def get_author_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url
        return None

    def create(self, validated_data):
        user = self.context['request'].user
        article = Article.objects.create(user=user, **validated_data)
        return article

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance