from rest_framework import generics
from .models import DepositProduct
from .serializers import DepositProductSerializer

class DepositProductListView(generics.ListAPIView):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer

class DepositProductDetailView(generics.RetrieveAPIView):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer
    lookup_field = 'deposit_ID'