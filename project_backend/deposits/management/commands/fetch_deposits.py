from django.core.management.base import BaseCommand
import requests
import os
from dotenv import load_dotenv
from deposits.models import DepositProduct, DepositOption

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
API_KEY = os.getenv('BANK_API_KEY')

BASE_URLS = {
    '예금': 'https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json',
    '적금': 'https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json',
}

FIN_GROUPS = {
    '은행': '020000',
    '저축은행': '030300',
}


class Command(BaseCommand):
    help = '은행/저축은행의 예금/적금 데이터를 금융감독원 API에서 수집하여 DB에 저장합니다.'

    def handle(self, *args, **kwargs):
        if not API_KEY:
            self.stderr.write(self.style.ERROR('ERROR: BANK_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.'))
            return

        for product_type, url in BASE_URLS.items():
            for group_name, fin_group in FIN_GROUPS.items():
                self.fetch_and_save(
                    url=url,
                    product_type=product_type,
                    fin_group=fin_group,
                    group_name=group_name
                )

    def fetch_and_save(self, url, product_type, fin_group, group_name):
        full_url = f"{url}?auth={API_KEY}&topFinGrpNo={fin_group}&pageNo=1"
        res = requests.get(full_url)

        if res.status_code != 200:
            self.stderr.write(f"[ERROR] {group_name} {product_type} 요청 실패: {res.status_code}")
            return

        data = res.json()
        base_list = data.get('result', {}).get('baseList', [])
        option_list = data.get('result', {}).get('optionList', [])

        for item in base_list:
            try:
                DepositProduct.objects.update_or_create(
                    deposit_ID=item.get('fin_prdt_cd'),
                    defaults={
                        'product_type': product_type,
                        'dcls_month': item.get('dcls_month') or '',
                        'fin_co_no': item.get('fin_co_no') or '',
                        'kor_co_nm': item.get('kor_co_nm') or '',
                        'fin_prdt_nm': item.get('fin_prdt_nm') or '',
                        'join_way': item.get('join_way') or '',
                        'mtrt_int': item.get('mtrt_int') or '',
                        'spcl_cnd': item.get('spcl_cnd') or '',
                        'join_deny': item.get('join_deny') or '',
                        'join_member': item.get('join_member') or '',
                        'etc_note': item.get('etc_note') or '',
                        'max_limit': item.get('max_limit') if item.get('max_limit') not in [None, ''] else None,
                        'dcls_strt_day': item.get('dcls_strt_day') or '',
                        'dcls_end_day': item.get('dcls_end_day') or '',
                        'fin_co_subm_day': item.get('fin_co_subm_day') or '',
                    }
                )
            except Exception as e:
                self.stderr.write(f"[ERROR] 상품 저장 실패 ({item.get('fin_prdt_cd')}): {str(e)}")
                continue

        for opt in option_list:
            try:
                product = DepositProduct.objects.filter(deposit_ID=opt.get('fin_prdt_cd')).first()
                if not product:
                    continue

                DepositOption.objects.update_or_create(
                    deposit=product,
                    save_trm=opt.get('save_trm') or '',
                    intr_rate_type=opt.get('intr_rate_type') or '',
                    defaults={
                        'intr_rate_type_nm': opt.get('intr_rate_type_nm') or '',
                        'rsrv_type': opt.get('rsrv_type') or '',
                        'rsrv_type_nm': opt.get('rsrv_type_nm') or '',
                        'intr_rate': opt.get('intr_rate') if opt.get('intr_rate') not in [None, ''] else None,
                        'intr_rate2': opt.get('intr_rate2') if opt.get('intr_rate2') not in [None, ''] else None,
                    }
                )
            except Exception as e:
                self.stderr.write(f"[ERROR] 옵션 저장 실패 ({opt.get('fin_prdt_cd')}): {str(e)}")
                continue

        self.stdout.write(self.style.SUCCESS(
            f"[SUCCESS] {group_name} {product_type} - 상품 {len(base_list)}건, 옵션 {len(option_list)}건 적재 완료"
        ))
