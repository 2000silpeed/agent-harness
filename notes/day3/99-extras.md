# Day3 부가 자료

> 원본: Google Drive의 `Day03_01.png`, `prompt.txt`, `cc_tip.txt`
> 이미지는 Drive 텍스트 추출(OCR) 결과를 바탕으로 정리했습니다. 손글씨 판서라서 OCR이 깨진 글자는 원문 그대로 두고 `(?)`로 표시했습니다. 요소 간 정확한 위치나 화살표 연결은 추출 결과만으로 확인되지 않아 추정을 덧붙이지 않았습니다.

## 1. Day03_01.png (판서 이미지)

수업 중 화이트보드 판서입니다. Drive가 붙인 이미지 라벨은 Diagram, Screenshot, Plot, Chord, Handwriting, Letter, Sketch입니다. 추출된 텍스트를 내용 묶음별로 정리하면 아래와 같습니다.

### (1) Tool / RAG / Agent Loop / Skills
- `Tool`
- `RAG`: 저장 / 검색 / 활용
- `Agent Loop`
- `-VectorDB X` (OCR: "VectorDBX". VectorDB를 쓰지 않는다는 표시로 보임)
- `・FS, 계층, index.md` (OCR: "index.nd")
- `1. 다 읽어버림`
- `2. <발췌>`
- `Skills = 32 *|| what, when` (OCR 원문 그대로. 일부 글자 판독 불가)
- `DeepAgents: FileSystem Tools`
  - `-ls, grep, read, write,....` (OCR: "-Is")

### (2) 프레임워크
- `Why LangChain (LangGraph)`
- `-Spring AI`
- `-P: Agent 478` (OCR 원문 그대로, 판독 불확실)
- `-Pydantic AI` (OCR: "Pydantie AI")
- `9개`

### (3) Multi Agent Pattern
- `Multi Agent Pattern`
- `Router(Supervisor)`, `Task.`
- `OpenAI`, `Expert Agent 1`, `Expert Agent 21` (OCR 원문 그대로), `Expert Agent`
- `Swarm (Network)`
- `Loop`
- `Plan`, `Executor`, `Executor`
- `DeepResearch`
- `Single-> Multi`
- `Multi-Agent Arch Context Isolation`

### (4) Model / Context Window / KV Cache
- `Model`
- `Context Window`
- `GPT, Auto-Regressive"`
- `LLM KV Cache => Text Matching` (OCR: "LUM KV Cache")
- `Tokenizer`
- `"완전히 똑같은 텍스트`
- `Date: 20261104093300`
- `| skill 1-10`
- `Cache`
- `사용자: (**)이메일....`
- `skill 변경`
- `Process-> "IPC", FS`
- `(대화) 세션`
- `LLM 호출 세션(Context)`

판서 흐름으로 보면, KV Cache는 텍스트가 완전히 같아야 맞는다는 점(Text Matching)과, 프롬프트 앞부분에 날짜·스킬 목록이 바뀌면 캐시가 깨진다는 예시를 적은 것으로 보입니다. 다만 화살표 연결은 추출 결과로 확인할 수 없습니다.

### (5) 사례: 배달 앱의 메뉴 검색 시스템 개선
- `Topic: 배달 앱의 메뉴 검색 시스템 개선`
- `"엽떡" 검색 -> ("엽기떡볶이" -> 떡볶이 -> 분식`
- `<양이 너무 많다>`
- `5000만개`
- `실행 방식: "배치"`
- `150만개/D`
- 초기 구조:
  - `1. Tool + System prompt`
  - `- "Tool: 조회`
  - `"prompt: 매핑(로직)`
  - `-Tool: 매핑 결과 > File`
- `1) 후보군을 추려야 하는 스킬`
- `[대 카테고리: Skill - 20개 내외`
- `-3개정도, 후보군을 또 추려야.... 스킬을 깎아서... 잘 나오게 해! > 다른 개발자`
- `'처리 건수가...`
- 개선 아이디어:
  - `1. 라우팅을 '미리' 해둘 수 없을까? > 컬럼 새로: "가야할 스킬"`
  - `(후보군,,, 그중에 어디로 가야할까?)`
  - `개별 Agent`
  - `2. 데이터 조회, 매번 새로 해야되는가?`
  - `"데이터를 미리 조회" > 캐시`
  - `개별 Agent`
- `..확정...`
  - `1. 사람 > Gold`
  - `2. AI 로 맞춰나가는..`
- 모델: `Gemma 31B`, `Qwen 8B`, `유동적..`
- `SKILL.md` (OCR: "SKILLand") `=` `a system prompt`
- 스킬 예시 데이터:

```
[데이터]
중 카테고리: 분식
하위 음식명:
*1. 떡볶이*
2. 라면
3. 오뎅

[가맹점-데이터]
떡볶이
-
신전
-엽기
```

## 2. prompt.txt

기존 Agent 코드의 구조를 Context 관점과 Multi Agent 관점에서 최적화하도록 Claude Code에 요청하는 예시 프롬프트입니다. 동작을 바꾸지 않는다는 원칙과, 개선마다 근거를 남기라는 요구가 들어 있습니다. (자료로 그대로 옮긴 것이며, 이 노트 작성 과정에서 실행하지 않았습니다.)

```text
[파일경로]의 구조를 최적화 하려고 합니다.

동작이 바뀌어선 안되는게 주요 원칙입니다.

## Context 관점

1. Tool 의 개수를 적절하게 줄였으면 좋겠습니다.
2. Prompt 를 좀 더 적게 넣고 동적으로 유연하게 제어할 수 있어야합니다.
3. Skills 를 도입할 곳은 없을지 점검.


## Multi Agent 관점

1. latency 를 고려해서, 서브 에이전트로 분리하는게 좋을까요?
2. 현재 Sonnet 모델을 사용하고 있는데, Haiku 모델로 처리할 수 있으면 더 빠를 것 같습니다.


## 기타

1. 판단하는 부분을 Jev 로 바꿔본다면 어떨까요?(또 Jev 모델을 껏다켰다 해서 동작을 확인할 수 있다면)
2. 모든 최적화 작업에는 기존 작업이 어떤 문제를 가지고 있었고 어떻게 개선했다라는 근거가 꼭 필요합니다.
```

## 3. cc_tip.txt

강사가 공유한 Claude Code 활용 팁 링크 모음입니다. DAG 기반 Workflow, 토큰 절감, 인터뷰, 디자인 목업, 리버스 엔지니어링 주제별로 GitHub 저장소를 정리했습니다.

```text
[Claude Code Tips]

## DAG 기반 Workflow
1. https://github.com/HyunjunJeon/claude-workflow-mods

## 토큰 절감
1. https://github.com/juliusbrussee/caveman
2. https://github.com/ayghri/i-have-adhd

## Interview
1. https://github.com/Q00/ouroboros
2. https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling


## Design, Mock
1. https://github.com/kgoedecke/doop

## Reverse Eng
1. https://github.com/morluto/rea
```
