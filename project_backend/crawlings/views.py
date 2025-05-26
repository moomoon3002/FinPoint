from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from .models import StockData, UserStockInterest
import time
import os
from datetime import datetime, timedelta
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import StockDataSerializer, UserStockInterestSerializer
import yfinance as yf
import json
from django.utils import timezone

logger = logging.getLogger(__name__)

# Selenium 기본 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.add_argument("--window-size=800,600")
service = Service(ChromeDriverManager().install())

# OpenAI API 키 설정
api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key is not set. Please set OPENAI_API_KEY in your environment variables or settings.")

client = OpenAI(api_key=api_key)

def ask_comment(prompt, model="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in analyzing stock market trends and sentiment. Please provide your analysis in Korean."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"오류 발생: {e}"

def get_stock_price_and_trend(driver):
    try:
        logger.info("\n[1/3] 페이지 로딩 확인")
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(10)
        logger.info("- 페이지 로딩 완료")

        # 현재가 정보 가져오기
        logger.info("\n[2/3] 현재가 정보 수집")
        try:
            price_selector = "main > div > div > div > div:nth-child(3) > div > div:nth-child(3) > div:nth-child(2) > span:nth-child(1)"
            current_price_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, price_selector))
            )
            current_price_text = current_price_element.text.strip()
            current_price = int(''.join(filter(str.isdigit, current_price_text)))
            logger.info(f"- 현재가 추출: {current_price:,}원")
        except Exception as e:
            logger.error(f"- 현재가 추출 실패: {e}")
            raise Exception("현재가를 찾을 수 없습니다")

        # 날짜 정보 가져오기
        logger.info("\n[3/3] 날짜 및 변동 정보 수집")
        try:
            # 날짜 정보 (두 번째 span)
            date_selector = "main > div > div > div > div:nth-child(3) > div > div:nth-child(3) > div:nth-child(2) > span:nth-child(2)"
            date_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, date_selector))
            )
            current_date = date_element.text.strip()
            # "보다" 제거
            if "보다" in current_date:
                current_date = current_date.replace("보다", "").strip()
            logger.info(f"- 날짜 추출: {current_date}")
        except Exception as e:
            logger.error(f"- 날짜 추출 실패: {e}")
            current_date = datetime.now().strftime("%m월 %d일")

        # 변동 정보 가져오기
        try:
            # 변동 정보 (세 번째 span 내부의 span)
            change_selector = "main > div > div > div > div:nth-child(3) > div > div:nth-child(3) > div:nth-child(2) > span:nth-child(3) > span"
            change_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, change_selector))
            )
            change_text = change_element.text.strip()
            logger.info(f"- 변동 정보 추출: {change_text}")
            
            if not change_text or '%' not in change_text:
                change_text = "0원 (0.0%)"
        except Exception as e:
            logger.error(f"- 변동 정보 추출 실패: {e}")
            try:
                # 폴백: 세 번째 span 전체를 시도
                fallback_selector = "main > div > div > div > div:nth-child(3) > div > div:nth-child(3) > div:nth-child(2) > span:nth-child(3)"
                change_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, fallback_selector))
                )
                change_text = change_element.text.strip()
                if not change_text or '%' not in change_text:
                    change_text = "0원 (0.0%)"
            except Exception as e2:
                logger.error(f"- 폴백 변동 정보 추출 실패: {e2}")
                change_text = "0원 (0.0%)"

        # 색상 정보 결정 (+/- 기호로 판단)
        change_color = 'red' if '+' in change_text else 'blue' if '-' in change_text else 'black'

        result = {
            'current_price': current_price,
            'previous_date': current_date,
            'change_text': change_text,
            'change_color': change_color
        }

        logger.info("\n=== 수집 결과 ===")
        logger.info(f"현재가: {current_price:,}원")
        logger.info(f"기준일: {current_date}")
        logger.info(f"변동 정보: {change_text} ({change_color})")
        logger.info("================\n")
        return result

    except Exception as e:
        logger.error(f"\n[!] 주가 정보 수집 중 오류 발생: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return None

def get_stock_code_and_name(driver, company_name):
    try:
        logger.info("\n=== 크롤링 시작 ===")
        logger.info(f"검색어: '{company_name}'")
        
        # 회사명으로 종목코드 매핑
        company_codes = {
            '엘지전자': '066570',
            'lg전자': '066570',
            'LG전자': '066570',
            'LG Electronics': '066570',
            '삼성전자': '005930',
            'samsung electronics': '005930',
            'SAMSUNG ELECTRONICS': '005930',
            '현대차': '005380',
            '현대자동차': '005380',
            'HYUNDAI MOTOR': '005380',
            'SK하이닉스': '000660',
            'sk하이닉스': '000660',
            'SK HYNIX': '000660'
        }
        
        # 매핑된 종목코드가 있으면 직접 URL 접근
        stock_code = company_codes.get(company_name.lower())
        if stock_code:
            direct_url = f'https://tossinvest.com/stocks/{stock_code}'
            logger.info(f"\n[1/4] 직접 URL 접근 시도: {direct_url}")
            driver.get(direct_url)
            logger.info("페이지 로딩 중...")
            time.sleep(7)
        else:
            # 토스증권 메인 페이지로 이동
            logger.info("\n[1/4] 토스증권 메인 페이지 접속")
            driver.get('https://tossinvest.com/')
            logger.info("메인 페이지 로딩 중...")
            
            # 페이지 로딩 대기
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(5)

            try:
                logger.info("\n[2/4] 검색 시도")
                # 검색 버튼 클릭
                logger.info("- 검색 버튼 찾는 중...")
                search_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'u09klc0'))
                )
                ActionChains(driver).move_to_element(search_button).click().perform()
                logger.info("- 검색 버튼 클릭 완료")
                time.sleep(2)

                # 검색어 입력
                logger.info("- 검색창에 입력 중...")
                search_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, '_1x1gpvi6'))
                )
                search_input.clear()
                search_input.send_keys(company_name)
                time.sleep(2)
                search_input.send_keys(Keys.RETURN)
                logger.info(f"- '{company_name}' 검색어 입력 완료")
                time.sleep(3)

                # 첫 번째 검색 결과 클릭
                logger.info("\n[3/4] 검색 결과 선택")
                logger.info("- 첫 번째 결과 클릭 시도...")
                first_result = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'u09klc0'))
                )
                ActionChains(driver).move_to_element(first_result).click().perform()
                logger.info("- 종목 페이지로 이동 중...")
                time.sleep(5)

            except Exception as e:
                logger.error(f"\n[!] 검색 과정 실패: {e}")
                if company_name.isdigit() and len(company_name) == 6:
                    direct_url = f'https://tossinvest.com/stocks/{company_name}'
                    logger.info(f"- 직접 URL 접근 시도: {direct_url}")
                    driver.get(direct_url)
                    time.sleep(5)
                else:
                    raise Exception("종목을 찾을 수 없습니다")

        # 종목명과 종목코드 가져오기
        logger.info("\n[4/4] 종목 정보 수집")
        try:
            logger.info("- 종목명과 코드 추출 시도...")
            
            # 페이지 완전 로딩 대기
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(5)
            
            # 모든 div 요소 가져오기
            divs = driver.find_elements(By.CSS_SELECTOR, "div._1sivumi0 div")
            
            if not divs:
                raise Exception("종목 정보 컨테이너를 찾을 수 없습니다")
            
            # 첫 번째 div의 모든 span 요소 확인
            name = None
            extracted_code = None
            
            for div in divs:
                spans = div.find_elements(By.TAG_NAME, "span")
                for span in spans:
                    text = span.text.strip()
                    logger.info(f"검사 중인 텍스트: {text}")
                    
                    # 종목코드 형식 확인 (숫자 6자리)
                    if text and any(c.isdigit() for c in text):
                        digits = ''.join(filter(str.isdigit, text))
                        if len(digits) == 6:
                            extracted_code = digits
                            logger.info(f"- 종목코드 발견: {extracted_code}")
                    
                    # 종목명이 아직 없고, 숫자가 없는 경우 종목명으로 간주
                    elif text and not name and not any(c.isdigit() for c in text):
                        name = text
                        logger.info(f"- 종목명 발견: {name}")
                    
                    if name and extracted_code:
                        break
                if name and extracted_code:
                    break
            
            if not extracted_code:
                if stock_code:  # 미리 매핑된 종목코드가 있으면 사용
                    extracted_code = stock_code
                    logger.info(f"- 미리 매핑된 종목코드 사용: {stock_code}")
                else:
                    raise Exception("올바른 종목 코드를 찾을 수 없습니다")
            
            if not name:
                name = company_name
                logger.info(f"- 입력된 회사명 사용: {name}")
            
            stock_code = extracted_code
            logger.info(f"- 최종 종목 정보: {name} ({stock_code})")
            
        except Exception as e:
            logger.error(f"- 종목명/코드 추출 실패: {e}")
            if stock_code:  # 미리 매핑된 종목코드가 있으면 사용
                logger.info(f"- 미리 매핑된 종목코드 사용: {stock_code}")
                name = company_name
            else:
                raise Exception("종목 정보를 찾을 수 없습니다")

        # 주가 정보 수집
        logger.info("\n=== 주가 정보 수집 시작 ===")
        price_info = get_stock_price_and_trend(driver)
        if not price_info:
            raise Exception("주가 정보 수집 실패")
        logger.info("=== 주가 정보 수집 완료 ===\n")

        return stock_code, name, price_info

    except Exception as e:
        logger.error(f"\n[!] 종목 정보 수집 중 오류 발생: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        raise e

def scrape_comments(driver):
    try:
        driver.get(driver.current_url.split('/order')[0] + '/community')

        comment_container = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'article > div > a > span')
            )
        )
        filtered_comments = []
        exclude_phrases = ["더보기", "더 보기", "더 보 기"]

        for comment in comment_container:
            comment_text = comment.text.strip()
            normalized_text = comment_text.replace(" ", "")
            if normalized_text and all(exclude not in normalized_text for exclude in exclude_phrases):
                filtered_comments.append(comment_text)

        return filtered_comments
    except Exception as e:
        raise e

def scrape_company_data(driver):
    try:
        comments = scrape_comments(driver)
        driver.quit()
        return comments
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        raise e

def analyze_comments(comments, company_name):
    if comments:
        combined_comments = "\n".join(comments)
        prompt = f"다음은 {company_name}에 대한 댓글들입니다. 종합적인 분석을 한글로 작성하고, 마지막 줄에는 여론을 긍정적, 부정적, 중립으로 판단해 주세요:\n{combined_comments}"
        return ask_comment(prompt)
    return "댓글을 찾을 수 없습니다."

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def index(request):
    driver = None
    company_name = request.data.get('company_name', '').strip().lower()

    if not company_name:
        return Response({
            'error_message': "회사명을 입력하세요.",
        })

    try:
        # 기존 데이터 확인
        existing_data = StockData.objects.filter(
            company_name__icontains=company_name
        ).first()

        if existing_data:
            # 기존 데이터가 있어도 관심 주식으로 등록
            UserStockInterest.objects.update_or_create(
                user=request.user,
                stock_code=existing_data.stock_code,
                defaults={
                    'company_name': existing_data.company_name,
                    'last_price': float(json.loads(existing_data.price_info)['current_price']),
                }
            )
            return Response({
                'company_name': existing_data.company_name,
                'stock_code': existing_data.stock_code,
                'comments': existing_data.comments.split("\n"),
                'chatgpt_response': existing_data.analysis,
                'price_info': existing_data.price_info
            })

        # Chrome 드라이버 초기화
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 주식 정보 수집
        stock_code, company_name, price_info = get_stock_code_and_name(driver, company_name)
        
        if not price_info:
            raise Exception("주가 정보를 가져올 수 없습니다.")
            
        # 댓글 수집
        comments = scrape_company_data(driver)
        
        # AI 분석
        chatgpt_response = analyze_comments(comments, company_name)

        # 데이터베이스 저장
        stock_data = StockData(
            company_name=company_name,
            stock_code=stock_code,
            comments="\n".join(comments),
            analysis=chatgpt_response,
            price_info=price_info
        )
        stock_data.save()

        # 관심 주식으로 등록
        UserStockInterest.objects.update_or_create(
            user=request.user,
            stock_code=stock_code,
            defaults={
                'company_name': company_name,
                'last_price': float(price_info['current_price']),
            }
        )

        return Response({
            'company_name': company_name,
            'stock_code': stock_code,
            'comments': comments,
            'chatgpt_response': chatgpt_response,
            'price_info': price_info
        })

    except Exception as e:
        return Response({
            'error_message': f"데이터 수집 중 오류 발생: {str(e)}"
        })
        
    finally:
        if driver:
            driver.quit()

@api_view(['POST'])
def delete_comment(request):
    stock_code = request.data.get('stock_code')
    comment_index = request.data.get('comment_index')

    if stock_code and comment_index is not None:
        try:
            comment_index = int(comment_index)
            stock_data = StockData.objects.get(stock_code=stock_code)

            if stock_data:
                comments = stock_data.comments.split("\n")
                if 0 <= comment_index < len(comments):
                    del comments[comment_index]
                    stock_data.comments = "\n".join(comments)
                    stock_data.analysis = analyze_comments(comments, stock_data.company_name)
                    stock_data.save()

                    return Response({
                        'company_name': stock_data.company_name,
                        'stock_code': stock_data.stock_code,
                        'comments': comments,
                        'chatgpt_response': stock_data.analysis,
                    })
        except ValueError:
            pass

    return Response({
        'error_message': "댓글 삭제 중 오류가 발생했습니다.",
    })

@api_view(['GET'])
def get_stock_history(request, period):
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        stock_code = request.GET.get('stock_code', '005930')  # 기본값으로 삼성전자
        
        # 기간에 따른 URL 파라미터 설정
        period_params = {
            '1D': 'day',
            '1W': 'week',
            '1M': 'month',
            '3M': '3month',
            '1Y': 'year',
            'custom': 'custom'
        }
        
        if period not in period_params:
            return Response({
                'error': '유효하지 않은 기간입니다.'
            }, status=400)

        driver = None
        try:
            # Chrome 드라이버 초기화
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # URL 설정
            base_url = f'https://tossinvest.com/stocks/{stock_code}'
            driver.get(base_url)
            
            # 페이지 로딩 대기
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(5)
            
            if period == 'custom' and start_date and end_date:
                # 사용자 지정 기간 처리
                chart_data = get_custom_period_data(driver, start_date, end_date)
            else:
                # 기본 기간 처리
                try:
                    period_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[data-period='{period_params[period]}']"))
                    )
                    period_button.click()
                    time.sleep(3)
                except Exception as e:
                    print(f"기간 선택 버튼 클릭 실패: {e}")
                    # 기본 데이터 수집 시도
                
                chart_data = get_chart_data(driver)
            
            return Response(chart_data)
            
        except Exception as e:
            return Response({
                'error': f'차트 데이터 수집 중 오류 발생: {str(e)}'
            }, status=500)
            
        finally:
            if driver:
                driver.quit()
                
    except Exception as e:
        return Response({
            'error': f'서버 오류: {str(e)}'
        }, status=500)

def get_custom_period_data(driver, start_date, end_date):
    try:
        # 날짜 선택 버튼 클릭
        date_picker_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.date-picker-button"))
        )
        date_picker_button.click()
        time.sleep(1)

        # 시작일 입력
        start_date_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.start-date"))
        )
        start_date_input.clear()
        start_date_input.send_keys(start_date)
        time.sleep(1)

        # 종료일 입력
        end_date_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.end-date"))
        )
        end_date_input.clear()
        end_date_input.send_keys(end_date)
        time.sleep(1)

        # 적용 버튼 클릭
        apply_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.apply-date-range"))
        )
        apply_button.click()
        time.sleep(3)

        return get_chart_data(driver)

    except Exception as e:
        raise Exception(f'사용자 지정 기간 데이터 수집 중 오류 발생: {str(e)}')

def get_chart_data(driver):
    try:
        chart_data = {
            'dates': [],
            'prices': [],
            'volumes': []
        }
        
        try:
            # 가격 정보 수집
            price_elements = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.price-point"))
            )
            
            for element in price_elements:
                try:
                    date = element.get_attribute("data-date")
                    price = element.get_attribute("data-price")
                    volume = element.get_attribute("data-volume")
                    
                    if date and price:
                        chart_data['dates'].append(date)
                        chart_data['prices'].append(float(price.replace(',', '')))
                        if volume:
                            chart_data['volumes'].append(int(volume.replace(',', '')))
                        else:
                            chart_data['volumes'].append(0)
                except Exception as e:
                    print(f"데이터 포인트 처리 중 오류: {e}")
                    continue
            
        except Exception as e:
            print(f"가격 정보 수집 실패: {e}")
            # 대체 방법으로 시도
            try:
                price_text = driver.find_element(By.CSS_SELECTOR, "span.current-price").text
                date_text = driver.find_element(By.CSS_SELECTOR, "span.price-date").text
                
                if price_text and date_text:
                    chart_data['dates'].append(date_text)
                    chart_data['prices'].append(float(price_text.replace(',', '')))
                    chart_data['volumes'].append(0)
            except Exception as e2:
                print(f"대체 데이터 수집 실패: {e2}")
        
        return chart_data
        
    except Exception as e:
        raise Exception(f'차트 데이터 추출 중 오류 발생: {str(e)}')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_stock_voice(request):
    try:
        company_name = request.data.get('company_name')
        if not company_name:
            return Response({'error': '회사명이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 주식 정보 가져오기
        stock_data = get_stock_info(company_name)
        if not stock_data:
            return Response({'error': '주식 정보를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # 관심 주식으로 자동 저장
        UserStockInterest.objects.update_or_create(
            user=request.user,
            stock_code=stock_data.stock_code,
            defaults={
                'company_name': stock_data.company_name,
                'last_price': float(json.loads(stock_data.price_info)['현재가'].replace(',', '')),
            }
        )

        serializer = StockDataSerializer(stock_data)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stock_interests(request):
    """사용자의 관심 주식 목록을 반환합니다."""
    interests = UserStockInterest.objects.filter(user=request.user)
    serializer = UserStockInterestSerializer(interests, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_stock_interest(request, stock_code):
    """특정 관심 주식을 삭제합니다."""
    try:
        interest = UserStockInterest.objects.get(user=request.user, stock_code=stock_code)
        interest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except UserStockInterest.DoesNotExist:
        return Response({'error': '관심 주식을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND) 