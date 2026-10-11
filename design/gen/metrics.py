"""색 지표 — 대비(WCAG)와 색차(CIEDE2000)를 계산해 표로 낸다. 가이드의 수치는 전부 여기서 나온다."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import brand as B

def rgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def lum(h):
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b=[f(v/255) for v in rgb(h)]; return 0.2126*r+0.7152*g+0.0722*b
def contrast(a,b):
    x,y=sorted([lum(a),lum(b)],reverse=True); return (x+0.05)/(y+0.05)
def lab(h):
    f=lambda c: ((c+0.055)/1.055)**2.4 if c>0.04045 else c/12.92
    r,g,b=[f(v/255) for v in rgb(h)]
    x=(0.4124*r+0.3576*g+0.1805*b)/0.95047; y=0.2126*r+0.7152*g+0.0722*b; z=(0.0193*r+0.1192*g+0.9505*b)/1.08883
    g_=lambda t: t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz=g_(x),g_(y),g_(z); return 116*fy-16,500*(fx-fy),200*(fy-fz)
def de2000(c1,c2):
    L1,a1,b1=lab(c1);L2,a2,b2=lab(c2)
    C1=math.hypot(a1,b1);C2=math.hypot(a2,b2);Cm=(C1+C2)/2
    G=0.5*(1-math.sqrt(Cm**7/(Cm**7+25**7)));a1p,a2p=(1+G)*a1,(1+G)*a2
    C1p,C2p=math.hypot(a1p,b1),math.hypot(a2p,b2)
    hf=lambda x,y:(math.degrees(math.atan2(y,x))%360) if (x or y) else 0
    h1,h2=hf(a1p,b1),hf(a2p,b2); dL=L2-L1; dC=C2p-C1p; dh=h2-h1
    if C1p*C2p==0: dh=0
    elif dh>180: dh-=360
    elif dh<-180: dh+=360
    dH=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dh/2)); Lm=(L1+L2)/2; Cmp=(C1p+C2p)/2
    if C1p*C2p==0: hm=h1+h2
    elif abs(h1-h2)<=180: hm=(h1+h2)/2
    else: hm=(h1+h2+360)/2 if h1+h2<360 else (h1+h2-360)/2
    T=1-0.17*math.cos(math.radians(hm-30))+0.24*math.cos(math.radians(2*hm))+0.32*math.cos(math.radians(3*hm+6))-0.2*math.cos(math.radians(4*hm-63))
    Sl=1+0.015*(Lm-50)**2/math.sqrt(20+(Lm-50)**2);Sc=1+0.045*Cmp;Sh=1+0.015*Cmp*T
    Rt=-2*math.sqrt(Cmp**7/(Cmp**7+25**7))*math.sin(math.radians(60*math.exp(-((hm-275)/25)**2)))
    return math.sqrt((dL/Sl)**2+(dC/Sc)**2+(dH/Sh)**2+Rt*(dC/Sc)*(dH/Sh))

CAT_LIGHT={"맞춤법":"#c22a22","띄어쓰기":"#8a5a00","조사":"#1f5bbf","문법":"#9b2d80","문체":"#0e7355"}
CAT_DARK ={"맞춤법":"#f08a80","띄어쓰기":"#d9a441","조사":"#79aaf0","문법":"#e58ac8","문체":"#3fbf94"}
BRAND={"먹 남 INK":B.INK,"중간 남 MID":B.MID,"전기 남 ELEC":B.ELEC,"상아 IVORY":B.IVORY,"포인트 SIGN":B.SIGN}

def tables():
    out=[]
    out.append("### 대비 (WCAG 2.x 명도 대비)\n\n| 앞 | 뒤 | 대비 | 쓰임 |\n|---|---|---|---|")
    pairs=[("상아 IVORY",B.IVORY,"먹 남 INK",B.INK,"마크 형상 / 타일 끝"),
           ("상아 IVORY",B.IVORY,"중간 남 MID",B.MID,"마크 형상 / 타일 중간"),
           ("상아 IVORY",B.IVORY,"전기 남 ELEC",B.ELEC,"마크 형상 / 타일 시작(가장 밝은 곳)"),
           ("포인트 SIGN",B.SIGN,"먹 남 INK",B.INK,"포인트 / 타일 끝"),
           ("포인트 SIGN",B.SIGN,"전기 남 ELEC",B.ELEC,"포인트 / 타일 시작"),
           ("흰색",B.WHITE,"먹 남 INK",B.INK,"작은 마크"),
           ("먹 남 INK",B.INK,"흰 바탕","#FFFFFF","워드마크(밝은)"),
           ("전기 남 ELEC",B.ELEC,"흰 바탕","#FFFFFF","워드마크 곁가지(밝은)"),
           ("상아 IVORY",B.IVORY,"다크 바탕","#141416","워드마크(어두운)"),
           ("포인트 SIGN",B.SIGN,"다크 바탕","#141416","워드마크 곁가지(어두운)")]
    for an,a,bn,b,use in pairs:
        out.append(f"| {an} `{a}` | {bn} `{b}` | **{contrast(a,b):.1f}:1** | {use} |")
    out.append("\n비텍스트 그래픽 기준(WCAG 1.4.11)은 3:1, 본문 글자 기준은 4.5:1 이다.\n")
    for title,cats in (("라이트",CAT_LIGHT),("다크",CAT_DARK)):
        out.append(f"### 색차 ΔE2000 — 브랜드색 vs 카테고리 밑줄색({title})\n")
        out.append("| 브랜드색 | "+" | ".join(cats)+" |\n|---|"+"---|"*len(cats))
        for bn,bc in BRAND.items():
            cells=[]
            for v in cats.values():
                d=de2000(bc,v); cells.append(f"**{d:.1f}**" if d<28 else f"{d:.1f}")
            out.append(f"| {bn} `{bc}` | "+" | ".join(cells)+" |")
        out.append("\n**굵은 값**은 `design/tokens.md`가 카테고리 색끼리 요구하는 28 미만이다 — UI에서 함께 쓰면 밑줄과 헷갈릴 수 있다.\n")
    return "\n".join(out)

if __name__=="__main__":
    print(tables())
