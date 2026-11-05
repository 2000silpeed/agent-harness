## 2일차 딥에이전트 실습 (녹음 없음, 재구성 장표)

> 장표 제목: "Deep Agent 실습과 에이전트 훅" (SDS AX Advanced · 2026-11-03 · 녹음 없는 수업 재구성)
> 이 노트의 원천은 녹음이 아니라 재구성 장표다. 장표 자체가 판서 이미지(Day01_02.png 오른쪽), 과정 페이지(bit.ly/sds-ax-ad-class → GitHub 과정 저장소: Day01 README, Ch06 미들웨어 노트북, deep-agents-core 스킬 문서), 앞 강의 전사, 그리고 [추정] 해석을 섞어 만든 것이며 "실제 수업 내용과 다를 수 있다"고 명시한다. 아래 각 항목에 출처 태그를 유지했다.

### 핵심 요약 (3~5줄)
- 6강 녹음(47:14 종료) 뒤 "쉬었다가 30분 정도 실습" 예고가 있었고, 그 뒤 수업은 녹음되지 않음. 회차는 6강 다음 시간(7강)으로 **추정**.
- `create_deep_agent` = `create_agent`(LangGraph 그래프 하나) + 기본 미들웨어(TodoList, Filesystem, SubAgent, Skills, Memory, HumanInTheLoop). 기본 미들웨어는 뺄 수 없음. [과정 페이지]
- 판서 오른쪽: Claude Code 훅 6종(SessionStart, UserPromptSubmit, Stop/StopFailure, Pre/PostToolUse, SubagentStart/End)으로 에이전트 루프에 끼어드는 지점을 표시. [이미지] 이를 LangChain 미들웨어 훅(before_agent, before_model, wrap_tool_call, after_agent)과 짝지은 것은 장표의 해석. [추정]
- 판서 끝 질문 "이 도구의 출력이 전달될 필요가 있을까?" → 필요 없으면 짧은 ToolMessage("필요 없었다")로 바꿔 컨텍스트 절약, 판단은 Jev 같은 디시전 모델. [이미지·추정]
- 실습: Day01 폴더를 읽고 무엇을 가르치는 자료인지 요약해 Day01 폴더에 파일로 저장, 새 도구 생성 금지. 다음은 멀티턴(다뤘는지는 모름).

### 주요 개념 (개념별 설명, 강사가 강조한 이유 포함)
- **앞 강의에서 이어지는 판서(왼쪽)** [이미지·전사 6강]: "User: 규격대로 줘 / JSON = {규격}" → 도구 정의(name: get_weather · desc: 실시간 날씨 · args: location) → function_calls → 도구 호출 실패(규격이 복잡할수록 실패율이 오른다). 도구 호출 결과는 ToolMessage로 모델에 돌아감(6강 22:58).
- **create_agent vs create_deep_agent** [과정 페이지 deep-agents-core · 전사 6강]:
  - 뼈대: LangGraph 그래프 하나 / create_agent를 반환
  - 도구: 직접 넣은 도구만 / 계획·파일·위임 도구가 기본
  - 맞는 일: 한 번에 끝나는 단순한 일 / 계획이 필요한 여러 단계 일
  - 설정: 모델·도구·미들웨어를 직접 고름 / 구현보다 설정(backend, subagents, skills)
- **Deep Agent 기본 미들웨어** (미들웨어마다 도구를 하나씩 붙임, 기본 미들웨어는 뺄 수 없음) [과정 페이지 deep-agents-core·orchestration]:
  - `TodoListMiddleware` — `write_todos`(여러 단계 계획)
  - `FilesystemMiddleware` — `ls` · `read_file` · `write_file` · `edit_file` · `glob` · `grep`
  - `SubAgentMiddleware` — `task`(새 서브에이전트에 일을 맡김)
  - `SkillsMiddleware` — SKILL.md를 필요할 때만 읽음
  - `MemoryMiddleware` — Store로 대화 사이 기억
  - `HumanInTheLoop` — 위험한 도구 실행 전 승인
- **에이전트 루프에 끼어드는 자리(판서 오른쪽, Claude Code 훅)** [이미지, 이름·설명은 판서 글자 그대로, 실제 설명 순서는 모름]:
  - SessionStart — Agent가 시작될 때
  - UserPromptSubmit — 사람이 입력했을 때
  - Stop / StopFailure — 종료 전
  - Pre / PostToolUse — 도구가 호출되기 전/후
  - SubagentStart / End — 서브에이전트가 호출되기 전/후
- **훅 ↔ LangChain 미들웨어 훅 짝짓기** [과정 페이지 Ch06 · 추정, 이름이 정확히 같지는 않음]:
  - 시작: SessionStart ↔ `before_agent`
  - 입력 뒤: UserPromptSubmit ↔ `before_model`(모델 호출 전)
  - 도구: PreToolUse / PostToolUse ↔ `wrap_tool_call`(실행을 감쌈)
  - 서브에이전트: SubagentStart / End ↔ `task` 도구 호출을 `wrap_tool_call`로
  - 끝: Stop / StopFailure ↔ `after_agent`
- **미들웨어가 하는 일** [과정 페이지 Day01 Ch06]: 감시(로그, 메시지 수, 도구 결과 기록), 수정(프롬프트·도구 선택·출력 형식), 제어(재시도, 폴백, 조기 종료), 강제(호출 횟수 제한, 가드레일, PII).
- **미들웨어 실행 순서** [과정 페이지 Day01 Ch06 '실행 순서']:
  - `before_*`는 앞에서부터: `middleware=[M1, M2]` → M1, M2 순서(순차)
  - `after_*`는 뒤에서부터: M2, M1 순서로 돌아 나옴(역순)
  - `wrap_*`는 겹쳐 감쌈: M1이 가장 바깥, handler를 0번·1번·여러 번 부를 수 있음(중첩)
- **도구 출력 전달 여부 판단** [이미지 · 전사 2강 16:43, 3강 41:24 · 추정]: 도구 실행 결과가 길 수 있음 → PostToolUse 자리(`wrap_tool_call`에서 결과를 받음) → 필요한가?(Jev 같은 디시전 모델이 판단) → 필요 없으면 짧은 ToolMessage. 판서: `ToolMessage("필요 없었다")`, `>> Jev`. Jev(제브)는 2강·3강에서 다룬 빠른 디시전 모델(저장소 확인: TypeSafe AI의 System One 모델, 텍스트를 생성하지 않고 정해진 질문에 구조화 답과 확률을 돌려줌 — `used_jev_deepagents/corpus/01-jev-system-one.md:3`). 판서 1의 Decision Model(like Jev)과 같은 흐름으로, "적게, 정확히 넣어 컨텍스트를 아낀다".
- **멀티턴(예고)** [전사 6강 44:55, 2강 45:58, 3강 28:08 · 이미지 Day01_01 · 추정]: 판서 1에 "멀티턴은 사용자에게만 멀티턴". 사용자가 보는 것: 대화가 이어지는 멀티턴, 화면에 모든 턴이 보임. 기술적으로는: 매번 싱글턴 호출, 압축·요약한 맥락을 다시 넣음, Context Change를 감지해 압축. Day01 Ch09 요약 미들웨어(`SummarizationMiddleware`)와 연결. 실제로 다뤘는지는 모름.

### 실습/데모 내용 (명령어, 파일 구조, 프롬프트, 코드 조각 등 원문 그대로 보존)
1. **과제(6강 끝에서 낸 것)** [전사 6강 44:01~46:00 · 추정 실습 진행]:
   - 읽기: Day01 폴더 → 요약: 무엇을 가르치는 자료인지 → 저장: 요약을 Day01 폴더에 파일로.
   - 파일로 저장하게 한 이유: 출력이 아주 길어서 보기 편하게.
   - 기존 도구만 쓰게 지시, 새 도구를 만들지 못하게 함.
   - 설계부터 Claude Code와 상의해도 됨(6강 46:00).
2. **실습 대상: 과정 저장소의 Day01(LangGraph V1 튜토리얼)** [과정 페이지 Day01/README.md 튜토리얼 목록]:
   ```
   Day01
   ├─ PART01 기초        StateGraph · 노드/엣지 · 조건부 분기
   │   ├─ Ch02 도구       @tool, get_weather, 도구 오류 처리
   │   └─ Ch04 구조화된 출력  규격 오류 시 재시도
   ├─ PART02 에이전트
   │   ├─ Ch06 미들웨어    before/after/wrap 훅
   │   └─ Ch07 컨텍스트 엔지니어링 · Ch09 메모리(요약)
   ├─ PART03 확장        멀티에이전트 · 서브그래프 · ToolNode · 스트리밍
   └─ PART04~05
   ```
   (장표의 묶음 표시를 트리로 옮긴 것이며, 각 항목의 PART 소속 배치는 장표 레이아웃 기준)
3. **실습 코드의 뼈대** — 장표 명시: "과정 문서의 예시를 실습 과제에 맞춰 줄였다. 수업에서 실제로 쓴 코드는 아니다." [과정 페이지 deep-agents-core 예시 · 전사 6강 24:18 · 추정 조합]
   1. `from deepagents import create_deep_agent` — 6강 24:18에서 셀을 만들어 불러 봄
   2. `backend=FilesystemBackend(root_dir=..., virtual_mode=True)` — 파일 도구가 볼 폴더를 Day01로 한정
   3. `system_prompt`: 기본 파일 도구만 쓰고 새 도구는 만들지 말 것 — 읽기 → 요약 → `write_file`로 저장
   4. `middleware`: `wrap_tool_call`로 도구 호출 기록 — 어떤 도구를 몇 번 불렀는지 확인
   - 저장소 확인: 6강 노트북 마지막 셀에 이 과제의 실제 구현이 있다(`Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` 셀 #36). 위 뼈대와 다른 점: backend는 `CompositeBackend(default=FilesystemBackend(root_dir=DAY01_DIR, virtual_mode=True), routes={"/_agent_scratch/": StateBackend()}, artifacts_root="/_agent_scratch")`, `FilesystemPermission` 목록으로 점 파일·그림·PDF 읽기와 요약 폴더 밖 쓰기를 막음, `tools=[]`·`middleware=[]`(도구 호출 기록 미들웨어는 없음), 저장 경로 `/sample_data/summary/day01_overview.md`, `config={"recursion_limit": 80}`. 발췌:
     ```python
     agent = create_deep_agent(
         model=model,  # 위에서 만든 model 을 그대로 쓴다
         tools=[],  # 새 도구 없음: 기본 파일 도구만 쓴다
         middleware=[],
         system_prompt=system_prompt,
         backend=backend,
         permissions=permissions,
     )
     result = agent.invoke({"messages": [{"role": "user",
         "content": "Day01 폴더를 읽고 어떤 내용을 가르치는 자료인지 요약해서 저장해줘."}]},
         config={"recursion_limit": 80})
     ```

### 강사 팁·주의사항
- (녹음 없음) 강사가 말로 한 팁은 확인 불가. 아래는 판서·앞 강의 전사에서 확인되는 지침만 정리.
- 도구 결과를 모두 모델에 돌려줄 필요는 없음 — 필요 없으면 짧은 ToolMessage로 바꿔 컨텍스트를 아낄 것("적게, 정확히"). [이미지·추정]
- 새 도구를 만들지 말고 기존 파일 도구로 해결하도록 지시(6강 과제 조건). [전사]
- 긴 출력은 파일로 저장. [전사]
- 여러 미들웨어 사용 시 before/after/wrap의 실행 순서 규칙을 고려. [과정 페이지]

### 실제 프로젝트에 적용할 체크리스트 (- [ ] 행동 지침 형태)
- [ ] 단순 1회성 작업은 `create_agent`, 계획이 필요한 다단계 작업은 `create_deep_agent`로 구분해 선택한다.
- [ ] Deep Agent의 기본 미들웨어(TodoList, Filesystem, SubAgent, Skills, Memory, HumanInTheLoop)와 그 도구들이 항상 포함됨을 전제로 설계한다.
- [ ] 파일 시스템 백엔드는 `root_dir`로 접근 범위를 작업 폴더에 한정한다(예: `virtual_mode=True`).
- [ ] 시스템 프롬프트에 "기본 도구만 사용, 새 도구 생성 금지" 같은 제약을 명시한다.
- [ ] `wrap_tool_call` 미들웨어로 도구 호출 이름·횟수를 기록해 에이전트 행동을 검증한다.
- [ ] 에이전트 루프의 개입 지점(시작/입력 후/도구 전후/서브에이전트/종료)마다 필요한 감시·수정·제어·강제(가드레일, PII, 호출 횟수 제한) 로직을 배치한다.
- [ ] 미들웨어 순서를 정할 때 `before_*` 순차, `after_*` 역순, `wrap_*` 중첩(첫 번째가 가장 바깥) 규칙을 확인한다.
- [ ] 긴 도구 출력은 빠른 디시전 모델로 필요 여부를 판단해, 불필요하면 짧은 ToolMessage로 대체한다.
- [ ] 멀티턴 대화는 매번 싱글턴 호출에 요약·압축한 맥락을 넣는 구조로 설계하고, 요약 미들웨어 적용을 검토한다.

> 확인 필요: (전사가 불명확한 부분, 무발화 구간)
> - 이 수업 전체가 녹음 없음 — 강사 발화 내용, 시작·끝 시각, 회차(7강 여부)는 모두 추정.
> - 판서 훅 6종을 어떤 순서로, 어떤 예로 설명했는지 모름.
> - Claude Code 훅 ↔ LangChain 미들웨어 짝짓기는 장표의 해석이며 강사가 직접 대응시켰는지 모름.
> - 판서의 `>> Jev` 의미(디시전 모델을 이 자리에 쓰자는 뜻)는 장표의 해석.
> - 실습 코드·결과 화면이 없음 — 코드 뼈대는 과정 문서 예시를 줄인 것으로 수업 실제 코드가 아님. → 일부 해결: 저장소 노트북에 과제 구현 셀(`Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` 셀 #36)과 결과 파일(`Day01/sample_data/summary/day01_overview.md`)이 있다(실습 3항 참고). 수업 중 화면과 같은 코드인지는 확인할 수 없다.
> - 멀티턴 구현을 실제로 다뤘는지 모름(녹음·판서에 구현 장면 없음).
> - ~~6강 전사에서는 파일 시스템 도구를 `ls, read, write, edit, delete, glob`으로 언급했으나, 장표(과정 페이지 기준)는 `ls · read_file · write_file · edit_file · glob · grep`으로 표기 — 실제 도구명은 설치된 deepagents 버전으로 확인 필요.~~ → 해결: 둘 다 일부만 맞다. 실제 도구는 `ls`·`read_file`·`write_file`·`edit_file`·`delete`·`glob`·`grep`이고, 실행 가능한 backend면 `execute`가 더해진다 (저장소 확인: `Day08/dcode-analysis/deepagents/libs/deepagents/deepagents/middleware/filesystem.py:1470-1473`, `:1860-1867`, 소스 사본 0.7.14 기준).
