# 다듬 로고 작업 원본

다듬 저장소 PR #12(`design/logo-candidates`)의 작업 원본입니다. 이 폴더는 **전체 내보내기**(`.icns`, 모든 PNG 크기)까지 담고, PR에는 다시 만들 수 있는 큰 파일을 넣지 않았습니다.

- `gen/` — 생성기(`brand.py` · `export.py` · `motion.py` · `boards.py` · `metrics.py`). PR의 `src/`와 같습니다.
- `release/` — 후보 4종 전체 출력(macOS `DaDeum.icns` 포함)
- `boards/` — 가이드 보드 이미지
- `concepts/` — 탐색 시안 기록(ㄷ 단독, 통나무·결 무늬, 체크 3종 등 탈락안 포함)

다시 만들기:

```bash
python3 gen/brand.py release && python3 gen/export.py release && python3 gen/motion.py release && python3 gen/boards.py release boards
```
