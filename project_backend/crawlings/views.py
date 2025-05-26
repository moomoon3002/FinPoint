from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
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
from .models import StockData
import time
import os
from datetime import datetime

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
        # 현재가 정보 가져오기
        current_price_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="__next"]/div[1]/div[1]/main/div/div/div/div[3]/div/div[1]/div[1]/div[1]/span[1]'
            ))
        )
        current_price = current_price_element.text.strip()
        current_price = ''.join(filter(str.isdigit, current_price))

        # 등락률 정보 가져오기
        change_rate_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="__next"]/div[1]/div[1]/main/div/div/div/div[3]/div/div[1]/div[1]/div[2]/span[1]'
            ))
        )
        change_rate = change_rate_element.text.strip()

        # 가격 변동 정보 가져오기
        price_change_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="__next"]/div[1]/div[1]/main/div/div/div/div[3]/div/div[1]/div[1]/div[2]/span[2]'
            ))
        )
        price_change = price_change_element.text.strip()
        price_change = ''.join(filter(str.isdigit, price_change))
        if "+" in price_change_element.text:
            price_change = int(price_change)
        else:
            price_change = -int(price_change)

        # 날짜 정보 가져오기 (현재 날짜 사용)
        current_date = datetime.now().strftime("%m월 %d일")

        # 거래량 정보 가져오기
        volume_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="__next"]/div[1]/div[1]/main/div/div/div/div[3]/div/div[2]/div[1]/div[2]/span[2]'
            ))
        )
        volume = volume_element.text.strip()

        return {
            'current_price': int(current_price),
            'change_rate': change_rate,
            'price_change': price_change,
            'previous_date': current_date,
            'volume': volume
        }
    except Exception as e:
        print(f"주가 정보 수집 중 오류 발생: {e}")
        return None

def get_stock_code_and_name(driver, company_name):
    try:
        driver.get('https://tossinvest.com/')

        search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'u09klc0'))
        )
        ActionChains(driver).click(search_button).perform()

        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, '_1x1gpvi6'))
        )
        search_input.clear()
        search_input.send_keys(company_name)
        search_input.send_keys(Keys.RETURN)

        first_result = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'u09klc0'))
        )
        ActionChains(driver).click(first_result).perform()

        stock_name_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="__next"]/div[1]/div[1]/main/div/div/div/div[3]/div/div[3]/div[1]/span[1]',
            ))
        )
        stock_code = driver.current_url.split('/order')[0][-6:]
        name = stock_name_element.text.strip()

        # 주가 정보 수집
        price_info = get_stock_price_and_trend(driver)

        return stock_code, name, price_info
    except Exception as e:
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
def index(request):
    driver = None
    company_name = request.data.get('company_name', '').strip().lower()

    if not company_name:
        return Response({
            'error_message': "회사 이름을 입력하세요.",
        })

    try:
        existing_data = StockData.objects.filter(
            company_name__icontains=company_name
        ).first()

        if existing_data:
            return Response({
                'company_name': existing_data.company_name,
                'stock_code': existing_data.stock_code,
                'comments': existing_data.comments.split("\n"),
                'chatgpt_response': existing_data.analysis,
                'is_existing_data': True,
                'price_info': existing_data.price_info if hasattr(existing_data, 'price_info') else None,
            })

        driver = webdriver.Chrome(service=service, options=chrome_options)
        stock_code, company_name, price_info = get_stock_code_and_name(driver, company_name)
        comments = scrape_company_data(driver)

        chatgpt_response = analyze_comments(comments, company_name)

        stock_data = StockData(
            company_name=company_name,
            stock_code=stock_code,
            comments="\n".join(comments),
            analysis=chatgpt_response,
            price_info=price_info,
        )
        stock_data.save()

        return Response({
            'company_name': company_name,
            'stock_code': stock_code,
            'comments': comments,
            'chatgpt_response': chatgpt_response,
            'is_existing_data': False,
            'price_info': price_info,
        })

    except Exception as e:
        return Response({
            'error_message': f"스크래핑 중 오류 발생: {e}",
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