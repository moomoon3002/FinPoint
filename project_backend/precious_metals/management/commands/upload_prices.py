from django.core.management.base import BaseCommand
import pandas as pd
import os
from precious_metals.models import MetalPrice
from datetime import datetime
from dateutil.parser import parse
import traceback

class Command(BaseCommand):
    help = '금과 은 가격 데이터를 엑셀 파일에서 데이터베이스로 업로드합니다.'

    def clean_number(self, value, field_name=None, row_date=None):
        """숫자 필드 전처리 함수 - 날짜나 이상한 값 자동 제거"""
        if pd.isna(value):
            return None

        # datetime 객체 자체
        if isinstance(value, datetime):
            raise ValueError(f"'{field_name}' 열에 datetime 객체 있음: {value}")

        # 숫자일 경우 바로 처리
        if isinstance(value, (int, float)):
            return float(value)

        # 문자열인 경우
        if isinstance(value, str):
            try:
                # 날짜 형식 문자열 여부 판단
                parsed = parse(value, fuzzy=False)
                raise ValueError(f"'{field_name}' 열에 날짜 형식 문자열 있음: {value}")
            except Exception:
                # 날짜가 아니라면 숫자 문자열일 수 있음
                try:
                    return float(value.replace(',', '').strip())
                except ValueError:
                    raise ValueError(f"'{field_name}' 열에 잘못된 숫자 문자열: {value}")

        # 그 외 타입은 오류
        raise ValueError(f"'{field_name}' 열에 처리 불가한 값: {value} ({type(value)})")

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        # 금
        gold_file = os.path.join(base_dir, 'Gold_prices.xlsx')
        if os.path.exists(gold_file):
            self.stdout.write(f"📂 Found gold prices file: {gold_file}")
            self.upload_metal_prices(gold_file, 'GOLD')
        else:
            self.stdout.write(self.style.ERROR(f"❌ Gold prices file not found: {gold_file}"))

        # 은
        silver_file = os.path.join(base_dir, 'Silver_prices.xlsx')
        if os.path.exists(silver_file):
            self.stdout.write(f"📂 Found silver prices file: {silver_file}")
            self.upload_metal_prices(silver_file, 'SILVER')
        else:
            self.stdout.write(self.style.ERROR(f"❌ Silver prices file not found: {silver_file}"))

    def upload_metal_prices(self, file_path, metal_type):
        self.stdout.write(f"📈 Uploading {metal_type} prices from {file_path}...")

        try:
            df = pd.read_excel(file_path, header=0)
            self.stdout.write(f"✅ Successfully read {len(df)} rows from {file_path}")

            # 대상 열을 문자열로 캐스팅 (문자열 날짜/숫자 처리 가능하게)
            for col in ['Close/Last', 'Volume', 'Open', 'High', 'Low']:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            success_count = 0
            error_count = 0

            for _, row in df.iterrows():
                try:
                    MetalPrice.objects.update_or_create(
                        metal_type=metal_type,
                        date=pd.to_datetime(row['Date']).date(),
                        defaults={
                            'close_price': self.clean_number(row['Close/Last'], 'Close/Last', row.get('Date')),
                            'volume': self.clean_number(row['Volume'], 'Volume', row.get('Date')),
                            'open_price': self.clean_number(row['Open'], 'Open', row.get('Date')),
                            'high_price': self.clean_number(row['High'], 'High', row.get('Date')),
                            'low_price': self.clean_number(row['Low'], 'Low', row.get('Date')),
                        }
                    )
                    success_count += 1
                    if success_count % 100 == 0:
                        self.stdout.write(f"⏳ Processed {success_count} rows...")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error on row {row.get('Date')} - {e}"))
                    self.stdout.write(f"🪵 Skipped Row: {row.to_dict()}")
                    error_count += 1

            self.stdout.write(self.style.SUCCESS(f"✅ {metal_type} - {success_count}건 적재 완료"))
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f"⚠️ {error_count}건 오류로 인해 스킵됨"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error reading file {file_path}: {e}"))
            self.stdout.write(traceback.format_exc())
