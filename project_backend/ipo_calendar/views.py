from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
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

logger = logging.getLogger(__name__)

# Selenium 기본 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_ipo_calendar(request):
    driver = None
    try:
        # 드라이버 인스턴스 생성
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        url = 'https://www.finuts.co.kr/html/ipo/'
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        # li[data-date] 요소가 최소 하나 로드될 때까지 대기
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#ipo-calendar .calen-list li[data-date]")
        ))
        time.sleep(1)  # 혹시 필요한 짧은 추가 대기

        # calendar 영역 및 날짜 셀 조회
        cal = driver.find_element(By.CSS_SELECTOR, "#ipo-calendar .calen-list")
        date_cells = cal.find_elements(By.CSS_SELECTOR, "li[data-date]")
        logger.info(f"총 {len(date_cells)}일(data-date) 셀 발견")

        # 이벤트 타입 매핑
        type_mapping = {
            "type-01": "수요예측",
            "type-02": "청약",
            "type-03": "환불",
            "type-04": "상장",
            "type-05": "락업해제"
        }

        calendar_data = []
        for cell in date_cells:
            date_str = cell.get_attribute("data-date")  # ex. "2025-05-08"
            events = []

            # 셀 내부 ul.type-list > a 를 모두 순회
            for a in cell.find_elements(By.CSS_SELECTOR, "ul.type-list a"):
                title = a.text.strip()
                cls = a.get_attribute("class") or ""
                # 매핑된 한글 타입이 없으면 "기타"
                ev_type = "기타"
                for key, name in type_mapping.items():
                    if key in cls:
                        ev_type = name
                        break

                events.append({
                    "company": title,
                    "type": ev_type
                })

            # 빈 events 도 포함시켜 모든 날짜가 나올 수 있도록
            calendar_data.append({
                "date": date_str,
                "events": events
            })

        response_data = {
            "year": datetime.now().year,
            "month": datetime.now().month,
            "weekdays": ['월','화','수','목','금','토','일'],
            "calendar": calendar_data
        }

        logger.debug("크롤링 결과:", json.dumps(response_data, ensure_ascii=False, indent=2))
        return Response(response_data)

    except Exception as e:
        logger.error(f"IPO 캘린더 크롤링 오류: {e}", exc_info=True)
        # 오류 발생 시에도 빈 캘린더 구조 반환
        return Response({
            "year": datetime.now().year,
            "month": datetime.now().month,
            "weekdays": ['월','화','수','목','금','토','일'],
            "calendar": []
        })

    finally:
        if driver:
            driver.quit()
