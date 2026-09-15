"""
'3일 이내 100만 조회수 스레드'를 정확히 탐지하는 것은 Threads가 타 계정
게시물의 조회수를 API로 공개하지 않기 때문에 불가능하다 (이전 대화에서 안내드린 내용).

대신 이 모듈은 현재 한국에서 화제가 되고 있는 뉴스 헤드라인을 구글 뉴스 RSS에서
수집해서, 그중 아직 다루지 않은 주제 하나를 골라 반환한다.
이후 claude_client.generate_general_post()가 이 소재를 밀키웨이 계정 톤으로
재창작하는 방식으로 '벤치마킹'을 대신한다.
"""
import xml.etree.ElementTree as ET

import requests

from common.state import is_used

RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"


def _fetch_headlines() -> list:
    resp = requests.get(RSS_URL, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        desc = item.findtext("description", "").strip()
        if title:
            items.append({"title": title, "summary": desc})
    return items


def get_unused_topic() -> dict:
    """아직 사용하지 않은 헤드라인 하나를 반환한다."""
    headlines = _fetch_headlines()
    for item in headlines:
        if not is_used(item["title"]):
            return item
    # 전부 사용됐다면 (드문 경우) 가장 첫 항목을 재사용
    return headlines[0] if headlines else {"title": "오늘의 생활 정보", "summary": ""}
