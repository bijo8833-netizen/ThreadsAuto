"""
이미 사용한 소재(주제)를 기록해서 중복 게시를 막기 위한 모듈.
data/used_topics.json 파일에 최근 사용한 주제 제목들을 저장한다.
GitHub Actions에서는 워크플로 마지막에 이 파일을 git commit/push 해야
다음 실행 때도 기록이 유지된다 (워크플로 yml 참고).
"""
import json
import os

STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "used_topics.json",
)

MAX_HISTORY = 200  # 이 개수를 넘으면 오래된 것부터 삭제 (파일이 무한히 커지는 것 방지)


def load_used_topics() -> list:
    if not os.path.exists(STATE_PATH):
        return []
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def add_used_topic(topic: str) -> None:
    topics = load_used_topics()
    topics.append(topic)
    if len(topics) > MAX_HISTORY:
        topics = topics[-MAX_HISTORY:]
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)


def is_used(topic: str) -> bool:
    return topic in load_used_topics()
