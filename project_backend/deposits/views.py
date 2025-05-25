from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from .models import DepositProduct, DepositOption
from .serializers import DepositProductSerializer, DepositOptionSerializer

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