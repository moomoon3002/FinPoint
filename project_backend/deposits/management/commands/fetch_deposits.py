from django.core.management.base import BaseCommand
import requests
from deposits.models import DepositProduct, DepositOption

API_KEY = '여기에_인증키_입력'  # 보안상 .env로 숨기는 것이 좋습니다

BASE_URLS = {
    '예금': 'https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json',
    '적금': 'https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json',
}

FIN_GROUPS = {
    '은행': '020000',
    '저축은행': '090000',
}


class Command(BaseCommand):
    help = '은행/저축은행의 예금/적금 데이터를 금융감독원 API에서 수집하여 DB에 저장합니다.'

    def handle(self, *args, **kwargs):
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
            DepositProduct.objects.update_or_create(
                deposit_ID=item.get('fin_prdt_cd'),
                defaults={
                    'product_type': product_type,
                    'dcls_month': item.get('dcls_month', ''),
                    'fin_co_no': item.get('fin_co_no', ''),
                    'kor_co_nm': item.get('kor_co_nm', ''),
                    'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                    'join_way': item.get('join_way', ''),
                    'mtrt_int': item.get('mtrt_int', ''),
                    'spcl_cnd': item.get('spcl_cnd', ''),
                    'join_deny': item.get('join_deny', ''),
                    'join_member': item.get('join_member', ''),
                    'etc_note': item.get('etc_note', ''),
                    'max_limit': item.get('max_limit') or None,
                    'dcls_strt_day': item.get('dcls_strt_day', ''),
                    'dcls_end_day': item.get('dcls_end_day', ''),
                    'fin_co_subm_day': item.get('fin_co_subm_day', ''),
                }
            )

        for opt in option_list:
            product = DepositProduct.objects.filter(deposit_ID=opt.get('fin_prdt_cd')).first()
            if not product:
                continue

            DepositOption.objects.update_or_create(
                deposit=product,
                save_trm=opt.get('save_trm', ''),
                intr_rate_type=opt.get('intr_rate_type', ''),
                defaults={
                    'intr_rate_type_nm': opt.get('intr_rate_type_nm', ''),
                    'rsrv_type': opt.get('rsrv_type', ''),
                    'rsrv_type_nm': opt.get('rsrv_type_nm', ''),
                    'intr_rate': opt.get('intr_rate') or 0.0,
                    'intr_rate2': opt.get('intr_rate2') or 0.0,
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f"[SUCCESS] {group_name} {product_type} - 상품 {len(base_list)}건, 옵션 {len(option_list)}건 적재 완료"
        ))
