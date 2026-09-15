"""
Pexels API로 무료 실사 스톡사진을 검색하는 모듈.
- 무료, 상업적 이용 가능, 출처 표기 의무 없음 (Pexels 라이선스 기준)
- https://www.pexels.com/api/ 에서 API 키 무료 발급
"""
import os
import random
import requests

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
SEARCH_URL = "https://api.pexels.com/v1/search"


def search_photo_url(query: str) -> str:
    """
    주어진 검색어로 스톡사진을 검색해서 큰 사이즈 이미지 URL 하나를 반환한다.
    검색 결과가 없으면 좀 더 일반적인 키워드로 한 번 더 시도한다.
    """
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY 환경변수가 설정되지 않았습니다.")

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 15, "orientation": "square"}
    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    photos = resp.json().get("photos", [])

    if not photos:
        # 검색어가 너무 구체적이면 결과가 없을 수 있어서, 첫 단어만으로 재시도
        fallback_query = query.split(",")[0].strip()
        params["query"] = fallback_query
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        photos = resp.json().get("photos", [])

    if not photos:
        raise RuntimeError(f"'{query}'에 대한 스톡사진을 찾지 못했습니다.")

    chosen = random.choice(photos[: min(5, len(photos))])
    return chosen["src"]["large"]
