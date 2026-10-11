"""brand.py 가 만든 SVG를 실제로 쓰는 파일로 내보낸다.

    python3 export.py RELEASE_DIR

  png/            1024 · 512 · 256 · 180 · 128 · 64 (큰 마크), 48 · 32 · 16 (작은 마크)
  extension/      icon16 · 32 · 48 (작은 마크), icon128 (96px 그림 + 사방 16px 투명 여백,
                  어두운 배경용 은은한 흰 외곽 빛) — Chrome Web Store 이미지 지침
  favicon.ico     16 · 32 · 48
  menubar/        템플릿 이미지 18px · 36px(@2x)
  DaDeum.icns     macOS (1024 캔버스 · 824 몸체 격자)

렌더링: SVG를 헤드리스 Chrome으로 크게(1024) 그린 뒤 PIL(LANCZOS)로 줄인다.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageFilter

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def render(svg_path: str, size: int = 1024) -> Image.Image:
    """SVG → 투명 배경 RGBA 이미지(size x size)."""
    tmp = tempfile.mkdtemp()
    html = os.path.join(tmp, "r.html")
    png = os.path.join(tmp, "r.png")
    with open(html, "w") as fh:
        fh.write(f'<!doctype html><html><body style="margin:0;background:transparent">'
                 f'<img src="file://{os.path.abspath(svg_path)}" width="{size}" height="{size}" '
                 f'style="display:block"></body></html>')
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--default-background-color=00000000", f"--window-size={size},{size}",
                    f"--screenshot={png}", f"file://{html}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    im = Image.open(png).convert("RGBA")
    shutil.rmtree(tmp, ignore_errors=True)
    return im


def down(im: Image.Image, s: int) -> Image.Image:
    return im.resize((s, s), Image.LANCZOS)


def glow(art: Image.Image, radius: float = 1.2, alpha: float = 0.28) -> Image.Image:
    """그림의 알파를 흐려 흰 외곽 빛을 만들고 그림 아래에 깐다."""
    a = art.getchannel("A").filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    white = Image.new("RGBA", art.size, (255, 255, 255, 0))
    white.putalpha(a.point(lambda v: int(v * alpha)))
    out = Image.new("RGBA", art.size, (0, 0, 0, 0))
    out.alpha_composite(white)
    out.alpha_composite(art)
    return out


def export_mark(d: str) -> None:
    rich = render(os.path.join(d, "mark.svg"))
    small = render(os.path.join(d, "mark-small.svg"), 512)
    os.makedirs(os.path.join(d, "png"), exist_ok=True)
    for s in (1024, 512, 256, 180, 128, 64):
        down(rich, s).save(os.path.join(d, "png", f"mark-{s}.png"), optimize=True)
    for s in (48, 32, 16):
        down(small, s).save(os.path.join(d, "png", f"mark-{s}.png"), optimize=True)

    ext = os.path.join(d, "extension")
    os.makedirs(ext, exist_ok=True)
    for s in (16, 32, 48):
        down(small, s).save(os.path.join(ext, f"icon{s}.png"), optimize=True)
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    canvas.alpha_composite(down(rich, 96), (16, 16))
    glow(canvas).save(os.path.join(ext, "icon128.png"), optimize=True)

    ico = [down(small, s) for s in (16, 32, 48)]
    ico[2].save(os.path.join(d, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)],
                append_images=ico[:2])

    mb = os.path.join(d, "menubar")
    os.makedirs(mb, exist_ok=True)
    tpl = render(os.path.join(d, "mark-template.svg"), 512)
    down(tpl, 18).save(os.path.join(mb, "menubarTemplate.png"))
    down(tpl, 36).save(os.path.join(mb, "menubarTemplate@2x.png"))

    app = render(os.path.join(d, "appicon-macos.svg"))
    app_small = render(os.path.join(d, "appicon-macos-small.svg"))
    iconset = tempfile.mkdtemp(suffix=".iconset")
    plan = [(16, 1, app_small), (16, 2, app_small), (32, 1, app_small), (32, 2, app),
            (128, 1, app), (128, 2, app), (256, 1, app), (256, 2, app), (512, 1, app), (512, 2, app)]
    for base, scale, src in plan:
        name = f"icon_{base}x{base}{'@2x' if scale == 2 else ''}.png"
        down(src, base * scale).save(os.path.join(iconset, name))
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", os.path.join(d, "DaDeum.icns")], check=True)
    shutil.rmtree(iconset, ignore_errors=True)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "release"
    for key in sorted(os.listdir(root)):
        p = os.path.join(root, key)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "mark.svg")):
            export_mark(p)
            print("exported", key)
