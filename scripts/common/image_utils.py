"""
bijo0602 계정의 기존 스타일(실제 사진 배경 + 굵은 한글 헤드라인 카드)을
자동으로 재현하는 이미지 생성 모듈.

워크플로(GitHub Actions)에서는 `sudo apt-get install -y fonts-nanum` 로
나눔고딕 폰트를 설치한 뒤 이 스크립트를 실행한다.
"""
import io
import os
import textwrap

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CANVAS_SIZE = (1080, 1080)  # 스레드에 최적화된 정사각 비율

# GitHub Actions에서 fonts-nanum 설치 시 기본 경로
DEFAULT_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    os.environ.get("FONT_PATH", ""),
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in DEFAULT_FONT_CANDIDATES:
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise RuntimeError(
        "한글 폰트를 찾을 수 없습니다. GitHub Actions 워크플로에서 "
        "'sudo apt-get install -y fonts-nanum' 단계가 실행됐는지 확인하세요."
    )


def _download_image(url: str) -> Image.Image:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _fit_and_crop(img: Image.Image, size: tuple) -> Image.Image:
    """이미지를 잘리지 않게 비율 유지하며 정사각형으로 크롭한다."""
    target_w, target_h = size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_size = (int(src_w * scale), int(src_h * scale))
    img = img.resize(new_size, Image.LANCZOS)
    left = (img.width - target_w) // 2
    top = (img.height - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    lines = []
    for raw_line in text.split("\n"):
        words = list(raw_line)  # 한글은 어절보다 글자 단위 줄바꿈이 자연스러움
        current = ""
        for ch in words:
            test = current + ch
            if draw.textlength(test, font=font) <= max_width:
                current = test
            else:
                lines.append(current)
                current = ch
        lines.append(current)
    return lines


def create_headline_card(
    photo_url: str,
    headline: str,
    brand_text: str = "밀키웨이 | bijo0602",
    output_path: str = "output/images/card.jpg",
) -> str:
    """
    실사 스톡사진 위에 어두운 그라데이션 + 굵은 헤드라인 텍스트를 올린
    정사각 카드 이미지를 생성해서 output_path에 저장하고 경로를 반환한다.
    """
    base = _download_image(photo_url)
    base = _fit_and_crop(base, CANVAS_SIZE)

    # 하단 어두운 그라데이션 오버레이 (글씨 가독성 확보)
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(overlay)
    gradient_height = int(CANVAS_SIZE[1] * 0.55)
    for y in range(gradient_height):
        alpha = int(200 * (y / gradient_height))
        y_pos = CANVAS_SIZE[1] - gradient_height + y
        grad_draw.line([(0, y_pos), (CANVAS_SIZE[0], y_pos)], fill=(0, 0, 0, alpha))

    base = base.convert("RGBA")
    base = Image.alpha_composite(base, overlay)

    draw = ImageDraw.Draw(base)

    headline_font = _load_font(78)
    brand_font = _load_font(32)

    padding = 70
    max_text_width = CANVAS_SIZE[0] - padding * 2
    lines = _wrap_text(headline, headline_font, max_text_width, draw)

    line_height = headline_font.size + 14
    total_text_height = line_height * len(lines)
    y = CANVAS_SIZE[1] - padding - 60 - total_text_height

    for line in lines:
        # 얇은 외곽선(스트로크)으로 가독성 강화
        draw.text((padding, y), line, font=headline_font, fill="white",
                   stroke_width=3, stroke_fill=(0, 0, 0, 255))
        y += line_height

    draw.text((padding, CANVAS_SIZE[1] - padding - 10), brand_text,
               font=brand_font, fill=(255, 255, 255, 230))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base.convert("RGB").save(output_path, "JPEG", quality=90)
    return output_path


def create_product_card(
    product_image_url: str,
    product_name: str,
    price_text: str,
    badge_text: str = "오늘의 인기템",
    brand_text: str = "밀키웨이 | bijo0602",
    output_path: str = "output/images/product_card.jpg",
) -> str:
    """쿠팡 제휴 상품용 카드 이미지를 생성한다 (상품사진 + 상품명 + 가격 배지)."""
    product_img = _download_image(product_image_url)

    # 배경은 흐릿하게 확대한 상품 이미지, 중앙에 선명한 상품 이미지를 얹는 방식
    bg = _fit_and_crop(product_img, CANVAS_SIZE).filter(ImageFilter.GaussianBlur(30))
    bg = bg.convert("RGBA")

    dark_overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 90))
    bg = Image.alpha_composite(bg, dark_overlay)

    # 중앙 상품 이미지 (흰 배경 카드 위에)
    thumb_size = 700
    product_thumb = _fit_and_crop(product_img, (thumb_size, thumb_size))
    white_card = Image.new("RGBA", (thumb_size + 40, thumb_size + 40), (255, 255, 255, 255))
    white_card.paste(product_thumb, (20, 20))
    paste_x = (CANVAS_SIZE[0] - white_card.width) // 2
    paste_y = 140
    bg.paste(white_card, (paste_x, paste_y))

    draw = ImageDraw.Draw(bg)
    badge_font = _load_font(36)
    name_font = _load_font(48)
    price_font = _load_font(64)
    brand_font = _load_font(30)

    draw.text((70, 60), badge_text, font=badge_font, fill=(255, 210, 0))

    name_y = paste_y + white_card.height + 40
    max_text_width = CANVAS_SIZE[0] - 140
    for line in _wrap_text(product_name, name_font, max_text_width, draw)[:2]:
        draw.text((70, name_y), line, font=name_font, fill="white",
                   stroke_width=2, stroke_fill=(0, 0, 0, 255))
        name_y += name_font.size + 10

    draw.text((70, name_y + 10), price_text, font=price_font, fill=(255, 90, 90),
               stroke_width=2, stroke_fill=(0, 0, 0, 255))

    draw.text((70, CANVAS_SIZE[1] - 70), brand_text, font=brand_font, fill=(255, 255, 255, 230))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bg.convert("RGB").save(output_path, "JPEG", quality=90)
    return output_path
