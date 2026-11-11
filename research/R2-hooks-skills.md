# R2. 훅·스킬·플러그인·관측·비용 — 공식 문서 대조 결과

- 조사일: 2026-11-11. 대상 가이드: `claude-setup/GUIDE.md` A4~A10, `claude-setup/hooks/*`.
- 1차 출처: `https://code.claude.com/docs/en/<page>.md` 원문(마크다운)을 내려받아 직접 읽었다. 인용은 원문 그대로다. 내려받은 사본: `/tmp/claude-0/-home-user-agent-harness/9d24d4e0-4e22-527d-9ef4-148a860878ba/scratchpad/docs/`
- 로컬 확인(모델 호출 없음): 설치된 CLI `2.1.322 (Claude Code)`로 `claude --help`, `claude doctor`, `claude plugin validate`를 돌렸고, 훅 스크립트는 stdin에 JSON을 넣어 직접 실행했다. 실제 세션에서 훅이 발동하는지는 확인하지 않았다(5절).
- `anthropic.com/engineering/claude-code-best-practices`는 이제 `code.claude.com/docs/en/best-practices`로 308 리다이렉트된다. 엔지니어링 글이 따로 있지 않고 공식 문서 페이지가 그 자리를 대신한다.
- 표기: "≥2.1.295"는 공식 문서가 "Requires Claude Code v2.1.295 or later"라고 적은 것.

---

## 1. 확인된 사실

URL은 모두 `https://code.claude.com/docs/en/` 뒤에 붙는 경로다(다른 사이트는 전체 주소).

### 1.1 훅

| # | 주장 | 원문 인용 | URL |
|---|---|---|---|
| H1 | 훅 이벤트는 33개다 | 표에 나열된 이벤트: `SessionStart`, `Setup`, `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Notification`, `MessageDisplay`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`, `Elicitation`, `ElicitationResult`, `SessionEnd`. `claude doctor`(2.1.322)가 출력하는 "Valid events" 목록과 일치한다. | `hooks#hook-lifecycle` |
| H2 | 발동 주기는 세 가지다 | "per session: `SessionStart` and `SessionEnd` / per turn: `UserPromptSubmit`, `Stop`, and `StopFailure` / on every tool call inside the agentic loop: `PreToolUse` and `PostToolUse`" | `hooks#hook-lifecycle` |
| H3 | 핸들러 타입은 5개다 | "There are five types": `command`, `http`, `mcp_tool`, `prompt`, `agent`. "Agent hooks are experimental and may change." | `hooks#hook-handler-fields` |
| H4 | 매처 문법: 글자·숫자·`_`·`-`·공백·`,`·`\|`만 있으면 정확 일치 목록, 그 밖의 문자가 있으면 정규식 | "Only letters, digits, `_`, `-`, spaces, `,`, and `\|` → Exact string, or list of exact strings separated by `\|` or `,`" / "Contains any other character → JavaScript regular expression, unanchored" / "`Edit.*` matches both `Edit` and `NotebookEdit`; wrap the pattern in `^` and `$`, as in `^Edit$`, when you need a whole-string match." | `hooks#matcher-patterns` |
| H5 | 매처가 없거나 `"*"`·`""`면 전부 매치. 매처는 대소문자를 가린다 | "`\"*\"`, `\"\"`, or omitted → Match all" / "Matchers are case-sensitive" | `hooks#matcher-patterns`, `hooks-guide#hook-not-firing` |
| H6 | `UserPromptSubmit`·`Stop` 등은 매처가 없다. 넣어도 무시된다 | "`UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `MessageDisplay` → no matcher support" / "If you add a `matcher` field to an event without matcher support, it is silently ignored." | `hooks#matcher-patterns` |
| H7 | 도구 이벤트의 매처는 `tool_name`에 건다. MCP 도구는 `mcp__<server>__<tool>` | "For tool events, that field is `tool_name`." / "To match every tool from a server, append `.*` to the server prefix. The `.*` is required" | `hooks#matcher-patterns`, `hooks#match-mcp-tools` |
| H8 | `if` 필드로 인자까지 좁힐 수 있지만 최선 노력이다. 규칙은 하나만 | "`if` uses permission rule syntax ... so `\"Bash(git *)\"` runs when any subcommand of the Bash input matches `git *` and `\"Edit(*.ts)\"` runs only for TypeScript files." / "The `if` field holds exactly one permission rule." / "Because the `if` filter is best-effort, use the permission system rather than a hook to enforce a hard allow or deny." | `hooks#common-fields` |
| H9 | 공통 입력 필드 | `session_id`, `prompt_id`, `transcript_path`, `cwd`, `scratchpad_dir`(≥2.1.257), `permission_mode`, `effort`, `hook_event_name`; 서브에이전트 안에서는 `agent_id`, `agent_type`. "`permission_mode` ... The mode labeled **Manual** arrives as `\"default\"`, never as `\"manual\"`" | `hooks#common-input-fields` |
| H10 | PreToolUse 입력은 `tool_name`, `tool_input`, `tool_use_id`. 파일 도구의 경로는 항상 절대 경로 | "PreToolUse hooks receive `tool_name`, `tool_input`, and `tool_use_id`." / "For the file tools `Write`, `Edit`, and `Read`, `tool_input.file_path` is always absolute" / "Claude Code expands `~` and relative paths before hooks run, so a hook that matches on paths can't be bypassed via `~` or a relative spelling of the same path" | `hooks#pretooluse-input` |
| H11 | 도구별 `tool_input` 필드 | Write: `file_path`, `content`. Edit: `file_path`, `old_string`, `new_string`, `replace_all`. Bash: `command`, `description`, `timeout`, `run_in_background`. Read: `file_path`, `offset`, `limit`. NotebookEdit의 주 필드는 `notebook_path`("`notebook_path` for NotebookEdit") | `hooks#pretooluse-input`, `permissions` |
| H12 | PostToolUse 입력에는 `tool_response`와 `duration_ms`가 더 있다. 성공한 호출에만 발동한다 | "The input includes both `tool_input`, the arguments sent to the tool, and `tool_response`, the result it returned." / "Runs immediately after a tool completes successfully." 실패는 `PostToolUseFailure`. | `hooks#posttooluse` |
| H13 | UserPromptSubmit 입력은 `prompt`. 내가 친 프롬프트에만 발동하는 게 아니다 | "UserPromptSubmit hooks receive the `prompt` field containing the submitted text." / "Claude Code also runs them on: A session-scoped scheduled task firing, including a `/loop` iteration / A background subagent reporting back ... / A message another session sends" | `hooks#userpromptsubmit` |
| H14 | Stop 입력은 `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons`. 8회 연속 차단 상한이 있다 | "The `stop_hook_active` field is `true` when Claude Code is already continuing as a result of a stop hook. Check this value or process the transcript to avoid blocking on a condition that will never resolve." / "Claude Code applies an 8-consecutive-continuation cap: after stop hooks have continued the turn eight times in a row, Claude Code overrides the next block and ends the turn." (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`로 조정) | `hooks#stop-input` |
| H15 | Stop은 응답이 끝날 때마다 발동한다. 사용자 중단에는 발동하지 않는다 | "`Stop` hooks fire whenever Claude finishes responding, not only at task completion. They don't fire on user interrupts. API errors fire StopFailure instead." | `hooks-guide#limitations` |
| H16 | 종료 코드: 0=성공, 2=차단, 그 밖=비차단 오류(동작은 진행) | "**Success**: your hook exits 0. ... **Blocking error**: your hook exits 2. On events that can block, Claude Code stops the action. **Non-blocking error**: your hook exits with any other code, or fails in some other way, such as not starting or printing invalid JSON. The action goes ahead, except for hooks whose failure blocks the action ... On events such as `PreToolUse`, you see a `<hook name> hook error` notice in the transcript." | `hooks#exit-code-output` |
| H17 | exit 1은 막지 않는다 | "Exit code 1 without valid JSON output is a non-blocking error unless the hook is one whose failure blocks the action, even though 1 is the conventional Unix failure code. If your hook is meant to enforce a policy, use `exit 2`." | `hooks#other-exit-codes` |
| H18 | exit 0/2가 아니어도 stdout의 유효한 JSON이 결정한다 | "when a `PreToolUse` hook exits 1 but prints JSON that passes validation, that JSON can still decide what happens." | `hooks#exit-code-output` |
| H19 | exit 2의 효과는 이벤트마다 다르다 | `PreToolUse`: "Blocks the tool call" / `UserPromptSubmit`: "Blocks the prompt, so it never reaches Claude." / `Stop`: "Prevents Claude from stopping, continues the conversation" / `PostToolUse`: "Shows stderr to Claude; the tool already ran" / `PreCompact`: "Blocks compaction" / `SessionEnd`·`SessionStart`: "Shows stderr to user only" / `PermissionRequest`: "Exit code 2 isn't honored for this event" | `hooks#exit-code-2-behavior-per-event` |
| H20 | exit 2의 메시지는 stderr다. exit 0의 stderr는 모델이 못 본다 | "The message that comes with the block is your hook's stderr." / "Claude never sees stderr from a hook that exits 0." / "To surface a warning to Claude from a `PostToolUse` or `PostToolUseFailure` hook, exit 2 instead so Claude sees the stderr even though the tool already ran." | `hooks#exit-code-2`, `hooks#exit-code-0` |
| H21 | stdout은 대부분 디버그 로그로만 간다. UserPromptSubmit·SessionStart 등만 일반 텍스트 stdout이 컨텍스트에 들어간다 | "For most events, Claude Code writes stdout to the debug log and doesn't show it in the transcript." / "**`UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and `PostModelSwitch`**: Claude Code adds plain-text stdout as context that Claude can see and act on." / "**`PreCompact`**: your stdout becomes instructions for the compaction summary" | `hooks#exit-code-0` |
| H22 | stdout이 JSON으로 읽히려면 JSON 객체 하나만 있어야 한다 | "your stdout counts as JSON output only when you print one JSON object, on one line or several, with nothing around it but whitespace." / "Output that doesn't start with `{` ...: plain text." | `hooks#exit-code-0` |
| H23 | JSON 공통 필드 | `continue`(기본 true; false면 "Claude stops processing entirely"), `stopReason`, `suppressOutput`("Has no effect"), `systemMessage`, `terminalSequence` | `hooks#json-output` |
| H24 | PreToolUse 결정은 `hookSpecificOutput.permissionDecision` = allow/deny/ask/defer | "`\"allow\"` skips the permission prompt ... `\"deny\"` prevents the tool call. `\"ask\"` prompts the user to confirm. `\"defer\"` ends the turn so the tool can be resumed later, and requires non-interactive mode with the `-p` flag." / "When multiple PreToolUse hooks return different decisions, precedence is `deny` > `defer` > `ask` > `allow`." / 그 밖에 `permissionDecisionReason`, `updatedInput`, `additionalContext` | `hooks#pretooluse-decision-control` |
| H25 | PreToolUse의 최상위 `decision`은 폐기 예정이다 | "PreToolUse previously used top-level `decision` and `reason` fields, but these are deprecated for this event. ... Other events like PostToolUse and Stop continue to use top-level `decision` and `reason` as their current format." | `hooks#pretooluse-decision-control` |
| H26 | 그 밖 이벤트의 차단은 최상위 `decision: "block"` + `reason` | "UserPromptSubmit, UserPromptExpansion, PostToolUse, PostToolUseFailure, PostToolBatch, Stop, SubagentStop, ConfigChange, PreCompact → Top-level `decision`" / "The only value for `decision` is `\"block\"`." | `hooks#decision-control` |
| H27 | 필드를 잘못된 층에 두면 오류 없이 무시된다 | "When your hook returns `permissionDecision` or `additionalContext` at the top level instead of inside `hookSpecificOutput`, the JSON still parses, and Claude Code ignores the misplaced fields without reporting an error." | `hooks-guide#fields-at-the-wrong-level` |
| H28 | `additionalContext`·stdout은 1만 자 상한 | "A hook's `additionalContext`, `systemMessage`, and `initialUserMessage` strings, and its plain stdout, are capped at 10,000 characters" (넘으면 파일로 저장하고 앞 2,000자만 미리보기) | `hooks#json-output` |
| H29 | 붙이는 글은 사실 진술로 쓴다. 변하지 않는 지침은 CLAUDE.md가 낫다 | "For instructions that never change, prefer CLAUDE.md." / "Write the text as factual statements rather than imperative system instructions. ... Text framed as out-of-band system commands can trigger Claude's prompt-injection defenses, which causes Claude to surface the text to you instead of treating it as context." | `hooks#add-context-for-claude` |
| H30 | 붙인 글은 대화 기록에 저장된다 | "Claude Code saves the injected text in the session transcript. For mid-session events like `PostToolUse` or `UserPromptSubmit`, when you resume ... Claude Code replays the saved text rather than re-running the hook for past turns" | `hooks#add-context-for-claude` |
| H31 | 타임아웃 기본값(초) | "Defaults: 600 for `command`, `http`, and `mcp_tool`; 30 for `prompt`; 60 for `agent`. Claude Code lowers the `command`, `http`, and `mcp_tool` default to 30 on `UserPromptSubmit`, `PreModelSwitch`, and `PostModelSwitch`, and to 10 on `MessageDisplay`. `SessionEnd` hooks share a 1.5-second budget" | `hooks#common-fields` |
| H32 | 시간 초과된 PreToolUse 훅은 막지 않는다 | "On `PreToolUse`, a timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call ... so don't count on a stalled hook to act as a gate. To block the call when a `command` or `http` hook times out, set `onFailure: \"block\"`." | `hooks#timeouts` |
| H33 | `onFailure: "block"`으로 실패 시 차단(fail closed)할 수 있다 (≥2.1.295) | "On most events, when a hook fails or times out, Claude Code still carries out the action. A policy hook with a wrong path or a crashing script then lets everything through. To block the action instead, set `\"onFailure\": \"block\"` on a `command` or `http` hook. Requires Claude Code v2.1.295 or later." 실패로 치는 것: "Can't start", "Exit code other than 0 or 2", "HTTP error", "Timeout", "Invalid output". Stop·SubagentStop·TaskCompleted·TeammateIdle과 async 훅에는 효과가 없다. | `hooks#block-the-action-when-a-hook-fails` |
| H34 | 훅은 서브에이전트의 도구 호출에도 발동한다 | "Hooks from settings files, managed policy settings, and plugins also run inside subagents. When a subagent calls a tool, tool events such as `PreToolUse` and `PostToolUse` fire the same configured hooks as in the main conversation, and the input carries the `agent_id` and `agent_type` common input fields" | `hooks#hook-locations` |
| H35 | Bash로 파일을 쓰면 `Edit\|Write` 매처 훅은 발동하지 않는다 | "Claude Code doesn't run a `PostToolUse` hook matching `Edit\|Write` when a `Bash` command or a process outside Claude Code rewrites the same file." / "To run a hook when a specific file changes on disk, whatever wrote it, use FileChanged instead ... they have no decision control, so they can't block the write." | `hooks#posttooluse`, `hooks#pretooluse` |
| H36 | `@`로 파일을 붙이면 PreToolUse(Read)가 발동하지 않는다 | "By default, files you reference with `@` in your prompt are added without any tool call. ... so no PreToolUse hook fires for them, including hooks matching `Read`." (막으려면 `Read` deny 규칙 또는 `CLAUDE_CODE_DISABLE_FILE_MENTIONS=1`) | `hooks#pretooluse` |
| H37 | 훅의 allow는 권한 규칙을 못 넘는다. deny는 모든 모드에서 유효하다 | "PreToolUse hook decisions don't bypass permission rules. Claude Code evaluates deny and ask rules regardless of what a PreToolUse hook returns" / "a hook that returns `permissionDecision: \"deny\"` blocks the tool even in `bypassPermissions` mode or with `--dangerously-skip-permissions`." | `permissions#precedence-among-rules-hooks-and-mods`, `hooks-guide#hooks-and-permission-modes` |
| H38 | 같은 이벤트의 훅은 병렬로 돈다. 하나가 deny해도 나머지는 끝까지 돈다 | "When an event fires, its matching hooks run in parallel." / "One hook returning `deny` doesn't stop sibling hooks from executing." / "If you define the same handler in more than one settings file, it runs once." | `hooks#hook-handler-fields`, `hooks-guide#combine-results-from-multiple-hooks` |
| H39 | PostToolUse는 병렬 도구 호출마다 동시에 돈다. 묶음당 한 번은 PostToolBatch | "`PostToolUse` fires once per tool, which means it fires concurrently when Claude makes parallel tool calls. `PostToolBatch` fires exactly once with the full batch" | `hooks#posttoolbatch` |
| H40 | `prompt`·`agent` 훅은 결정적이지 않다 | "A `prompt` or `agent` hook asks *another model* to decide, so it isn't deterministic either. For real enforcement, use a `command` or `http` hook, and add `onFailure: \"block\"` if the action should also be stopped when the hook itself crashes or times out." | `best-practices#enforce-steps-with-hooks` |
| H41 | `async: true` 훅은 막지 못한다 | "Async hooks can't block or control Claude's behavior: response fields like `decision`, `permissionDecision`, and `continue` have no effect" | `hooks#run-hooks-in-the-background` |
| H42 | 경로 자리표시자와 exec 형식 | "`${CLAUDE_PROJECT_DIR}`: the project root where the session started." / "Prefer exec form for any hook that references a path placeholder. In shell form, wrap each placeholder in double quotes." / exec 형식: "**Exec form** runs when `args` is present. ... There is no shell" | `hooks#reference-scripts-by-path`, `hooks#exec-form-and-shell-form` |
| H43 | 워크트리에서는 `CLAUDE_PROJECT_DIR`가 그대로고 `cwd`가 따라간다 | "**`${CLAUDE_PROJECT_DIR}` stays put**: it still points at the project root where the session started ... **`cwd` follows Claude**: the `cwd` field in the hook's input JSON is the worktree root after Claude enters a worktree, and the new directory after Claude runs `cd`." | `hooks#reference-scripts-by-path` |
| H44 | 보안: 명령 훅은 내 전체 권한으로 돈다 | "Command hooks execute shell commands with your full user permissions. They can modify, delete, or access any files your user account can access. Review and test all hook commands before adding them to your configuration." | `hooks#security-considerations` |
| H45 | 작업 공간 신뢰: 대화형은 신뢰 대화상자 전까지 훅을 보류한다. `-p`는 신뢰한 것으로 친다 | "**Interactive session**: Claude Code holds back hooks from every settings file ... until you accept the workspace trust dialog" / "**`-p` or SDK session**: Claude Code never shows the dialog and treats the folder as trusted, so hooks committed in a repository's `.claude/settings.json` run in a folder you've never trusted" / "Before you script `claude -p` over a repository you didn't write, review its `.claude/` settings files, start with `--bare`, or turn hooks off for that run with `--settings '{\"disableAllHooks\": true}'`." | `hooks#workspace-trust` |
| H46 | 훅을 둘 수 있는 곳 | `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, 관리 정책, 플러그인 `hooks/hooks.json`, 스킬 frontmatter("The rest of the session once the skill is invoked"), 서브에이전트 frontmatter("While that subagent is running") | `hooks#hook-locations` |
| H47 | `/hooks`는 읽기 전용 목록이다. 설정 파일 수정은 보통 자동 반영된다 | "Type `/hooks` in Claude Code to open a read-only browser for your configured hooks." / "Direct edits to hooks in settings files are normally picked up automatically by the file watcher." | `hooks#the-hooks-menu` |
| H48 | 디버그 방법 | "Start Claude Code with `claude --debug-file <path>` to write the log to a known location" / `Hooks: PostToolUse:Write [.claude/hooks/log-write.sh] finished with status 0 (31ms)` 형식의 줄(≥2.1.296) / "Press `Ctrl+O` to open the transcript view and look for the hook's outcome" | `hooks#debug-hooks`, `hooks-guide#check-what-a-hook-did` |
| H49 | SessionEnd는 막지 못하고 기본 1.5초다 | "SessionEnd hooks have no decision control. They can't block session termination" / "SessionEnd hooks have a default timeout of 1.5 seconds." | `hooks#sessionend` |
| H50 | 압축 뒤 맥락 재주입은 SessionStart의 `compact` 매처로 한다 | "Use a `SessionStart` hook with a `compact` matcher to re-inject critical context after every compaction." | `hooks-guide#re-inject-context-after-compaction` |
| H51 | 설정 변경을 훅으로 감사·차단할 수 있다 | "Runs when a configuration file changes during a session. Use this to audit settings changes, enforce security policies, or block unauthorized modifications to configuration files." (`ConfigChange`, 매처 `project_settings` 등) | `hooks#configchange` |
| H52 | `MultiEdit`는 현재 도구 목록에 없다(레거시). 파일 수정 도구는 `Edit`, `Write`, `NotebookEdit` | 도구 표에 `Edit`, `Write`, `NotebookEdit`만 있고 `MultiEdit` 행이 없다. 권한 문서: "**`Write`, `NotebookEdit`, or legacy `MultiEdit`**: use `Edit(docs/**)` in place of `Write(docs/**)`." | `tools-reference`, `permissions` |
| H53 | 훅은 하나씩 끌 수 없다. 전부 끄는 설정만 있다 | "There is no way to disable an individual hook while keeping it in the configuration." / `"disableAllHooks": true` | `hooks#disable-or-remove-hooks` |

### 1.2 스킬

| # | 주장 | 원문 인용 | URL |
|---|---|---|---|
| S1 | 스킬 위치 | Personal `~/.claude/skills/<skill-name>/SKILL.md`, Project `.claude/skills/<skill-name>/SKILL.md`, Nested `<subdir>/.claude/skills/...`, Plugin `<plugin>/skills/<skill-name>/SKILL.md`(`/plugin-name:skill-name`), Enterprise(관리 설정 디렉터리) | `skills#choose-where-skills-load` |
| S2 | `.claude/commands/`는 옛 형식이고 아직 동작한다 | "a Markdown file in `.claude/commands/` is the older format and still works. It supports the same frontmatter except `name` and `paths`. ... Prefer a skill for new work" | `skills#choose-where-skills-load` |
| S3 | frontmatter 필드(공식 표 전체) | `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility` | `skills#frontmatter-reference` |
| S4 | 모든 필드는 선택이다. 모르는 필드는 오류 없이 무시된다 | "All fields are optional. Only `description` is recommended so Claude knows when to use the skill. A field name must match the table exactly, hyphens included: Claude Code ignores a field it doesn't recognize without reporting an error." | `skills#frontmatter-reference` |
| S5 | 설명 길이 상한 | "the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing" (`skillListingMaxDescChars`로 조정) | `skills#frontmatter-reference` |
| S6 | 스킬 목록 전체 예산은 컨텍스트 창의 1% | "The budget scales at 1% of the model's context window. When the listing overflows, Claude Code drops descriptions starting with the skills you invoke least" (`skillListingBudgetFraction`) | `skills#skill-descriptions-are-cut-short` |
| S7 | 호출 주체 제어 | 표: (default) 사람·Claude 모두 / "`disable-model-invocation: true` → You can invoke: Yes, Claude can invoke: Not on its own, **Description not in context**" / "`user-invocable: false` → You can invoke: No, Claude can invoke: Yes, Description always in context" | `skills#control-who-invokes-a-skill` |
| S8 | 부작용 있는 절차는 `disable-model-invocation: true` | "Use this for workflows with side effects or that you want to control timing, like `/commit`, `/deploy`, or `/send-slack-message`." | `skills#control-who-invokes-a-skill` |
| S9 | `allowed-tools`는 제한이 아니라 사전 승인이고 그 턴에만 유효하다 | "The `allowed-tools` field grants permission for the listed tools during the turn that invokes the skill ... The grant clears when you send your next message ... It does not restrict which tools are available" / "Workspace trust doesn't gate this field. ... review the `allowed-tools` of skills checked into a repository before you run Claude Code there." | `skills#pre-approve-tools-for-a-skill` |
| S10 | `context: fork`는 대화 기록 없이 서브에이전트에서 돈다 | "Claude Code starts a new subagent of the type set in the `agent` field and gives it the skill content as its prompt. The subagent doesn't see your conversation history" / 기본은 백그라운드, `background: false`로 기다린다 | `skills#run-skills-in-a-subagent` |
| S11 | 본문은 호출 뒤 계속 컨텍스트에 남는다 | "the rendered `SKILL.md` content enters the conversation as a single message and stays there across later turns. ... Claude Code does not re-read the skill file on later turns" / "Keep the body itself concise. Once a skill loads, its content stays in context across turns, so every line is a recurring token cost." | `skills#skill-content-lifecycle`, `skills#types-of-skill-content` |
| S12 | 압축 뒤에는 스킬당 앞 5,000토큰, 합계 25,000토큰만 다시 붙는다 | "Claude Code re-attaches the most recent invocation of each skill after the summary, keeping the first 5,000 tokens of each. Re-attached skills share a combined budget of 25,000 tokens." → "put the most important instructions near the top of `SKILL.md`" | `skills#skill-content-lifecycle` |
| S13 | SKILL.md는 500줄 이하 | "Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files." | `skills#add-supporting-files` |
| S14 | `scripts/`·`references/`·`assets/`는 Agent Skills 규격의 폴더 이름이다 | `scripts/ # Optional: executable code`, `references/ # Optional: documentation`, `assets/ # Optional: templates, resources` / `name`: "Max 64 characters. Lowercase letters, numbers, and hyphens only." / `description`: "Max 1024 characters." / "Instructions (< 5000 tokens recommended)" | `https://agentskills.io/specification` |
| S15 | claude.ai 업로드·Skills API에서는 규격 6개 필드만 된다 | "`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`" 외 필드가 있으면 "packaging or upload fails with a hard error" | `skills#using-skill-frontmatter-outside-claude-code` |
| S16 | 호출 방식 | "You can type `/skill-name` to invoke it directly, and Claude can load it automatically when relevant to your conversation." / "To run a skill directly, put its name at the start of your message." / 권한 규칙 `Skill(name)`, `Skill(name *)` | `skills#control-who-invokes-a-skill`, `skills#restrict-claudes-skill-access` |
| S17 | 평가는 기준선 비교로 한다 | "Seeing a skill trigger tells you Claude found it, not that it did what you intended." / "Collect a few realistic prompts, run each one in a fresh session with the skill available and again with it turned off, and compare the results." (끄는 법: `skillOverrides`의 `"off"`) | `skills#evaluate-and-iterate-on-a-skill` |
| S18 | frontmatter 오류는 `claude plugin validate`로 찾는다 (≥2.1.233) | "run `claude plugin validate` on the skills directory, for example `claude plugin validate .claude/skills`" / "If the frontmatter YAML is malformed, Claude Code loads the skill body with empty metadata, so `/skill-name` still works but Claude can't match against your `description`." | `skills#skill-not-triggering` |
| S19 | 안 쓰는 스킬 찾기 | "Run `/skill-doctor` to see what each of your skills costs and how often it gets used" (≥2.1.252) / `/skills`에서 `t`로 토큰 순 정렬 | `skills#find-unused-skills`, `commands` |
| S20 | 매번 지켜야 하는 규칙은 스킬이 아니라 훅 | "**Claude skipped a rule that must hold every time**: move the rule into a hook." | `skills#claude-stops-following-a-skill` |
| S21 | 스킬 frontmatter의 훅은 호출 뒤 세션 끝까지 유지된다 | "**Skill hooks**: Claude Code registers them when you or Claude invoke the skill and keeps running them for the rest of the session" (`once: true`로 한 번만) | `hooks#hooks-in-skills-and-agents` |

### 1.3 서브에이전트

| # | 주장 | 원문 인용 | URL |
|---|---|---|---|
| A1 | 정의 파일 위치와 우선순위 | 관리 설정(1) > `--agents` CLI 플래그(2) > `.claude/agents/`(3) > `~/.claude/agents/`(4) > 플러그인 `agents/`(5) | `sub-agents#choose-the-subagent-scope` |
| A2 | 필수 필드는 `name`, `description`. 필드 이름은 camelCase | "Only `name` and `description` are required." / "Multi-word field names use camelCase, such as `maxTurns` and `disallowedTools` ... Claude Code ignores a field it doesn't recognize without reporting an error." | `sub-agents#frontmatter-reference` |
| A3 | 지원 필드 | `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `autoCompactWindow`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental` | `sub-agents#frontmatter-reference` |
| A4 | 본문이 시스템 프롬프트가 된다 | "The body becomes the system prompt that guides the subagent's behavior. Subagents receive only this system prompt plus basic environment details like the working directory, not the Claude Code system prompt." | `sub-agents#write-subagent-files` |
| A5 | 시작할 때 대화 기록을 못 본다 | "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read." | `sub-agents#what-loads-at-startup` |
| A6 | 내장 Explore·Plan은 CLAUDE.md 없이 시작한다 | "Explore and Plan start without your CLAUDE.md files and the git status snapshot to keep research fast and inexpensive." | `sub-agents#built-in-subagents` |
| A7 | 모델 결정 순서 | "1. The per-invocation `model` parameter 2. The subagent definition's `model` frontmatter ... 3. The `CLAUDE_CODE_SUBAGENT_MODEL` environment variable ... 4. The main conversation's model" | `sub-agents#choose-a-model` |
| A8 | 기본으로 백그라운드에서 돈다. 중첩 3단, 동시 20개 | "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." / "up to three layers below the main conversation" / "when 20 subagents are running in a session, spawning another with the Agent tool fails" | `sub-agents` |
| A9 | 플러그인 서브에이전트는 `hooks`·`mcpServers`·`permissionMode`를 못 쓴다 | "For security reasons, plugin subagents don't support the `hooks`, `mcpServers`, or `permissionMode` frontmatter fields." | `sub-agents#choose-the-subagent-scope` |
| A10 | 서브에이전트는 토큰을 더 쓴다. 답이 더 좋아지지는 않는다 | "What they cost you is mostly tokens, since every subagent sends its own requests" / "You get parallelism or a fresh pair of eyes out of it, but not a smarter answer." / "Set `model: haiku` in a subagent's definition if its work is simple" | `best-practices#know-what-subagents-cost` |
| A11 | 읽기 전용 리뷰어는 `tools`로 강제한다 | "Give a custom subagent in `.claude/agents/` only `tools: Read, Grep, Glob`. Now it's a reviewer that can't edit anything, and that limit is enforced by Claude Code rather than requested in a prompt." | `best-practices#know-what-subagents-cost` |

### 1.4 플러그인

| # | 주장 | 원문 인용 | URL |
|---|---|---|---|
| P1 | 플러그인은 묶음 단위다. 여러 저장소·팀에 배포할 때 쓴다 | "A plugin bundles skills, hooks, subagents, and MCP servers into a single installable unit." / "Keep that standalone setup while it serves one project or only you. Make a plugin when you want to share the setup with teammates, install it in several projects, or publish versioned releases." | `features-overview`, `plugins/create#decide-when-to-use-a-plugin` |
| P2 | 구조 | `.claude-plugin/plugin.json`(매니페스트), `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`. "Only `plugin.json` goes inside `.claude-plugin/`. Components saved there don't load." / "`name` is the only required key." | `plugins/create#plugin-layout`, `plugins/manifest-reference#fields` |
| P3 | 설치 명령 | 세션: `/plugin install <plugin>@<marketplace>` (상세 창을 열어 범위를 고른다), `/plugin marketplace add <source>`. 셸: `claude plugin marketplace add <source>`, `claude plugin install <plugin>@<marketplace> [--scope project\|local]`. 한 번에: `claude plugin install <plugin> --marketplace <source>`(≥2.1.292) | `plugins/install` |
| P4 | 설치 범위 | user(`~/.claude/settings.json`의 `enabledPlugins`), project(`.claude/settings.json`, 커밋), local(`.claude/settings.local.json`). "Committing that entry turns the plugin on for your collaborators but doesn't download it to their machines." | `plugins/install#choose-an-install-scope` |
| P5 | 설치 없이 한 세션만 로드 | `claude --plugin-dir ./my-first-plugin` / "The plugin loads only in sessions you start with `--plugin-dir`." | `plugins/create` |
| P6 | 플러그인 스킬·에이전트는 이름에 플러그인 접두사가 붙는다 | "plugin skills and agents get the plugin name as a prefix, such as `/my-plugin:hello`, so two plugins can each provide a `hello` skill without colliding." | `plugins/create#decide-when-to-use-a-plugin` |
| P7 | 플러그인 훅은 내 권한으로, 샌드박스 밖에서 돈다 | "command hooks and monitors are shell commands that run with your full user permissions. Claude Code runs hooks, monitors, MCP servers, LSP servers, and the processes a mod starts outside the sandbox." | `plugins/security#understand-what-a-plugin-can-do` |
| P8 | 설치 전 검토 절차 | "run `claude plugin marketplace list` to print the source each marketplace was added from" / "The **Will install** section shows that a hook exists but not what it runs, so read these files in the plugin's directory: `hooks/hooks.json` ... `.mcp.json` ... `bin/`" / "run `claude --plugin-dir <plugin directory> plugin details <plugin name>` in your shell ... The command reads the plugin's files without starting a session" | `plugins/security#review-a-plugin-before-you-install` |
| P9 | 자동 업데이트되면 검토한 파일이 바뀔 수 있다 | "when auto-update is on for the marketplace you installed a plugin from, Claude Code updates that plugin in the background, so the files you reviewed can change on disk." | `plugins/security` |
| P10 | 컨텍스트 비용 확인 | "`claude plugin details <name>` ... The `Always-on` line is the number of tokens the plugin adds to every session where it's enabled" | `plugins/install`, `plugins/measure` |
| P11 | 검증 명령과 종료 코드 | `claude plugin validate <path> [--strict] [--json]`: 0 = "Validation passed", 1 = "Validation failed", 2 = "Unexpected error during validation" | `plugins/cli-reference#plugin-validate` |
| P12 | 플러그인 설치·제거는 캐시 영향이 구성요소마다 다르다 | "Claude Code never invalidates the cache for a plugin's skills, commands, agents, hooks, monitors, or themes." (MCP 서버가 있으면 MCP 규칙을 따른다) | `prompt-caching#enabling-or-disabling-a-plugin` |
| P13 | Langfuse 플러그인 설치 명령과 요건(플러그인 README, 제3자 출처) | `claude plugin marketplace add langfuse/Claude-Observability-Plugin` / `claude plugin install langfuse-observability@langfuse-observability` / "Restart Claude Code after installing, so that it loads the hook." / "The plugin needs uv on `PATH`." / "Only `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are required. Without `LANGFUSE_BASE_URL` the plugin uses `https://cloud.langfuse.com` (EU region)." / "The secret key is held in your OS keychain, not in a file." / "Automatic updates are off for marketplaces outside Anthropic's, so you run the update yourself." / 로그: `~/.claude/state/langfuse_hook.log` | `https://github.com/langfuse/Claude-Observability-Plugin` (README) |

### 1.5 관측 (OpenTelemetry·내장 명령)

| # | 주장 | 원문 인용 | URL |
|---|---|---|---|
| O1 | 내장 OTel 내보내기가 있다 | "Claude Code exports metrics as time series data via the standard metrics protocol, events via the logs/events protocol, and optionally distributed traces" | `monitoring-usage` |
| O2 | 켜는 환경 변수 | `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER`(`otlp`, `prometheus`, `console`, `none`), `OTEL_LOGS_EXPORTER`(`otlp`, `console`, `none`), `OTEL_EXPORTER_OTLP_PROTOCOL`(`grpc`, `http/json`, `http/protobuf`; "Claude Code has no default protocol"), `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL`(기본 60000ms), `OTEL_LOGS_EXPORT_INTERVAL`(기본 5000ms) | `monitoring-usage#quick-start` |
| O3 | 지표 8개 | `claude_code.session.count`, `claude_code.lines_of_code.count`, `claude_code.pull_request.count`, `claude_code.commit.count`, `claude_code.cost.usage`(USD), `claude_code.token.usage`(tokens; `type` = input/output/cacheRead/cacheCreation), `claude_code.code_edit_tool.decision`, `claude_code.active_time.total` | `monitoring-usage#metrics` |
| O4 | 이벤트(로그) | `claude_code.user_prompt`, `claude_code.assistant_response`, `claude_code.tool_result`(`tool_name`, `success`, `duration_ms`, `tool_use_id` …), `claude_code.api_request`(`cost_usd`, `duration_ms`, 토큰), `api_error`, `tool_decision`, `skill_activated`(`invocation_trigger`: "user-slash" / "claude-proactive" / "nested-skill"), `hook_execution_start`/`hook_execution_complete`(`num_blocking`, `num_non_blocking_error`, `total_duration_ms`), `compaction`(`pre_tokens`, `post_tokens`), subagent completed 등 | `monitoring-usage#events` |
| O5 | 한 프롬프트의 이벤트는 `prompt.id`로 묶는다 | "The `prompt.id` attribute lets you tie all of those events back to the single prompt that triggered them." (훅 입력의 `prompt_id`와 같다) | `monitoring-usage#event-correlation-attributes` |
| O6 | 기본값은 내용 비수집이다 | "User prompt content is not collected by default. Only prompt length is recorded. To include prompt content, set `OTEL_LOG_USER_PROMPTS=1`." / "Tool input arguments and parameters are not logged by default. To include them, set `OTEL_LOG_TOOL_DETAILS=1`." / "By default, raw file contents and code snippets aren't included in metrics or events." | `monitoring-usage#security-and-privacy` |
| O7 | 저장소 설정으로는 OTel을 켤 수 없다 | "Claude Code ignores the OpenTelemetry exporter variables in a repository's `.claude/settings.json` and `.claude/settings.local.json` ... Set them in managed settings, or have each developer set them in their shell or `~/.claude/settings.json`." | `monitoring-usage#administrator-configuration` |
| O8 | 동작 확인 방법 | "check your backend for the `claude_code.session.count` metric, which Claude Code emits when a session starts. To verify a logs-only setup, submit a prompt and check for the `claude_code.user_prompt` event." / "start Claude Code with `claude --debug-file <path>` ... `[3P telemetry]` errors" | `monitoring-usage#quick-start` |
| O9 | 트레이스는 베타다 | "Tracing is off by default. To enable it, set both `CLAUDE_CODE_ENABLE_TELEMETRY=1` and `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`, then set `OTEL_TRACES_EXPORTER`" (스팬: `claude_code.interaction` > `llm_request`, `tool`, `hook`) | `monitoring-usage#traces-beta` |
| O10 | 설치 없이 보는 내장 기록: `/usage`(`/cost`·`/stats`는 별칭), `/insights` | "`/cost` → Alias for `/usage`" / "`/usage` → Show session cost, plan usage limits, and activity stats." / "Run `/insights` for a report on how you work ... It analyzes your recent sessions on this machine and writes an HTML report covering what you work on, friction points such as misunderstood requests or buggy code, and suggestions" (`~/.claude/usage-data/report.html`, 한 번에 최대 200세션, 분석 토큰은 내 사용량에서 나간다) | `commands`, `costs#analyze-your-usage-patterns` |
| O11 | `/usage`의 달러 값은 추정이다 | "Claude Code computes the dollar figure locally from token counts at list price ... The figure is an estimate" | `costs#using-the-usage-command` |

### 1.6 비용·컨텍스트·캐시·상태줄

| # | 주장 | 원문 인용 | URL |
|---|---|---|---|
| C1 | 명령 존재 여부 | `/usage`(별칭 `/cost`, `/stats`), `/context [all]`, `/compact [instructions]`, `/clear [name]`(별칭 `/reset`, `/new`), `/rewind`(별칭 `/checkpoint`, `/undo`), `/goal [condition\|clear]`, `/autocompact [auto\|<tokens>]`(≥2.1.221), `/plan [description]`, `/btw`, `/recap`, `/effort`, `/model`, `/insights`, `/doctor`, `/hooks`, `/skills`, `/skill-doctor`, `/statusline`, `/output-style` 모두 명령 표에 있다. `/ultraplan`은 "Removed". | `commands` |
| C2 | 캐시는 접두부 정확 일치다 | "The match is exact, so a change anywhere in the prefix recomputes everything after it. There is no per-file or per-segment caching." 층: System prompt(핵심 지침, 도구 정의) → Project context(CLAUDE.md, auto memory, unscoped rules) → Conversation | `prompt-caching#how-the-cache-is-organized` |
| C3 | 캐시를 깨는 행동 | "Switching models", "Changing effort level", "Turning on fast mode", "Connecting or removing an MCP server", "Enabling or disabling a plugin", "Denying an entire tool", "Compacting the conversation", "Accumulating many images", "Upgrading Claude Code" | `prompt-caching#actions-that-invalidate-the-cache` |
| C4 | 캐시를 유지하는 행동 | "Editing files in your repository", "Editing CLAUDE.md mid-session"(단 "the edit also doesn't apply ... The new content loads on the next `/clear`, `/compact`, or restart"), "Changing permission mode", "Changing output style", "Invoking skills and commands", "Running `/recap`", "Rewinding the conversation", "Spawning a subagent" | `prompt-caching#actions-that-keep-the-cache` |
| C5 | 모델·추론 강도는 세션 처음에 정한다 | "Pick your model and effort level at the top of a session, then save `/compact` for natural breaks between tasks. The fewer changes you make mid-task, the higher your cache hit rate." | `prompt-caching` |
| C6 | 스킬·명령의 `model` 지정도 그 턴에는 모델 전환이다 | "When a skill or command's frontmatter names a `model` other than the session's current model, that turn is also a model switch: the next request reads the entire conversation history with no cache hits." | `prompt-caching#switching-models` |
| C7 | 캐시 수명 | 메인 대화: 구독(플랜 포함 사용량 안) "One hour", 사용 크레딧·API 키·클라우드 "Five minutes". 그 밖(서브에이전트, 압축 등): "Five minutes". 직접 지정: `promptCacheTtl`/`CLAUDE_CODE_PROMPT_CACHE_TTL`, `subagentPromptCacheTtl`(≥2.1.242) | `prompt-caching#cache-lifetime` |
| C8 | 캐시 범위는 사실상 머신+디렉터리 | "In Claude Code, the cache is effectively scoped to one machine and directory." | `prompt-caching#cache-scope` |
| C9 | `/compact`는 그 자체가 큰 요청이다. 캐시가 식으면 가장 비싸다 | "`/compact` reads the conversation it summarizes, so compacting a large context is itself a large request. When you want a fresh start instead of continuity, `/clear` costs nothing" / "This is why `/compact` costs the most when you resume an old session." | `costs#why-usage-climbs-in-a-long-session`, `prompt-caching#compacting-the-conversation` |
| C10 | 버릴 길이면 압축보다 되감기 | "If you've gone down a path you want to abandon entirely, `/rewind` to an earlier turn instead. Rewinding truncates back to a prefix that is already cached, rather than building a new one as compaction does." | `prompt-caching#compacting-the-conversation` |
| C11 | 압축 지시 방법 | "`/compact Focus on code samples and API usage` tells Claude what to preserve during summarization." / CLAUDE.md의 `# Compact instructions` 구역 / PreCompact 훅의 stdout("Claude Code uses its stdout as instructions for the compaction summary") | `costs#manage-context-proactively`, `hooks#precompact-output` |
| C12 | 압축 뒤 살아남는 것 | "Project-root CLAUDE.md and unscoped rules → Re-injected from disk" / "Rules with `paths:` frontmatter → Claude Code reloads them on demand" / "Files Claude read or edited → Claude Code re-reads up to five, most recently modified first" / "Invoked skill bodies → Re-injected, capped at 5,000 tokens per skill and 25,000 tokens total" / "Context that hooks added earlier → Summarized with the rest of the conversation" | `context-window#what-survives-compaction` |
| C13 | 부분 요약도 된다 | `/rewind` 메뉴의 "**Summarize from here**", "**Summarize up to here**" | `checkpointing#rewind-and-summarize` |
| C14 | MCP 도구 정의는 기본으로 지연 로드된다 | "Tool search is enabled by default: MCP tools are deferred and discovered on demand." / "Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window." / "Prefer CLI tools when available: Tools like `gh`, `aws`, `gcloud`, and `sentry-cli` are still more context-efficient than MCP servers" | `mcp#scale-with-mcp-tool-search`, `costs#reduce-mcp-server-overhead` |
| C15 | 기능별 컨텍스트 비용 | CLAUDE.md "Every request" / Skills "Low (descriptions every request)" / MCP servers "Low until a tool is used" / Subagents "Isolated from main session" / Hooks "Zero, unless hook returns additional context" | `features-overview#context-cost-by-feature` |
| C16 | 공식 입장: 컨텍스트 창 관리 자체는 더 이상 핵심 제약이 아니다. 비용 때문에 `/clear`는 여전히 유효하다 | "The context window is your main constraint, manage it aggressively → Most current models have a 1M-token window and compaction happens on its own, so running out is rare. `/clear` between tasks is still worth doing, because a focused context gets you better answers and costs less." / "Use subagents to protect your context window → Running out of context is rarely the problem anymore. Subagents are still great for parallel work, keeping noisy output out of your way, and independent review, but each of those costs extra tokens." | `best-practices#what-you-can-stop-doing` |
| C17 | 비용은 컨텍스트 크기에 비례한다 | "Token costs scale with context size" / "Every request sends the whole conversation, so a session that's collected three unrelated tasks re-reads all three on every turn of the fourth. That's discounted while the cache is warm and full price once it expires." | `costs#reduce-token-usage`, `best-practices#keep-cost-and-context-down` |
| C18 | 추론 강도 기본값과 쓰는 법 | "Claude Fable 5.2, Opus 5.5, Sonnet 5.5, and Haiku 5.5 default to `medium`" / "Save `max` for a hard problem you want Claude to work through without you ... On ordinary tasks it tends to overthink" / "Thinking tokens are billed as output tokens" | `best-practices#change-the-model-and-effort`, `costs#adjust-extended-thinking` |
| C19 | 출력 줄이기: 내장 Concise 출력 스타일 | "Concise → Responses lead with the result and leave out preamble, narration, and recaps" (`/output-style concise`, ≥2.1.269) | `output-styles`, `commands` |
| C20 | 상태줄 입력 JSON의 컨텍스트 필드 | `context_window.used_percentage`, `remaining_percentage`, `context_window_size`("200000 by default, or 1000000 for models with extended context"), `total_input_tokens`, `current_usage.{input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}`. "The `used_percentage` field is calculated from input tokens only" / null 가능: "`context_window.used_percentage` ... may be `null` early in the session" | `statusline#available-data` |
| C21 | 상태줄 입력 JSON의 캐시 필드 (≥2.1.251) | `prompt_cache.warm`("Whether the cached prefix is still within its TTL"), `hit_ratio`("Cache read tokens as a fraction of all input tokens this session, from 0 to 1"), `misses`, `expected_rebuilds`, `ttl`(`"5m"`/`"1h"`), `expires_at`, `last_miss_cause.causes`(예: `tools_changed`, `system_prompt_changed`, `ttl_expired_5m`, `likely_server_side`; ≥2.1.260), `recache_tokens_if_cold`. "Claude Code doesn't count subagent requests in these statistics." | `statusline#prompt-cache-fields` |
| C22 | 상태줄 입력 JSON의 비용·한도 필드 | `cost.total_cost_usd`("Estimated session cost in USD, computed client-side at list price ... May differ from your actual bill."), `cost.total_duration_ms`, `rate_limits.five_hour.used_percentage`, `rate_limits.seven_day.used_percentage`(구독자만), `model.display_name`, `effort.level` | `statusline#available-data` |
| C23 | 상태줄 설정과 특성 | `"statusLine": {"type": "command", "command": "~/.claude/statusline.sh"}`(+`padding`, `refreshInterval`) / "The status line runs locally and does not consume API tokens." / `/statusline <설명>`으로 생성 가능 | `statusline` |
| C24 | 같은 캐시 통계는 `/usage`에도 나온다 | `Prompt cache (main):   14 requests · 91% of input tokens from cache · 2 misses (...) · warm (1h TTL, last activity 40s ago)` | `costs#prompt-cache-statistics` |
| C25 | 유휴 압축 | "On the one-hour cache, a session past about 200K tokens that sits idle is compacted shortly before the cache expires" (`idleCompaction: false`로 끔, ≥2.1.290) | `best-practices#keep-cost-and-context-down`, `prompt-caching` |
| C26 | 체크포인트는 Bash·서브에이전트 수정을 다 되돌리지 못한다 | "A file that only Bash commands changed isn't tracked and stays as it is. To revert it, use version control, such as Git." / "**Any other subagent**: rewinding restores only the files Claude had already edited in your conversation." | `checkpointing#limitations` |

### 1.7 작업 루틴 (계획·목표·검증)

| # | 주장 | 원문 인용 | URL |
|---|---|---|---|
| W1 | 계획 모드 진입 | "Enter plan mode by pressing `Shift+Tab` or prefixing a single prompt with `/plan`." / `claude --permission-mode plan` / 기본값으로: `.claude/settings.json`의 `defaultMode: plan` | `permission-modes#analyze-before-you-edit-with-plan-mode` |
| W2 | 계획 모드는 승인 전까지 수정을 막는다(예외 있음) | "Claude reads files, runs shell commands to explore, and writes a plan, but does not edit your source. Except in interactive terminal sessions with bypass permissions available, edits stay blocked until you approve the plan." | 같은 곳 |
| W3 | 승인 선택지 | "Yes, and use auto mode" / "Yes, manually approve edits" / "No, keep planning". "Press `Ctrl+G` to open the proposed plan in your default text editor and edit it directly" | `permission-modes#review-and-approve-a-plan` |
| W4 | `/goal`은 존재한다. 완료 조건을 걸어 두는 명령이다 | "The `/goal` command sets a completion condition and Claude keeps working toward it without you prompting each step. After each turn, a model checks whether the condition holds." / "`/goal` is a wrapper around a session-scoped prompt-based Stop hook." | `goal` |
| W5 | 평가자는 대화에 드러난 것만 본다 | "The evaluator judges your condition against what Claude has surfaced in the conversation. It doesn't run commands or read files independently, so write the condition as something Claude's own output can demonstrate." | `goal#write-an-effective-condition` |
| W6 | 좋은 조건의 모양과 상한 | "**One measurable end state** ... **A stated check** ... **Constraints that matter**" / "The condition can be up to 4,000 characters." / "include a turn or time clause in the condition, such as `or stop after 20 turns`" | 같은 곳 |
| W7 | `/goal`은 권한 모드를 바꾸지 않는다 | "A goal doesn't change your permission mode. To let goal turns run unattended, run `/goal` in auto mode." | `goal#set-a-goal` |
| W8 | 검증: 통과/실패가 나오는 검사를 준다 | "Give Claude something it can run that comes back pass or fail. Once it has that, it can keep going on its own and you don't have to watch." / "Whichever option you use, ask Claude for *evidence*: the command it ran and its output, or the screenshot. \"All tests pass\" on its own tells you very little" | `best-practices#give-claude-a-check-to-run` |
| W9 | 검증 강도의 네 단계 | 프롬프트("run the auth tests after, and keep going until they pass") → `/goal` → `Stop` 훅("This one is enforced by Claude Code (the harness)") → 코드를 쓰지 않은 리뷰어("`/code-review` reviews the diff in a fresh subagent that never saw your conversation") | 같은 곳 |
| W10 | 스펙 대비 리뷰 프롬프트와 주의점 | "use a subagent to review the rate limiter diff against SPEC.md, check every requirement is implemented and the listed edge cases have tests, report gaps that affect correctness and skip style" / "A reviewer that's asked to find problems will always find *something*." | `best-practices#review-against-your-spec` |
| W11 | 개입 요령 | "Watch the first minute, press `Esc` the moment Claude drifts, and after two failed corrections run `/clear` and write a better prompt instead of a third." | `best-practices#steer-the-session` |
| W12 | 결정적/비결정적 구분 | "Non-deterministic: you write the instruction, and Claude (the model) reads it. This can be your prompt, `CLAUDE.md`, or a skill. ... Deterministic: you configure the instruction, and Claude Code (the harness) *has* to execute this. This can be a hook, a deny rule, or a managed setting." | `best-practices#deterministic-and-non-deterministic-instructions` |
| W13 | 강제 규칙은 적게 유지한다 | "Whatever the scope, keep the enforced set small. Every hook and deny rule will occasionally fire when it shouldn't, and someone has to maintain each one." / "a hook is for a rule with *zero* exceptions" | `best-practices#choose-who-a-rule-applies-to` |
| W14 | 승격 순서(공식 표) | "Claude gets a convention or command wrong twice → Add it to CLAUDE.md" / "You paste the same playbook or multi-step procedure into chat for the third time → Capture it as a skill" / "You want something to happen every time without asking → Write a hook" / "A second repository needs the same setup → Package it as a plugin" | `features-overview#build-your-setup-over-time` |
| W15 | 무인 실행 전 다섯 질문 | "1. Does it know what done looks like? ... 2. Can it check its own work? ... 3. What's it allowed to touch? ... 4. What stops it? `--max-turns`, `--max-budget-usd`, a spend limit. 5. Where does the result go, and who signs off?" | `best-practices#let-claude-run-without-you` |
| W16 | 설정 점검 명령 | "For read-only installation diagnostics without starting a session, run `claude doctor` in your terminal" / `/doctor`(세션 안, 고쳐 주기까지) / `--safe-mode`("Start with all customizations disabled to troubleshoot a broken configuration") / "run `/context` for a live breakdown by category" | `skills#check-your-setup-with-doctor`, `cli-reference`, `context-window` |
| W17 | 앱을 실제로 띄워 확인하는 내장 스킬 | "`/verify` → Build and run your app to confirm a code change does what it should, without falling back to tests or type checks" | `skills#run-and-verify-your-app` |
| W18 | CLAUDE.md는 유저 메시지로 전달된다(A0의 서술은 맞다) | "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself." | `memory` |

### 1.8 로컬에서 직접 확인한 것 (CLI 2.1.322, 모델 호출 없음)

| # | 확인 내용 | 방법·결과 |
|---|---|---|
| L1 | `claude doctor`는 현재 폴더의 설정 파일을 읽어 훅 설정 오류를 잡는다 | 일부러 틀린 설정을 넣고 실행 → `Invalid settings` 아래에 `hooks.NoSuchEvent: Unknown hook event "NoSuchEvent" was ignored. Valid events: ...`, `Unknown hook type "commnd" ... Valid types: command, prompt, agent, http, mcp_tool`, `onFailure: Invalid value. Expected one of: "continue", "block"`, `timeout: Expected number, but received string` 출력. |
| L2 | 잘못된 PreToolUse 훅 항목이 있으면 그 설정 파일 전체가 적용되지 않는다고 doctor가 경고한다 | 출력 원문: "a PreToolUse/PermissionRequest hook that cannot be loaded may be what guards the permissions declared beside it, so nothing it sits in is applied until the entry is fixed or removed." |
| L3 | 현재 `settings.example.json`은 스키마상 유효하다. 4절의 수정안도 유효하다 | 두 파일 모두 `claude doctor`에서 `Invalid settings` 없음. `args`, `timeout`, `onFailure`, `if`, `statusMessage`, `statusLine.refreshInterval` 키가 2.1.322에서 받아들여진다. |
| L4 | doctor는 매처 값이 실제 도구 이름인지는 검사하지 않는다 | `MultiEdit`가 들어 있어도 경고 없음. |
| L5 | `claude plugin validate <skills 폴더>`는 모델 호출 없이 frontmatter를 검사한다 | `claude plugin validate kit/.claude/skills` → `√ Validation passed` |
| L6 | 현재 `plan_gate.py`는 일부 깨진 입력에서 exit 1로 끝난다(= 통과) | stdin `[]`, `"x"`, `{"tool_input":"x"}`, `{"tool_input":{"file_path":123}}` → `AttributeError`/`TypeError`, exit 1. H16·H17에 따라 비차단 오류다. |
| L7 | 현재 `plan_gate.py`는 Claude가 계획 파일에 `status: approved`를 직접 쓰는 것을 허용한다 | `design/plans/p1.md`에 `content: "status: approved"`인 Write 입력 → exit 0. 그 뒤 `.py` 수정도 exit 0. |
| L8 | 현재 `test_after_edit.py`는 `[]` 입력에서 exit 1, `.claude/hooks/*.py`를 고쳐도 짝 테스트 없음으로 exit 2 | 직접 실행으로 확인. |

---

## 2. 현재 가이드·훅 예시에서 틀리거나 부정확한 곳과 수정안

심각도: **높음** = 사실과 다르거나 안전장치가 뚫린다 / **중간** = 낡았거나 조건이 빠졌다 / **낮음** = 표현 보강.

### 2.1 GUIDE.md

| 위치 | 현재 서술 | 문제 | 수정안 | 근거 |
|---|---|---|---|---|
| A6 함정 1 (높음) | "명시적 차단 신호(exit 2 또는 JSON 거부)만 막는다. **exit 1, 스크립트 오류, 시간 초과는 조용히 통과한다.**" | 방향은 맞다. 빠진 것: ① 통과는 하지만 대화 기록에 `<hook name> hook error` 알림이 뜬다("조용히"가 아니다). ② `onFailure: "block"`(≥2.1.295)을 주면 실패·시간 초과도 막는다. ③ 경로 오타로 스크립트가 시작조차 못 해도 통과한다. | "차단은 exit 2나 JSON 거부로만 된다. exit 1, 스크립트 오류, 시간 초과, 경로 오타는 `hook error` 알림만 남기고 통과한다. 꼭 막아야 하는 훅에는 설정에 `"onFailure": "block"`을 넣어 실패해도 막히게 한다." | H16, H17, H32, H33 |
| A6 함정 4 (중간) | "훅은 권한을 조일 수는 있어도 풀 수는 없다." | 부정확하다. 훅은 `permissionDecision: "allow"`로 **권한 확인 창을 건너뛰게** 할 수 있다. 못 하는 것은 deny·ask 규칙을 넘는 것이다. | "훅의 거부(deny)는 모든 권한 모드에서 통한다. 훅의 허용(allow)은 확인 창을 건너뛸 뿐 권한 설정의 deny·ask 규칙을 넘지 못한다." | H24, H37 |
| A6 할 일 (중간) | "세션 종료에는 중요한 정리를 맡기지 않는다. 정상 종료가 드물다." | "정상 종료가 드물다"는 공식 근거가 없다. 문서상 근거는 SessionEnd가 막지 못하고 기본 1.5초 안에 끝나야 한다는 것이다. | "세션 종료(SessionEnd)에는 중요한 정리를 맡기지 않는다. 막을 수 없고 기본 제한 시간이 1.5초다." | H49 |
| A6 할 일 (중간) | "입력 제출(UserPromptSubmit)은 … 자꾸 잊는 지침을 붙이기 좋다." | 공식 권고와 다르다. 변하지 않는 지침은 CLAUDE.md에 두라고 하고, 붙이는 글은 사실 진술로 쓰라고 한다. 또 이 훅은 내 프롬프트 외에 예약 작업·백그라운드 서브에이전트 보고·세션 간 메시지에도 돌고, 붙인 글은 대화 기록에 쌓인다. | "입력 제출(UserPromptSubmit)은 모델에 가기 전이다. **그때그때 달라지는 상태**(현재 브랜치, 승인된 계획 유무 등)를 붙이기 좋다. 변하지 않는 지침은 CLAUDE.md에 둔다. 붙이는 글은 명령문이 아니라 사실 진술로 짧게 쓴다(요청마다 쌓인다)." | H13, H29, H30 |
| A6 할 일 (중간) | "끝내기 전(Stop)은 확인한다." | 조건이 빠졌다. Stop은 작업이 끝날 때가 아니라 응답이 끝날 때마다 돌고, 사용자 중단에는 돌지 않는다. 무한 반복을 막으려면 `stop_hook_active`를 봐야 하고 8회 상한이 있다. | "끝내기 전(Stop)은 확인한다. 응답이 끝날 때마다 돈다(사용자가 중단하면 안 돈다). 입력의 `stop_hook_active`가 true면 다시 막지 않는다. 8번 연속 막으면 하네스가 턴을 끝낸다." | H14, H15 |
| A6 함정 6 (낮음) | "끝내기 전 검사의 두 번째 통과는 재검증이 아니다." | 뜻이 불분명하다. | "`stop_hook_active`를 보고 물러나는 Stop 훅은 두 번째 종료 때 검사를 하지 않는다. 두 번째에 통과했다고 고쳐진 것이 아니다." | H14 |
| A6 함정 (높음, 누락) | — | 훅이 서브에이전트에도 걸린다는 것, `@` 파일 첨부는 PreToolUse(Read)를 거치지 않는다는 것, 같은 이벤트의 훅은 병렬로 돈다는 것, `-p` 실행은 신뢰 확인 없이 저장소 훅을 돌린다는 것이 없다. | 함정 목록에 네 줄 추가(3절 A6 참조). | H34, H36, H38, H45 |
| A6 "실행 후(PostToolUse)" (낮음) | "실행 후(PostToolUse)는 고치게 한다." | 성공한 호출에만 돈다. 실패한 호출은 `PostToolUseFailure`다. 병렬 도구 호출이면 훅도 동시에 여러 번 돈다. | 한 줄 보강. 무거운 검사는 `PostToolBatch`(묶음당 1회)나 Stop으로 옮기는 선택지를 적는다. | H12, H39 |
| A6 확인 (낮음) | "훅 스크립트에 입력을 직접 넣어 본다." | 설정 파일 자체의 검증 방법이 없다. | `claude doctor`(설정 스키마), `/hooks`(등록 확인), `claude --debug-file`(실행 기록)을 추가. | L1, H47, H48 |
| A4 (중간) | Langfuse 플러그인만 예로 든다. "어느 폴더에서 켜든 기록이 쌓인다" | ① 설치 없이 쓰는 내장 수단(`/usage`, `/insights`, OTel)이 빠졌다. ② 플러그인 요건(uv)과 `/plugin configure`가 빠졌다. ③ "어느 폴더에서 켜든"은 user 범위로 설치했을 때만 참이다. ④ OTel 환경 변수는 저장소 설정에서 무시된다. | 3절 A4 참조. Langfuse 문단에 "uv가 PATH에 있어야 한다", "키는 `/plugin configure langfuse-observability@langfuse-observability`로 넣는다(비밀 키는 OS 키체인에 저장)", "user 범위로 설치한다"를 추가. | P13, P4, O1~O10 |
| A4 (낮음, 미확인) | "기록은 응답이 끝날 때 전송된다." "리전에 맞는 주소를 넣지 않으면 인증 오류가 난다." | 플러그인 README에는 전송 시점이 없다. README는 "`LANGFUSE_BASE_URL`이 없으면 EU 리전"이라고만 적는다. | 전송 시점 문장은 "바로 안 보이면 `~/.claude/state/langfuse_hook.log`의 최근 줄을 본다"로 바꾼다. 리전 문장은 "기본 주소는 EU 리전이다. 다른 리전·셀프호스팅이면 `LANGFUSE_BASE_URL`을 넣는다"로 바꾼다. | P13 |
| A5 할 일 (중간) | "설명(description)은 … 짧게 쓴다. 이 한 줄로 불릴지가 정해진다." | 맞다. 수치가 없다. | "설명과 `when_to_use`를 합쳐 1,536자에서 잘리므로 핵심 용도를 맨 앞에 둔다. 스킬이 많으면 목록 예산(컨텍스트 창의 1%)을 넘겨 설명이 통째로 빠진다." | S5, S6 |
| A5 할 일 (중간) | "부작용이 있거나 순서가 중요한 절차는 … (`disable-model-invocation: true`)" | 맞다. 빠진 효과: 설명이 컨텍스트에서 빠져 비용이 0이 된다. 반대 필드 `user-invocable: false`와 `allowed-tools`의 뜻(제한이 아니라 사전 승인)도 없다. | 3절 A5 참조. | S7, S9 |
| A5 확인 (중간) | "불려야 하는 요청 3개와 불리면 안 되는 요청 3개를 넣어 본다." | 공식 방법은 "불렸는가"와 "결과가 나아졌는가"를 따로 재고, **새 세션**에서 스킬을 켠 것과 끈 것을 비교하는 것이다. | 6건 시험은 유지하되 "새 세션에서", "스킬을 끈(`skillOverrides: off`) 결과와 비교"를 추가. frontmatter는 `claude plugin validate .claude/skills`로 먼저 검사. | S17, S18 |
| A5 할 일 (낮음) | "본문은 XML 태그로 구역을 나누고 핵심만 둔다." | XML 태그는 공식 요구가 아니다(금지도 아니다). 공식 수치는 500줄 이하, 압축 뒤 앞 5,000토큰만 남는다는 것이다. | "본문은 500줄 이하로, 가장 중요한 지시를 맨 위에 둔다(압축 뒤에는 스킬당 앞 5,000토큰만 남는다)."를 추가. XML 태그는 이 저장소의 관례로 남겨도 된다. | S12, S13 |
| A7 4번 (중간) | "개인화 버전을 설치하면 원본은 지운다. 둘 다 있으면 충돌한다." | 플러그인 스킬·에이전트는 접두사가 붙어 이름은 충돌하지 않는다. 실제 문제는 **훅이 둘 다 돈다**(훅은 합쳐진다)는 것과 설명이 두 벌 컨텍스트에 실린다는 것이다. | "둘 다 켜 두면 훅이 두 번 돌고 스킬 설명이 두 벌 실린다. 원본은 `claude plugin uninstall <이름>@<마켓>`로 지운다." | P6, H38, P10 |
| A7 1·2번 (중간) | "설치 전에 Claude에게 … 분석시킨다" / "설정 폴더를 지우면 되는 환경" | 모델에게 맡기지 않고도 볼 수 있는 결정적 수단이 있다. 설치하지 않고 한 세션만 로드하는 방법도 있다. | 3절 A7 참조(`claude plugin marketplace list`, `claude --plugin-dir <폴더> plugin details <이름>`, `hooks/hooks.json`·`.mcp.json`·`bin/` 직접 읽기, `claude --plugin-dir`로 시험). | P5, P8 |
| A9 "컨텍스트 사용률" (중간) | "60~65%에서 경고하고, 80%를 넘으면 요청을 보내기 전에 압축부터 한다." | 공식 문서에 없는 수치다. 공식 입장은 "창이 차는 일은 드물다, 자동 압축이 있다"이고, 압축은 그 자체가 큰 요청이라 캐시가 식었을 때 가장 비싸다. 1M 창에서는 같은 %가 전혀 다른 토큰 수다. | 수치는 "내 기준값"임을 밝히고, 판단 기준을 바꾼다: "작업이 바뀌면 `/clear`, 같은 작업을 이어가면 자연스러운 끊김에서 `/compact <남길 것>`, 버릴 길이면 `/rewind`. 자동 압축 시점은 `/autocompact`로 조정한다. 압축은 캐시가 살아 있을 때 한다." | C9, C10, C16, C25 |
| A9 "MCP 도구 수" (중간) | "연결만 해도 도구 설명이 컨텍스트를 먹는다." | 기본값에서는 낡은 서술이다. 도구 검색이 기본으로 켜져 있어 이름과 서버 안내만 실린다. | "MCP 도구 정의는 기본으로 필요할 때만 로드된다(이름만 상시). `/context all`로 실제 점유를 본다. 도구 검색이 꺼진 환경(옛 모델, 일부 클라우드, `ENABLE_TOOL_SEARCH=false`)에서는 전체 정의가 실리고, 세션 중 서버를 붙였다 떼면 캐시도 깨진다. CLI(`gh` 등)가 있으면 MCP보다 가볍다." | C14, C3 |
| A9 "캐시" (낮음) | "프롬프트 앞부분이 바뀌면 캐시가 깨진다. 상태줄에 캐시 상태를 띄워 두면 알아챌 수 있다." | 맞다. 무엇이 깨는지와 어떤 필드를 띄우는지가 없다. | 깨는 행동 목록(C3)과 유지하는 행동(C4), 상태줄 필드 `prompt_cache.warm`·`hit_ratio`·`last_miss_cause`(C21), `/usage`의 `Prompt cache (main)` 줄을 적는다. | C3, C4, C21, C24 |
| A9 "역할별 모델" (중간) | "계획은 강한 모델, 단순 작업은 작은 모델." | 세션 중에 `/model`로 오가면 매번 캐시를 통째로 다시 만든다. | "모델과 추론 강도는 세션을 시작할 때 정한다. 역할 분리는 세션 중 전환이 아니라 서브에이전트 정의(`model: haiku`)나 별도 세션으로 한다." | C3, C5, A7, A10 |
| A9 "서브에이전트" (낮음) | "큰 탐색은 서브에이전트에 맡기고 결론만 받는다." | 맞다. 대가가 빠졌다. | "서브에이전트는 토큰을 더 쓴다(자기 요청을 따로 보낸다). 답이 더 좋아지지는 않는다. 쓰는 이유는 병렬, 시끄러운 출력 격리, 독립 리뷰다. 결과는 짧은 요약으로 받는다." | A10, C16 |
| A10 3번 (높음) | "실행: 계획이 서면 목표만 주고 방법은 맡긴다(`/goal`)." | `/goal`은 있다. 하지만 "목표를 주고 방법을 맡기는" 명령이 아니라 **완료 조건**을 거는 명령이고, 평가자는 대화에 드러난 것만 본다. 권한 모드도 바꾸지 않는다. | "실행: 긴 작업이면 완료 조건을 건다(`/goal <측정 가능한 끝 상태 + 확인 방법 + 지킬 제약 + 중단 조건>`). 평가자는 대화에 나온 출력만 보므로 조건은 Claude가 직접 돌려 보여 줄 수 있는 것으로 쓴다. 예: `/goal tests/auth의 테스트가 모두 통과하고 lint가 깨끗하다. 다른 테스트 파일은 고치지 않는다. 20턴 안에 안 되면 멈춘다`" | W4~W7 |
| A10 2번 (낮음) | "계획 → 리뷰 → 승인" | 내장 계획 모드 언급이 없다. | "`Shift+Tab` 또는 `/plan`으로 계획 모드에 들어간다. 계획은 `Ctrl+G`로 직접 고칠 수 있다. 리뷰는 대화를 보지 않은 서브에이전트에 맡긴다." | W1~W3, W10 |
| A10 5번 (낮음) | "새 세션에서 '내 대화 기록을 분석해줘'" | 내장 명령이 있다. | "`/insights`를 돌려 보고서(`~/.claude/usage-data/report.html`)를 읽는다. `/usage`의 권고와 `/skill-doctor`도 같이 본다." | O10, S19 |
| 한눈에 보기 표 A4 (낮음) | "한 턴을 돌리면 기록이 보인다" | 유지. | — | — |

### 2.2 훅 예시

| 파일 | 문제 | 심각도 | 수정안 | 근거 |
|---|---|---|---|---|
| `settings.example.json` | 매처 `Edit\|Write\|MultiEdit`: 문법은 유효하다(정확 일치 목록). `MultiEdit`는 현재 도구 목록에 없는 레거시 이름이고, 실제 파일 수정 도구인 `NotebookEdit`가 빠져 있다. | 중간 | PreToolUse는 `Edit\|Write\|NotebookEdit`, PostToolUse는 `Edit\|Write`(짝 테스트 규칙이 `.py` 대상이라 노트북은 불필요). | H4, H52 |
| `settings.example.json` | `plan_gate`에 `onFailure`가 없다. 파이썬이 없거나 경로가 틀리거나 시간 초과면 그대로 통과한다. | 높음 | `"onFailure": "block"`(≥2.1.295)과 짧은 `timeout` 추가. | H32, H33 |
| `settings.example.json` | 셸 형식 `python3 "$CLAUDE_PROJECT_DIR/..."`. 따옴표를 썼으니 틀리지는 않다. 공식 권장은 exec 형식이다. | 낮음 | `"command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/plan_gate.py"]` | H42 |
| `plan_gate.py` | "입력을 못 읽으면 막는다(fail closed)"는 `JSONDecodeError`에만 해당한다. JSON 배열·문자열, `tool_input`이 객체가 아닌 경우, `file_path`가 문자열이 아닌 경우, 계획 파일 읽기 오류는 예외 → exit 1 → **통과**한다. | 높음 | `main()` 전체를 `try/except Exception`으로 감싸 exit 2. 설정의 `onFailure: "block"`과 이중화. | L6, H17 |
| `plan_gate.py` | Claude가 `design/plans/*.md`에 `status: approved`를 직접 써서 스스로 승인할 수 있다(`design/`과 `.md`가 허용 목록이라 무조건 통과). 가이드의 "내가 승인한다"가 지켜지지 않는다. | 높음 | 계획 폴더에 `status: approved`를 써넣는 Edit/Write는 `permissionDecision: "ask"`로 사람 확인을 받는다. (Bash로 쓰는 우회는 남는다. README에 명시.) | L7, H24 |
| `plan_gate.py` | `NotebookEdit`는 `notebook_path`를 쓴다. `file_path`만 읽으면 대상이 빈 문자열이 된다(지금은 우연히 막히지만 메시지가 `'.'`로 나온다). | 중간 | `file_path` 또는 `notebook_path`를 읽는다. | H11 |
| `plan_gate.py` | `"status: approved" in text` 부분 문자열 검사라 "not yet status: approved" 같은 문장도 승인으로 본다. | 낮음 | 줄 단위 정규식 `^status:\s*approved\s*$`. | — |
| `plan_gate.py` | 워크트리 세션에서는 `CLAUDE_PROJECT_DIR`가 원래 체크아웃을 가리켜, 워크트리 안 파일이 "프로젝트 밖"으로 판정된다(허용 목록이 안 먹고 전부 계획 요구). 막는 쪽으로 틀리므로 안전하지만 문서 수정도 막힌다. | 낮음 | README에 한계로 적는다. | H43 |
| `test_after_edit.py` | 실행 명령이 `python`으로 고정. `python`이 없고 `python3`만 있는 환경에서는 `FileNotFoundError` → exit 1 → 테스트가 조용히 안 돈다. | 중간 | `sys.executable` 사용, `OSError`를 잡아 exit 2로 알린다. | H16 |
| `test_after_edit.py` | `.claude/hooks/*.py`, `__init__.py`, `tests/` 안 헬퍼를 고쳐도 "짝 테스트 없음"으로 exit 2를 낸다. 매번 모델에 잡음이 간다. | 중간 | 건너뛸 폴더·파일 이름 목록 추가. | L8 |
| `test_after_edit.py` | 비정상 입력(`[]`)에서 exit 1. 의도는 "건너뛴다"인데 매번 `hook error` 알림이 뜬다. | 낮음 | 타입 오류도 잡아 exit 0. | L8 |
| `test_after_edit.py` | 병렬 편집이면 훅도 동시에 여러 번 돌아 pytest가 겹친다. | 낮음 | README에 한계로 적고, 무거워지면 `PostToolBatch`나 Stop 훅으로 옮기라고 안내. | H39 |
| `test_after_edit.py` | 워크트리에서 원래 체크아웃의 테스트를 돌린다. | 낮음 | 수정한 파일을 품은 쪽(`CLAUDE_PROJECT_DIR` 또는 입력의 `cwd`)을 루트로 고른다. | H43 |
| `test_after_edit.py` | exit 2 + stderr로 모델에 알리는 방식, `tool_input.file_path` 필드명 | 정상 | 그대로 둔다. | H10, H19, H20 |
| `prompt_reminder.sh` | 동작은 문서와 맞다(exit 0의 일반 텍스트 stdout이 컨텍스트에 추가). | 정상 | 주석 보강: `{`로 시작하면 JSON으로 해석된다, 요청마다 쌓인다. | H21, H22, H30 |
| `reminders.md` | 명령문("…확인한다")이다. 공식 권고는 사실 진술이다. | 낮음 | "이 저장소는 …을 요구한다" 식으로 바꾼다. | H29 |
| `README.md` | 표의 "PreToolUse (Edit·Write)", 주의 문단이 위 변경을 반영하지 않는다. "훅은 권한을 조일 수는 있어도 풀 수는 없다"도 같은 문제. | 중간 | 4절의 README 수정안. | — |

---

## 3. A4~A10 단계별로 추가할 내용

형식: 고민할 것 / 할 일 / 확인 방법(실제 명령) / 끝났다는 기준. 가이드의 문체(평서문, 단계별)에 맞췄다.

### A4. 기록 붙이기

**고민할 것**
- 기록을 어디까지 남길지. 지표(토큰·비용·시간)만인지, 프롬프트와 도구 인자까지인지. 내장 OTel은 기본으로 내용을 남기지 않는다. 내용을 남기려면 `OTEL_LOG_USER_PROMPTS=1`, `OTEL_LOG_TOOL_DETAILS=1`을 따로 켠다.
- 기록이 어디로 가는지. 회사 코드가 외부 클라우드로 나가도 되는지.
- 도구를 새로 붙여야 하는지. 혼자 쓰는 수준이면 내장 명령으로 충분할 수 있다.

**할 일** (가벼운 것부터)
1. 설치 없이: `/usage`(세션 비용·토큰·캐시 통계, `/cost`는 별칭), `/context`(지금 컨텍스트 구성), `/insights`(최근 세션 분석 HTML 보고서).
2. 내장 OpenTelemetry: 수집기가 있으면 `~/.claude/settings.json`의 `env`에 넣는다. 저장소의 `.claude/settings.json`에 넣으면 무시된다.
   ```json
   {
     "env": {
       "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
       "OTEL_METRICS_EXPORTER": "otlp",
       "OTEL_LOGS_EXPORTER": "otlp",
       "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
       "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317"
     }
   }
   ```
3. 제3자 플러그인(예: Langfuse): 턴 단위 추적 화면이 필요할 때. uv가 PATH에 있어야 한다. user 범위로 설치해야 어느 폴더에서든 기록된다. 키는 세션 안에서 `/plugin configure langfuse-observability@langfuse-observability`로 넣는다.

**확인 방법**
```bash
# 내장
/usage            # 세션 안에서. Session 블록과 "Prompt cache (main)" 줄
/insights         # 끝나면 ~/.claude/usage-data/report.html

# OTel: 세션을 하나 열고 프롬프트를 하나 보낸 뒤 수집기에서 확인
#   지표 claude_code.session.count, 이벤트 claude_code.user_prompt
claude --debug-file /tmp/claude-otel.log     # 안 오면 로그에서 "[3P telemetry]" 검색

# 플러그인
claude plugin list
tail -n 20 ~/.claude/state/langfuse_hook.log   # Langfuse 훅 로그
```

**끝났다는 기준**
- [ ] 한 턴을 돌린 뒤 그 턴의 도구 호출·소요 시간·토큰을 볼 수 있다 (`/usage`, 수집기, 또는 플러그인 화면 중 하나)
- [ ] 프롬프트·도구 인자를 남기는지 여부를 내가 정했고 설정이 그 결정과 같다
- [ ] 기록이 가는 곳(로컬, 사내 수집기, 외부 클라우드)을 알고 있다

### A5. 스킬

**고민할 것**
- 이 내용이 스킬인가. 항상 적용할 규칙이면 지침, 매번 강제해야 하면 훅, 필요할 때만 읽는 절차·지식이면 스킬이다.
- 누가 부르는가. 부작용이 있으면 나만(`disable-model-invocation: true`), 배경 지식이면 Claude만(`user-invocable: false`).
- 대화 맥락이 필요한가. 필요 없고 출력이 길면 `context: fork`로 서브에이전트에서 돌린다(대화 기록을 못 본다).
- 스킬이 늘수록 설명 목록이 길어진다. 목록 예산(컨텍스트 창의 1%)을 넘으면 덜 쓰는 스킬의 설명부터 빠진다.

**할 일**
- frontmatter는 필요한 필드만 쓴다. 자주 쓰는 것: `name`, `description`, `when_to_use`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `context`, `agent`, `paths`, `argument-hint`. 필드 이름이 틀리면 오류 없이 무시된다.
- `description`+`when_to_use`는 1,536자에서 잘린다. 핵심 용도를 맨 앞에 쓴다.
- `allowed-tools`는 도구 제한이 아니다. 그 턴 동안 확인 창 없이 쓰게 하는 사전 승인이다. 저장소에 들어온 남의 스킬은 이 필드를 먼저 읽는다.
- 본문은 500줄 이하. 가장 중요한 지시를 맨 위에 둔다(압축 뒤에는 스킬당 앞 5,000토큰만 남는다).
- claude.ai나 Skills API에도 올릴 스킬이면 frontmatter를 규격 6개 필드(`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`)로 제한한다.
- 스킬 안에서만 지켜야 하는 강제 규칙은 스킬 frontmatter의 `hooks`에 둔다(호출 뒤 세션 끝까지 유지).

**확인 방법**
```bash
claude plugin validate .claude/skills        # frontmatter 문법. 모델 호출 없음. 0=통과
claude plugin validate ~/.claude/skills
```
세션 안에서: `/skills`(목록, `t`로 토큰 순 정렬), `/context`(Skills 행), `/skill-doctor`(스킬별 비용과 사용 빈도).
호출 시험은 **새 세션**에서 한다. 불려야 하는 요청 3개, 불리면 안 되는 요청 3개. 결과 품질은 스킬을 끈 상태와 비교한다:
```json
{ "skillOverrides": { "<스킬 이름>": "off" } }
```
(`.claude/settings.local.json`. `/skills`에서 Space로도 바꿀 수 있다.)

**끝났다는 기준**
- [ ] `claude plugin validate`가 통과한다
- [ ] 새 세션의 호출 시험 6건이 기대와 같다
- [ ] 스킬을 켠 결과가 끈 결과보다 낫다는 것을 한 번 이상 비교했다
- [ ] 부작용 있는 스킬은 `disable-model-invocation: true`다
- [ ] 본문 500줄 이하, 설명 1,536자 이하

### A6. 훅

**고민할 것**
- 이 규칙에 예외가 정말 0개인가. 예외가 있으면 지침에 둔다. 강제 규칙은 적게 유지한다(가끔 잘못 발동하고, 누군가 유지해야 한다).
- 훅이 고장 나면 막을 것인가 통과시킬 것인가. 막는 훅(게이트)은 fail closed, 알려 주는 훅(피드백)은 fail open으로 정하고 코드와 설정에 둘 다 반영한다.
- 어느 이벤트인가. 막기는 PreToolUse(도구 실행 전)·UserPromptSubmit(프롬프트)·Stop(종료)만 된다. PostToolUse는 이미 실행된 뒤다.
- 어떤 경로가 이 훅을 비켜 가는가: Bash로 파일 쓰기, `@` 파일 첨부(Read 훅을 안 거친다), 사람이 직접 고치기, 매처에 없는 도구(MCP 등).
- 판정을 코드로 할 수 있는가. `prompt`·`agent` 타입 훅은 다른 모델이 판단하므로 결정적이지 않다.
- 얼마나 자주, 얼마나 오래 도는가. PreToolUse·PostToolUse는 도구 호출마다, 서브에이전트 안에서도 돈다. 병렬 호출이면 동시에 돈다.

**할 일**
- 종료 코드 규칙을 지킨다: 0 = 의견 없음(통과), 2 = 차단(stderr가 사유), 그 밖 = 오류지만 통과.
- 게이트 훅에는 설정에 `"onFailure": "block"`(≥2.1.295)과 짧은 `timeout`을 준다.
- 경로는 `${CLAUDE_PROJECT_DIR}`로 쓰고 exec 형식(`command` + `args`)을 쓴다.
- 매처는 실제 도구 이름으로: 파일 수정은 `Edit|Write`(노트북 포함이면 `Edit|Write|NotebookEdit`). `MultiEdit`는 현재 도구가 아니다. `Edit.*` 같은 정규식은 `NotebookEdit`도 잡는다.
- 사람 확인이 필요한 경우는 막지 말고 묻게 한다: PreToolUse에서 `permissionDecision: "ask"`.
- JSON으로 답할 때는 stdout에 JSON 객체 하나만 찍는다. PreToolUse의 결정은 `hookSpecificOutput` 안에 둔다(최상위에 두면 오류 없이 무시된다).
- 모델에 붙이는 글은 사실 진술로, 1만 자 이하로.
- Stop 훅은 `stop_hook_active`를 확인한다.
- 꼭 막아야 하는 것은 권한 deny 규칙과 이중화한다. 훅의 `allow`는 deny·ask 규칙을 넘지 못한다.

**함정 목록에 추가할 줄**
- 훅은 서브에이전트의 도구 호출에도 돈다. 입력의 `agent_id`·`agent_type`으로 구분한다.
- `@`로 붙인 파일은 도구 호출이 아니라서 Read용 PreToolUse 훅을 거치지 않는다. 읽기를 막으려면 권한 deny 규칙을 쓴다.
- 같은 이벤트의 훅은 병렬로 돈다. 한 훅이 막아도 다른 훅의 부작용은 일어난다.
- `claude -p`(비대화형)는 신뢰 확인 없이 저장소의 훅을 돌린다. 남의 저장소에서는 `--bare`나 `--settings '{"disableAllHooks": true}'`로 연다.
- 설정 파일에 잘못된 훅 항목이 하나 있으면 그 파일의 다른 설정까지 적용되지 않을 수 있다. 고친 뒤 `claude doctor`로 확인한다.

**확인 방법**
```bash
# 1) 스크립트 단위: 정상 / 위반 / 깨진 입력
echo '{"tool_name":"Edit","tool_input":{"file_path":"'"$PWD"'/src/a.py"}}' | python3 .claude/hooks/plan_gate.py; echo "exit=$?"
echo '{"tool_name":"Write","tool_input":{"file_path":"'"$PWD"'/README.md"}}' | python3 .claude/hooks/plan_gate.py; echo "exit=$?"
echo '[]'      | python3 .claude/hooks/plan_gate.py; echo "exit=$?"     # 게이트면 2여야 한다
echo '{broken' | python3 .claude/hooks/plan_gate.py; echo "exit=$?"

# 2) 설정 파일: 모델 호출 없이 스키마 검사 ("Invalid settings"가 없어야 한다)
claude doctor

# 3) 세션 안: 등록 확인
/hooks

# 4) 실제 발동 기록
claude --debug-file /tmp/claude-hooks.log
grep 'Hooks:' /tmp/claude-hooks.log      # 예: Hooks: PostToolUse:Write [...] finished with status 0 (31ms)
```
세션에서 위반을 시도했을 때 대화 기록(`Ctrl+O`)에 차단 사유가 보이는지, `hook error` 알림이 없는지 본다. `onFailure: "block"`은 스크립트 경로를 일부러 틀리게 해서 막히는지 본다.

**끝났다는 기준**
- [ ] 켠 훅마다 세 가지 입력(정상, 위반, 깨진 입력) 시험 결과가 있다
- [ ] `claude doctor`에 `Invalid settings`가 없고 `/hooks`에 훅이 보인다
- [ ] 실제 세션에서 위반을 시도했을 때 막힌다
- [ ] 게이트 훅은 스크립트가 없거나 죽어도 막힌다(`onFailure: "block"` 확인)
- [ ] 막지 못하는 우회 경로를 적어 뒀다

### A7. 공개 하네스·플러그인

**고민할 것**
- 플러그인이 내 PC에서 무엇을 실행하는가. 훅·모니터·MCP 서버는 내 권한으로, 샌드박스 밖에서 돈다. 권한 규칙은 Claude의 도구 호출에만 적용된다.
- 매 세션 얼마를 더 내는가(스킬·에이전트 설명의 상시 토큰).
- 어느 범위에 설치할 것인가. user(모든 프로젝트), project(저장소에 커밋), local(나만, 이 저장소).
- 자동 업데이트를 켤 것인가. 켜면 검토한 파일이 바뀔 수 있다.
- 포크를 플러그인으로 유지할 것인가, 필요한 스킬·훅만 `.claude/`로 가져올 것인가. 한 프로젝트·나 혼자면 `.claude/`가 낫다.

**할 일**
1. 출처 확인: `claude plugin marketplace list`.
2. 내용 확인(설치 전, 세션 없이): 저장소를 클론해 `claude --plugin-dir <플러그인 폴더> plugin details <이름>`으로 구성과 토큰 비용을 본다. `hooks/hooks.json`, `.mcp.json`, `bin/`은 직접 읽는다.
3. 시험: 설치하지 않고 `claude --plugin-dir <플러그인 폴더>`로 한 세션만 로드한다.
4. 포크: 바꾼 뒤 `claude plugin validate <폴더> --strict`.
5. 설치: `claude plugin marketplace add <소스>` → `claude plugin install <이름>@<마켓> [--scope project|local]`.
6. 원본 제거: `claude plugin uninstall <이름>@<마켓>`. 둘 다 켜 두면 훅이 두 번 돌고 설명이 두 벌 실린다.

**확인 방법**
```bash
claude plugin marketplace list
claude --plugin-dir ./fork plugin details <이름>     # Component inventory, Always-on 토큰
claude plugin validate ./fork --strict                # 0=통과
claude plugin list                                    # 설치·활성 상태
```
세션 안에서: `/plugin`(Installed·Errors 탭), `/hooks`(플러그인 훅 출처 표시), `/context`.

**끝났다는 기준**
- [ ] `claude plugin list`에 포크본 하나만 있다
- [ ] 포크의 `hooks/hooks.json`·`.mcp.json`·`bin/`을 직접 읽었다
- [ ] 상시 토큰 비용(`Always-on`)을 알고 있다
- [ ] 무엇을 왜 바꿨는지 적어 뒀다

### A8. 검증

**고민할 것**
- 무엇을 보면 "세팅이 동작한다"고 할 것인가. 지침·스킬·훅·기록 각각에 대해 관찰할 증거를 미리 정한다.
- 모델의 "됐습니다"가 아니라 명령 출력으로 확인할 수 있는가.

**할 일**
- 세션을 열기 전에 정적 점검을 먼저 한다(모델 호출 없음).
- 빈 폴더의 작은 작업은 계획 모드로 시작한다(`claude --permission-mode plan` 또는 `Shift+Tab`).
- 끝에는 증거를 요구한다: 실행한 명령과 그 출력.
- 리뷰는 대화를 보지 않은 쪽에 맡긴다(`/code-review`, 또는 읽기 전용 리뷰어 서브에이전트).

**확인 방법**
```bash
# 정적 점검 (세션 없이)
claude doctor                                   # 설치 상태, Invalid settings
claude plugin validate .claude/skills           # 스킬 frontmatter
claude plugin validate .claude/agents           # 서브에이전트 frontmatter
claude plugin list
python3 -m json.tool .claude/settings.json > /dev/null

# 세션 안 점검
/context     # 로드된 지침·스킬·MCP 점유
/memory      # 로드된 CLAUDE.md, 자동 메모리
/hooks       # 등록된 훅
/skills      # 스킬 목록
/mcp         # MCP 서버 상태
/status      # 버전, 모델, 설정 출처
/doctor      # 전체 점검(수정 제안 포함)

# 문제가 세팅 탓인지 가르기
claude --safe-mode       # 모든 사용자 설정을 끄고 시작
```
훅이 실제로 돌았는지는 `claude --debug-file <경로>` 로그의 `Hooks:` 줄로 본다.

**끝났다는 기준** (기존 항목에 추가)
- [ ] 정적 점검 명령이 모두 통과했다
- [ ] 지침·스킬·훅·기록 각각에 대해 "동작했다"는 증거(명령 출력, 로그 줄)를 남겼다
- [ ] 완료 판정을 테스트 출력으로 했다

### A9. 비용·컨텍스트 관리

**고민할 것**
- 지금 비용을 키우는 것이 무엇인가: 긴 대화(요청마다 전체를 다시 보낸다), 캐시 미스, 백그라운드 작업(`/loop`, `/goal` 확인, 서브에이전트) 중 어느 것인가. `/usage`가 10% 넘는 원인을 짚어 준다.
- 이 대화를 이어갈 것인가 버릴 것인가. 작업이 바뀌면 `/clear`(무료), 이어가면 `/compact`(큰 요청), 잘못 든 길이면 `/rewind`(캐시 유지).
- 캐시 수명이 얼마인가. 구독이면 메인 대화 1시간, API 키·사용 크레딧이면 5분, 서브에이전트는 5분. 자리를 비우는 시간이 이보다 길면 돌아와서 첫 요청이 전체 재처리다.
- 서브에이전트를 쓰는 이유가 맞는가. 병렬·출력 격리·독립 리뷰면 쓴다. "더 좋은 답"을 기대하면 쓰지 않는다. 토큰은 더 든다.

**할 일**
- 상태줄에 컨텍스트 사용률과 캐시 상태를 띄운다. 쓸 수 있는 필드: `context_window.used_percentage`, `prompt_cache.warm`, `prompt_cache.hit_ratio`, `prompt_cache.misses`, `prompt_cache.last_miss_cause.causes`, `cost.total_cost_usd`. 예시 스크립트는 4.6절.
- 모델과 추론 강도는 세션을 시작할 때 정한다. 세션 중 전환은 캐시를 통째로 다시 만든다.
- 세션 중에 하지 않는다: MCP 서버 붙였다 떼기(도구 검색이 꺼진 환경), 도구 전체 deny 추가, fast mode 전환.
- 세션 중에 해도 된다(캐시 유지): 파일 수정, 권한 모드 전환, 출력 스타일 전환, 스킬 호출, `/rewind`, 서브에이전트 호출. CLAUDE.md 수정은 캐시를 안 깨지만 `/clear`·`/compact`·재시작 전에는 적용도 안 된다.
- 압축은 자연스러운 끊김에서, 남길 것을 지정해서: `/compact <남길 것>`. 프로젝트 CLAUDE.md에 `# Compact instructions` 구역을 둘 수 있다. 일부만 줄이려면 `/rewind` → Summarize from here / up to here.
- 자동 압축 시점은 `/autocompact <토큰 수>`로 조정한다.
- 출력 줄이기: `/output-style concise`. 추론 강도는 기본(medium)에서 시작하고 필요한 요청에만 올린다.
- 단순한 서브에이전트는 정의에 `model: haiku`. 결과는 짧은 요약으로 받는다.
- 주기적으로 `/skill-doctor`, `/context all`, `claude plugin details <이름>`로 상시 비용을 줄인다.

**확인 방법**
```text
/usage        Session 블록의 "Prompt cache (main): N requests · X% of input tokens from cache · M misses ..."
              플랜 사용자는 원인별 비중과 권고
/context      범주별 점유 (/context all 로 항목별)
```
```bash
# 상태줄 스크립트 단독 시험
echo '{"model":{"display_name":"Opus"},"context_window":{"used_percentage":8},"prompt_cache":{"warm":true,"hit_ratio":0.91,"misses":2}}' | python3 ~/.claude/statusline.py
# 메인 대화의 캐시 수명 확인 (모델 호출 1회): 결과 JSON의 usage.cache_creation에서
#   ephemeral_1h_input_tokens / ephemeral_5m_input_tokens
claude -p "hello" --output-format json
```

**끝났다는 기준** (습관이므로 점검 항목)
- [ ] 상태줄에서 컨텍스트 사용률과 캐시 warm/cold를 볼 수 있다
- [ ] 캐시 미스가 났을 때 원인(`last_miss_cause` 또는 `/usage`의 likely cause)을 찾을 수 있다
- [ ] 작업이 바뀔 때 `/clear`하는 습관이 있다
- [ ] 내 캐시 수명(1시간/5분)을 알고 있다

### A10. 작업 루틴

**고민할 것**
- 이 작업의 "끝"을 무엇으로 판정할 것인가. 통과/실패가 나오는 검사(테스트, 빌드 종료 코드, 린터, 스크립트)가 있는가. 없으면 먼저 만든다.
- 내가 지켜볼 것인가 맡기고 떠날 것인가. 떠날 거면 다섯 가지를 정한다: 끝의 정의, 스스로 확인할 수단, 건드려도 되는 범위, 멈추는 조건(`--max-turns`, `--max-budget-usd`), 결과를 받는 곳과 승인자.
- 정정이 두 번 실패했는가. 그러면 세 번째 정정 대신 `/clear` 하고 배운 것을 넣어 프롬프트를 새로 쓴다.

**할 일** (가이드의 5단계에 붙일 구체 수단)
1. 요구 정리: 그대로 유지.
2. 계획 → 리뷰 → 승인: `Shift+Tab` 또는 `/plan <설명>`으로 계획 모드. 계획은 `Ctrl+G`로 직접 고친다. 리뷰는 대화를 보지 않은 서브에이전트에 스펙 대조로 맡기고 "스타일은 건너뛴다"를 붙인다.
3. 실행: 긴 작업이면 완료 조건을 건다. `/goal <측정 가능한 끝 상태 + 확인 방법 + 제약 + 중단 조건>`. 평가자는 대화에 나온 출력만 본다. 권한 확인을 줄이려면 auto 모드와 같이 쓴다.
4. 검증: 실행한 명령과 출력을 증거로 받는다. 필요하면 `/verify`(앱을 실제로 띄워 확인), `/code-review`(새 서브에이전트가 diff 리뷰). 매번 강제하려면 Stop 훅(4.5절).
5. 주간 회고: `/insights` 보고서와 `/usage` 권고, `/skill-doctor`를 읽고 승격 규칙에 따라 반영한다.

개입 수단: `Esc`(중단, 진행분 유지), `Esc` 두 번 또는 `/rewind`(코드·대화 되감기. Bash로 바꾼 파일과 서브에이전트 수정은 git으로 되돌린다), `/btw`(기록에 안 남는 곁질문), `/clear <이름>`(이름 붙여 새로 시작).

**확인 방법**
```text
/goal                 현재 조건, 경과 시간, 평가 횟수, 토큰, 평가자의 최근 사유
/rewind               체크포인트 목록
/insights             ~/.claude/usage-data/report.html
```
```bash
# 무인 실행은 상한을 건다
claude -p "/goal tests/auth의 테스트가 모두 통과한다" --max-turns 30 --max-budget-usd 5 --output-format stream-json --verbose
```

**끝났다는 기준** (습관이므로 점검 항목)
- [ ] 작업마다 통과/실패가 나오는 검사가 하나 이상 있다
- [ ] 완료를 명령 출력으로 확인했다
- [ ] 주간 회고에서 `/insights`·`/usage`를 보고 한 가지 이상 반영했다

---

## 4. 훅 예시 파일 수정안

아래 코드는 스크래치 폴더에서 정상·위반·깨진 입력으로 실행해 종료 코드를 확인했다(Python 3.9 이상 필요: `Path.is_relative_to`). `settings.json`은 `claude doctor`(2.1.322)에서 `Invalid settings` 없음. 사본: `/tmp/claude-0/-home-user-agent-harness/9d24d4e0-4e22-527d-9ef4-148a860878ba/scratchpad/proposed/`

### 4.1 `hooks/settings.example.json`

바뀐 점: exec 형식(`command` + `args`), 매처에서 `MultiEdit` 제거·`NotebookEdit` 추가(PreToolUse), `plan_gate`에 `onFailure: "block"`과 `timeout`.
`onFailure`는 v2.1.295 이상에서만 유효하다. 그보다 낮은 버전에서는 이 키를 빼야 한다(`claude --version`으로 확인).

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/plan_gate.py"],
            "timeout": 10,
            "onFailure": "block"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/test_after_edit.py"],
            "timeout": 330
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/prompt_reminder.sh"],
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### 4.2 `hooks/plan_gate.py`

바뀐 점: ① 모든 예외를 exit 2로(fail closed). ② `notebook_path` 지원. ③ 계획 폴더에 `status: approved`를 써넣는 수정은 사람에게 묻는다(`permissionDecision: "ask"`). ④ 승인 표시는 줄 단위로 검사.

시험 결과(계획 없음 상태): 일반 `.py` → 2, `.md` → 0, `{broken` → 2, 빈 입력 → 2, `[]` → 2, `"x"` → 2, `{"tool_input":"x"}` → 2, `file_path: 123` → 2, NotebookEdit → 2, 프로젝트 밖 경로 → 2, `design/../src/a.py` → 2, 계획 파일에 `status: approved` 쓰기 → 0 + ask JSON, `status: draft` 쓰기 → 0. 계획에 "not yet status: approved by anyone"만 있을 때 → 2. `status: approved` 줄이 있을 때 `.py` → 0.

```python
#!/usr/bin/env python3
"""PreToolUse 훅: 승인된 계획 없이 코드를 바꾸지 못하게 막는다.

stdin으로 받은 훅 입력(JSON)에서 수정 대상 파일을 읽고,
design/plans/*.md 중 `status: approved` 줄이 있는 계획이 없으면 exit 2로 차단한다.
design/, harness/, .claude/, 문서(.md) 수정은 계획 없이도 허용한다.
계획 파일에 `status: approved`를 써넣는 수정은 사람에게 확인을 받는다(ask).
어떤 이유로든 판정하지 못하면 막는다(fail closed).
"""
import json
import os
import re
import sys
from pathlib import Path

ALLOW_PREFIXES = ("design/", "harness/", ".claude/")
ALLOW_SUFFIXES = (".md",)
PLANS_DIR = "design/plans/"
APPROVED = re.compile(r"^status:\s*approved\s*$", re.MULTILINE)


def decide() -> int:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        raise ValueError("tool_input이 객체가 아닙니다")
    # Edit·Write는 file_path, NotebookEdit는 notebook_path. 공식 문서상 항상 절대 경로다.
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(target, str) or not target:
        raise ValueError("수정 대상 경로가 없습니다")
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    try:
        rel = Path(target).resolve().relative_to(root).as_posix()
    except ValueError:
        rel = Path(target).as_posix()  # 프로젝트 밖(워크트리 포함)은 허용 목록에 걸리지 않는다

    if rel.startswith(PLANS_DIR):
        written = "\n".join(str(tool_input.get(k) or "") for k in ("content", "new_string"))
        if APPROVED.search(written):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"plan_gate: '{rel}'에 status: approved를 쓰려 합니다. 계획 승인은 사람이 합니다.",
            }}, ensure_ascii=False))
            return 0
    if rel.startswith(ALLOW_PREFIXES) or rel.endswith(ALLOW_SUFFIXES):
        return 0
    for plan in sorted((root / "design" / "plans").glob("*.md")):
        if APPROVED.search(plan.read_text(encoding="utf-8", errors="ignore")):
            return 0
    print(
        f"plan_gate: 승인된 계획이 없어 '{rel}' 수정을 막았습니다. "
        "design/plans/에 계획(수정 대상, 순서, 테스트 방법)을 쓰고 리뷰·승인(status: approved)을 받은 뒤 다시 시도하세요.",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    try:
        return decide()
    except Exception as exc:  # 깨진 입력·예상 못 한 오류도 exit 1(통과)이 아니라 exit 2(차단)로 끝낸다
        print(f"plan_gate: 판정하지 못해 차단합니다(fail closed): {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

### 4.3 `hooks/test_after_edit.py`

바뀐 점: ① `python` 고정 대신 `sys.executable`. ② `.claude/`, `tests/`, `__init__.py`, `conftest.py`는 건너뜀. ③ 비정상 입력은 exit 0(fail open). ④ 워크트리면 `cwd` 쪽을 루트로. ⑤ 실행 실패(`OSError`)도 알림.

시험 결과: 짝 테스트 없음 → 2, 통과 → 0, 실패 → 2(끝 3,000자), `[]` → 0, `{x` → 0, `{"tool_input":"x"}` → 0, `.md` → 0, `.claude/hooks/plan_gate.py` → 0, `__init__.py` → 0, `tests/helper.py` → 0.

```python
#!/usr/bin/env python3
"""PostToolUse 훅: 코드 파일을 고치면 이름 규칙으로 짝지은 테스트만 돌린다.

LLM 판단 없이 규칙으로 테스트를 고른다. 규칙은 TEST_RULES를 프로젝트에 맞게 고친다.
테스트가 실패하면 exit 2로 stderr를 모델에 돌려준다. Post 훅은 이미 실행된 수정을 되돌리지 않는다.
입력을 못 읽거나 훅 자체가 실패하면 검사를 건너뛴다(fail open). 최종 방어선은 CI다.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# (소스 확장자, 테스트 경로 만들기, 실행 명령)
TEST_RULES = [
    (".py", lambda p: Path("tests") / f"test_{p.stem}.py", [sys.executable, "-m", "pytest", "-q"]),
]
SKIP_DIRS = {".claude", "tests"}          # 이 폴더 아래 파일은 짝 테스트를 요구하지 않는다
SKIP_NAMES = {"__init__.py", "conftest.py"}
TIMEOUT_SEC = 300                         # settings의 훅 timeout(초)보다 작게 둔다
TAIL_CHARS = 3000                         # 모델에 돌려주는 출력 상한(훅 출력 한도는 10,000자)


def find_root(data: dict, target: Path) -> Path:
    """수정한 파일을 품은 루트를 고른다. 워크트리에서는 CLAUDE_PROJECT_DIR가 아니라 cwd가 맞다."""
    for cand in (os.environ.get("CLAUDE_PROJECT_DIR"), data.get("cwd")):
        if cand and target.is_relative_to(Path(cand).resolve()):
            return Path(cand).resolve()
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()


def main() -> int:
    try:
        data = json.load(sys.stdin)
        raw = data["tool_input"].get("file_path") or ""
    except (json.JSONDecodeError, AttributeError, KeyError, TypeError):
        return 0
    if not isinstance(raw, str) or not raw:
        return 0
    target = Path(raw).resolve()
    root = find_root(data, target)
    if target.name in SKIP_NAMES or target.name.startswith("test_"):
        return 0
    if target.is_relative_to(root) and SKIP_DIRS & set(target.relative_to(root).parts[:-1]):
        return 0
    for suffix, to_test, cmd in TEST_RULES:
        if target.suffix != suffix:
            continue
        test_file = root / to_test(target)
        if not test_file.exists():
            print(f"test_after_edit: {target.name}에 짝지은 테스트({to_test(target)})가 없습니다.", file=sys.stderr)
            return 2
        try:
            result = subprocess.run(cmd + [str(test_file)], cwd=root, capture_output=True, text=True, timeout=TIMEOUT_SEC)
        except subprocess.TimeoutExpired:
            print(f"test_after_edit: {test_file.name}이 {TIMEOUT_SEC}초 안에 끝나지 않았습니다.", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"test_after_edit: 테스트 명령을 실행하지 못했습니다: {exc}", file=sys.stderr)
            return 2
        if result.returncode != 0:
            tail = (result.stdout + result.stderr)[-TAIL_CHARS:]
            print(f"test_after_edit: {test_file.name} 실패\n{tail}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 4.4 `hooks/prompt_reminder.sh`와 `hooks/reminders.md`

동작은 그대로다. 주석과 문구만 바꿨다(사실 진술).

```bash
#!/usr/bin/env bash
# UserPromptSubmit 훅: 자꾸 잊는 지침을 매 요청에 덧붙인다.
# exit 0일 때 stdout의 일반 텍스트가 모델 컨텍스트에 추가된다('{'로 시작하면 JSON으로 해석되니 피한다).
# 붙인 글은 대화 기록에 남아 요청마다 쌓인다. reminders.md는 몇 줄로 유지하고, 변하지 않는 규칙은 CLAUDE.md에 둔다.
f="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/reminders.md"
[[ -s "$f" ]] && cat "$f"
exit 0
```

```markdown
<reminders>
- 이 저장소는 코드 변경 전에 design/plans/의 승인된 계획(status: approved)을 요구한다.
- 이 저장소의 완료 기준은 테스트 결과와 실제 파일 상태다.
</reminders>
```

### 4.5 (선택) `hooks/stop_check.py` — 새 예시

가이드가 "끝내기 전(Stop)은 확인한다"고 적지만 예시가 없어서 제안한다. 공식 예시(`pnpm tsc --noEmit 1>&2 || exit 2`)와 같은 방식에 `stop_hook_active` 확인을 넣었다. 기본으로 켜지 않는다.

시험 결과: `stop_hook_active: true` → 0, 테스트 실패 → 2, 통과 → 0, 깨진 입력 → 0.

```python
#!/usr/bin/env python3
"""Stop 훅(선택): 끝내기 전에 정한 검사 명령을 돌리고, 실패하면 exit 2로 계속 일하게 한다.

stop_hook_active가 true면(이미 이 훅 때문에 이어서 일하는 중) 다시 막지 않는다.
검사 명령은 CHECK_CMD를 프로젝트에 맞게 고친다.
"""
import json
import os
import subprocess
import sys

CHECK_CMD = [sys.executable, "-m", "pytest", "-q"]
TIMEOUT_SEC = 300


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if not isinstance(data, dict) or data.get("stop_hook_active"):
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or "."
    try:
        result = subprocess.run(CHECK_CMD, cwd=root, capture_output=True, text=True, timeout=TIMEOUT_SEC)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"stop_check: 검사를 끝내지 못했습니다: {exc}", file=sys.stderr)
        return 0  # 검사 자체가 고장이면 모델이 고칠 수 없으니 보내 준다
    if result.returncode != 0:
        print("stop_check: 검사가 실패했습니다. 고친 뒤 끝내세요.\n" + (result.stdout + result.stderr)[-3000:], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

연결:
```json
{
  "hooks": {
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/stop_check.py"], "timeout": 330 }] }
    ]
  }
}
```
주의: Stop 훅에는 `onFailure`가 효과가 없다(문서: "exit code 2 on these events sends Claude back to keep working, and Claude can't repair a hook that won't run"). 전체 테스트가 느리면 응답마다 그만큼 기다린다.

### 4.6 (선택) 상태줄 예시 `statusline.py` — A9용

`~/.claude/statusline.py`에 두고 `~/.claude/settings.json`에 `"statusLine": {"type": "command", "command": "python3 ~/.claude/statusline.py"}`를 넣는다. 공식 문서의 샘플 JSON으로 실행해 `Opus | ctx 8% | cache warm 91% miss×2(tools_changed) | $0.01` 출력을 확인했다. 60/80 경계는 내 기준값이고 공식 권장값이 아니다.

```python
#!/usr/bin/env python3
"""상태줄: 모델 · 컨텍스트 사용률 · 프롬프트 캐시 상태 · 세션 비용(추정).

Claude Code가 stdin으로 주는 JSON을 읽어 한 줄을 출력한다. API 토큰을 쓰지 않는다.
없는 필드(prompt_cache는 v2.1.251 이상, 첫 응답 뒤에 생김)와 null은 건너뛴다.
"""
import json
import sys

WARN_PCT, HIGH_PCT = 60, 80  # 내 기준값. 공식 권장값이 아니다.


def main() -> None:
    try:
        d = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("statusline: 입력을 읽지 못함")
        return
    parts = [(d.get("model") or {}).get("display_name") or "?"]

    cw = d.get("context_window") or {}
    pct = cw.get("used_percentage")
    if pct is not None:
        mark = "!!" if pct >= HIGH_PCT else "!" if pct >= WARN_PCT else ""
        parts.append(f"ctx {pct:.0f}%{mark}")

    pc = d.get("prompt_cache")
    if pc:
        state = "warm" if pc.get("warm") else "cold"
        hit = pc.get("hit_ratio")
        text = f"cache {state}"
        if hit is not None:
            text += f" {hit * 100:.0f}%"
        if pc.get("misses"):
            causes = ((pc.get("last_miss_cause") or {}).get("causes")) or []
            text += f" miss×{pc['misses']}" + (f"({causes[0]})" if causes else "")
        parts.append(text)

    cost = (d.get("cost") or {}).get("total_cost_usd")
    if cost is not None:
        parts.append(f"${cost:.2f}")
    print(" | ".join(parts))


if __name__ == "__main__":
    main()
```

### 4.7 `hooks/README.md` 수정안

```markdown
# 훅 예시 (필요할 때 켠다)

아래 훅은 설치해도 기본으로 켜지지 않는다. 규칙이 생기고 필요가 확인되면 `.claude/settings.json`에 연결해서 켠다. 연결 예시는 `settings.example.json`이고, 프로젝트에 설치되면 `.claude/hooks/`에 놓인다.

| 파일 | 이벤트 (매처) | 하는 일 | 차단 여부 | 고장 나면 |
|---|---|---|---|---|
| `plan_gate.py` | PreToolUse (`Edit\|Write\|NotebookEdit`) | 승인된 계획(`design/plans/*.md`의 `status: approved` 줄)이 없으면 코드 수정을 막는다. 계획에 승인 표시를 써넣는 수정은 사람에게 묻는다 | 막음 (exit 2), 물음 (JSON ask) | 막는다 (스크립트의 예외 처리 + 설정의 `onFailure: "block"`) |
| `test_after_edit.py` | PostToolUse (`Edit\|Write`) | 고친 파일과 이름 규칙으로 짝지은 테스트만 돌리고, 실패하면 결과를 모델에 돌려준다 | 이미 실행된 뒤라 막지 않음, 피드백 (exit 2) | 건너뛴다 |
| `prompt_reminder.sh` + `reminders.md` | UserPromptSubmit (매처 없음) | 짧은 사실 진술을 매 요청에 덧붙인다 | 막지 않음 | 건너뛴다 |
| `stop_check.py` (선택) | Stop (매처 없음) | 끝내기 전에 검사 명령을 돌리고 실패하면 계속 일하게 한다 | 종료를 막음 (exit 2) | 보내 준다 |

## 켜기 전에
- `claude --version`이 2.1.295 이상인지 본다. 그보다 낮으면 `settings.example.json`의 `onFailure`를 뺀다.
- 설정을 붙인 뒤 `claude doctor`를 돌려 `Invalid settings`가 없는지 본다. 세션 안에서는 `/hooks`로 등록을 확인한다.
- 스크립트마다 정상·위반·깨진 입력을 넣어 종료 코드를 본다.
  `echo '<JSON>' | python3 .claude/hooks/plan_gate.py; echo $?`
- Python 3.9 이상이 필요하다.

## 주의
- 차단은 exit 2나 JSON 결정(PreToolUse는 `hookSpecificOutput.permissionDecision`)으로만 된다. **exit 1, 스크립트 오류, 시간 초과, 경로 오타는 `hook error` 알림만 남기고 통과한다.** 꼭 막아야 하는 훅에는 설정에 `"onFailure": "block"`을 넣고, 권한 deny 설정으로도 이중화한다.
- 매처를 비켜 가는 경로가 있다. 셸 명령으로 파일을 쓰면 `Edit|Write` 매처를 거치지 않는다. `plan_gate.py`만으로 완전히 막히지 않고, 계획 파일의 승인 표시도 셸로는 쓸 수 있다.
- 훅은 서브에이전트의 도구 호출에도 돈다. 병렬 호출이면 동시에 돈다(`test_after_edit.py`의 테스트가 겹칠 수 있다).
- 훅의 거부는 모든 권한 모드에서 통한다. 훅의 허용은 확인 창을 건너뛸 뿐 권한 설정의 deny·ask 규칙을 넘지 못한다.
- 명령 훅은 내 사용자 권한으로 실행된다. 클론한 저장소의 훅도 내 PC에서 실행되니 신뢰한 작업 공간에서만 켠다. `claude -p`는 신뢰 확인 없이 저장소 훅을 돌린다.
- 워크트리 세션에서는 `CLAUDE_PROJECT_DIR`가 원래 체크아웃을 가리킨다. `plan_gate.py`는 워크트리 안의 파일을 프로젝트 밖으로 보고 전부 계획을 요구한다.
- `prompt_reminder.sh`가 붙인 글은 대화 기록에 요청마다 쌓인다. 몇 줄로 유지하고, 변하지 않는 규칙은 지침 파일에 둔다. 이 훅은 예약 작업이나 백그라운드 서브에이전트 보고에도 돈다.
- Post·Stop 훅의 통과는 수정 완료의 증거가 아니다. 최종 방어선은 PR 리뷰와 CI다.
- 이벤트 이름, 입력 필드, 차단 방식은 도구 버전마다 다를 수 있다. 켜기 전에 쓰는 도구의 훅 공식 문서로 확인하고, 일부러 틀린 입력으로 차단되는지 시험한다.
```

---

## 5. 확인 못 한 것

- **실제 세션에서의 훅 발동.** 모델 호출을 쓰지 않아서, 수정안이 실제 세션에서 차단·ask 창·피드백으로 이어지는지는 보지 않았다. 확인한 것은 스크립트의 종료 코드·출력과 `claude doctor`의 설정 스키마 검사까지다. 특히 `permissionDecision: "ask"`가 auto 모드에서 확인 창으로 가는지(문서: "normally sends the tool call to the permission prompt")와 `onFailure: "block"`의 실제 차단은 한 번 세션에서 확인해야 한다.
- **`NotebookEdit`의 `tool_input` 전체 스키마.** 훅 문서에는 NotebookEdit 입력 표가 없다. `notebook_path`는 권한 문서의 한 문장("`notebook_path` for NotebookEdit")이 근거다.
- **`if: "Edit(*.py)"`가 Write 호출에도 맞는지.** 권한 규칙에서는 `Edit(...)`가 Edit·Write·NotebookEdit를 모두 덮는다고 하지만, 훅의 `if`에서도 같은지는 문서에 명시가 없다. 그래서 수정안에 `if`를 넣지 않았다.
- **잘못된 훅 항목이 설정 파일 전체를 무효로 만드는 범위.** `claude doctor`의 경고 문구(L2)만 봤다. 공식 문서에서 같은 서술을 찾지 못했다.
- **`OTEL_METRICS_EXPORTER=console`을 대화형 세션에서 썼을 때의 화면.** 문서에 옵션으로 있지만 실행해 보지 않았다. 3절에는 OTLP 수집기 방식만 적었다.
- **Langfuse 플러그인의 전송 시점과 사용하는 훅 이벤트.** README에 없다. 플러그인 소스(`hooks/hooks.json`)는 읽지 않았다. "리전 주소가 틀리면 인증 오류"도 README에는 없다.
- **`/goal`의 최소 버전.** 문서의 Requirements 절에는 작업 공간 신뢰·`disableAllHooks`·`allowManagedHooksOnly` 조건만 있고 버전 숫자가 없다. 2.1.322의 명령 표에는 있다.
- **가이드 A9의 60~65%/80% 수치와 A7의 "20턴"의 출처.** 공식 문서에 없다. 출처를 찾지 못했다.
- **상태줄 `prompt_cache` 객체의 실제 값.** 문서의 스키마와 샘플만 썼다. 실제 세션 입력으로 스크립트를 돌려 보지는 않았다.
- **Windows 동작.** 훅 경로의 역슬래시, Git Bash 없는 환경의 실패 처리(문서에 별도 절이 있다)는 수정안에 반영하지 않았다. `plan_gate.py`의 `ALLOW_PREFIXES` 비교는 `as_posix()`를 써서 구분자 문제는 없을 것으로 보이나 실행해 보지 않았다.
- **MCP 문서(`mcp.md`) 전체, 플러그인 마켓플레이스 작성(`create-marketplace`, `marketplace-reference`), 헤드리스 문서 전체.** 필요한 절만 읽었다. 마켓플레이스 파일(`.claude-plugin/marketplace.json`)의 필드는 정리하지 않았다.
