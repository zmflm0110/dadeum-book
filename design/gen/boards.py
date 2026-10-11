"""가이드용 보드 이미지(HTML → PNG). python3 boards.py RELEASE_DIR OUT_DIR"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import brand as B

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
KEYS = [("1-da", "① 다", "한글 음절 '다'. ㅏ의 곁가지 = 커서이자 교정 표시"),
        ("2-dd", "② DD", "DaDeum 머리글자. 겹친 자리를 파낸 모노그램"),
        ("3-daepaebap", "③ 대패밥", "판 위로 끝이 얇아지며 말려 오르는 대패밥 (요청 후보)"),
        ("4-check", "④ 밑줄 → 체크", "밑줄 한 획이 그대로 체크가 된다 (리서치 후보)")]
FONT = '"Apple SD Gothic Neo", "Pretendard", sans-serif'


def shot(html_path, png_path, w, h, scale=2):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--force-device-scale-factor={scale}", f"--window-size={w},{h}",
                    f"--screenshot={png_path}", f"file://{os.path.abspath(html_path)}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def overview(rel, out):
    cards = ""
    for k, name, concept in KEYS:
        r = os.path.relpath(os.path.join(rel, k), out)
        cards += f'''<div class=card>
  <div class=hero><img src="{r}/mark.svg" width=190></div>
  <div class=name>{name}</div><div class=concept>{concept}</div>
  <div class=sizes><img src="{r}/png/mark-128.png" width=64><img src="{r}/png/mark-32.png" width=32><img src="{r}/png/mark-16.png" width=16>
    <span class=mono><img src="{r}/mark-template.svg" width=28></span><span class="mono dark"><img src="{r}/mark-white.svg" width=28></span></div>
  <div class=lock><img src="{r}/lockup-h-light.svg" height=46></div>
  <div class="lock dark"><img src="{r}/lockup-h-dark.svg" height=46></div>
</div>'''
    chips = "".join(f'<div class=chip><div class=sw style="background:{c}"></div><b>{n}</b><code>{c}</code></div>'
                    for n, c in [("먹 남", B.INK), ("중간 남", B.MID), ("전기 남", B.ELEC), ("상아", B.IVORY), ("포인트", B.SIGN)])
    html = f'''<!doctype html><meta charset=utf-8><style>
body{{margin:0;padding:36px 40px;font-family:{FONT};background:#fafafb;color:#131316}}
h1{{margin:0 0 4px;font-size:26px;letter-spacing:-.02em}} .sub{{color:#6b6b76;font-size:14px;margin-bottom:26px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.card{{background:#fff;border:1px solid #e6e6ea;border-radius:22px;padding:22px;box-shadow:0 6px 24px rgba(20,34,74,.06)}}
.hero{{display:flex;justify-content:center;padding:12px 0 14px;background:radial-gradient(circle at 50% 40%,#eef0ff,#fff 70%);border-radius:16px}}
.name{{font-weight:800;font-size:19px;margin-top:14px}} .concept{{color:#55555f;font-size:13px;line-height:1.5;min-height:40px;margin-top:4px}}
.sizes{{display:flex;gap:12px;align-items:center;margin:14px 0}} .sizes img{{display:block}}
.mono{{background:#f1f1f3;border-radius:8px;padding:4px}} .mono.dark{{background:#141416}}
.lock{{background:#f6f6f7;border-radius:12px;padding:12px;margin-top:8px}} .lock.dark{{background:#141416}} .lock img{{display:block}}
.pal{{display:flex;gap:14px;margin-top:26px;align-items:center}} .chip{{display:flex;gap:8px;align-items:center;background:#fff;border:1px solid #e6e6ea;border-radius:12px;padding:8px 12px;font-size:13px}}
.sw{{width:22px;height:22px;border-radius:6px;border:1px solid rgba(0,0,0,.08)}} code{{color:#6b6b76}}
.rule{{margin-left:auto;font-size:13px;color:#8a2a22;background:#fff4f2;border:1px solid #f3d3cf;padding:8px 12px;border-radius:12px}}
</style>
<h1>다듬 로고 후보</h1><div class=sub>네 후보 모두 같은 색·같은 타일·같은 워드마크를 씁니다. 큰 마크는 그라디언트와 입체, 32px 이하는 단순화본입니다.</div>
<div class=grid>{cards}</div>
<div class=pal>{chips}<div class=rule>브랜드 남색은 로고·아이콘 안에서만 — 조사 밑줄색과 ΔE 9.7</div></div>'''
    p = os.path.join(out, "board-overview.html"); open(p, "w").write(html)
    shot(p, os.path.join(out, "board-overview.png"), 1460, 800)


def donts(rel, out):
    r = os.path.relpath(os.path.join(rel, "4-check"), out)
    m = f"{r}/mark.svg"
    items = [
        ("늘이거나 줄이지 않는다", f'<img src="{m}" width=110 style="transform:scaleX(1.45)">'),
        ("돌리지 않는다", f'<img src="{m}" width=110 style="transform:rotate(14deg)">'),
        ("타일 색을 바꾸지 않는다", f'<img src="{m}" width=110 style="filter:hue-rotate(150deg) saturate(1.4)">'),
        ("효과를 더하지 않는다", f'<img src="{m}" width=110 style="filter:drop-shadow(0 0 0 #ff0) drop-shadow(6px 10px 0 #f0a) blur(.3px)">'),
        ("작은 크기에 큰 마크를 쓰지 않는다", '<div style="display:flex;gap:26px;align-items:center"><div style="text-align:center"><img src="rich-16.png" width=64 style="image-rendering:pixelated"><div class=t>큰 마크를 16px로 (탁하다)</div></div><div style="text-align:center"><img src="small-16.png" width=64 style="image-rendering:pixelated"><div class=t>작은 마크 16px (또렷하다)</div></div></div>'),
        ("브랜드 남색으로 밑줄을 긋지 않는다", '<div style="font-size:18px;line-height:2.2">학교<span style="border-bottom:3px solid #1f5bbf">를</span> 갔다 <span style="border-bottom:3px solid #4B4FE8">브랜드</span><div class=t>왼쪽 = 조사 밑줄(#1f5bbf) / 오른쪽 = 브랜드 남색 — 구분이 안 된다</div></div>'),
    ]
    cells = "".join(f'<div class=cell><div class=x>✕</div><div class=demo>{d}</div><div class=cap>{c}</div></div>' for c, d in items)
    html = f'''<!doctype html><meta charset=utf-8><style>
body{{margin:0;padding:34px 40px;font-family:{FONT};background:#fff;color:#131316}}
h1{{margin:0 0 20px;font-size:24px}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.cell{{position:relative;border:1px solid #ececf0;border-radius:18px;padding:22px;height:220px;display:flex;flex-direction:column;justify-content:space-between;background:#fbfbfc}}
.x{{position:absolute;top:14px;right:16px;color:#c22a22;font-weight:800;font-size:20px}}
.demo{{flex:1;display:flex;align-items:center;justify-content:center}} .cap{{font-weight:700;font-size:15px}}
.t{{font-size:11px;color:#6b6b76;margin-top:6px}}
</style><h1>이렇게 쓰지 않습니다</h1><div class=grid>{cells}</div>'''
    p = os.path.join(out, "board-donts.html"); open(p, "w").write(html)
    shot(p, os.path.join(out, "board-donts.png"), 1100, 690)


def spec(rel, out):
    """가로 락업 치수: 마크 100, 간격 24, 워드마크 높이 52, 여백 25(마크의 1/4)."""
    k = 2.0
    wm, ww = B.wordmark(B.INK, B.ELEC, x=124, y=24, h=52)
    W = 124 + ww
    ox, oy = 170, 70
    mark = B.tile_rich() + B.MARKS["4-check"]["rich"]()
    def dim(x1, y1, x2, y2, label, lx, ly):
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#c22a22" stroke-width="1.2" marker-start="url(#a)" marker-end="url(#a)"/>'
                f'<text x="{lx}" y="{ly}" font-size="13" fill="#c22a22" font-family="Apple SD Gothic Neo" text-anchor="middle">{label}</text>')
    pad = 25 * k
    lx, ly, lw, lh = ox, oy, W * k, 100 * k
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{lw + ox * 2 + 170:.0f}" height="{lh + oy * 2 + 90:.0f}">
<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#c22a22"/></marker><marker id="b" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#4B4FE8"/></marker></defs>
{B.defs_rich()}
<rect width="100%" height="100%" fill="#fff"/>
<rect x="{lx - pad}" y="{ly - pad}" width="{lw + pad * 2}" height="{lh + pad * 2}" fill="none" stroke="#4B4FE8" stroke-dasharray="6 5"/>
<g transform="translate({lx} {ly}) scale({k})">{mark}{wm}</g>
{dim(lx, ly + lh + 18, lx + 100 * k, ly + lh + 18, "마크 100", lx + 50 * k, ly + lh + 36)}
{dim(lx + 100 * k, ly + lh + 18, lx + 124 * k, ly + lh + 18, "24", lx + 112 * k, ly + lh + 36)}
{dim(lx + W * k + 14, ly + 24 * k, lx + W * k + 14, ly + 76 * k, "", 0, 0)}
<text x="{lx + W * k + pad + 12}" y="{ly + 50 * k + 5}" font-size="13" fill="#c22a22" font-family="Apple SD Gothic Neo">워드마크 높이 52</text>
<line x1="{lx - pad}" y1="{ly + 50 * k}" x2="{lx}" y2="{ly + 50 * k}" stroke="#4B4FE8" stroke-width="1.2" marker-start="url(#b)" marker-end="url(#b)"/>
<text x="{lx - pad - 8}" y="{ly + 50 * k - 10}" font-size="13" fill="#4B4FE8" font-family="Apple SD Gothic Neo" text-anchor="end">여백 25</text>
<text x="{lx - pad - 8}" y="{ly + 50 * k + 8}" font-size="11" fill="#4B4FE8" font-family="Apple SD Gothic Neo" text-anchor="end">(마크의 1/4)</text>
<text x="{lx}" y="{ly + lh + pad + 64}" font-size="14" fill="#131316" font-family="Apple SD Gothic Neo">최소 크기 — 마크 16px(작은 마크 사용) · 가로 락업 높이 32px · 세로 락업 너비 64px</text>
</svg>'''
    p = os.path.join(out, "board-spec.svg"); open(p, "w").write(svg)
    html = os.path.join(out, "board-spec.html")
    open(html, "w").write(f'<!doctype html><body style="margin:0"><img src="board-spec.svg">')
    import re
    w = int(re.search(r'width="(\d+)"', svg).group(1)); h = int(re.search(r'height="(\d+)"', svg).group(1))
    shot(html, os.path.join(out, "board-spec.png"), w, h)


def wordmark_board(out):
    k = 3.0
    body, w = B.wordmark(B.INK, B.ELEC)
    W = w * k
    guides = ""
    for y, lab in [(0, "0"), (10, "10 · ㄷ 위"), (33, "33 · 듬의 ㄷ 아래"), (44, "44 · ㅡ"), (55.5, "55.5"), (66.5, "66.5 · ㅁ 위"), (90, "90 · ㄷ 아래"), (100, "100")]:
        guides += (f'<line x1="0" y1="{y * k}" x2="{W}" y2="{y * k}" stroke="#4B4FE8" stroke-opacity=".35" stroke-dasharray="4 4"/>'
                   f'<text x="{W + 10}" y="{y * k + 4}" font-size="12" fill="#4B4FE8" font-family="Apple SD Gothic Neo">{lab}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W + 190:.0f}" height="{100 * k + 120:.0f}">
<rect width="100%" height="100%" fill="#fff"/>
<g transform="translate(40 40)">{guides}<g transform="scale({k})">{body}</g>
<text x="0" y="{100 * k + 44}" font-size="14" fill="#131316" font-family="Apple SD Gothic Neo">세로획 {B.SV:g} · 가로획 {B.SH:g} (가로획을 조금 얇게 — 같은 두께로 보이게 하는 광학 보정) · 자간 {B.TRACK} · 곁가지만 포인트색</text></g></svg>'''
    p = os.path.join(out, "board-wordmark.svg"); open(p, "w").write(svg)
    html = os.path.join(out, "board-wordmark.html")
    open(html, "w").write('<!doctype html><body style="margin:0"><img src="board-wordmark.svg">')
    shot(html, os.path.join(out, "board-wordmark.png"), int(W + 190), int(100 * k + 120))


def context(rel, out):
    """실제 화면 속 모습: macOS Dock, 브라우저 탭(16px), 크롬 툴바(밝음·어두움), 메뉴바(밝음·어두움)."""
    generic = ["linear-gradient(160deg,#ffb36b,#ff6a3d)", "linear-gradient(160deg,#7be0b0,#1aa36f)",
               "linear-gradient(160deg,#d6d6db,#9b9ba4)", "linear-gradient(160deg,#8fd0ff,#2b86ff)"]
    cols = "110px 300px 250px 140px 140px 130px 130px"
    css = (f"body{{margin:0;padding:22px;font-family:{FONT};background:#fff;color:#131316}}"
           f".row,.head{{display:grid;grid-template-columns:{cols};gap:14px;align-items:center;margin-bottom:14px}}"
           ".head{font-size:12px;color:#6b6b76;margin-bottom:8px}.lab{font-weight:700;font-size:14px}"
           ".dock{display:flex;gap:9px;align-items:flex-end;padding:9px 12px;border-radius:18px;background:rgba(235,235,240,.85);border:1px solid #d8d8de;box-shadow:0 8px 22px rgba(0,0,0,.12)}"
           ".dock .g{width:40px;height:40px;border-radius:10px}.dock img{width:48px;height:48px;display:block}"
           ".tabs{background:#dfe1e5;border-radius:10px;padding:6px 6px 0}.tab{background:#fff;border-radius:8px 8px 0 0;padding:8px 10px;display:flex;gap:8px;align-items:center;font-size:12px;width:200px}.tab img{width:16px;height:16px}"
           ".tb{display:flex;gap:10px;align-items:center;padding:8px 10px;border-radius:10px}.tb .o{width:16px;height:16px;border-radius:4px;opacity:.55}.tb img{width:16px;height:16px;display:block}"
           ".tbl{background:#fff;border:1px solid #e3e3e6}.tbl .o{background:#5f6368}.tbd{background:#35363a}.tbd .o{background:#c4c7c5}"
           ".mb{display:flex;gap:12px;align-items:center;justify-content:flex-end;padding:3px 10px;height:22px;border-radius:6px;font-size:12px}"
           ".mbl{background:#ececec;color:#000}.mbd{background:#28282a;color:#fff}.mb img{width:18px;height:18px;display:block}.mbd img{filter:invert(1)}")
    rows = ("<div class=head><div></div><div>macOS Dock</div><div>브라우저 탭 (16px)</div><div>크롬 툴바 · 밝음</div>"
            "<div>크롬 툴바 · 어두움</div><div>메뉴바 · 밝음</div><div>메뉴바 · 어두움</div></div>")
    for k, name, _ in KEYS:
        r = os.path.relpath(os.path.join(rel, k), out)
        g1 = "".join(f'<div class=g style="background:{c}"></div>' for c in generic[:2])
        g2 = "".join(f'<div class=g style="background:{c}"></div>' for c in generic[2:])
        rows += (f'<div class=row><div class=lab>{name}</div>'
                 f'<div class=dock>{g1}<img src="{r}/png/mark-256.png">{g2}</div>'
                 f'<div class=tabs><div class=tab><img src="{r}/png/mark-32.png">다듬 — 맞춤법 검사</div></div>'
                 f'<div class="tb tbl"><div class=o></div><div class=o></div><img src="{r}/extension/icon32.png"><div class=o></div></div>'
                 f'<div class="tb tbd"><div class=o></div><div class=o></div><img src="{r}/extension/icon32.png"><div class=o></div></div>'
                 f'<div class="mb mbl"><span>100%</span><img src="{r}/menubar/menubarTemplate@2x.png"><span>12:30</span></div>'
                 f'<div class="mb mbd"><span>100%</span><img src="{r}/menubar/menubarTemplate@2x.png"><span>12:30</span></div></div>')
    p = os.path.join(out, "board-context.html"); open(p, "w").write(f"<!doctype html><meta charset=utf-8><style>{css}</style>{rows}")
    shot(p, os.path.join(out, "board-context.png"), 1360, 420)


def tiny_compare(rel, out):
    """'작은 크기에 큰 마크를 쓰지 않는다' 예시에 쓸 실제 16px 이미지."""
    from export import render, down
    from PIL import Image
    down(render(os.path.join(rel, "4-check", "mark.svg")), 16).save(os.path.join(out, "rich-16.png"))
    Image.open(os.path.join(rel, "4-check", "png", "mark-16.png")).save(os.path.join(out, "small-16.png"))


if __name__ == "__main__":
    rel, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    tiny_compare(rel, out); overview(rel, out); context(rel, out); donts(rel, out); spec(rel, out); wordmark_board(out)
    print("ok")
