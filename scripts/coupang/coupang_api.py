"""
쿠팡파트너스 오픈API 연동 모듈.

1) get_best_product(): 지정한 카테고리의 '베스트카테고리 상품' 중 하나를 가져온다.
   -> 쿠팡은 정확한 '3일간 판매량' 수치를 API로 공개하지 않기 때문에,
      실질적으로 가장 가까운 대안인 베스트카테고리 랭킹(인기순)을 사용한다.
2) create_deeplink(): 일반 쿠팡 URL을 파트너스 수익 링크로 변환한다.

주의: CATEGORY_IDS는 쿠팡파트너스 공식 문서 기준 예시 값입니다.
      실제 연동 전 파트너스 개발자센터 문서에서 최신 카테고리ID 표를 반드시 확인해서
      원하는 카테고리로 교체하세요 (문서 위치: 오픈API > 상품 조회 > 카테고리 코드).
"""
import os
import random

import requests

from coupang_auth import generate_auth_header
from common import state

DOMAIN = "https://api-gateway.coupang.com"

# 예시 카테고리 ID (검증 필요) - 필요한 카테고리로 자유롭게 수정/추가하세요.
CATEGORY_IDS = {
    "생활용품": 1007,
    "가전디지털": 1009,
    "헬스/건강식품": 1016,
}


def _request(method: str, path_with_query: str, body: dict = None) -> dict:
    auth_header = generate_auth_header(method, path_with_query)
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json;charset=UTF-8",
    }
    url = DOMAIN + path_with_query
    if method == "GET":
        resp = requests.get(url, headers=headers, timeout=30)
    else:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_best_product(category_name: str = None, limit: int = 20) -> dict:
    """
    지정한 카테고리(없으면 랜덤 카테고리)의 베스트 상품 중,
    아직 소개하지 않은 상품 하나를 골라 반환한다.
    """
    if category_name is None:
        category_name = random.choice(list(CATEGORY_IDS.keys()))
    category_id = CATEGORY_IDS[category_name]

    path = f"/v2/providers/affiliate_open_api/apis/openapi/products/bestcategories/{category_id}?limit={limit}"
    data = _request("GET", path)
    products = data.get("data", [])

    if not products:
        raise RuntimeError(f"'{category_name}' 카테고리에서 상품을 가져오지 못했습니다: {data}")

    for product in products:
        key = f"coupang:{product.get('productId')}"
        if not state.is_used(key):
            return product

    # 전부 최근에 소개했다면 1위 상품 재사용
    return products[0]


def create_deeplink(product_url: str) -> str:
    """일반 쿠팡 상품 URL을 파트너스 수익 링크(딥링크)로 변환한다."""
    sub_id = os.environ.get("COUPANG_SUBID", "milkyway7")
    path = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
    body = {"coupangUrls": [product_url], "subId": sub_id}
    data = _request("POST", path, body)
    links = data.get("data", [])
    if not links:
        raise RuntimeError(f"딥링크 생성 실패: {data}")
    return links[0]["shortenUrl"]
