from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from allauth.account.adapter import get_adapter
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(required=True, max_length=20)
    age = serializers.IntegerField(required=False, default=0)
    gender = serializers.IntegerField(required=False, allow_null=True)
    salary = serializers.IntegerField(required=False, default=0)

    def validate_nickname(self, nickname):
        if User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return nickname

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError("나이는 0에서 150 사이여야 합니다.")
        return value

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'nickname': self.validated_data.get('nickname', ''),
            'age': self.validated_data.get('age', 0),
            'gender': self.validated_data.get('gender', None),
            'salary': self.validated_data.get('salary', 0),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        
        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('email')
        user.nickname = self.cleaned_data.get('nickname')
        user.age = self.cleaned_data.get('age')
        user.gender = self.cleaned_data.get('gender')
        user.salary = self.cleaned_data.get('salary')
        user.e_mail = self.cleaned_data.get('email')
        
        adapter.save_user(request, user, self)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'age', 'salary', 'profile_image')
        read_only_fields = ('username',)

    def validate_nickname(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def validate_age(self, value):
        if value is not None and (value < 0 or value > 150):
            raise serializers.ValidationError("나이는 0에서 150 사이여야 합니다.")
        return value

    def validate_salary(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("연봉은 0 이상이어야 합니다.")
        return value
