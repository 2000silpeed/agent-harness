## 2일차 6강 — Structured Output과 도구 호출: Deep Agent 코드 읽기와 실습

> 장표 제목: "출력 규격에서 파일 작업까지" (SDS AX Advanced · 2026-11-03 · 47:14)

### 핵심 요약 (3~5줄)
- Structured Output(Response Format)은 "원하는 출력 형태를 주고 그대로 달라"는 것 = LLM의 **지시 이행**. 규격이 복잡(중첩·긴 설명·깊은 관계)할수록 실패율이 높아지므로 **도구를 최대한 단순하게 쪼개야** 함. "Structured Output은 도구 호출의 관점에서" 볼 것.
- 도구 호출은 **메시지일 뿐**이고 실제 실행·결과/오류 메시지 구성은 **우리 런타임**이 제어. 여러 호출은 순서가 없으면 비동기로, 순서가 필요하면 순서대로 호출해 주는 도구로 처리.
- Pydantic `ContactInfo`(name/email/phone) + `create_agent`(노드 하나짜리 LangGraph 추상화) 예제 → `read` 스키마가 Claude Code의 Read 도구와 닮았음을 보여줌.
- `create_deep_agent` 소스를 반환부부터 추적: `create_agent` + 미들웨어(FilesystemMiddleware, SubAgentMiddleware)로 ls/read/write/edit/delete/glob 등 도구 추가, recursion limit 9999.
- 실습: deep agent 호출 → Tavily 검색 붙이기(TODO 1) → 결과 저장(TODO 2) → Day 01 폴더를 읽어 요약을 같은 폴더에 저장(새 도구 생성 금지 지시).

### 주요 개념 (개념별 설명, 강사가 강조한 이유 포함)
- **Response Format / Structured Output**: "니가 이 데이터를 판단해서 그 아웃풋을 우리한테 그대로 줘". 코드에 안 쓰여 있고 개념적으로 헷갈리므로 "꼭 이해하고 넘어가셔야" 한다고 강조.
- **지시 이행**: 규격대로 메시지를 채우는 능력. "공부를 많이 한 친구 vs 못한 친구" 비유. 과거 모델은 규격 맞추기를 어려워했지만 요즘은 아주 작은 모델도 잘함. 단, JSON 객체 안에 객체 안에 객체처럼 복잡해지면 "깨집니다".
- **도구 호출 실패**: Claude Code에서 자주 보는 "도구 호출 실패" 메시지가 그 예. "그 규격이 간단하면 실패 거의 안 하면 돼요. 점점점점 복잡해질수록 실패율은 높아집니다." Claude도 실패함.
- **도구 정의 스키마**: 함수 이름(`getWeather`) + 간단한 설명("실시간 날씨") + arguments 객체(`location`: string, description: "지역을 자연어로 표시"). 도구 리스트도 결국 이런 데이터로 LLM에 전달됨. 인자가 복잡/설명이 길/관계가 깊을수록 실패 확률 상승.
- **function calls 메시지**: OpenAI 기준 설명(모델사마다 필드 이름은 다름). LLM은 "어떤 펑션에 어떤 파라미터를 채워주세요"라는 정해진 규격의 메시지를 출력. 이제는 도구 호출이 한 개가 아님.
- **도구 호출 순서 제어**: 순서가 없으면 먼저 들어오는 대로 비동기로 실행. 순서가 있으면 "받은 순서대로 다른 도구를 호출해 주는 도구"를 둠. 도구는 겹쳐 쓸 수 있음(도구 안에서 도구) — 어차피 정해진 메시지 규격이기 때문.
- **런타임 제어**: "메시지여서 우리가 그 실행을 결정하면 돼요." 실행은 에이전트를 만드는 우리 환경에서 돌거나 우리가 대신 API 요청. 우리는 모델 호출의 I/O만 중개.
- **도구 단순화**: 예제는 단순하지만 실제 에이전트의 도구 호출 아웃풋은 굉장히 복잡 → 그대로 두면 자주 실패하므로 단순하게 쪼개야 함.
- **Pydantic**: 구조체 구성 라이브러리. `ContactInfo`(Name, Email, Phone 모두 string)와 필드 설명으로 "어떤 데이터를 채워줘"를 전달.
- **create_agent**: 노드 하나짜리 LangGraph를 추상화한 함수. 백본은 LangGraph. 직접 LangGraph로 짜면 한 땀 한 땀 제어 가능하지만 어려우므로 함수로 제공. 입력: model, tools, response_format, state.
- **Read 도구 스펙**: 설명·필드 설명을 생략한 `read` 클래스(파라미터 3개: 경로, 몇 번째 줄부터 몇 번째 줄까지)만으로도 파일 읽기 도구임을 알 수 있음 → Claude Code의 Read와 유사(정확한 스펙은 공개된 적 없음, 실제 실행기는 다름). "이게 그 도구의 스펙입니다."
- **Deep Agent (create_deep_agent)**: LangChain이 만든 에이전트. `create_agent`에 우리 컴퓨터에서 돌 수 있는 도구(주로 파일 시스템: 프로세스 실행, 파일 읽기/쓰기 등)를 추가한 것.
- **미들웨어(FilesystemMiddleware, SubAgentMiddleware)**: 기본 도구를 넣어주는 역할. 파일 시스템 미들웨어는 `ls`, `read`, `write`, `edit`, `delete`, `glob` 등 리눅스 CLI 같은 시스템을 툴로 만들어 넣음. (저장소 확인: 실제 도구 이름은 `ls`·`read_file`·`write_file`·`edit_file`·`delete`·`glob`·`grep`, 실행 가능한 backend일 때 `execute`가 더해짐 — `Day08/dcode-analysis/deepagents/libs/deepagents/deepagents/middleware/filesystem.py:1860-1867`)
- **ToolMessage**: 도구 결과를 프로그램으로 확인해 정상이면 정상 메시지, 오류면 오류 메시지를 우리가 구성해 반환(예: `grep`류 도구 호출 에러 → ToolMessage 반환).
- **도구를 늘리지 말고 규칙을 주기**: "이런 도구를 계속 뒤로 늘리는 건 별로 좋은 방향이 아니에요." 이미 있는 파일 시스템 도구로 JSON 파일을 저장하도록 규칙(시스템 프롬프트)을 주는 것이 가장 좋음.

### 실습/데모 내용 (명령어, 파일 구조, 프롬프트, 코드 조각 등 원문 그대로 보존)
1. **노트북**: Part 2 → 챕터 4 "구조화된 출력"(Structured Output) 노트북(전사상 `랭그래프 structure.off` 파일 → 저장소 확인: `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb`).
   - LangSmith 추적 설정 코드는 **주석 처리**, 환경 변수 로드 셀은 실행.
2. **Pydantic 예제**: `ContactInfo`(name, email, phone: str + 필드 설명) → 모델을 Sonnet으로 바꿔 `create_agent(model, tools, response_format, ...)`에 메시지 넣어 호출 → name/email/phone 결과 확인.
3. **Read 스키마 시연**: 설명을 생략한 `read` 클래스(파라미터 3개)를 정의하자 Copilot이 바로 알아챔. 2·3항의 노트북 원문(저장소 확인: `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` 셀 #6, 0부터 센 셀 번호, 독스트링 생략):
   ```python
   class ContactInfo(BaseModel):
       name: str = Field(description="The name of the person")  # 이름
       email: str = Field(description="The email address of the person")  # 이메일 주소
       phone: str = Field(description="The phone number of the person")  # 전화번호

   class Read(BaseModel):
       file_path: str
       start: int
       end: int

   model = init_chat_model("claude-sonnet-5-5")
   agent = create_agent(model=model, tools=[], response_format=ContactInfo)
   result = agent.invoke({"messages": [{"role": "user",
       "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]})
   print(result["structured_response"])
   ```
4. **create_deep_agent 소스 읽기**: 함수 끝 `return`만 보면 됨 → `create_agent(...)` 호출: model, system prompt 조합, tools, middleware, response_format, context schema, checkpointer 등 → `.with_config(...)`의 recursion limit **9999**("일단 그냥 멈추지 않는다"). tools 추적 → FilesystemMiddleware, SubAgentMiddleware. (저장소 확인: `Day08/dcode-analysis/deepagents/libs/deepagents/deepagents/graph.py:956-971` — `return create_agent(...).with_config({"recursion_limit": 9_999, ...})`. 저장소의 deepagents 소스 사본은 0.7.14, 실습 환경은 루트 README 기준 0.7.32)
5. **실습 1** (노트북 맨 아래 새 셀):
   ```python
   from deepagents import create_deep_agent
   ```
   - 단순 호출로 결과가 정상인지 확인(위의 `create_agent` 코드 참고 또는 Claude에게 요청).
   - Tavily 키가 없던 사람은 이때 발급.
   - 단일 셀에서 두 가지 작업:
     - **TODO 1**: Tavily 도구를 붙여 실행(질문도 Tavily를 쓰도록 변경).
     - **TODO 2**: Tavily 조회 결과를 날리지 않고 저장(경로는 강사가 지정).
   - 저장소 노트북의 이 셀(저장소 확인: `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` 셀 #35, 발췌). 저장 경로는 `Day01/sample_data/tavily/`이고, 강사 리뷰처럼 저장용 도구 `save_tavily_result`를 따로 둔 형태다:
     ```python
     from deepagents import create_deep_agent
     from langchain_tavily import TavilySearch

     SAVE_DIR = DAY01_DIR / "sample_data" / "tavily"
     tavily = TavilySearch(max_results=3)          # TODO 1

     @tool
     def save_tavily_result(query: str, results: list[dict]) -> str:   # TODO 2
         """Tavily 검색 결과를 Day01/sample_data/tavily/ 에 JSON 파일로 저장한다."""
         ...

     agent = create_deep_agent(model=model, tools=[tavily, save_tavily_result],
         system_prompt="웹 검색이 필요하면 Tavily 검색 도구를 사용한다. ...")
     ```
   - 모델: Sonnet high 정도면 충분, Opus까지 갈 필요 없음. 단일 파일 작업이면 VS Code 익스텐션도 무방, 또는 Claude Code 세션.
6. **강사 결과 리뷰**:
   - Claude가 처음에 Tavily search를 감싸 메모리 백엔드에 쓰는 래핑 도구를 직접 만들겠다고 함 → "약간 바보 같은 생각"(이미 파일 시스템 도구가 있음) → "그거 말고 직접 파일 시스템에 저장하는 도구를 호출하도록 구성해라"로 재지시.
   - 결과 코드: `sample_data/tavily` 폴더(없으면 생성)에 저장, Tavily 도구가 TODO 1에 붙음, `max_results=3`(왜 3인지 모름), 그래도 조회 결과 저장 도구를 또 만들었음("잘못 만들었네").
   - Claude가 만든 질문: "랭체인 최신 버전이 뭔지 웹에서 검색해서 한 줄로 알려줘."
   - 저장된 JSON: source URL, title, content, score(쿼리 매칭 점수) — 상위 점수 기준 3개.
7. **실습 2** (휴식 후 약 30분):
   - Day 01 폴더 **전체**를 읽어, 어떤 내용을 가르치는 자료인지 설명(요약)하는 딥 에이전트 구현.
   - 요약을 다시 Day 01 폴더에 파일로 저장(출력이 길어지므로).
   - 에이전트에게 반드시 지시: "Tavily 도구 외에 새로운 도구를 만들 수 없도록" (기본 도구로 해결).
   - 저장소 노트북에 이 과제의 구현 셀이 있다(저장소 확인: `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` 셀 #36). 요점: `tools=[]`로 새 도구 없이 기본 파일 도구만 쓰고, backend를 `CompositeBackend(default=FilesystemBackend(root_dir=DAY01_DIR, virtual_mode=True), routes={"/_agent_scratch/": StateBackend()}, ...)`로 바꿔 실제 Day01을 보게 하며, `FilesystemPermission`으로 `.env` 등 점 파일·그림·PDF 읽기와 요약 폴더 밖 쓰기를 막는다. 요약은 `/sample_data/summary/day01_overview.md`에 저장하고, `config={"recursion_limit": 80}`으로 상한을 직접 준다. 결과 파일도 저장소에 있다(`Day01/sample_data/summary/day01_overview.md`).
   - 설계부터 Claude Code와 대화해도 됨. 다음(마지막 시간)은 멀티턴 실습으로 이어져 오늘 이론을 코드로 연결.

### 강사 팁·주의사항
- 출력 규격(도구 스키마)은 단순하게: 인자 수·중첩·설명 길이를 줄이고 작은 역할로 쪼갤 것.
- 모델의 호출 출력과 실제 실행을 구분 — 실행 여부·순서·오류 메시지는 런타임이 결정.
- 소스 코드는 앞의 파라미터 조합부보다 반환부부터 따라 읽기.
- Deep Agent는 recursion limit 9999로 사실상 멈추지 않게 설정되어 있음을 인지.
- 에이전트(Claude)가 불필요한 래핑 도구를 만들면 기존 도구 사용을 명시적으로 재지시. 도구 수를 늘리기보다 규칙을 줄 것.
- 한 번에 확장하지 말고 단순 호출 정상 확인 → Tavily → 저장 순서로(장표).
- 단순 작업에 Opus는 과함 — Sonnet high로 충분.

### 실제 프로젝트에 적용할 체크리스트 (- [ ] 행동 지침 형태)
- [ ] 도구 스키마(이름·설명·인자)를 단순하게 설계하고, 중첩이 깊은 인자는 여러 도구로 분리한다.
- [ ] 도구 호출 실패율을 모니터링하고 실패가 잦은 도구는 스키마를 쪼갠다.
- [ ] 도구 실행은 런타임에서 통제하고, 정상/오류 결과를 명확한 ToolMessage로 구성해 반환한다.
- [ ] 순서 의존이 있는 도구 호출은 순차 실행 래퍼로 묶고, 독립 호출은 비동기로 처리한다.
- [ ] 구조화된 출력은 Pydantic 모델과 필드 설명으로 정의한다.
- [ ] 프레임워크(예: `create_deep_agent`) 도입 전 소스의 반환부·미들웨어·recursion limit 같은 기본값을 확인한다.
- [ ] 새 도구를 추가하기 전에 기존 도구(파일 시스템 등) + 규칙(시스템 프롬프트)으로 해결 가능한지 먼저 검토한다.
- [ ] 에이전트에게 "새 도구를 만들지 말 것" 같은 제약을 명시하고, 생성된 코드를 리뷰해 중복 도구를 제거한다.
- [ ] 긴 결과물은 파일로 저장하도록 지시하고 저장 경로를 명시한다.
- [ ] 작업 난이도에 맞게 모델/effort를 선택한다(단순 코드 작업은 Sonnet).

> 확인 필요: (전사가 불명확한 부분, 무발화 구간)
> - ~~노트북 파일명 "랭그래프 structure.off"는 전사 그대로이며 실제 파일명 확인 필요.~~ → 해결: `05-LangGraph-Structured-Output.ipynb` (저장소 확인: `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb`).
> - 22:43 "스카운트 같은 것도 두고 있고요" — 도구명 미확인. 22:50 이후 "그래프 툴"은 `grep` 도구로 추정되나 전사상 "그래프"로만 나옴. → deepagents 파일 시스템 도구에 `grep`이 실제로 있다 (저장소 확인: `Day08/dcode-analysis/deepagents/libs/deepagents/deepagents/middleware/filesystem.py:1860-1866`). '스카운트'는 저장소에서 확인되지 않음.
> - 23:59 "reg를 해야 되기 때문에" — 의미 미확인.
> - ~~`from deepagents import create_deep_agent`는 전사("from deep agent, import create deep agent")와 분석 요약 기준 표기 — 실제 패키지명 확인 필요.~~ → 해결: 패키지명 `deepagents`, 표기 그대로 맞다 (저장소 확인: `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` 셀 #35, 루트 `README.md` "`deepagents` 0.7.32 기준").
> - ~~`ContactInfo`, `read` 클래스, deep agent 셀의 실제 코드 원문은 전사에 없음.~~ → 해결: 위 3항·5항·7항에 저장소 노트북 원문을 넣었다(셀 #6·#35·#36). `read` 클래스의 실제 이름은 `Read`, 파라미터는 `file_path`·`start`·`end`. 저장소 노트북은 수업 뒤 정리된 상태일 수 있다.
> - ~~Tavily 결과 저장 경로를 강사가 "이렇게 정의해드리도록" 했으나 화면 내용(정확한 경로 문자열)은 전사에 없음(결과는 `sample_data/tavily`).~~ → 해결: `SAVE_DIR = DAY01_DIR / "sample_data" / "tavily"` (저장소 확인: `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` 셀 #35). 저장된 JSON 2개도 `Day01/sample_data/tavily/`에 있다.
> - 45:13 "두 개로 구현하는 멀티턴"의 구체 내용 미확인.
> - 25:03~26:08, 30:40~34:45, 41:33~43:57, 46:24~47:12 실습 대기 무발화 구간.
