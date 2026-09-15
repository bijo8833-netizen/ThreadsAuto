"""
쿠팡파트너스 오픈API의 CEA(HmacSHA256) 인증 헤더를 생성하는 모듈.
공식 문서: https://developers.coupangcorp.com/hc/ko/articles (오픈API 인증 가이드)

* 이 서명 방식은 쿠팡이 공개한 예시 코드를 기반으로 구현한 것으로,
  실제 연동 전 반드시 쿠팡파트너스 개발자센터에서 최신 스펙을 확인하세요.
"""
import hashlib
import hmac
import os
import time


def generate_auth_header(method: str, url_path_with_query: str) -> str:
    access_key = os.environ["COUPANG_ACCESS_KEY"]
    secret_key = os.environ["COUPANG_SECRET_KEY"]

    datetime_gmt = time.strftime("%y%m%d", time.gmtime()) + "T" + time.strftime("%H%M%S", time.gmtime()) + "Z"

    if "?" in url_path_with_query:
        path, query = url_path_with_query.split("?", 1)
    else:
        path, query = url_path_with_query, ""

    message = datetime_gmt + method + path + query
    signature = hmac.new(
        secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return (
        f"CEA algorithm=HmacSHA256, access-key={access_key}, "
        f"signed-date={datetime_gmt}, signature={signature}"
    )
