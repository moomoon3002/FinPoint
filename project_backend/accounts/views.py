# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserUpdateSerializer, UserSerializer

User = get_user_model()

class SignUpView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'detail': '모든 필드를 입력하세요.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'detail': '이미 존재하는 사용자입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'detail': '회원가입 성공'}, status=status.HTTP_201_CREATED)

class CheckNicknameView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        nickname = request.data.get('nickname')
        if not nickname:
            return Response({'detail': '닉네임을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        exists = User.objects.filter(nickname=nickname).exists()
        if exists:
            return Response({'detail': '이미 사용 중인 닉네임입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': '사용 가능한 닉네임입니다.'}, status=status.HTTP_200_OK)

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(instance=serializer.instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
