"""
1단계: 쿠팡 베스트상품 조회 -> 딥링크 생성 -> 문구/이미지 생성 -> 메타데이터 저장.
이후 워크플로가 git commit & push 하고 나서 _publish.py 가 Threads에 게시한다.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "coupang"))

from common import claude_client, image_utils, state
from coupang import coupang_api

META_PATH = "output/meta/coupang_latest.json"


def main():
    product = coupang_api.get_best_product()
    product_name = product["productName"]
    price = f"{int(product['productPrice']):,}원"
    product_image_url = product["productImage"]
    product_url = product["productUrl"]
    category = product.get("categoryName", "인기상품")

    print(f"[선정 상품] {product_name} / {price}")
    print(f"[디버그] product_url = {product_url}")
    deeplink = coupang_api.create_deeplink(product_url)
    print(f"[딥링크] {deeplink}")

    body_text = claude_client.generate_coupang_post(product_name, price, category)
    full_body = f"{body_text}\n\n{deeplink}"

    image_path = image_utils.create_product_card(
        product_image_url, product_name, price, output_path="output/images/coupang_card.jpg"
    )
    print(f"[이미지 저장] {image_path}")

    state.add_used_topic(f"coupang:{product.get('productId')}")

    os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({"body": full_body, "image_path": image_path}, f, ensure_ascii=False, indent=2)
    print(f"[메타데이터 저장 완료] {META_PATH}")


if __name__ == "__main__":
    main()
