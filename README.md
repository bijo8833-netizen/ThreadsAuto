# 밀키웨이(bijo0602) 스레드 자동 게시 프로그램

하루 5회, 완전 자동으로 Threads에 게시하는 프로그램입니다.

- **일반 소재 3회** (06:00 / 15:00 / 21:00 KST): 화제 뉴스를 소재로 bijo0602 계정
  톤에 맞춰 AI가 새 글을 쓰고, 실사 스톡사진으로 카드 이미지를 만들어 게시
- **쿠팡 제휴 2회** (11:30 / 18:00 KST): 쿠팡 베스트카테고리 인기상품을 골라
  제휴 링크를 자동 생성하고, 상품 이미지 카드와 함께 게시

한 번 설정해두면 GitHub Actions가 매일 정해진 시간에 알아서 실행합니다.
PC를 켜둘 필요가 없습니다.

---

## 0. 먼저 알아두실 점 (한계 안내)

- Threads는 다른 계정 게시물의 **정확한 조회수를 API로 공개하지 않아서**,
  "3일 내 100만 조회수 게시물"을 자동으로 찾아내는 것은 불가능합니다.
  대신 **구글 뉴스에서 지금 화제가 되는 소재**를 가져와 AI가 bijo0602 톤으로
  새로 써내는 방식으로 대체했습니다.
- 쿠팡도 **정확한 3일간 판매량 수치는 API로 공개하지 않아서**, 가장 가까운
  대안인 **베스트카테고리 랭킹(인기순)**을 기준으로 상품을 선정합니다.
- 이미지는 요청하신 대로 **AI 생성 이미지가 아닌 실제 스톡사진**(Pexels)에
  굵은 글씨 카드를 입히는 방식이라, 사실감 있는 결과물이 나옵니다.

---

## 1. 필요한 것 準備 체크리스트

| 항목 | 어디서 발급 | 비용 |
|---|---|---|
| GitHub 계정 | github.com 가입 | 무료 |
| Threads Access Token, User ID | developers.facebook.com (이전 안내 참고) | 무료 |
| Anthropic API Key | console.anthropic.com | 사용량 과금 (하루 5건이면 매우 저렴, 월 몇천 원 수준) |
| Pexels API Key | pexels.com/api | 무료 |
| 쿠팡파트너스 Access/Secret Key | partners.coupang.com > 오픈API | 무료 |

---

## 2. GitHub에 이 코드 올리기

1. github.com에서 새 저장소(Repository) 생성 (예: `milkyway-auto`), **Private**로 설정 권장
2. 이 폴더 전체를 그 저장소에 업로드
   - GitHub 웹사이트에서 "Add file → Upload files"로 전체 폴더를 드래그해도 되고,
     git이 익숙하시면 아래처럼 하셔도 됩니다.
   ```
   git init
   git remote add origin https://github.com/사용자명/milkyway-auto.git
   git add .
   git commit -m "init"
   git branch -M main
   git push -u origin main
   ```

## 3. 비밀 키(Secrets) 등록하기

저장소 페이지 → **Settings → Secrets and variables → Actions → New repository secret**
에서 아래 7개를 하나씩 등록하세요. (`.env.example` 파일에 있는 이름과 동일하게)

- `THREADS_ACCESS_TOKEN`
- `THREADS_USER_ID`
- `ANTHROPIC_API_KEY`
- `PEXELS_API_KEY`
- `COUPANG_ACCESS_KEY`
- `COUPANG_SECRET_KEY`
- `COUPANG_SUBID` (예: `milkyway7` — 자유롭게 정하시면 됩니다)

## 4. 자동 실행 켜기

Secrets만 등록하면 `.github/workflows/` 안의 두 워크플로가 자동으로 매일
정해진 시간(위 표 참고)에 실행됩니다. 별도로 켤 필요 없습니다.

**바로 테스트하고 싶다면:**
저장소 → **Actions** 탭 → 왼쪽에서 워크플로 선택
("일반 소재 스레드 자동 게시" 또는 "쿠팡 제휴 스레드 자동 게시")
→ 우측 **Run workflow** 버튼으로 즉시 1회 실행해볼 수 있습니다.

---

## 5. 쿠팡 카테고리 수정하기 (선택)

`scripts/coupang/coupang_api.py` 상단의 `CATEGORY_IDS` 딕셔너리에서
소개하고 싶은 상품 카테고리를 자유롭게 수정하세요.
코드에 넣어둔 값은 예시이니, **쿠팡파트너스 개발자센터 문서**에서
최신 카테고리 코드 표를 확인해서 정확한 값으로 교체하시는 걸 권장합니다.

---

## 6. 문제가 생겼을 때

- Actions 탭 → 실패한 실행(빨간 X) 클릭 → 로그를 열어보면 어느 단계에서
  왜 실패했는지 한글/영어 에러 메시지로 나옵니다.
- 자주 발생하는 원인:
  - Threads Access Token 만료 (Meta 토큰은 보통 60일 후 만료 → 재발급 필요)
  - 쿠팡 서명 오류: `coupang_auth.py`의 인증 방식이 최신 쿠팡 스펙과
    다를 경우 실패할 수 있음 → 개발자센터 문서와 비교 확인 필요
  - GitHub Actions의 스케줄은 서버 부하에 따라 **몇 분~십수 분 정도 늦게**
    실행될 수 있습니다 (GitHub 공식 정책, 정확히 정시 실행을 100% 보장하지 않음)

---

## 7. 법적 고지 관련

쿠팡 제휴 게시글에는 자동으로 아래 문구가 포함됩니다 (공정거래위원회 표시광고
가이드라인 준수 목적). 임의로 삭제하지 마세요.

> (이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.)
