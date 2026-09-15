"""
Meta Threads API로 텍스트+이미지 게시글을 올리는 모듈.

절차 (Threads 공식 API 스펙):
  1) 미디어 컨테이너 생성 (POST /{threads_user_id}/threads)
  2) 컨테이너 게시 (POST /{threads_user_id}/threads_publish)

주의: image_url은 반드시 인터넷에 공개적으로 접근 가능한 URL이어야 한다.
      (이 프로젝트에서는 GitHub 저장소에 커밋한 이미지의 raw.githubusercontent.com
       URL을 사용한다 - publish 스크립트가 git push 이후에 호출되는 이유)
"""
import os
import time

import requests

THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = os.environ.get("THREADS_USER_ID")
BASE_URL = "https://graph.threads.net/v1.0"


def _require_config():
    if not THREADS_ACCESS_TOKEN or not THREADS_USER_ID:
        raise RuntimeError("THREADS_ACCESS_TOKEN / THREADS_USER_ID 환경변수가 필요합니다.")


def post_image_thread(text: str, image_url: str, wait_seconds: int = 8) -> str:
    """
    이미지 + 텍스트로 스레드 게시글을 올린다.
    성공 시 게시된 스레드의 id를 반환한다.
    """
    _require_config()

    # 1) 미디어 컨테이너 생성
    create_resp = requests.post(
        f"{BASE_URL}/{THREADS_USER_ID}/threads",
        params={
            "media_type": "IMAGE",
            "image_url": image_url,
            "text": text,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=60,
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    # Threads 서버가 이미지를 처리할 시간을 잠깐 준다 (공식 문서 권장)
    time.sleep(wait_seconds)

    # 2) 게시
    publish_resp = requests.post(
        f"{BASE_URL}/{THREADS_USER_ID}/threads_publish",
        params={
            "creation_id": creation_id,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=60,
    )
    publish_resp.raise_for_status()
    return publish_resp.json()["id"]


def post_text_thread(text: str) -> str:
    """이미지 없이 텍스트만 게시할 때 사용 (실패 시 대체 수단)."""
    _require_config()

    create_resp = requests.post(
        f"{BASE_URL}/{THREADS_USER_ID}/threads",
        params={
            "media_type": "TEXT",
            "text": text,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=60,
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    time.sleep(3)

    publish_resp = requests.post(
        f"{BASE_URL}/{THREADS_USER_ID}/threads_publish",
        params={"creation_id": creation_id, "access_token": THREADS_ACCESS_TOKEN},
        timeout=60,
    )
    publish_resp.raise_for_status()
    return publish_resp.json()["id"]
