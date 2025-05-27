from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as filters
from .models import DepositProduct, DepositOption, FavoriteDeposit
from .serializers import DepositProductSerializer, DepositOptionSerializer, FavoriteDepositSerializer

class DepositProductFilter(filters.FilterSet):
    min_rate = filters.NumberFilter(field_name='options__intr_rate', lookup_expr='gte')
    bank = filters.CharFilter(field_name='kor_co_nm', lookup_expr='icontains')
    product_name = filters.CharFilter(field_name='fin_prdt_nm', lookup_expr='icontains')
    period = filters.NumberFilter(field_name='options__save_trm')

    class Meta:
        model = DepositProduct
        fields = ['product_type', 'min_rate', 'bank', 'product_name', 'period']

class DepositProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepositProduct.objects.all().prefetch_related('options')
    serializer_class = DepositProductSerializer
    filterset_class = DepositProductFilter
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def options(self, request, pk=None):
        product = self.get_object()
        options = product.options.all()
        serializer = DepositOptionSerializer(options, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        product = self.get_object()
        user = request.user

        if request.method == 'POST':
            favorite, created = FavoriteDeposit.objects.get_or_create(user=user, deposit=product)
            if created:
                return Response({'status': 'added to favorites'}, status=status.HTTP_201_CREATED)
            return Response({'status': 'already in favorites'}, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            try:
                favorite = FavoriteDeposit.objects.get(user=user, deposit=product)
                favorite.delete()
                return Response({'status': 'removed from favorites'}, status=status.HTTP_200_OK)
            except FavoriteDeposit.DoesNotExist:
                return Response({'status': 'not in favorites'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_favorites(self, request):
        favorites = FavoriteDeposit.objects.filter(user=request.user).select_related('deposit')
        serializer = FavoriteDepositSerializer(favorites, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorites(request):
    favorites = FavoriteDeposit.objects.filter(user=request.user)
    serializer = FavoriteDepositSerializer(favorites, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request, product_id):
    try:
        product = DepositProduct.objects.get(deposit_ID=product_id)
        favorite, created = FavoriteDeposit.objects.get_or_create(
            user=request.user,
            deposit=product
        )
        if created:
            serializer = FavoriteDepositSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': '이미 관심상품으로 등록되어 있습니다.'}, status=status.HTTP_200_OK)
    except DepositProduct.DoesNotExist:
        return Response({'error': '상품을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, product_id):
    try:
        favorite = FavoriteDeposit.objects.get(user=request.user, deposit_id=product_id)
        favorite.delete()
        return Response({'message': '관심상품이 해제되었습니다.'}, status=status.HTTP_200_OK)
    except FavoriteDeposit.DoesNotExist:
        return Response({'error': '관심상품을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_favorite(request, product_id):
    try:
        is_favorite = FavoriteDeposit.objects.filter(
            user=request.user,
            deposit_id=product_id
        ).exists()
        return Response({'is_favorite': is_favorite})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_recommend(request):
    age = int(request.data.get('age', 0))
    salary = int(request.data.get('salary', 0))
    period = int(request.data.get('period', 0))

    if not period:
        return Response({'error': '가입 기간을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

    # 추천 로직: 30세 이하 & 연봉 4000만원 이하 → 적금, 그 외 → 예금
    if age <= 30 and salary <= 40000000:
        products = DepositProduct.objects.filter(product_type='적금').prefetch_related('options')
    else:
        products = DepositProduct.objects.filter(product_type='예금').prefetch_related('options')

    recommend_list = []
    for product in products:
        # 입력한 기간과 일치하는 옵션 찾기
        matching_options = [opt for opt in product.options.all() if int(opt.save_trm) == period]
        if not matching_options:
            continue
        
        # 해당 기간의 최고 금리 옵션 선택
        best_option = max(matching_options, key=lambda o: float(o.intr_rate or 0))
        recommend_list.append({
            'name': product.fin_prdt_nm,
            'bank': product.kor_co_nm,
            'interestRate': float(best_option.intr_rate or 0),
            'period': int(best_option.save_trm or 0)
        })

    # 금리 높은 순으로 3개 추천
    recommend_list = sorted(recommend_list, key=lambda x: x['interestRate'], reverse=True)[:3]

    return Response({'recommendations': recommend_list})