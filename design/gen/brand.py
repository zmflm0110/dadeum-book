"""다듬 로고 후보 — 단일 생성기.

    python3 brand.py OUT_DIR

손으로 고친 SVG는 서로 어긋난다(다듬 저장소 scripts/build-icons.sh 주석과 같은 이유).
그래서 모든 마크·변형·락업을 이 파일의 수치에서 만든다. 좌표계는 100x100.

변형
  mark.svg           그라디언트 타일 + 입체감 (64px 이상)
  mark-small.svg     평면 타일, 굵은 획 (16·32px, 파비콘)
  mark-template.svg  타일 없이 검정 + 투명도 (macOS 메뉴바 템플릿 이미지)
  mark-white.svg     타일 없이 흰색 (어두운 바탕)
  mark-animated.svg  (일부) 한 번 재생되는 움직임
  lockup-*.svg       마크 + 워드마크
  appicon-macos.svg  1024 캔버스, 824 몸체(애플 아이콘 격자)
"""
from __future__ import annotations

import math
import os
import sys

# ── 색 ──────────────────────────────────────────────────────────────
INK = "#14224A"     # 먹 남
MID = "#232D8F"
ELEC = "#4B4FE8"    # 전기 남 — 로고 안에서만 (조사 밑줄색과 ΔE 9.7)
IVORY = "#F6F0E0"   # 상아
SIGN = "#C9CCFF"    # 포인트
DEEP = "#0A1030"
WHITE = "#FFFFFF"
BLACK = "#000000"


# ── 타일: 초타원(n=5) ────────────────────────────────────────────────
def squircle(n: float = 5.0, steps: int = 180, pad: float = 0.0) -> str:
    r = 50 - pad
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        pts.append(f"{50 + r * math.copysign(abs(c) ** (2 / n), c):.2f} "
                   f"{50 + r * math.copysign(abs(s) ** (2 / n), s):.2f}")
    return "M" + " L".join(pts) + " Z"


SQ = squircle()
SQ_IN = squircle(pad=0.9)


def defs_rich(extra: str = "") -> str:
    return f'''<defs>
    <linearGradient id="g-bg" gradientUnits="userSpaceOnUse" x1="5" y1="0" x2="95" y2="100">
      <stop offset="0" stop-color="{ELEC}"/><stop offset=".52" stop-color="{MID}"/><stop offset="1" stop-color="{INK}"/>
    </linearGradient>
    <radialGradient id="g-hi" cx=".28" cy=".06" r=".85">
      <stop offset="0" stop-color="#fff" stop-opacity=".30"/><stop offset=".6" stop-color="#fff" stop-opacity=".04"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="g-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".38"/><stop offset=".5" stop-color="#fff" stop-opacity=".04"/><stop offset="1" stop-color="#000" stop-opacity=".25"/>
    </linearGradient>
    <filter id="f-sh" x="-25%" y="-25%" width="150%" height="160%">
      <feDropShadow dx="0" dy="2.4" stdDeviation="2.1" flood-color="{DEEP}" flood-opacity=".55"/>
    </filter>{extra}
  </defs>'''


def tile_rich() -> str:
    return (f'<path d="{SQ}" fill="url(#g-bg)"/><path d="{SQ}" fill="url(#g-hi)"/>'
            f'<path d="{SQ_IN}" fill="none" stroke="url(#g-rim)" stroke-width="1.1"/>')


SMALL_DARK = "#2F37C8"   # 작은 타일의 아래쪽. 먹 남은 어두운 툴바와 대비 1.28:1 이라 묻힌다.


def defs_small(extra: str = "") -> str:
    return (f'<defs><linearGradient id="g-sm" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100" y2="100">'
            f'<stop offset="0" stop-color="{ELEC}"/><stop offset="1" stop-color="{SMALL_DARK}"/></linearGradient>{extra}</defs>')


def tile_flat() -> str:
    """작은 크기(16·32·48px) 타일. 전기 남 계열이라 밝은·어두운 툴바 어디서나 경계가 남는다
    (최소 대비 2.06:1, 흰 글리프와 5.86:1 — gen/metrics.py)."""
    return f'<path d="{SQ}" fill="url(#g-sm)"/>'


# ── 리본(대패밥) ─────────────────────────────────────────────────────
def ribbon(points, widths) -> str:
    n = len(points)
    left, right = [], []
    for i, (x, y) in enumerate(points):
        if i == 0:
            dx, dy = points[1][0] - x, points[1][1] - y
        elif i == n - 1:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in left)
    ew = widths[-1] / 2
    d += f" A{ew:.2f} {ew:.2f} 0 0 0 {right[-1][0]:.2f} {right[-1][1]:.2f}"
    d += " L" + " L".join(f"{x:.2f} {y:.2f}" for x, y in reversed(right))
    sw = widths[0] / 2
    d += f" A{sw:.2f} {sw:.2f} 0 0 0 {left[0][0]:.2f} {left[0][1]:.2f} Z"
    return d


def shaving(x0=20.0, cx=60.0, cy=43.0, r0=18.5, r1=6.0, turns=1.25, w0=10.0, w1=4.2,
            steps=160) -> str:
    """판 위의 곧은 리본이 위로 말려 들어가는 대패밥. 로그 나선 r(t)=r0*(r1/r0)^t,
    굵기는 처음 15%를 지난 뒤 끝으로 갈수록 얇아진다."""
    pts, ws = [], []
    y_base = cy + r0
    for i in range(24):
        t = i / 24
        pts.append((x0 + (cx - x0) * t, y_base))
        ws.append(w0)
    for i in range(steps + 1):
        t = i / steps
        r = r0 * (r1 / r0) ** t
        th = math.radians(90 - 360 * turns * t)
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
        k = 0 if t < .15 else ((t - .15) / .85) ** 0.9
        ws.append(w0 + (w1 - w0) * k)
    return ribbon(pts, ws)


SHAVING = shaving()


def dshape(x, y, w, h, s) -> str:
    """두께 s의 D 외곽(evenodd)."""
    r = h / 2
    ri = r - s
    return (f"M{x} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w - r} {y + h} H{x} Z "
            f"M{x + s} {y + s} H{x + w - r} A{ri} {ri} 0 0 1 {x + w - r} {y + h - s} H{x + s} Z")


D1 = dshape(16, 29, 33, 42, 9)
D2 = dshape(47, 29, 33, 42, 9)
KO_GAP = 3.2


# ── 글리프(타일 위에 놓이는 형상) ────────────────────────────────────
def g_check(color, w, shadow, animated=False) -> str:
    f = ' filter="url(#f-sh)"' if shadow else ''
    anim = ''
    extra = ''
    if animated:
        extra = ' pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"'
        anim = ('<animate attributeName="stroke-dashoffset" from="100" to="0" dur="0.7s" begin="0.15s" '
                'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>')
    return (f'<g transform="translate(0 -4.5)"{f}><path d="M21 71 H40.5 L52.5 82 L79.5 29" fill="none" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{extra}>{anim}</path></g>')


def g_da(color, accent, w, shadow, animated=False) -> str:
    f = ' filter="url(#f-sh)"' if shadow else ''
    half = w / 2
    anim = ('<animate attributeName="opacity" values="1;.25;1;.25;1" keyTimes="0;.25;.5;.75;1" dur="1.4s" '
            'begin="0.3s" fill="freeze"/>') if animated else ''
    return (f'<g transform="translate(-3 0)"{f}>'
            f'<path d="M51.5 31.5 H29.5 V68.5 H51.5" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="miter" stroke-miterlimit="4"/>'
            f'<path d="M65.5 22 V78" fill="none" stroke="{color}" stroke-width="{w}"/>'
            f'<path d="M{65.5 + half:.2f} 50 H81.5" fill="none" stroke="{accent}" stroke-width="{w}">{anim}</path></g>')


def g_dd(c1, c2, o2, shadow) -> str:
    f = ' filter="url(#f-sh)"' if shadow else ''
    return (f'<g transform="translate(2 0)"{f}>'
            f'<path d="{D1}" fill="{c1}" fill-rule="evenodd" mask="url(#ko)"/>'
            f'<path d="{D2}" fill="{c2}" fill-opacity="{o2}" fill-rule="evenodd"/></g>')


DD_MASK = (f'<mask id="ko" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
           f'<rect width="100" height="100" fill="#fff"/>'
           f'<path d="{D2}" fill="#000" stroke="#000" stroke-width="{KO_GAP * 2}"/></mask>')


def g_bap(color, plank, plank_o, shadow) -> str:
    f = ' filter="url(#f-sh)"' if shadow else ''
    return (f'<g transform="translate(0 -3)"{f}>'
            f'<rect x="16" y="72" width="68" height="6.5" rx="3.25" fill="{plank}" fill-opacity="{plank_o}"/>'
            f'<path d="{SHAVING}" fill="{color}"/></g>')


# ── 문서 조립 ────────────────────────────────────────────────────────
def svg(body: str, defs: str = "", title: str = "", desc: str = "", vb: str = "0 0 100 100") -> str:
    t = f'<title>{title}</title><desc>{desc}</desc>' if title else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img">{t}{defs}{body}</svg>\n'


MARKS = {
    "1-da": dict(
        title="다듬 — 다", desc="한글 음절 '다'(ㄷ+ㅏ). ㅏ의 가로획은 글 쓰는 곳의 커서이자 교정 표시.",
        rich=lambda: g_da(IVORY, SIGN, 9.5, True), small=lambda: g_da(WHITE, SIGN, 11, False),
        template=lambda: g_da(BLACK, BLACK, 11, False), white=lambda: g_da(WHITE, WHITE, 11, False),
        animated=lambda: g_da(IVORY, SIGN, 9.5, True, animated=True), mask=""),
    "2-dd": dict(
        title="다듬 — DD", desc="DaDeum 머리글자. 두 D가 겹친 자리를 파내 하나의 모노그램으로 묶었다.",
        rich=lambda: g_dd(IVORY, SIGN, 1, True), small=lambda: g_dd(WHITE, SIGN, 1, False),
        template=lambda: g_dd(BLACK, BLACK, .55, False), white=lambda: g_dd(WHITE, WHITE, .6, False),
        animated=None, mask=DD_MASK),
    "3-daepaebap": dict(
        title="다듬 — 대패밥", desc="대패질한 판 위로 끝이 얇아지며 말려 올라오는 대패밥.",
        rich=lambda: g_bap(IVORY, SIGN, 1, True), small=lambda: g_bap(WHITE, SIGN, 1, False),
        template=lambda: g_bap(BLACK, BLACK, .55, False), white=lambda: g_bap(WHITE, WHITE, .6, False),
        animated=None, mask=""),
    "4-check": dict(
        title="다듬 — 밑줄이 체크가 되다", desc="틀린 자리의 밑줄이 한 획으로 이어져 확정(체크)이 된다.",
        rich=lambda: g_check(IVORY, 11, True), small=lambda: g_check(WHITE, 12.5, False),
        template=lambda: g_check(BLACK, 12, False), white=lambda: g_check(WHITE, 12, False),
        animated=lambda: g_check(IVORY, 11, True, animated=True), mask=""),
}


# ── 워드마크 '다듬' ───────────────────────────────────────────────────
SV, SH = 13.0, 11.5
TRACK = 14


def _wm_rects():
    r, x0 = [], 0
    r += [(x0, 10, 46, SH), (x0, 10, SV, 80), (x0, 90 - SH, 46, SH)]
    r += [(x0 + 59, 0, SV, 100)]
    tick = (x0 + 59 + SV, 50 - SH / 2, 17, SH)
    x0 = 89 + TRACK
    r += [(x0 + 7, 0, 86, SH), (x0 + 7, 0, SV, 33), (x0 + 7, 33 - SH, 86, SH)]
    r += [(x0, 44, 100, SH)]
    r += [(x0 + 7, 66.5, 86, SH), (x0 + 7, 100 - SH, 86, SH),
          (x0 + 7, 66.5, SV, 33.5), (x0 + 93 - SV, 66.5, SV, 33.5)]
    return r, tick, x0 + 100


def wordmark(fill, accent, x=0.0, y=0.0, h=100.0):
    rects, tick, w = _wm_rects()
    s = h / 100

    def R(a, c):
        return (f'<rect x="{x + a[0] * s:.2f}" y="{y + a[1] * s:.2f}" '
                f'width="{a[2] * s:.2f}" height="{a[3] * s:.2f}" fill="{c}"/>')
    return "".join(R(a, fill) for a in rects) + R(tick, accent), w * s


def build(out: str) -> None:
    os.makedirs(out, exist_ok=True)
    wm_dir = os.path.join(out, "wordmark")
    os.makedirs(wm_dir, exist_ok=True)
    for theme, fill, acc in (("light", INK, ELEC), ("dark", IVORY, SIGN)):
        body, w = wordmark(fill, acc)
        open(os.path.join(wm_dir, f"wordmark-{theme}.svg"), "w").write(
            svg(body, title="다듬", desc="다듬 워드마크", vb=f"0 0 {w:.0f} 100"))

    for key, m in MARKS.items():
        d = os.path.join(out, key)
        os.makedirs(d, exist_ok=True)
        T, Dsc, mask = m["title"], m["desc"], m["mask"]
        rich = tile_rich() + m["rich"]()
        open(os.path.join(d, "mark.svg"), "w").write(svg(rich, defs_rich(mask), T, Dsc))
        open(os.path.join(d, "mark-small.svg"), "w").write(
            svg(tile_flat() + m["small"](), defs_small(mask), T + " (작은 크기)", Dsc))
        open(os.path.join(d, "mark-template.svg"), "w").write(
            svg(m["template"](), f"<defs>{mask}</defs>" if mask else "", T + " (템플릿)", Dsc))
        open(os.path.join(d, "mark-white.svg"), "w").write(
            svg(m["white"](), f"<defs>{mask}</defs>" if mask else "", T + " (흰색)", Dsc))
        if m["animated"]:
            open(os.path.join(d, "mark-animated.svg"), "w").write(
                svg(tile_rich() + m["animated"](), defs_rich(mask), T + " (움직임)", Dsc))

        # 락업: 가로(마크 100 + 간격 24 + 워드마크 높이 52), 세로(마크 위, 워드마크 아래)
        for theme, fill, acc in (("light", INK, ELEC), ("dark", IVORY, SIGN)):
            wm, ww = wordmark(fill, acc, x=124, y=24, h=52)
            body = f'<g>{rich}</g>{wm}'
            open(os.path.join(d, f"lockup-h-{theme}.svg"), "w").write(
                svg(body, defs_rich(mask), T + " 가로 락업", Dsc, vb=f"0 0 {124 + ww:.0f} 100"))
            wm_v, wv = wordmark(fill, acc, h=34)
            x = (100 - wv) / 2
            wm_v, _ = wordmark(fill, acc, x=x, y=118, h=34)
            body = f'<g>{rich}</g>{wm_v}'
            open(os.path.join(d, f"lockup-v-{theme}.svg"), "w").write(
                svg(body, defs_rich(mask), T + " 세로 락업", Dsc, vb="0 0 100 152"))

        # macOS 앱 아이콘: 1024 캔버스, 824 몸체, 그림자
        app_defs = defs_rich(mask + '<filter id="f-app" x="-10%" y="-10%" width="120%" height="125%">'
                             '<feDropShadow dx="0" dy="1.2" stdDeviation="1.2" flood-color="#000" flood-opacity=".30"/></filter>')
        body = f'<g transform="translate(100 100) scale(8.24)"><g filter="url(#f-app)">{rich}</g></g>'
        open(os.path.join(d, "appicon-macos.svg"), "w").write(
            svg(body, app_defs, T + " (macOS 앱 아이콘)", Dsc, vb="0 0 1024 1024"))
        small_app = f'<g transform="translate(100 100) scale(8.24)">{tile_flat() + m["small"]()}</g>'
        open(os.path.join(d, "appicon-macos-small.svg"), "w").write(
            svg(small_app, defs_small(mask), T + " (macOS 작은 아이콘)", Dsc, vb="0 0 1024 1024"))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "release")
    print("ok")
