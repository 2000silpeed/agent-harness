# 1일차 자료

> Drive 폴더에는 1일차 **강의 녹화본과 녹취록이 없습니다.** 남아 있는 자료는 판서 이미지 2장(`Day01_01.png`, `Day01_02.png`)뿐입니다.
> 아래 내용은 Drive 텍스트 추출(OCR) 결과를 바탕으로 옮겼습니다. 손글씨라서 깨진 글자는 원문 그대로 두고 `(OCR: ...)`로 표시했습니다. 화살표나 박스 연결은 추출 결과로 확인되지 않아 추정하지 않았고, 내용 묶음별로만 정리했습니다.

## Day01_01.png: 데이터(검색·생성), 모델, Skill, Context, 비용

Drive 이미지 라벨: Diagram, Schematic, Network Software, Plot, Line art, Electronics Manual, Circuit diagram, Screenshot, Technical drawing

### (1) 데이터: 1. 잘 찾아오기 (검색)
- `데이터`
- `1. 잘 찾아오기` / `(검색)`
- `예제: VectorDB` (OCR: "VectorbB")
- `자연어 검색` (OCR: "자연이 검색")
  - `1. 임베딩 모델....`
  - `2. BM25(텍스트 검색)`
- `[비정형]`
  - `1. 처리(Load-Parse)`
  - `2. 저장`
- 계층형 인덱스 구조:

```
대 카테고리
  index.md
  - 중 카테고리들
      index.md        (OCR: "index.nd")
      - 소 카테고리들
          index.md    (OCR: "indexand")
          <<내가 원하는 파일>>
```

### (2) 데이터: 2. 잘 이야기하게끔 (생성)
- `2. 잘 이야기하게끔` / `(생성)`
- `[(구) 시스템 프롬프트`
- `치환`
- `[GPU]`
- `>새로운 요청`
- `'스킬`
- `Tool`
- `Agent Loop`

### (3) 모델 크기
- `작은 Model` / `큰 Model`
- `Haiku 700B`
- `Qwen-27B`
- `Opus-3T`
- `Qwen-Flash-200B`
- `Decision Model(like Jev)`
- `Context Window`
- `Sub-Agent Loop`

### (4) Agent Skill = 조각 지식
- `Agent Skill = 조각 지식`
- `SKILL.md`
  - `name/desc`: `what, when`
  - `본문`
- `Context: 삼성SDS 휴가 관련 문서`
- 예시 질문:
  - `우리 회사 휴가 규정은?` → `주요 내용 요약`
  - `올해 쓰기 좋은 휴가 날씨는?`
  - `캐릭터.... (NSFW)`
- `-창립기념일 X월일, 휴가는 통념상 언제 쓰면 안되고...`
- `0000)` (OCR 원문 그대로)

### (5) Memory / 대화 이력
- `/history`
- `Skill.md -> index`
- `/tip`
- `원본 대화내용 찾아가기"`
- `>> Memory.md <<` (OCR: "Memoryomd")
- `memory.md`
- `2026-11-03, Production RAG, 삼성SDS`

### (6) Main Context / Context 관리
- `Tool("마케팅 메시지")`
- `사용자`
- `Main` / `Context`
- `주제 변경` → `Context Change`
- `싱글턴, "멀티턴"`
- `Context Compress"`
  - `1) 주제만 간단하게 요약`
  - `2) 육하원칙, 요약해서 전달 (요청시)`
- `Cross-model KV Cache`

### (7) 생성 모델의 동작 방식
- `GPT, Auto-Regressive`
- `Diffusion LLM` (OCR: "Defusion LLM")
- `끝말잇기`
- `입력: 프롬프트` / `출력: 다음 토큰`
- 입출력 형식:

```
Input: 펼쳐진 텍스트
  <system>        (OCR: "ksystem>")
  <user>          (OCR: "Kuser>")
    질문, 스킬
Output: <assistant> 답변~~   (OCR: "cassistant>")
```

### (8) 비용과 Closed Question
- `Cost`
  - `-Input:`
  - `-Output: (계산) → 어떻게 줄이지?`
- `[closed Question]`
  - `Q: 휴가 규정 파일이 여기에 있어?`
  - `A: 예(1), 아니오(0)` (OCR: "4:")
- `AICC`
- `Decision` / `Generate`

## Day01_02.png: Claude Code Hooks와 Function Call

Drive 이미지 라벨: Chord, Diagram, Screenshot, Orbit, Point

### (1) Claude Code(CC) Hook 이벤트
| 판서 표기 | 설명(판서 원문) |
|---|---|
| `CC: SessionStart` | Agent가 시작될 때 |
| `CC: UserPromptSubmit` | 사람이 Input 했을 때 |
| `CC: Pre/PostToolUse` | 도구가 호출되기 전/후 |
| `CC: Stop / StopFailure` | 종료 전 |
| `CC: SubagentStart/End` | 서브에이전트가 호출되기 전/후 |

### (2) "지시" 이행과 도구 호출 실패
- `"지시" 이행`
- `User: "규격"대로 줘`
- `▶"도구" 호출 실패`
- `JSON = {규격~}` (OCR: "{규격\~3")

### (3) Function Call 정의와 호출 예시
판서에 적힌 함수 정의와 실제 호출 인자입니다. OCR의 오타(`argsi`, `stringi`, `} 3,0]`)는 손글씨 `:`, `}` 등의 오인식으로 보입니다.

```
function_calls = [{
  name: get_weather,
  desc: "실시간 날씨",
  args: {                       (OCR: "argsi {")
    location: string,           (OCR: "stringi")
    desc: "지역을 자연어로 표시."
  }
}, ...]

name: get_weather, args: {
  location: "서울",
}
```

OCR 결과에는 `desc: "지역을 자연어로 표시."`가 호출 예시(`location: "서울"`) 바로 다음에 나옵니다. 위 배치는 의미상 정의 쪽에 둔 것이며, 판서의 정확한 위치는 확인할 수 없습니다.

### (4) 도구 출력 전달 여부
- `이 도구의 출력이... 전달될 필요가 있을까?`
- `→ToolMessage("필요 없었따") >> Jev`
