from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from bs4 import BeautifulSoup
import json
import re

@api_view(['GET'])
def get_stock_info(request):
    query = request.GET.get('query')
    if not query:
        return Response({'error': '종목명을 입력해주세요.'}, status=400)

    try:
        # 토스증권 검색 API를 통해 종목 정보 가져오기
        search_url = f"https://finance.toss.im/api/search?keyword={query}"
        response = requests.get(search_url)
        search_data = response.json()

        if not search_data['stocks']:
            return Response({'error': '종목을 찾을 수 없습니다.'}, status=404)

        # 첫 번째 검색 결과 사용
        stock = search_data['stocks'][0]
        code = stock['code']

        # 종목 상세 정보 가져오기
        detail_url = f"https://finance.toss.im/api/stocks/{code}"
        detail_response = requests.get(detail_url)
        stock_data = detail_response.json()

        # 댓글 정보 가져오기
        comments_url = f"https://finance.toss.im/api/stocks/{code}/discussion"
        comments_response = requests.get(comments_url)
        comments_data = comments_response.json()

        # 응답 데이터 구성
        stock_info = {
            'name': stock['name'],
            'code': code,
            'price': stock_data['price']['current'],
            'change': stock_data['price']['change'],
            'changePercent': stock_data['price']['changePercent'],
        }

        comments = []
        for comment in comments_data['comments'][:5]:  # 최근 5개 댓글만
            comments.append({
                'id': comment['id'],
                'text': comment['content'],
                'time': comment['createdAt']
            })

        return Response({
            'stockInfo': stock_info,
            'comments': comments
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500) 