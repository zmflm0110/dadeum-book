# 4장. 서버와 API: 요청 하나가 지나가는 길

## 4.1 서버와 클라이언트

식당에 비유하면 이렇습니다.

| 식당 | 다듬 | 
|---|---|
| 손님 | **클라이언트**: 웹 페이지, 크롬 확장, 맥 앱 |
| 주방 | **서버**: `backend/`의 파이썬 프로그램 |
| 주문서 | **요청(request)**: "이 글을 검사해 줘" |
| 음식 | **응답(response)**: 지적 목록 |
| 메뉴판의 정해진 주문 방식 | **API** |

손님(화면)은 직접 요리하지 않습니다. 주문서만 써서 주방에 넘기고 음식을 받아 보여 줍니다.
그래서 **교정 로직은 서버 하나에만** 있고, 화면 세 개는 같은 서버를 부릅니다.
서버는 내 컴퓨터 안(`localhost:8000`)에서 돌기 때문에 글이 인터넷으로 나가지 않습니다.

## 4.2 API란

**API**는 "이렇게 주문하면 이렇게 답한다"는 약속입니다. 다듬의 API는 둘뿐입니다.

| 주소 | 방식 | 하는 일 |
|---|---|---|
| `/api/check` | POST | 글을 받아 지적 목록을 돌려줌 |
| `/api/health` | GET | "살아 있나, 어느 층이 켜져 있나" 확인 |

POST는 "내용을 담아 보낸다", GET은 "그냥 달라고 한다"입니다.

## 4.3 주문서와 음식의 모양: `schemas.py`

```python
class CheckRequest(BaseModel):
    text: str = Field(max_length=20_000)

class Issue(BaseModel):
    id: int
    start: int
    end: int
    category: Category          # "spacing" | "spelling" | "josa" | "grammar" | "style"
    source: str
    original: str
    suggestions: list[str]
    message: str
    confidence: Confidence      # "high" | "medium" | "low"

class CheckResponse(BaseModel):
    issues: list[Issue]
    elapsed_ms: dict[str, float] = {}
```

- `BaseModel`(pydantic)은 "이 모양이 아니면 받지 않는다"는 검문소입니다. 모양이 틀린 주문서가 오면 서버가 안으로 들이지 않고 **422** 오류를 돌려줍니다.
- `max_length=20_000`: 글은 2만 자까지만. 원인은 서버 보호입니다. 2만 자는 서버 한 명을 약 4초 붙잡는 길이입니다.
- `Literal[...]`(글자 고정 목록): `category`는 다섯 값 중 하나여야 합니다.

### 실제로 있었던 사고: `style`이 빠져서 서버가 죽었다

`schemas.py` 맨 위 주석에 적힌 이야기입니다.

> 문체 일관성 검사기(`consistency.py`)는 처음부터 `category="style"`을 냈는데, 스키마의 `Category` 목록에 `style`이 없었습니다.
> 문체가 섞인 글을 검사하면 **`/api/check`가 500 오류로 죽었습니다**(2026-08-30 실측).

왜 테스트가 못 잡았나? 두 측정이 서로 다른 길을 탔기 때문입니다.

| 측정 | 길 | 결과 |
|---|---|---|
| D 경로 게이트 | 검사기를 **직접** 불러서 잼 | 재현율 1.000 (정상으로 보임) |
| corpus-suite | **API를 거쳐서** 잼 | 예외로 죽어 0.000 |

두 숫자가 정반대인데 아무도 비교하지 않았습니다. 이후 "체커가 내는 모든 category가 스키마에 있는지 소스를 훑어 대조하는 계약 테스트"(`tests/test_category_contract.py`)가 생겼습니다.
**교훈:** 같은 것을 두 군데서 다른 방법으로 재면, 둘이 어긋나는지 서로 대조해야 합니다.

## 4.4 서버 뼈대: `app/main.py`

```python
app = FastAPI(title="다듬 API", version=APP_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=..., allow_methods=["GET","POST"], ...)
app.middleware("http")(rate_limit_middleware)
app.include_router(api_router, prefix="/api")
app.mount("/core", StaticFiles(directory=CORE_DIR), name="core")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
```

- **FastAPI**: 파이썬으로 서버를 만드는 틀(프레임워크)입니다.
- **미들웨어**: 요청이 본 로직에 닿기 전에 지나가는 관문입니다. 여기서는 CORS와 레이트리밋이 관문입니다.
- **라우터**: 주소별로 어느 함수가 맡을지 정한 배정표입니다. `prefix="/api"`라서 `check` 함수는 `/api/check`가 됩니다.
- **mount**: 폴더를 통째로 웹 주소에 연결합니다. 웹 앱의 `index.html`, `app.js`도 이 서버가 내줍니다.

**등록 순서가 동작입니다.** 주석의 경고: 정적 파일 mount는 "무엇이든 받는" 그물이라서 `/api` 라우터보다 먼저 등록하면 `/api/check` 요청까지 삼켜 버립니다. 그래서 라우터를 먼저 등록합니다.

### CORS

브라우저는 보안상 "다른 곳에서 온 페이지가 이 서버를 부르는 것"을 기본으로 막습니다.
크롬 확장은 `chrome-extension://` 출처라서 막힙니다. 서버는 쿠키·로그인이 없으므로 모두 허용(`*`)이 안전하다고 판단했고, 운영에서는 `ALLOWED_ORIGINS` 환경변수로 좁힐 수 있습니다.

### 캐시 재검증 미들웨어

```python
@app.middleware("http")
async def revalidate_static(request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache"
    return response
```

정적 파일은 기본으로 캐시 지시가 없어서 브라우저가 낡은 `app.js`를 쓰는 일이 있었습니다(배포 후에도 옛 화면).
`no-cache`는 "저장은 하되 쓰기 전에 서버에 확인"이라는 뜻이고, 안 바뀌었으면 가벼운 304 응답으로 끝납니다.

## 4.5 레이트리밋: `ratelimit.py`

한 사용자가 서버를 독점하지 못하게 합니다. 검사는 CPU를 쓰기 때문입니다.

```
IP마다: 60초 창 안에서 60번까지. 61번째부터 429 오류 + "몇 초 뒤 재시도" 안내.
```

작동 방식은 단순합니다.

```python
_buckets[key] = (window_start, count)    # IP → (창 시작 시각, 횟수)
...
if now - window_start >= WINDOW:         # 창이 끝났으면 새로 시작
    window_start, count = now, 0
count += 1
if count > REQUESTS_PER_WINDOW:
    return JSONResponse(..., status_code=429, headers={"Retry-After": ...})
```

- `threading.Lock()`: 동시에 여러 요청이 `_buckets`를 고치면 값이 꼬이므로 한 번에 한 명만 들어가게 하는 자물쇠입니다.
- 5분마다 오래된 키를 청소합니다(메모리가 계속 늘지 않게).
- **한계가 코드에 적혀 있습니다.** 메모리 안에서만 세므로 서버가 여러 대면 공유가 안 됩니다. 한 대로 쓰는 지금은 충분하다는 판단입니다.

### 어느 IP인가: `clientip.py`

프록시 뒤에서는 모든 요청의 접속자가 프록시로 보입니다. 원래 IP는 `X-Forwarded-For` 헤더에 있는데, **이 헤더는 누구나 위조할 수 있습니다.**
위조를 믿으면 요청마다 헤더를 바꿔 한도를 무한히 우회합니다.

| 설정 | 동작 |
|---|---|
| 기본 | 헤더를 믿지 않고 직접 접속한 IP만 사용 |
| `TRUSTED_PROXIES=IP목록` | 접속자가 그 목록일 때만 헤더를 믿음 (권장) |
| `TRUST_PROXY=1` | 옛 방식(누구 헤더든 믿음), 경고 출력 |

예전엔 기본값이 "믿음"이라 우회가 가능했고, 기본을 "안 믿음"으로 뒤집었습니다. **안전한 쪽이 기본값**이어야 한다는 원칙입니다.

## 4.6 `/api/check` 한 줄씩

```python
@router.post("/check", response_model=CheckResponse)
def check(request: CheckRequest, x_dadeum_client: str | None = Header(default=None)):
    _note_client(x_dadeum_client)
    text = request.text
    if not text.strip():
        return CheckResponse(issues=[])

    result = analyze_long(text)
    return CheckResponse(
        issues=[build_issue(idx, r) for idx, r in enumerate(result.issues)],
        elapsed_ms=result.elapsed_ms,
    )
```

1. `@router.post("/check")`: 데코레이터. "아래 함수를 `/check` POST 주문 담당으로 등록하라."
2. `request: CheckRequest`: 검문소를 통과한 주문서가 들어옵니다.
3. `x_dadeum_client`: 헤더 `X-Dadeum-Client`를 읽습니다. 확장이 "나 여기 있다"고 알리는 용도입니다(4.8).
4. 빈 글이면 바로 빈 목록.
5. `analyze_long(text)`가 엔진을 돌립니다(5장).
6. `build_issue(idx, r)`로 내부 자료(`RawIssue`)를 응답 모양(`Issue`)으로 바꾸고, 목록 번호를 `id`로 붙입니다.

실제 응답은 이런 JSON입니다(예문 `학교을 갔다`, 제가 `check()`를 직접 불러 얻은 값).

```json
{"issues": [{"id": 0, "start": 2, "end": 3, "category": "josa",
             "source": "josa_rule", "original": "을", "suggestions": ["를"],
             "message": "받침 여부를 확인하면 '를'이 맞는 조사입니다.",
             "confidence": "high"}],
 "elapsed_ms": {"layer1": 4278.2, "layer2": 2.0}}
```

- `message`의 끝 `이/가`는 **제안한 조사 자신의 받침**으로 고릅니다(`_issue()`의 `marker`). `를`은 받침 ㄹ이 있어 `'를'이`, `가`는 받침이 없어 `'가'가`가 됩니다. 설명문조차 같은 받침 계산으로 맞춰 쓰는 것입니다.
- `layer1`이 4278ms로 큰 것은 **서버를 막 띄운 뒤 첫 요청**이라서입니다(사전·모델을 처음 읽는 비용). 두 번째부터는 한 자릿수 ms입니다. 이 값은 `/check` 응답에 그대로 실려서 "어느 층이 시간을 쓰는지" 보는 용도입니다.

## 4.7 긴 글: `analyze_long`

```python
CHUNK_LIMIT = 4000

def analyze_long(text, use_l2=True):
    if len(text) <= CHUNK_LIMIT:
        return analyze(text, use_l2)
    ...
    for start, end in _chunk_bounds(text, CHUNK_LIMIT):
        part = analyze(text[start:end], use_l2)
        for r in part.issues:
            issues.append(replace(r, start=r.start + start, end=r.end + start))
```

4000자를 넘으면 **문장 경계에서** 잘라 조각마다 따로 돌리고, 위치(start, end)를 원문 기준으로 되돌립니다(조각의 시작 위치를 더함).

왜 필요했나? 예전에는 스키마 상한이 5,000자였고, 클라이언트들이 글을 자르지 않고 통째로 보냈습니다.
**긴 문서는 422로 튕겨서 검사가 아예 안 됐습니다**(데스크톱·확장·웹 모두 해당). 이후 엔진이 직접 나눠 돌리게 바꿨고 상한을 2만 자로 올렸습니다.

`_chunk_bounds`의 핵심:

```python
for sent in _kiwi.split_into_sents(text):
    if sent.end - start > limit and cur > start:
        bounds.append((start, cur))     # 여기까지 한 조각
        start = cur
    while sent.end - start > limit:     # 마침표 없이 이어진 아주 긴 덩어리
        bounds.append((start, start + limit))
        start += limit
    cur = sent.end
```

- Kiwi의 `split_into_sents`가 문장 경계를 줍니다.
- 문장이 상한을 넘기면 그 문장만 억지로 4000자씩 자릅니다.

한계(주석에 있음): 문체 일관성은 글 전체를 봐야 하는데 조각 안에서만 판정합니다.

## 4.8 `/api/health`: 지금 어느 층이 켜져 있나

```python
{"status": "ok", "version": ..., "model_family": "gyeol-1",
 "layer2_pairs": ["an", "doe", "den", "roseo"],
 "boundary_model": True, "lexicon": 1806050,
 "spacing_tagger": False, "extension_live": False}
```

**왜 이렇게 자세한가:** 이 엔진의 층은 전부 "선택"입니다. 모델 파일이 없거나 torch가 없으면 그 층만 조용히 빠집니다.
그러면 "내 컴퓨터에서는 잡히는데 배포본에서는 안 잡힌다" 같은 일이 생기고, 원인을 찾기 어렵습니다.
`/api/health`가 각 층의 적재 여부를 답해 주므로 **결과가 다를 때 가장 먼저 볼 곳**입니다.

`extension_live`는 맥 앱이 읽습니다. 맥 앱은 크롬에서 확장이 담당하므로 "확장이 살아 있을 때만" 비켜섭니다. 확장이 `check`/`health` 요청마다 `X-Dadeum-Client: extension` 헤더를 달고, 서버가 마지막으로 본 시각을 기억해 **180초 안이면 살아 있다**고 답합니다.
(설치 안 된 확장을 믿고 맥 앱이 비켜서면 크롬에서 아무 교정도 안 나오는 일이 있었습니다. 그것을 막는 장치입니다.)

## 4.9 직접 따라 하기

서버를 띄우고 직접 주문해 볼 수 있습니다.

```bash
cd dadeum/backend
source .venv/bin/activate
uvicorn app.main:app --port 8000

# 다른 터미널에서
curl -s localhost:8000/api/health
curl -s -X POST localhost:8000/api/check \
     -H "Content-Type: application/json" \
     -d '{"text": "학교을 갔다"}'
```

## 4.10 확인 문제

1. 글이 25,000자이면 어떤 응답이 올까? (422: 스키마 상한 2만 자 초과)
2. 같은 IP가 1분에 61번 요청하면? (61번째부터 429 + Retry-After)
3. 서버가 `style`로 죽었던 이유는? (스키마의 Category 목록에 style이 없었음)
