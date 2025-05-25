from django.core.management.base import BaseCommand
import pandas as pd
import os
from precious_metals.models import MetalPrice
from datetime import datetime

class Command(BaseCommand):
    help = '금과 은 가격 데이터를 엑셀 파일에서 데이터베이스로 업로드합니다.'

    def clean_number(self, value):
        if isinstance(value, str):
            return float(value.replace(',', ''))
        return float(value)

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # 금 가격 데이터 업로드
        gold_file = os.path.join(base_dir, 'Gold_prices.xlsx')
        if os.path.exists(gold_file):
            self.stdout.write(f"Found gold prices file: {gold_file}")
            self.upload_metal_prices(gold_file, 'GOLD')
        else:
            self.stdout.write(self.style.ERROR(f"Gold prices file not found: {gold_file}"))
        
        # 은 가격 데이터 업로드
        silver_file = os.path.join(base_dir, 'Silver_prices.xlsx')
        if os.path.exists(silver_file):
            self.stdout.write(f"Found silver prices file: {silver_file}")
            self.upload_metal_prices(silver_file, 'SILVER')
        else:
            self.stdout.write(self.style.ERROR(f"Silver prices file not found: {silver_file}"))

    def upload_metal_prices(self, file_path, metal_type):
        self.stdout.write(f"Uploading {metal_type} prices from {file_path}...")
        
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)
            self.stdout.write(f"Successfully read {len(df)} rows from {file_path}")
            
            # 데이터 처리 및 저장
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    MetalPrice.objects.update_or_create(
                        metal_type=metal_type,
                        date=pd.to_datetime(row['Date']).date(),
                        defaults={
                            'close_price': self.clean_number(row['Close/Last']),
                            'volume': self.clean_number(row['Volume']),
                            'open_price': self.clean_number(row['Open']),
                            'high_price': self.clean_number(row['High']),
                            'low_price': self.clean_number(row['Low'])
                        }
                    )
                    success_count += 1
                    if success_count % 100 == 0:  # 진행 상황 표시
                        self.stdout.write(f"Processed {success_count} rows...")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row: {row['Date']} - {str(e)}"))
                    error_count += 1
            
            self.stdout.write(self.style.SUCCESS(f"Successfully processed {success_count} rows"))
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f"Encountered {error_count} errors"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file {file_path}: {str(e)}"))
            self.stdout.write(f"Current working directory: {os.getcwd()}") 