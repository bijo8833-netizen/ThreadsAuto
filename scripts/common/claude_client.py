"""
Anthropic Claude API를 호출해서 bijo0602(밀키웨이) 계정 톤에 맞는
스레드 게시글 문구를 자동으로 생성하는 모듈.

- 일반 소재 글: generate_general_post()
- 쿠팡 제휴 상품 글: generate_coupang_post()  (scripts/coupang 쪽에서 사용)
"""
import os
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

# bijo0602 계정의 실제 게시글 톤을 반영한 스타일 가이드.
# (담담하고 실용적인 정보 전달, 숫자/기간으로 정리, 마지막에 블로그 링크 유도)
STYLE_GUIDE = """
너는 '밀키웨이' 라는 이름의 스레드(Threads) 계정을 운영하는 작가야.
계정 소개는 "그냥 생각나는 것들을 올립니다" 이고, 실제 톤은 이렇다:

- 문장은 짧고 담담하다. 과장된 감탄사나 이모지 남발이 없다.
- 정보를 숫자·기간·단계로 정리해서 신뢰감을 준다. (예: "꼭 기억해야 할 숫자는 4개")
- 어렵지 않은 일상어로 쓰되, 실용적인 정보(돈, 절차, 법, 건강, 생활 팁 등)를 다룬다.
- 마지막 문장은 다음 내용을 궁금하게 만드는 문장으로 끝맺는다.
- 절대 특정 브랜드·유명인을 비방하거나 근거 없는 자극적 주장을 하지 않는다.
- 300~500자 내외의 스레드 한 개 분량으로 작성한다.
"""


def _call_claude(prompt: str, max_tokens: int = 800) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text").strip()


def generate_general_post(topic_title: str, topic_summary: str = "") -> dict:
    """
    화제가 되고 있는 소재(뉴스 헤드라인 등)를 받아서
    bijo0602 스타일의 스레드 게시글 본문 + 헤드라인(이미지 카드용)을 생성한다.

    반환값: {"headline": "이미지 카드에 넣을 짧은 제목", "body": "스레드 본문 전체"}
    """
    prompt = f"""{STYLE_GUIDE}

아래는 지금 화제가 되고 있는 뉴스/이슈다. 이 소재를 활용해서 밀키웨이 계정 톤으로
스레드 게시글 하나를 새로 창작해줘. 뉴스를 그대로 요약하지 말고, 사람들이 실생활에서
바로 써먹을 수 있는 정보/관점으로 재구성해.

[소재 제목]
{topic_title}

[소재 요약]
{topic_summary}

다음 형식의 JSON으로만 답해. 다른 설명은 붙이지 마.
{{
  "headline": "이미지 카드 상단에 들어갈 12자 내외의 임팩트 있는 제목",
  "body": "스레드에 실제로 게시할 본문 전체 (줄바꿈 포함, 300~500자)"
}}
"""
    raw = _call_claude(prompt)
    return _parse_json_loose(raw)


def extract_image_keywords(text: str) -> str:
    """
    스톡사진 검색에 쓸 영어 키워드 2~3개를 뽑아낸다.
    (Pexels는 영어 검색 결과가 훨씬 풍부하고 정확함)
    """
    prompt = f"""다음 한국어 문장의 분위기와 주제에 어울리는 영어 스톡사진 검색 키워드를
2~3개만, 쉼표로 구분해서 출력해. 설명 없이 키워드만 출력해.

문장: {text}
"""
    result = _call_claude(prompt, max_tokens=50)
    return result.strip().strip('"')


def generate_coupang_post(product_name: str, price: str, category: str) -> str:
    """
    쿠팡 제휴 상품 소개 스레드 문구를 생성한다.
    법적으로 필수인 파트너스 고지 문구를 마지막에 반드시 포함한다.
    """
    prompt = f"""{STYLE_GUIDE}

아래 상품을 밀키웨이 계정 톤으로 짧게 소개하는 스레드 게시글을 써줘.
과장 광고 문구("최저가", "완판임박" 등 근거 없는 표현) 없이, 담백하게 왜 요즘 인기인지
1~2문장으로 설명하는 정도로 작성해. 200자 이내.

[상품명] {product_name}
[가격] {price}
[카테고리] {category}

본문만 출력하고, 마지막 줄에는 반드시 아래 문구를 그대로 추가해:
"(이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.)"
"""
    return _call_claude(prompt, max_tokens=400)


def _parse_json_loose(raw: str) -> dict:
    import json
    import re

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Claude 응답에서 JSON을 찾지 못했습니다: {raw}")
    return json.loads(match.group(0))
