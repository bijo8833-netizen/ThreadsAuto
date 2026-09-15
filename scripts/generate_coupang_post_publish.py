import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from common import threads_client

META_PATH = "output/meta/coupang_latest.json"


def build_raw_github_url(local_path: str) -> str:
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_BRANCH", "main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{local_path}"


def main():
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    image_url = build_raw_github_url(meta["image_path"])
    print(f"[게시할 이미지 URL] {image_url}")

    thread_id = threads_client.post_image_thread(meta["body"], image_url)
    print(f"[게시 완료] thread_id={thread_id}")


if __name__ == "__main__":
    main()
