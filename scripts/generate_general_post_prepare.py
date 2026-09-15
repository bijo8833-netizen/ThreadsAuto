"""
1단계: 화제 소재 수집 -> 문구 생성 -> 이미지 생성 -> 메타데이터 저장.
이 스크립트 실행 후 워크플로가 output/ 폴더를 git commit & push 하고,
그 다음 generate_general_post_publish.py 가 실제로 Threads에 게시한다.
(이미지가 GitHub에 올라가서 공개 URL이 생긴 뒤에 게시해야 하기 때문)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from common import claude_client, image_utils, pexels_client, state
import fetch_trending_topic

META_PATH = "output/meta/general_latest.json"


def main():
    topic = fetch_trending_topic.get_unused_topic()
    print(f"[소재] {topic['title']}")

    generated = claude_client.generate_general_post(topic["title"], topic.get("summary", ""))
    headline = generated["headline"]
    body = generated["body"]
    print(f"[헤드라인] {headline}")
    print(f"[본문]\n{body}")

    keywords = claude_client.extract_image_keywords(headline + " " + body[:100])
    print(f"[이미지 검색어] {keywords}")
    photo_url = pexels_client.search_photo_url(keywords)

    image_path = image_utils.create_headline_card(photo_url, headline)
    print(f"[이미지 저장] {image_path}")

    state.add_used_topic(topic["title"])

    os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"body": body, "image_path": image_path, "topic": topic["title"]},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"[메타데이터 저장 완료] {META_PATH}")


if __name__ == "__main__":
    main()
