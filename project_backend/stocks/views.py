from rest_framework.decorators import api_view
from rest_framework.response import Response
import openai
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from rest_framework.views import APIView
from rest_framework import status
from .models import Stock
from .serializers import StockSerializer
import requests
from django.conf import settings
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

# 환경 변수 로딩
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

def retry_on_exception(retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1:  # 마지막 시도에서 실패
                        raise e
                    logger.warning(f"Attempt {i + 1} failed: {str(e)}. Retrying...")
                    time.sleep(delay * (i + 1))  # 지수 백오프
            return None
        return wrapper
    return decorator

# 1. 주가 및 댓글 정보 크롤링
@api_view(['GET'])
def get_stock_info(request):
    query = request.GET.get('query')
    if not query:
        return Response({'error': '종목명을 입력해주세요.'}, status=400)

    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        wait = WebDriverWait(driver, 200)

        # 검색 페이지 로드 및 결과 대기
        search_url = f"https://tossinvest.com/search?query={query}"
        driver.get(search_url)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "a[href^='/stocks/']"))

        # 첫 번째 종목 링크 선택
        try:
            first_stock_link = driver.find_elements(By.CSS_SELECTOR, "a[href^='/stocks/']")[0]
        except IndexError:
            return Response({'error': '검색 결과를 찾을 수 없습니다.'}, status=404)

        href = first_stock_link.get_attribute("href")
        stock_code = href.split("/")[-1]
        stock_name = first_stock_link.text.strip()

        # 종목 상세 페이지
        driver.get(href)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".price-area span.value")))

        price_el = driver.find_element(By.CSS_SELECTOR, ".price-area span.value")
        change_el = driver.find_element(By.CSS_SELECTOR, ".price-area span.change")
        price = price_el.text.strip()
        change_text = change_el.text.strip()

        # 등락 방향 파악
        direction = 'neutral'
        if '▲' in change_text:
            direction = 'up'
        elif '▼' in change_text:
            direction = 'down'

        parts = change_text.replace('▲', '').replace('▼', '').strip().split()
        change_value = parts[0] if parts else ''
        change_percent = parts[-1].replace('%', '') if parts else ''

        # 댓글 추출 (최대 5개)
        comments = []
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, ".comment-card .content-text"))
        comment_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-card .content-text")
        time_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-card .date")
        for i, el in enumerate(comment_elements[:5]):
            comments.append({
                'id': i,
                'text': el.text.strip(),
                'time': time_elements[i].text.strip() if i < len(time_elements) else ''
            })

        return Response({
            'stockInfo': {
                'name': stock_name,
                'code': stock_code,
                'price': price,
                'change': change_value,
                'changePercent': change_percent,
                'direction': direction
            },
            'comments': comments
        })

    except TimeoutException:
        return Response({'error': '페이지 로드 또는 요소 대기 중 타임아웃'}, status=504)
    except NoSuchElementException as e:
        return Response({'error': f'크롤링 중 요소를 찾을 수 없음: {e}'}, status=500)
    except Exception as e:
        print("❌ Selenium 오류:", e)
        return Response({'error': str(e)}, status=500)
    finally:
        if driver:
            driver.quit()

# 2. OpenAI 분석 요청
@api_view(['POST'])
def analyze_sentiment(request):
    try:
        stock = request.data.get("stockInfo")
        comments = request.data.get("comments")

        if not stock or not comments:
            return Response({'error': '입력 데이터 부족'}, status=400)

        prompt = f"""
다음은 {stock['name']}의 주가 정보입니다:
- 현재가: {stock['price']}
- 변동: {stock['change']} ({stock['changePercent']}%)

최근 댓글:
{chr(10).join([f"- {c['text']}" for c in comments])}

이 정보를 바탕으로 현재 시장 반응과 투자자 심리를 간결하게 분석해 주세요.
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        result = response.choices[0].message.get("content", "").strip()
        return Response({'analysis': result})

    except Exception as e:
        print("❌ OpenAI 분석 오류:", e)
        return Response({'error': str(e)}, status=500)

class StockDataView(APIView):
    @retry_on_exception(retries=3, delay=2)
    def get_stock_data(self, symbol):
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920x1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            # 페이지 로드 타임아웃 설정 증가
            driver.set_page_load_timeout(30)
            wait = WebDriverWait(driver, 30)  # 대기 시간 30초로 증가

            # 종목 상세 페이지로 직접 이동
            url = f"https://tossinvest.com/stocks/{symbol}"
            driver.get(url)

            # 페이지 로딩 완료 대기
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

            # 주요 요소들이 모두 로드될 때까지 대기
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".price-area")))
            
            def get_element_safely(selector, wait_time=5):
                try:
                    element = WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return element.text.strip()
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                    logger.error(f"Error finding element {selector}: {str(e)}")
                    raise

            # 주가 정보 추출
            price_text = get_element_safely(".price-area span.value")
            change_text = get_element_safely(".price-area span.change")
            name_text = get_element_safely("h1.stock-name")
            volume_text = get_element_safely(".volume .value")

            # 데이터 파싱
            price = int(price_text.replace(',', ''))
            name = name_text
            volume = int(volume_text.replace(',', ''))

            # 등락 파싱
            parts = change_text.replace('▲', '').replace('▼', '').strip().split()
            change_value = int(parts[0].replace(',', ''))
            change_rate = float(parts[-1].replace('%', ''))

            if '▼' in change_text:
                change_value = -change_value
                change_rate = -change_rate

            return {
                'name': name,
                'current_price': price,
                'change': change_value,
                'change_rate': change_rate,
                'volume': volume
            }

        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            raise  # 재시도를 위해 예외를 다시 발생시킴
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.error(f"Error closing driver: {str(e)}")

    def generate_ai_analysis(self, stock_data):
        try:
            prompt = f"""
            다음 주식 데이터를 분석해주세요:
            종목명: {stock_data['name']}
            현재가: {stock_data['current_price']}원
            변동: {stock_data['change']}원 ({stock_data['change_rate']}%)
            거래량: {stock_data['volume']}

            위 데이터를 바탕으로 간단한 투자 의견을 제시해주세요.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional stock market analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating AI analysis: {str(e)}")
            return "AI 분석을 생성하는 중 오류가 발생했습니다."

    def get(self, request):
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({"error": "종목 심볼이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 웹 크롤링으로 데이터 가져오기
            stock_data = self.get_stock_data(symbol)
            if not stock_data:
                return Response({"error": "주식 데이터를 가져오는데 실패했습니다."}, 
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # AI 분석 생성
            ai_analysis = self.generate_ai_analysis(stock_data)

            # 데이터베이스에 저장
            stock, created = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': stock_data['name'],
                    'current_price': stock_data['current_price'],
                    'change': stock_data['change'],
                    'change_rate': stock_data['change_rate'],
                    'volume': stock_data['volume'],
                    'ai_analysis': ai_analysis
                }
            )

            serializer = StockSerializer(stock)
            return Response(serializer.data)

        except TimeoutException:
            return Response(
                {"error": "데이터를 가져오는 중 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."}, 
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "데이터를 가져오는 중 오류가 발생했습니다."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
