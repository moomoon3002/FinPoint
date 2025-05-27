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