from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import logging
import json
import time
import re
from .models import IPOEvent, UserIPOInterest

logger = logging.getLogger(__name__)

# Selenium 기본 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

@api_view(['GET'])
def get_ipo_calendar(request):
    """IPO 캘린더 데이터를 크롤링하여 반환"""
    driver = None
    try:
        # 크롬 드라이버 설정
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 페이지 접속
        logger.info("IPO 캘린더 페이지 접속 중...")
        url = 'https://www.finuts.co.kr/html/ipo/'
        driver.get(url)
        
        # 명시적 대기 설정
        wait = WebDriverWait(driver, 20)
        
        # 페이지가 완전히 로드될 때까지 대기
        wait.until(EC.presence_of_element_located((By.ID, "ipo-calendar")))
        time.sleep(5)  # 추가 대기 시간
        
        # 캘린더 데이터 추출
        calendar_data = []
        
        try:
            # 1. ipo-calendar 영역 찾기
            calendar = driver.find_element(By.ID, "ipo-calendar")
            logger.info("ipo-calendar 영역 찾음")
            
            # 2. calen-list 클래스를 가진 ol 찾기
            calen_list = calendar.find_element(By.CLASS_NAME, "calen-list")
            logger.info("calen-list 찾음")
            
            # 3. 날짜별 데이터 추출
            date_cells = calen_list.find_elements(By.TAG_NAME, "li")
            logger.info(f"발견된 날짜 셀 수: {len(date_cells)}")
            
            for cell in date_cells:
                try:
                    # data-date 속성에서 날짜 가져오기
                    date_str = cell.get_attribute('data-date')
                    if not date_str:
                        continue
                    
                    logger.info(f"처리 중인 날짜: {date_str}")
                    
                    # 이벤트 목록 추출
                    events = []
                    
                    # type-list 클래스를 가진 ul 찾기
                    type_lists = cell.find_elements(By.CLASS_NAME, "type-list")
                    for type_list in type_lists:
                        # li 태그들 찾기
                        event_items = type_list.find_elements(By.TAG_NAME, "li")
                        for event_item in event_items:
                            try:
                                # a 태그 찾기
                                a_element = event_item.find_element(By.TAG_NAME, "a")
                                event_text = a_element.text.strip()
                                if not event_text:
                                    continue
                                
                                # 이벤트 타입 결정
                                event_type = "기타"
                                class_name = a_element.get_attribute("class").lower()
                                
                                type_mapping = {
                                    "type-01": "수요예측",
                                    "type-02": "청약",
                                    "type-03": "환불",
                                    "type-04": "상장",
                                    "type-05": "락업해제"
                                }
                                
                                for type_class, type_name in type_mapping.items():
                                    if type_class.replace("-", "") in class_name.replace("-", ""):
                                        event_type = type_name
                                        break
                                
                                events.append({
                                    'company': event_text,
                                    'type': event_type
                                })
                                logger.info(f"이벤트 추가: {event_text} ({event_type})")
                                
                            except Exception as e:
                                logger.warning(f"이벤트 처리 중 오류: {str(e)}")
                                continue
                    
                    if events:  # 이벤트가 있는 경우만 추가
                        calendar_data.append({
                            'date': date_str,
                            'events': events,
                            'is_current_month': True
                        })
                
                except Exception as e:
                    logger.warning(f"날짜 셀 처리 중 오류: {str(e)}")
                    continue
            
            logger.info(f"총 {len(calendar_data)}개의 날짜 데이터 추출 완료")
            
        except Exception as e:
            logger.error(f"데이터 추출 중 오류 발생: {str(e)}")
            raise
        
        if not calendar_data:
            logger.warning("추출된 IPO 데이터가 없습니다.")
            # 빈 달력 데이터 반환
            return Response({
                'year': datetime.now().year,
                'month': datetime.now().month,
                'weekdays': ['월', '화', '수', '목', '금', '토', '일'],
                'calendar': []
            })
        
        response_data = {
            'year': datetime.now().year,
            'month': datetime.now().month,
            'weekdays': ['월', '화', '수', '목', '금', '토', '일'],
            'calendar': calendar_data
        }
        
        logger.info("=== 최종 추출 데이터 ===")
        logger.info(json.dumps(response_data, ensure_ascii=False, indent=2))
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"IPO 데이터 크롤링 중 오류 발생: {str(e)}")
        # 오류 발생 시에도 빈 달력 데이터 반환
        return Response({
            'year': datetime.now().year,
            'month': datetime.now().month,
            'weekdays': ['월', '화', '수', '목', '금', '토', '일'],
            'calendar': []
        })
        
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"드라이버 종료 중 오류 발생: {e}")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_ipo_interest(request, event_id):
    """IPO 이벤트 관심 등록/해제"""
    try:
        ipo_event = IPOEvent.objects.get(id=event_id)
        interest, created = UserIPOInterest.objects.get_or_create(
            user=request.user,
            ipo_event=ipo_event
        )
        
        if not created:
            interest.delete()
            return Response({'message': '관심 IPO 해제 완료'})
            
        return Response({'message': '관심 IPO 등록 완료'})
        
    except IPOEvent.DoesNotExist:
        return Response({
            'error': '해당 IPO 이벤트를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_ipo_interests(request):
    """사용자의 관심 IPO 목록 조회"""
    try:
        interests = UserIPOInterest.objects.filter(user=request.user).select_related('ipo_event')
        data = [{
            'id': interest.ipo_event.id,
            'company_name': interest.ipo_event.company_name,
            'event_type': interest.ipo_event.event_type,
            'event_date': interest.ipo_event.event_date
        } for interest in interests]
        
        return Response(data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500) 