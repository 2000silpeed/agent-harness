# 4일차 부가 자료

## Day04_01.png (판서)

- 원본: Google Drive fileId `16EIY5N8le8rrknFrFwkxWRuxBuwGUEAJ` (`Day04_01.png`, 늦게 업로드된 4일차 판서)
- 주의: OCR 추출 텍스트를 주제별로 묶었다. 화살표·연결선의 방향과 대상은 추측하지 않았고, OCR에 `->`로 남은 것만 그대로 옮겼다. 판독이 애매한 부분은 원문 그대로 두었다.

### 1. MCP Primitives

- MCP
- Primitives: Resources / Prompts (Get) / Tools
- Tool list — `MCP: tool/list`, 각 도구는 Name / Desc

### 2. 도구가 너무 많을 때 ("도구가 너무 많아요...")

- 1\. RAG
- 2\. "모델이 찾으면..?"
  - 1) name, desc / 2) name, desc / 3) name, desc (도구 목록 나열)
- 판서에 같이 적힌 항목 (번호 원문 그대로):
  1) 임베딩 모델
  2) Update
  3) LLM 모델이 좋아졌다!
  4) 비용이 아주아주 낮음 -> Decision Model...

### 3. Long Running Task

- 요청 확인 -> 수행중.... -> 완료

### 4. Skills — 평가 관점

- 1\. 잘 실행되는가
  - > Name, 'Desc' - when
  - > (Trigger)
  - >> Case
- 2\. 원하는대로 잘 동작하는가
  - › Body
  - >> CodeMode

### 5. CodeMode (스킬 본문에서 코드 실행)

- 본문 예: 첫번째 코드 "scripts/1.sh" 실행하세요.
- 스킬의 동작을 '확정' X
- >> 코드를 짜서 실행해라 <<
- 기존 방식 (도구별 왕복):
  - USER -> AI (Tool 1,2,3)
  - Tool1 -> AI
  - Tool2 -> AI
  - Tool3 -> AI
- 스크립트 방식:
  - `#!/bin/bash` / Tool1,2,3 / Output -> AI
- 판서의 의사 코드 (OCR 원문, 일부 판독 불확실):
  ```
  RUN(1.sh, "Context1....., [
  RUN(2.sh, "Context2....., +
  2.sh AH")
  3.sh ")
  ```
