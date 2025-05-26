from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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