"""움직임 미리보기 GIF — SVG 애니메이션과 같은 타이밍을 프레임으로 계산해 그린다.
(GitHub README 는 SVG 애니메이션을 재생하지 않는다.)"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import brand as B
from export import render
from PIL import Image

def bezier_ease(x, p1=(0.2, 0.8), p2=(0.2, 1.0)):
    """CSS cubic-bezier(p1x,p1y,p2x,p2y)에서 x(시간)→y(진행). 이분법으로 t를 찾는다."""
    def bx(t): return 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3
    def by(t): return 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo+hi)/2
        if bx(mid) < x: lo = mid
        else: hi = mid
    return by((lo+hi)/2)

def check_frame(progress):
    off = 100 * (1 - progress)
    g = (f'<g transform="translate(0 -4.5)" filter="url(#f-sh)"><path d="M21 71 H40.5 L52.5 82 L79.5 29" fill="none" '
         f'stroke="{B.IVORY}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" pathLength="100" '
         f'stroke-dasharray="100" stroke-dashoffset="{off:.3f}"/></g>') if progress > 0 else ''
    return B.svg(B.tile_rich() + g, B.defs_rich())

def da_frame(op):
    s = B.g_da(B.IVORY, B.SIGN, 9.5, True).replace(f'stroke="{B.SIGN}"', f'stroke="{B.SIGN}" stroke-opacity="{op}"')
    return B.svg(B.tile_rich() + s, B.defs_rich())

def gif(frames, durations, path, size=240):
    tmp = tempfile.mkdtemp()
    ims = []
    for i, svg in enumerate(frames):
        p = os.path.join(tmp, f"f{i}.svg"); open(p, "w").write(svg)
        im = render(p, 512).resize((size, size), Image.LANCZOS)
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
        ims.append(bg.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG))
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=durations, loop=0, optimize=False)

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "release"
    # 체크: 밑줄만 보이는 상태 0.15초 → 0.7초 동안 체크로 솟음(25fps) → 1.4초 유지
    U = 0.2047   # 밑줄 구간 = 경로 길이의 비율 (brand.ANIM_CSS 와 같은 값)
    fr, du = [check_frame(U)], [150]
    n = 18
    for i in range(1, n+1):
        fr.append(check_frame(U + (1-U)*bezier_ease(i/n))); du.append(int(700/n))
    fr.append(check_frame(1)); du.append(1400)
    gif(fr, du, os.path.join(root, "4-check", "motion.gif"))
    # 다: 커서처럼 두 번 흐려졌다 켜진 채로 멈춘다(0까지 끄지 않는다)
    seq = [(1, 300), (.25, 350), (1, 350), (.25, 350), (1, 1600)]  # 완전히 끄면 "디"로 읽힌다
    gif([da_frame(o) for o, _ in seq], [d for _, d in seq], os.path.join(root, "1-da", "motion.gif"))
    print("ok")
