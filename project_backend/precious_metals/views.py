from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from .serializers import MetalPriceSerializer, MetalPriceUploadSerializer
from .models import MetalPrice
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class MetalPriceListView(APIView):
    permission_classes = [AllowAny]  # 인증 없이도 접근 가능하도록 설정
    
    def get(self, request):
        metal_type = request.query_params.get('metal_type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        logger.info(f"Fetching metal prices with metal_type={metal_type}, start_date={start_date}, end_date={end_date}")
        
        try:
            # 기본 쿼리셋 생성
            queryset = MetalPrice.objects.all()
            
            # 금속 유형으로 필터링
            if metal_type:
                queryset = queryset.filter(metal_type=metal_type)
            
            # 날짜 범위로 필터링
            if start_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(date__gte=start_date)
                except ValueError:
                    logger.warning(f"Invalid start_date format: {start_date}")
            
            if end_date:
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(date__lte=end_date)
                except ValueError:
                    logger.warning(f"Invalid end_date format: {end_date}")
            
            # 날짜순으로 정렬
            queryset = queryset.order_by('date')
            
            # 쿼리셋 데이터 로깅
            logger.info(f"Query: {queryset.query}")
            logger.info(f"Count: {queryset.count()}")
            
            # 첫 번째와 마지막 레코드 로깅
            if queryset.exists():
                first_record = queryset.first()
                last_record = queryset.last()
                logger.info(f"First record: {first_record.date} - {first_record.close_price}")
                logger.info(f"Last record: {last_record.date} - {last_record.close_price}")
            
            serializer = MetalPriceSerializer(queryset, many=True)
            logger.info(f"Serialized data count: {len(serializer.data)}")
            
            if not serializer.data:
                logger.warning("No data found after serialization")
                return Response({'detail': '데이터가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
            
            # 응답 데이터 샘플 로깅
            sample_data = serializer.data[:2] if serializer.data else []
            logger.info(f"Sample response data: {sample_data}")
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}", exc_info=True)
            return Response({'detail': '데이터를 가져오는 중 오류가 발생했습니다.'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MetalPriceUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = MetalPriceUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = request.FILES['file']
            metal_type = serializer.validated_data['metal_type']
            
            try:
                # 엑셀 파일 읽기
                df = pd.read_excel(file)
                
                # 데이터 처리 및 저장
                for _, row in df.iterrows():
                    # 날짜 처리
                    date_str = str(row['Date'])
                    try:
                        # 다양한 날짜 형식 처리
                        date_obj = pd.to_datetime(date_str).date()
                    except Exception as e:
                        logger.error(f"Error parsing date {date_str}: {str(e)}")
                        continue
                    
                    # 숫자 데이터 처리
                    try:
                        close_price = float(str(row['Close/Last']).replace(',', ''))
                        volume = int(str(row['Volume']).replace(',', ''))
                        open_price = float(str(row['Open']).replace(',', ''))
                        high_price = float(str(row['High']).replace(',', ''))
                        low_price = float(str(row['Low']).replace(',', ''))
                    except Exception as e:
                        logger.error(f"Error parsing numeric data for date {date_str}: {str(e)}")
                        continue
                    
                    try:
                        MetalPrice.objects.update_or_create(
                            metal_type=metal_type,
                            date=date_obj,
                            defaults={
                                'close_price': close_price,
                                'volume': volume,
                                'open_price': open_price,
                                'high_price': high_price,
                                'low_price': low_price
                            }
                        )
                    except Exception as e:
                        logger.error(f"Error saving data for date {date_str}: {str(e)}")
                        continue
                
                return Response({'detail': '데이터가 성공적으로 업로드되었습니다.'}, 
                              status=status.HTTP_201_CREATED)
            
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return Response({'detail': f'파일 처리 중 오류가 발생했습니다: {str(e)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
