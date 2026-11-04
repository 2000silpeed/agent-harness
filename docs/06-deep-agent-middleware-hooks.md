# 6. Deep Agent, 미들웨어, 훅

## create_agent vs create_deep_agent [강의]
| 구분 | create_agent | create_deep_agent |
|---|---|---|
| 뼈대 | LangGraph 그래프 하나 | create_agent를 반환 |
| 도구 | 직접 넣은 것만 | 계획, 파일, 위임 도구가 기본 |
| 맞는 일 | 한 번에 끝나는 일 | 여러 단계 계획이 필요한 일 |

- Deep Agent 기본 미들웨어: TodoList(`write_todos`), Filesystem(`ls, read_file, write_file, edit_file, glob, grep`), SubAgent(`task`), Skills, Memory, HumanInTheLoop
- 파일 도구가 기본인 이유는 서브에이전트와 **파일 시스템을 매개로** 작업과 결과를 주고받기 때문입니다. "대부분의 작업을 파일 시스템 기반으로 해야 되기 때문입니다." 직접 통신(IPC)은 고려하지 않습니다.
- `recursion_limit 9999`로 사실상 멈추지 않습니다. 예산과 종료 조건은 직접 둬야 합니다([10-harness.md](10-harness.md)).

## 훅과 미들웨어 대응 [강의 판서, 일부 추정]
| Claude Code 훅 | LangChain 미들웨어 | 쓸 만한 용도 |
|---|---|---|
| SessionStart | before_agent | 환경 점검, 컨텍스트 주입 |
| UserPromptSubmit | before_model | 입력 가드레일, 주제 변경 감지 |
| Pre/PostToolUse | wrap_tool_call | 권한 검사, 도구 기록, 결과 축약 |
| SubagentStart/Stop | task 도구 wrap | 위임 기록 |
| Stop | after_agent | 세션 요약, 근거 저장 |

- 미들웨어의 역할은 **감시**(로그, 호출 수), **수정**(프롬프트, 도구 선택), **제어**(재시도, 폴백, 조기 종료), **강제**(호출 제한, 가드레일, PII)입니다.
- 실행 순서: `before_*`는 M1→M2, `after_*`는 역순 M2→M1, `wrap_*`는 중첩(M1이 가장 바깥)입니다.
- 판서의 질문: **"이 도구의 출력이 전달될 필요가 있을까?"** PostToolUse 지점에서 작은 판단 모델이 필요 여부를 판단합니다. 필요 없으면 짧은 메시지로 바꿔 컨텍스트를 아낍니다.

## 하네스 적용 [제안]
- `.claude/hooks/log-tool-use.sh`는 PostToolUse **감시** 예시입니다. 어떤 도구를 몇 번 불렀는지 기록합니다.
- 결과 축약 훅은 정보가 빠질 위험이 있어 기본으로 넣지 않았습니다. 필요하면 원본을 파일로 보존하는 조건으로 추가합니다.
