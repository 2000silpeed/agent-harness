# R1 — 설정·메모리(A0~A3) 공식 문서 검증

- 조사일: 2026-11-11. 로컬 CLI `claude --version` = 2.1.322.
- 출처: `https://code.claude.com/docs/llms.txt` 색인에서 고른 공식 페이지의 `.md` 원문(memory, settings, settings-reference, settings-example, permissions, permission-modes, sandboxing, claude-directory, context-window, how-claude-code-works, features-overview, env-vars, model-config, llm-gateway-connect, best-practices, costs, commands, cli-reference, statusline, debug-your-config, prompt-caching, skills, hooks, mcp, managed-settings). 블로그는 쓰지 않았다.
- 스키마: `https://json.schemastore.org/claude-code-settings.json` (최상위 속성 142개, `additionalProperties: true`).
- 인용문은 원문 그대로다. 표에서 가져온 인용은 여러 칸·여러 행을 " / "로 이어 붙였고, 생략한 곳은 "..."로 표시했다. URL은 `https://code.claude.com/docs/en/` 뒤에 붙는 페이지 이름으로 적었다. `#` 뒤는 해당 절의 제목이며 실제 앵커 문자열과 조금 다를 수 있다.
- 실제 세션을 띄워 동작을 재현하지는 않았다(중첩 세션 미실행). 재현하지 못한 항목은 5절에 모았다.

---

## 1. 확인된 사실

### 1-1. 세션 시작 시 무엇이 어떤 형태로 로드되는가

| 주장 | 원문 인용 | URL |
|---|---|---|
| 시작 시 자동 로드: CLAUDE.md, 자동 메모리, MCP 도구 이름, 스킬 설명 | "**Before you type anything**: CLAUDE.md, auto memory, MCP tool names, and skill descriptions all load into context. AGENTS.md files can load in place of CLAUDE.md. Your own setup may add more here, like an output style or text from `--append-system-prompt`." | context-window#what-the-timeline-shows |
| CLAUDE.md는 시스템 프롬프트가 아니라 유저 메시지로 들어간다 | "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance" | memory#claude-isn't-following-my-claude-md |
| 여러 CLAUDE.md는 덮어쓰지 않고 이어붙는다 | "All discovered files are concatenated into context rather than overriding each other. Across the directory tree, content is ordered from the filesystem root down to your working directory." | memory#how-claude-md-files-load |
| 요청은 3개 층으로 정렬된다 (캐시 관점) | "System prompt: Core instructions, tool definitions / Project context: CLAUDE.md, auto memory, unscoped rules / Conversation: Your messages, Claude's responses, tool results" | prompt-caching |
| 세션 중 CLAUDE.md를 고쳐도 반영되지 않는다 | "Your project-root and user-level CLAUDE.md files are read once at session start and held in memory. Editing them mid-session does not invalidate the cache, but the edit also doesn't apply. ... The new content loads on the next `/clear`, `/compact`, or restart." | prompt-caching#editing-claude-md-mid-session |
| 자동 메모리는 `MEMORY.md` 앞 200줄 또는 25KB만 로드 | "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation. Content beyond that threshold is not loaded at session start." | memory#how-it-works |
| 자동 메모리의 주제 파일은 시작 시 로드되지 않는다 | "Claude Code doesn't load topic files such as `user_role.md` or `feedback_testing.md` at startup. Claude reads them on demand using its standard file tools" | memory#how-it-works |
| CLAUDE.md는 4 MiB 이하면 통째로 로드 | "Claude gets the whole of each CLAUDE.md file that loads at launch, as long as the file is 4 MiB or smaller. Claude Code skips a file over 4 MiB and loads none of it." | memory#how-it-works |
| 스킬 설명 목록 예산은 컨텍스트 윈도우의 1% | "The listing always contains every skill name, but if you have many skills, Claude Code drops some descriptions to fit the listing's character budget ... The budget scales at 1% of the model's context window. When the listing overflows, Claude Code drops descriptions starting with the skills you invoke least" | skills#skill-descriptions-are-cut-short |
| 스킬 한 개당 설명 상한 1,536자 | "each entry's combined text is capped at 1,536 characters regardless of budget. The cap is configurable with `skillListingMaxDescChars`." (키: `skillListingBudgetFraction` 기본 `0.01`, `skillListingMaxDescChars` 기본 `1536`) | skills#skill-descriptions-are-cut-short, settings-reference#skilllistingbudgetfraction |
| 스킬 본문은 쓸 때만 로드. `disable-model-invocation: true`면 설명도 안 올라간다 | "By default, descriptions load at session start and full content loads when used. For user-only skills (`disable-model-invocation: true`), nothing loads until you invoke them." | features-overview#understand-how-features-load |
| MCP는 도구 이름과 서버 지침만, 스키마는 지연 로드 | "**What loads:** Tool names and server instructions from connected servers. Full JSON schemas stay deferred until Claude needs a specific tool." / "Tool search is on by default, so idle MCP tools consume minimal context." | features-overview#understand-how-features-load |
| 훅은 컨텍스트 비용 0 (출력을 돌려줄 때만 비용) | "**Context cost:** Zero, unless the hook returns output that gets added as messages to your conversation." | features-overview#understand-how-features-load |
| 압축(compaction) 뒤 살아남는 것 | "Project-root CLAUDE.md and unscoped rules: Re-injected from disk / Auto memory: Re-injected from disk / Rules with `paths:` frontmatter: Claude Code reloads them on demand / Nested CLAUDE.md in subdirectories: Claude Code reloads them on demand / Invoked skill bodies: Re-injected, capped at 5,000 tokens per skill and 25,000 tokens total; oldest dropped first" | context-window#what-survives-compaction |
| Claude Code가 스스로 넣는 컨텍스트 | "As you work, Claude Code adds its own context to the conversation alongside your messages: Your CLAUDE.md files / The instructions of your output style / A note when a file Claude read earlier changes on disk / The commit and pull request attribution lines" | how-claude-code-works#context-claude-code-adds-on-its-own |
| git 지침과 git 상태 스냅샷도 기본으로 들어간다 | "Claude Code gives Claude two git-related pieces of context: its built-in instructions for how to write commits and pull requests, in the Bash tool's description, and a git status snapshot of your repository." (`includeGitInstructions`, 기본 `true`) | settings-reference#includegitinstructions |
| 부탁과 강제의 구분은 공식 용어로 non-deterministic / deterministic | "Non-deterministic: you write the instruction, and Claude (the model) reads it. This can be your prompt, `CLAUDE.md`, or a skill. ... Deterministic: you configure the instruction, and Claude Code (the harness) *has* to execute this. This can be a hook, a deny rule, or a managed setting." | best-practices#deterministic-and-non-deterministic-instructions |
| 서브에이전트: 내장 Explore·Plan은 CLAUDE.md를 읽지 않는다 | "The built-in Explore and Plan agents skip `CLAUDE.md` at startup. A custom subagent loads it the same way the main conversation does, unless it has `omitClaudeMd` set" | debug-your-config#check-common-causes |

### 1-2. CLAUDE.md 위치·순서·import·크기

| 주장 | 원문 인용 | URL |
|---|---|---|
| 위치 4종과 로드 순서(넓은 범위 → 좁은 범위) | "The table below lists them in load order, from broadest scope to most specific": Managed policy(macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`, Linux·WSL `/etc/claude-code/CLAUDE.md`, Windows `C:\Program Files\ClaudeCode\CLAUDE.md`) → User `~/.claude/CLAUDE.md` → Project `./CLAUDE.md` or `./.claude/CLAUDE.md` → Local `./CLAUDE.local.md` | memory#choose-where-to-put-claude-md-files |
| 상위 디렉터리는 시작 시, 하위 디렉터리는 필요할 때 | "CLAUDE.md and CLAUDE.local.md files in the directory hierarchy above the working directory are loaded at launch. Files in subdirectories load on demand." | 같은 곳 |
| 하위 디렉터리 파일이 로드되는 조건 | "Claude Code loads each one once Claude reads, writes, or edits another file in that subdirectory. Reading includes viewing the file with a Bash command that counts as a read, such as `cat` or `head` on a single file." | memory#how-claude-md-files-load |
| 같은 디렉터리에서는 `CLAUDE.local.md`가 뒤에 붙는다 | "Within each directory, `CLAUDE.local.md` is appended after `CLAUDE.md`, so your personal notes are the last thing Claude reads at that level." | 같은 곳 |
| 충돌하면 어느 쪽을 따를지 보장 없음 | "if two instructions contradict each other, Claude may pick one arbitrarily." | memory#write-effective-instructions |
| 권장 크기 200줄 | "**Size**: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." | 같은 곳 |
| 공식 권장 구조는 마크다운 헤더와 불릿 | "**Structure**: group related instructions under markdown headers and bullets. Organized sections are easier for Claude to follow than dense paragraphs." | 같은 곳 |
| 구체적으로 쓰라는 기준 | "\"Use 2-space indentation\" instead of \"Format code properly\" / \"Run `npm test` before committing\" instead of \"Test your changes\"" | 같은 곳 |
| import 문법과 깊이 | "CLAUDE.md files can import additional files using `@path/to/import` syntax. ... Relative paths resolve relative to the file containing the import, not the working directory. Imported files can recursively import other files, with a maximum depth of four hops." | memory#import-additional-files |
| import는 비용을 줄이지 않는다 | "Imports help you organize a long file but don't reduce its context cost, because imported files load together with the CLAUDE.md that imports them." | memory#write-effective-instructions |
| 경로를 import 없이 적으려면 백틱 | "Import parsing skips Markdown code spans and fenced code blocks. ... writing `` `@README` `` keeps the text literal, while `@README` outside backticks imports the file." | memory#import-additional-files |
| 작업 디렉터리 밖 import는 승인 창 | "The first time Claude Code encounters external imports in a project, it shows an approval dialog listing the files. If you decline, the imports stay disabled and the dialog doesn't appear again." | 같은 곳 |
| HTML 주석은 토큰을 쓰지 않는다 | "Block-level HTML comments (`<!-- maintainer notes -->`) in CLAUDE.md files are stripped before the content is injected into Claude's context. ... Comments inside code blocks are preserved." | memory#how-claude-md-files-load |
| 길이 경고 | "If one of your instruction files is over the recommended length, you see a warning at startup and when you run `/status`. ... Each CLAUDE.md, rules file, and `@path` import counts as a separate file." | memory#my-claude-md-is-too-large |
| 무엇을 넣을지 | "the file works best when it only holds what Claude couldn't work out from the code itself: How to confirm work in this repo ... Places where the code is misleading ... Decisions that aren't in the repo ... Anything you've had to correct twice already" | best-practices#keep-claude-md-short |
| 언제 추가할지(두 번 규칙) | "Add to it when: Claude makes the same mistake a second time / A code review catches something Claude should have known about this codebase / You type the same correction or clarification into chat that you typed last session / A new teammate would need the same context to be productive" | memory#when-to-add-to-claude-md |
| 승격 순서 표 | "Claude gets a convention or command wrong twice → Add it to CLAUDE.md / You paste the same playbook or multi-step procedure into chat for the third time → Capture it as a skill / You want something to happen every time without asking → Write a hook / A second repository needs the same setup → Package it as a plugin" | features-overview#build-your-setup-over-time |
| 강조를 더해도 안 지켜지면 훅으로 | "If Claude keeps ignoring a line that *is* in `CLAUDE.md`, adding IMPORTANT probably won't fix it. Either the file has grown long enough that the line gets lost, or the line is a rule that can't have exceptions, in which case it belongs in a hook." | best-practices#keep-claude-md-short |
| 압축 때 남길 내용을 지정하는 구역 | "To control what's preserved during compaction, add a \"Compact Instructions\" section to CLAUDE.md or run `/compact` with a focus" | how-claude-code-works#when-context-fills-up |
| 모노레포에서 남의 CLAUDE.md 제외 | "The `claudeMdExcludes` setting lets you skip specific files by path or glob pattern. You can't exclude a managed CLAUDE.md file with `claudeMdExcludes`." / "Patterns are matched against absolute file paths using glob syntax." | memory#exclude-specific-claude-md-files |
| `--add-dir` 디렉터리의 CLAUDE.md는 기본으로 안 읽는다 | "By default, CLAUDE.md files from these directories are not loaded." (`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`이면 읽음) | memory#load-from-additional-directories |

### 1-3. `.claude/rules/`

| 주장 | 원문 인용 | URL |
|---|---|---|
| `paths` 없는 규칙은 시작 시 로드 | "Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`." | memory#set-up-rules |
| 하위 폴더까지 재귀 탐색 | "All `.md` files are discovered recursively, so you can organize rules into subdirectories like `frontend/` or `backend/`" | 같은 곳 |
| frontmatter는 `paths` 하나뿐 | "`paths` is the only field Claude Code reads from a rule; any other field is ignored without an error. Claude Code removes the frontmatter before loading the rule into context." / "Accepts a YAML list or a comma-separated string" | memory#rule-frontmatter-reference |
| 경로 규칙이 로드되는 시점 | "A path-scoped rule loads when Claude uses the Read, Write, or Edit tool on a matching file. It also loads when Claude views a matching file with a Bash command that counts as a read, such as `cat` or `head` on a single file." | memory#path-specific-rules |
| 패턴 기준 디렉터리 | "**Project rules**: the directory that contains the rule's `.claude` folder / **User-level rules**: the session's primary working directory" | 같은 곳 |
| 패턴 예시 | "`**/*.ts`: `.ts` files anywhere under the base directory / `*.md`: `.md` files anywhere under the base directory / `/*.md`: `.md` files directly in the base directory, not in subfolders" / 중괄호 확장 `"src/**/*.{ts,tsx}"` | 같은 곳 |
| YAML이 깨지면 조건 없이 로드 | "If the YAML between the markers doesn't parse, Claude Code ignores the frontmatter and loads the rule as if it had no `paths`. Run `claude --debug` to see the parse error." | memory#rule-frontmatter-reference |
| 경로 규칙·하위 CLAUDE.md는 파일당 크기 제한 | "**200K context window**: 40,000 characters / **1M context window**: 200,000 characters on Claude Opus 4.6 and Claude Sonnet 4.6, and 150,000 characters on later models" ... "Claude receives only the start of it." | memory#claude-ignores-the-end-of-my-subdirectory-claude-md |
| 경로 규칙은 압축 때 사라진다 | "Path-scoped rules and nested CLAUDE.md files load into message history when Claude reads, writes, or edits their trigger file, so compaction summarizes them away with everything else. If a rule must persist across compaction, drop the `paths:` frontmatter or move it to the project-root CLAUDE.md." | context-window#what-survives-compaction |
| 사용자 수준 규칙 | "Personal rules in `~/.claude/rules/` apply to every project on your machine." / "Claude Code loads user-level rules before project rules" | memory#user-level-rules |
| 규칙과 스킬의 차이 | "Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use skills instead" | memory#organize-rules-with-claude/rules/ |
| 로드 여부를 기록하는 훅 | "Use the `InstructionsLoaded` hook to log which `CLAUDE.md` and rules files are loaded, when they load, and why." / `load_reason`: "`session_start`, `nested_traversal`, `path_glob_match`, `include`, or `compact`" | memory#troubleshoot-memory-issues, hooks#instructionsloaded |

### 1-4. AGENTS.md / CLAUDE.local.md

| 주장 | 원문 인용 | URL |
|---|---|---|
| AGENTS.md를 직접 읽는다 (v2.1.277+) | "Claude Code can read `AGENTS.md` as your project instructions, so a repository already set up for other coding agents works without adding a `CLAUDE.md`, an import, or a setting." / "Reading `AGENTS.md` directly requires Claude Code v2.1.277 or later." | memory#agents-md |
| 기본 동작: CLAUDE.md가 없을 때만 | "By default, Claude reads `AGENTS.md` only when you have no `CLAUDE.md` in your working directory or above it." | memory#when-claude-code-reads-agents-md |
| 무엇이 AGENTS.md를 막는가 | "**Count, so Claude reads them instead of `AGENTS.md`**: a `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` in your working directory or any directory above it / **Don't count, and keep loading alongside `AGENTS.md`**: your `~/.claude/CLAUDE.md`, your organization's managed `CLAUDE.md`, and `.claude/rules/` files" | 같은 곳 |
| `CLAUDE.local.md`가 AGENTS.md를 끈다 | "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you. To keep your `CLAUDE.local.md` and still have Claude read `AGENTS.md`, set **Project instructions** to `claude-md-and-agents-md`." | 같은 곳 |
| 설정값 4개 | "`claude-md-or-agents-md` ... This is the default / `claude-md-and-agents-md` / `claude-md` / `managed-only`" (`/config` → **Project instructions**) | memory#choose-which-instruction-files-load |
| 설정 파일로 지정할 때의 위치 제한 | "Add it to `pluginConfigs` under `cc-plugin-agents-md@builtin` ... Claude Code reads the entry from `~/.claude/settings.json`, a `--settings` file, or managed settings, and ignores it in project and local settings files." | 같은 곳 |
| 읽지 않는 파일 | "**Not read**: `AGENTS.local.md`, `AGENTS.override.md`, or anything under a `.agents/` directory" | memory#when-claude-code-reads-agents-md |
| 한 파일을 원본으로 두는 방법 | "you can still keep it as the one file every tool shares by putting an `@AGENTS.md` import in a `CLAUDE.md` next to it. ... Add any Claude-specific instructions below the import" / 심볼릭 링크 `ln -s AGENTS.md CLAUDE.md`도 가능하나 "if you or anyone who clones the repository works on Windows, use the `@AGENTS.md` import instead." | memory#share-one-file-with-other-coding-tools |
| 로드 확인 메시지 | "In an interactive session you see a line such as `no CLAUDE.md found; AGENTS.md loaded: /home/you/repo/AGENTS.md` in the conversation" / "To check whether Claude read your `AGENTS.md`, run `/memory` and look for its path in the list." | memory#when-claude-code-reads-agents-md, memory#my-agents-md-isn't-loading |
| CLAUDE.local.md | "create a `CLAUDE.local.md` at the project root. It loads alongside `CLAUDE.md` and is treated the same way. Add `CLAUDE.local.md` to your `.gitignore` so it isn't committed." | memory#import-additional-files |
| 워크트리에서는 CLAUDE.local.md가 따라오지 않는다 | "a gitignored `CLAUDE.local.md` only exists in the worktree where you created it. To share personal instructions across worktrees, import a file from your home directory instead: `- @~/.claude/my-project-instructions.md`" | 같은 곳 |

### 1-5. 자동 메모리

| 주장 | 원문 인용 | URL |
|---|---|---|
| 위치 | "Each project gets its own memory directory at `~/.claude/projects/<project>/memory/`. The `<project>` path is derived from the git repository, so all worktrees and subdirectories within the same repo share one auto memory directory." | memory#storage-location |
| 내 PC에만 있다 | "Auto memory is machine-local. ... Files are not shared across machines or cloud environments." | 같은 곳 |
| 기본 켜짐 | "Auto memory is on by default in local sessions." | memory#enable-or-disable-auto-memory |
| 끄는 법 3가지 | "open `/memory` in a session and use the auto memory toggle, which saves `autoMemoryEnabled` to your user settings" / 프로젝트만: `{"autoMemoryEnabled": false}` / "set `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`" | 같은 곳 |
| 위치 바꾸기 | "`autoMemoryDirectory` ... The value must be an absolute path or start with `~/`." | memory#storage-location |
| 무엇을 저장하나 | "`user` / `feedback` / `project` / `reference`" ... "Claude skips anything it can derive from the codebase ... It also skips anything your CLAUDE.md files already say." | memory#auto-memory |
| 들여다보는 법 | "Run `/memory` and select the auto memory folder to browse what Claude has saved. Everything is plain markdown you can read, edit, or delete." | memory#i-don't-know-what-auto-memory-saved |
| "기억해"라고 하면 자동 메모리에 저장 | "When you ask Claude to remember something ... Claude saves it to auto memory. To add instructions to CLAUDE.md instead, ask Claude directly, like \"add this to CLAUDE.md,\"" | memory#view-and-edit-with-/memory |
| 보존 기간 정리에서 제외 | "Claude Code deletes old session transcripts after the `cleanupPeriodDays` retention period, but excludes the memory files in the memory directory from that retention sweep." | memory#storage-location |
| 서브에이전트에는 안 들어간다 | "The main conversation's auto memory isn't loaded into subagents; the exception is a fork" | memory#how-it-works |

### 1-6. 로드 상태를 보는 명령 (모두 commands 페이지에 존재)

| 명령 | 원문 인용 | URL |
|---|---|---|
| `/context [all]` | "The `/context` command shows everything occupying the context window for the current session. It breaks this down by category: system prompt, system tools, MCP tools, custom subagents with the source each loaded from, memory files, skills, and conversation messages." / "In fullscreen mode, `/context` collapses the per-item breakdown, so run `/context all` to expand it." | debug-your-config#see-what-loaded-into-context |
| `/memory` | "Edit `CLAUDE.md` files, enable or disable auto memory, and view auto memory entries" | commands |
| `/init` | "Initialize project with a `CLAUDE.md` guide. Set `CLAUDE_CODE_NEW_INIT=1` for an interactive flow that also walks through skills, hooks, and personal memory files." / "If a CLAUDE.md already exists, `/init` suggests improvements rather than overwriting it." | commands, memory#set-up-a-project-claude-md |
| `/doctor [prompt-audit [path]]` | "Run a setup checkup that diagnoses installation, settings, extension, and `CLAUDE.md` problems and proposes fixes that Claude applies after you confirm." / "`/doctor prompt-audit` requires Claude Code v2.1.283 or later." | commands, memory#audit-your-instruction-files |
| `claude doctor` (터미널) | "Print read-only installation and settings diagnostics from the terminal without starting a session, including install health, settings-file validation errors" | cli-reference |
| `/status` | "The **Status** tab includes a `Setting sources` line that lists each settings file Claude Code loaded for the current session" / "The line confirms which files Claude Code read; it doesn't show which file supplied each key." | settings#confirm-what-loaded |
| `/permissions` | "The dialog lists all permission rules and the `settings.json` file each rule comes from." | permissions#manage-permissions |
| `/skills`, `/hooks`, `/mcp`, `/debug` | 표: "`/skills`: Available skills from project, user, and plugin sources / `/hooks`: Active hook configurations / `/mcp`: Connected MCP servers and their status" | debug-your-config#see-what-loaded-into-context |
| `/config` | "It lists a short set of personal options such as theme, editor mode, and verbose output, not every settings key." / "`/status` and `/config` open the same dialog on different tabs, and the **Config** tab isn't a view of your `settings.json` contents." | settings#use-the-/config-menu |
| `/model`, `/effort`, `/statusline`, `/sandbox`, `/usage`(`/cost`는 별칭), `/skill-doctor`, `/import`, `/fewer-permission-prompts`, `/auto-mode-setup` | commands 표에 모두 있음 | commands |
| 깨끗한 설정으로 비교 | "Start with `claude --safe-mode`, which launches a session with your customizations disabled" / "`CLAUDE_CONFIG_DIR=~/claude-clean/config claude --setting-sources user`" | debug-your-config#test-against-a-clean-configuration |

### 1-7. 설정 파일 범위와 우선순위

| 주장 | 원문 인용 | URL |
|---|---|---|
| 파일 4개 | "User `~/.claude/settings.json` / Shared project `.claude/settings.json` / Project local `.claude/settings.local.json` / Managed `managed-settings.json` and other managed sources" | settings#settings-files-and-who-they-affect |
| 우선순위 | "Settings precedence, highest first: managed settings, command line, project local, shared project, user." (command line = `--settings <file-or-json>`) | settings#settings-precedence |
| 환경 변수는 이 순서에 없다 | "Environment variables aren't a level in this stack. ... `ANTHROPIC_MODEL` exported in your shell applies over the `model` key from any file" / "An `env` block inside a settings file is an ordinary key and follows the levels above." | 같은 곳 |
| 배열은 합쳐진다 | "When you set the same list key, such as `permissions.allow`, in more than one file, Claude Code combines the lists instead of picking one" | settings#lists-merge-instead-of-overriding |
| 설치만으로는 파일이 안 생긴다 | "Installing Claude Code doesn't create any settings file." | settings#find-or-create-your-settings-files |
| 엄격한 JSON | "Settings files are strict JSON: a `//` comment or a trailing comma is a syntax error, and Claude Code reports the file as a Settings Error at the next start." | settings#edit-a-settings-file |
| `$schema` | "The `$schema` line points to the published JSON schema ... The schema can lag behind the newest CLI releases, so a validation warning on a recently documented key doesn't mean your configuration is invalid." | 같은 곳 |
| 재시작 없이 반영 | "Claude Code watches your settings files and reloads them when they change, so it applies most edits to the running session without a restart, including edits to `permissions`, `hooks`" (예외: `model`, `effortLevel`, `modelSettings`는 시작 시 한 번만 읽음) | settings#when-edits-take-effect |
| 로컬 파일의 gitignore | "The first time Claude Code writes the file in a git repository that doesn't already ignore it, it adds `**/.claude/settings.local.json` to your global git excludes file ... If you created the file by hand and Claude Code hasn't written to it yet, add it to `.gitignore` yourself." | settings#keep-personal-settings-out-of-a-repository |
| 로컬 파일은 저장소 루트에 둔다 | "If you start Claude Code in a subdirectory of a git repository, it reads and writes that file at the repository root" (예외: 저장소 밖, Windows 등) | settings#where-claude-code-keeps-the-local-file-in-a-git-repository |
| 공유 프로젝트 설정은 시작 디렉터리에서만 | "Hooks and other `.claude/settings.json` keys load from the current working directory's `.claude/` folder with no parent-directory fallback" | permissions#where-output-styles-hooks-and-local-settings-load-from |
| `~/.claude.json`은 다른 파일 | "`~/.claude.json` holds app state and UI toggles. `permissions`, `hooks`, and `env` belong in `~/.claude/settings.json`. These are two different files." | debug-your-config#check-common-causes |
| MCP는 settings.json에 두지 않는다 | "`settings.json` does not read an `mcpServers` key. Define project servers in `.mcp.json` at the repository root, or run `claude mcp add --scope user` for user-scoped servers." | 같은 곳 |
| MCP 범위별 저장 위치 | "Local: `~/.claude.json` / Project: `.mcp.json` in project root / User: `~/.claude.json`" | mcp#mcp-installation-scopes |
| 커밋한 키가 팀원에게 안 먹는 두 경우 | "**Claude Code ignores the key in a repository file.** Look for `User, local, or managed`, `User or managed`, `User`, `Managed`, or `Global config` in the Scope column" / "**The key waits for trust.** `permissions.allow` rules, `permissions.additionalDirectories`, `extraKnownMarketplaces`, and most `env` values apply only after each teammate trusts the folder. ... `deny` and `ask` rules apply right away." | settings#a-committed-key-doesn't-reach-teammates |
| 클라우드 세션은 커밋된 프로젝트 설정만 | "**User and project local settings** (`~/.claude/settings.json` and `.claude/settings.local.json`): not read." | settings#settings-in-cloud-sessions |
| 관리 설정 파일 위치 | "macOS: `/Library/Application Support/ClaudeCode/managed-settings.json` / Linux and WSL: `/etc/claude-code/managed-settings.json`" | managed-settings |

### 1-8. 권한 규칙·모드·샌드박스

| 주장 | 원문 인용 | URL |
|---|---|---|
| 평가 순서 | "Rules are evaluated in order: deny, then ask, then allow. The first match in that order determines the outcome, and rule specificity doesn't change the order." | permissions#manage-permissions |
| deny에서 예외를 뺄 수 없다 | "An allow rule can't carve an exception out of a deny rule." | 같은 곳 |
| 어느 범위의 deny든 이긴다 | "If a tool is denied at any level, no other level can allow it." / "a user-level deny blocks a project-level allow" | permissions#settings-precedence |
| 규칙 형식 | "Permission rules follow the format `Tool` or `Tool(specifier)`." 예: "`Bash(npm run build)` / `Read(./.env)` / `WebFetch(domain:example.com)`" | permissions#permission-rule-syntax |
| 도구 이름만 쓴 deny는 도구를 컨텍스트에서 뺀다 | "A bare tool name like `Bash` removes the tool from Claude's context entirely, so Claude never sees it. ... A scoped rule like `Bash(rm *)` leaves the tool available and blocks matching calls" | permissions#manage-permissions |
| Bash 와일드카드 | "A `*` in a Bash rule matches any text, including spaces" / "`Bash(ls *)` requires a space after `ls`, so `lsof` doesn't match." / "The `:*` suffix is an equivalent way to write a trailing wildcard" | permissions#wildcard-patterns |
| 복합 명령 | "a rule like `Bash(safe-cmd *)` won't give it permission to run the command `safe-cmd && other-cmd`." | permissions#compound-commands |
| Bash deny는 보안 경계가 아니다 | "a deny or ask rule covers the invocation Claude usually produces and isn't a security boundary around the program." 예: `Bash(rm *)`는 `/bin/rm -rf build/`, `bash -c 'rm -rf build/'`를 못 막음 | permissions#what-a-bash-rule-doesn't-match |
| Read·Edit 경로 패턴 4종 | "`//path`: Absolute path from filesystem root / `~/path`: Path from home directory / `/path`: Path relative to the settings source / `path` or `./path`: Path relative to current directory" (gitignore 문법) | permissions#how-path-patterns-match |
| 사용자 설정에서 `/path`는 `~/.claude/` 기준 | "A deny rule such as `Read(/secrets/**)` in user settings blocks `~/.claude/secrets/**`, not a `secrets` directory in your project. To write a rule in user settings that applies inside every project, use a `//` absolute path or a `~/` home-relative path instead." | permissions#where-a-pattern-anchors |
| 파일 이름만 쓰면 모든 깊이 | "Bare filenames follow gitignore semantics and match at any depth, so `Read(.env)` and `Read(**/.env)` are equivalent" | permissions#how-deep-a-pattern-matches |
| Read deny가 막는 범위 | "Read and Edit deny rules apply to Claude's built-in file tools, to file commands Claude Code recognizes in Bash, such as `cat`, `head`, `tail`, `sed`, and `tee`, and to the targets of Bash redirections ... They don't apply to a command that reads files without naming them, such as `grep -r pattern .` ... or to arbitrary subprocesses" | permissions#what-read-and-edit-rules-cover |
| Read deny는 Edit·Write도 막는다 | "A `Read` deny rule also blocks the Edit and Write tools on the same path, including creating a new file there. NotebookEdit isn't covered" | 같은 곳 |
| `Write(path)`·`Grep(path)`는 동작하지 않는다 | "use `Edit(docs/**)` in place of `Write(docs/**)`" / "use `Read(docs/**)` in place of `Grep(docs/**)`" | permissions#write-path-glob-path-and-grep-path-rules-don't-match |
| `.claudeignore`는 효과 없음 | "If your project has a `.claudeignore` file, it has no effect, so move its entries into `Read` deny rules." | permissions#read-and-edit |
| `!` 부정 패턴 | "In one settings file's `deny` list, `Read(*.env)` followed by `Read(!sample.env)` blocks every file whose name ends in `.env` at any depth, except files named `sample.env`." | permissions#special-characters-and-!-negation |
| 프로젝트 allow는 신뢰 뒤에 적용 | "`permissions.allow` rules and `permissions.additionalDirectories` entries in a project's `.claude/settings.json` grant capability, so Claude Code applies them only after you accept the workspace trust dialog ... `deny` and `ask` rules aren't affected, since they only restrict." | permissions#project-allow-rules-and-workspace-trust |
| 규칙은 모델이 아니라 하네스가 집행 | "Permission rules are enforced by Claude Code, not by the model. Instructions in your prompt or `CLAUDE.md` shape what Claude tries to do, but they don't change what Claude Code allows." | permissions#manage-permissions |
| 모드 6개: `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` | "`default`: Prompts for permission on first use of each tool. Labeled Manual in the CLI, the VS Code and JetBrains extensions, and the desktop app, and Claude Code accepts `manual` as an alias" / "`dontAsk`: Auto-denies every call that would otherwise prompt" / "`bypassPermissions`: Skips permission prompts, except for the actions no mode auto-approves" | permissions#permission-modes |
| deny는 모든 모드에서 유효 | "Deny rules block in every mode, including `bypassPermissions`. ... Allow rules have no effect in `bypassPermissions`." | permission-modes#available-modes |
| 시작 모드 결정 순서 | "1. The `--permission-mode` flag, or `--dangerously-skip-permissions` 2. `permissions.defaultMode` in a settings file 3. The built-in default" | permission-modes#which-mode-a-session-starts-in |
| 기본 시작 모드는 auto | "In a terminal or through the VS Code extension: `auto` with Claude Code v2.1.283 or later" / "`claude -p` or the Agent SDK: `default`" | 같은 곳 |
| `auto`·`bypassPermissions`는 프로젝트·로컬 파일에서 무효 | "`auto` and `bypassPermissions` don't take effect from project or local settings, so set them in `~/.claude/settings.json` instead." | settings-reference#permissions-defaultmode |
| auto 모드는 강제가 아니다 | "Auto mode is a classifier model judging each action rather than a hard rule. ... so your \"never\" rules belong in deny rules or hooks." | best-practices#limit-access-with-permission-rules-and-the-sandbox |
| 모드 끄기 | "set `permissions.disableBypassPermissionsMode` or `permissions.disableAutoMode` to `\"disable\"` in any settings file." | permissions#permission-modes |
| 보호 경로 | "`.git`, `.config/git`, `.vscode`, `.idea`, `.husky`, ... `.claude`, with a few exceptions" / "`permissions.allow` rules in settings files do not pre-approve protected-path writes." | permission-modes#protected-paths |
| 샌드박스는 기본 꺼짐, 셸 명령만 감쌈 | "The sandbox is off by default. To turn it on, run `/sandbox` in a session ... or set `sandbox.enabled` to `true`" / "The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it." / "The sandbox runs on macOS, Linux, and WSL2. On native Windows, Claude Code runs commands unsandboxed." | sandboxing |
| 샌드박스가 Read deny의 구멍을 메운다 | "`Read(./.env)` on its own stops the file tools and commands that name the file, such as `cat .env`, but not `grep -r` run over the directory; the `sandbox` block in this file closes that gap, because the sandbox adds your `Read` deny paths to what every sandboxed command can't read." | settings-example#a-teams-shared-settings |
| 샌드박스를 못 쓰면 조용히 비샌드박스로 실행 | "By default, when the platform doesn't support the sandbox or the dependency check at startup fails, Claude Code runs commands without sandboxing. To make Claude Code exit at startup instead, set `sandbox.failIfUnavailable` to `true`." | sandboxing#get-started |
| 샌드박스 동작 확인 명령 | "`touch ~/sandbox-probe`: Fails with `Operation not permitted` on macOS, or `Read-only file system` on Linux and WSL2 / `curl --noproxy '*' https://example.com`: Fails with `Could not resolve host`" (Claude에게 시켜야 한다. `!`로 직접 치면 샌드박스 밖) | sandboxing#confirm-commands-run-inside-the-sandbox |
| 훅과 규칙의 우선 관계 | "PreToolUse hook decisions don't bypass permission rules. ... a matching deny rule blocks the call, and a matching ask rule still prompts even when the hook returned `\"allow\"`" / "A hook that exits with code 2 stops the tool call before permission rules are evaluated" | permissions#precedence-among-rules-hooks-and-mods |

### 1-9. `env`, 모델, effort, 상태줄, 보존 기간

| 주장 | 원문 인용 | URL |
|---|---|---|
| `env` 키 | "Set environment variables for every session and for the subprocesses Claude Code starts from it." / "**Type**: object mapping variable names to string values" | settings-reference#env |
| `env`는 셸 값을 덮는다 | "A value here overwrites the same variable exported in your shell" | settings-reference#how-env-values-interact-with-your-shell |
| `env` 값은 평문 | "Values here are plain text in the settings file and reach every subprocess Claude Code starts. ... for API credentials, use `apiKeyHelper`." | 같은 곳 |
| 프로젝트·로컬 `env`는 신뢰 뒤에 | "From project and local settings: after you trust the workspace, or at startup in `-p` mode" | settings-reference#when-claude-code-applies-env-values |
| 프로젝트·로컬 `env`가 못 정하는 변수 | "`CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR` ... `HOME`, `TMPDIR` ... The OpenTelemetry exporter variables" (`ANTHROPIC_BASE_URL`은 이 목록에 없다) | settings-reference#variables-claude-code-ignores-in-env |
| `~`·`$HOME`은 펼쳐지지 않는다 | "No shell processes them, so shorthand such as `~` or `$HOME` stays as typed." | env-vars#set-variables-in-settings-files |
| 게이트웨이 설정 방법 | "set the variables in the `env` block of a settings file ... `~/.claude/settings.json` applies to all your projects / `.claude/settings.local.json` applies to one project." 예시: `{"env": {"ANTHROPIC_BASE_URL": "https://llm-gateway.example.com", "ANTHROPIC_AUTH_TOKEN": "sk-gateway-key"}}` | llm-gateway-connect#set-in-a-settings-file |
| 자격 증명은 커밋되는 파일에 두지 않는다 | "Don't put the credential in a project's `.claude/settings.json`. That file is committed and shared with everyone who clones the repository." | 같은 곳 |
| 자격 증명 변수 선택 | "`ANTHROPIC_AUTH_TOKEN`: ... \"bearer token\" or \"Authorization header\" / `ANTHROPIC_API_KEY`: ... \"API key\" or \"x-api-key\" / `apiKeyHelper`: The credential rotates or comes from a vault" | llm-gateway-connect#set-the-credential-variable |
| 연결 확인 | "run `/status` ... `Anthropic base URL`: this line only appears when a gateway address is set." | llm-gateway-connect#check-for-an-existing-configuration |
| BASE_URL은 모델을 바꾸지 않는다 | "`ANTHROPIC_BASE_URL` changes where requests are sent, not which model answers them." | model-config#available-models |
| `ANTHROPIC_DEFAULT_SONNET_MODEL`은 별칭 매핑 | "`ANTHROPIC_DEFAULT_SONNET_MODEL`: The model to use for `sonnet`, or for `opusplan` when Plan Mode is not active." | model-config#environment-variables |
| 모델 지정 우선순위 | "1. During session: `/model` 2. At startup: `claude --model` 3. Environment variable: `ANTHROPIC_MODEL` 4. Settings: ... the `model` field 5. Default for new sessions: `ANTHROPIC_DEFAULT_MODEL`" | model-config#setting-your-model |
| `model` 키 | "**Scope**: `Any file` / **Type**: string, a model alias or full model ID" / 프로젝트 파일이 정하면 "the startup header shows which settings file set it" | settings-reference#model, model-config#setting-your-model |
| 로컬 파일로 팀 모델 덮기 | "if your team's file sets `\"model\": \"claude-sonnet-5\"` and you want Opus, put `\"model\": \"claude-opus-5-5\"` in your local file and only your sessions change." | settings#keep-personal-settings-out-of-a-repository |
| 기본 모델 | "**Pro, Max, Ultra, Team, Enterprise, and Anthropic API**: defaults to Opus 5.5" | model-config#default-model-setting |
| effort 수준과 기본값 | "Fable 5.2, Opus 5.5, Sonnet 5.5, and Haiku 5.5 default to `medium`, and Opus 4.7 defaults to `xhigh`. Other models in the effort levels table default to `high`." (수준: `low`, `medium`, `high`, `xhigh`, `max`) | model-config#adjust-effort-level |
| effort 결정 순서 | "1. The `CLAUDE_CODE_EFFORT_LEVEL` environment variable 2. A level you pick in the session, such as with `/effort` ... 3. Launching with `--effort` 4. Your settings ... 5. The model's default effort" | 같은 곳 |
| `/effort`는 모델별로 `modelSettings`에 저장 | "Claude Code saves the level per model, under the `modelSettings` key in your user settings" (v2.1.251+) | 같은 곳 |
| 사용자 파일의 `effortLevel`은 구형 | "In your user settings file, `~/.claude/settings.json`, this key is the older form ... Opus 5.5 and models released after it ignore it ... In project, local, and managed settings, and with `--settings`, this key applies to every model." 값: `"low"`, `"medium"`, `"high"`, `"xhigh"` | settings-reference#effortlevel |
| `max`는 세션 한정 | "Unless you set it through the `CLAUDE_CODE_EFFORT_LEVEL` environment variable, Claude Code applies `max` to the current session only." | model-config#adjust-effort-level |
| 상한 걸기 | "`maxEffortLevel`: Cap the effort level a session can use ... When several scopes set a cap, the lowest applies" (v2.1.267+) | settings-reference#maxeffortlevel |
| 모델을 바꾸면 캐시가 깨진다 | "Each model has its own prompt cache, so the first request after a switch re-reads the whole conversation uncached" | settings#when-edits-take-effect |
| `statusLine` 키 | "**Type**: object with `type` set to `\"command\"` and a `command` string, plus optional `padding` ..., `refreshInterval` ..., and `hideVimModeIndicator`" / "**Default**: unset, so no status line" | settings-reference#statusline |
| `/statusline` | "Claude Code generates a script file in `~/.claude/` and updates your settings automatically" | statusline#use-the-/statusline-command |
| 상태줄도 신뢰 필요 | "Until you accept the workspace trust dialog, the status line stays blank." | statusline#workspace-trust-required |
| `cleanupPeriodDays` | "**Type**: number of days, a whole number, minimum `1` / **Default**: `30`" / "Setting `0` fails validation" | settings-reference#cleanupperioddays |
| 대화 기록은 평문 | "Transcripts and history are not encrypted at rest. OS file permissions are the only protection. If a tool reads a `.env` file or a command prints a credential, that value is written to `projects/<project>/<session>.jsonl`." | claude-directory#plaintext-storage |
| 프로젝트 데이터 지우기 | "Run `claude purge` to delete the state Claude Code holds for one project." (`--dry-run` 있음. 자동 메모리도 지워짐) | claude-directory#clear-local-data |

### 1-10. 스키마 검증 결과

- `templates/settings.json`, `templates/settings.local.example.json`, `hooks/settings.example.json`: 스키마 검증 통과, 스키마에 없는 키 없음.
- 스키마에 있는 키: `$schema`, `permissions`(`allow`, `ask`, `deny`, `additionalDirectories`, `defaultMode`, `disableAutoMode`, `disableBypassPermissionsMode`), `env`, `model`, `effortLevel`(enum `low`·`medium`·`high`·`xhigh`), `statusLine`, `cleanupPeriodDays`(`minimum: 1`, `default: 30`), `autoMemoryEnabled`, `autoMemoryDirectory`, `sandbox`, `claudeMdExcludes`, `skillOverrides`, `disableBundledSkills`, `includeGitInstructions`, `attribution`, `hooks`, `apiKeyHelper`, `pluginConfigs`, `enabledMcpjsonServers`, `disabledMcpjsonServers`, `skillListingBudgetFraction`, `skillListingMaxDescChars`, `plansDirectory`.
- 스키마에 **없는** 키: `mcpServers`(공식 문서와 일치: settings.json은 이 키를 읽지 않는다). `modelSettings`, `maxEffortLevel`, `autoCompactWindow`, `permissions.blockReadsOutsideWorkingDirectories`도 없는데, 이 넷은 공식 문서에는 있다. 문서가 밝힌 대로 스키마가 뒤처진 것이다.
- 권한 규칙 문자열의 스키마 패턴: `^((Agent|Artifact|Bash|Cd|Edit|...|Read|...|WebFetch|WebSearch|Workflow|Write)(\([^)]+\))?|mcp__.*)$`. 우리 규칙 `Read(./.env)`, `Read(./.env.*)`, `Read(./secrets/**)`는 모두 통과.
- `env`의 스키마: 키 이름은 `^[A-Za-z_][A-Za-z0-9_]*$`, 값은 문자열. `ANTHROPIC_BASE_URL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`은 이름이 명시된 속성으로 올라 있다.

---

## 2. 현재 가이드에서 틀리거나 부정확한 곳과 수정안

줄 번호는 `claude-setup/GUIDE.md` 기준이다.

### 틀린 것

| 줄 | 현재 | 문제 | 수정안 |
|---|---|---|---|
| L103 | "`.claude/settings.json` 은 팀 공유(커밋): 훅, MCP, 권한 금지 목록" | MCP 서버는 settings.json에 두지 않는다. settings.json은 `mcpServers` 키를 읽지 않고, 팀 공유 MCP는 저장소 루트의 `.mcp.json`이다. | "`.claude/settings.json`은 팀 공유(커밋): 권한 규칙(deny·ask·allow), 훅, 플러그인, 프로젝트에 필요한 환경 변수. 팀 공유 MCP 서버는 저장소 루트의 `.mcp.json`에 둔다(`.claude/` 안이 아니다)." |
| L57 | "기본 모델과 추론 강도(effort)를 정한다." | 키 이름이 없고, 사용자 설정의 `effortLevel`은 구형 키라 Opus 5.5 이후 모델에서 무시된다. 손으로 `effortLevel`을 적으면 기대와 다르게 동작한다. | "기본 모델은 `/model`로 고른다(`model` 키로 사용자 설정에 저장된다). 추론 강도는 `/effort <수준>`으로 고른다. 모델별로 `modelSettings`에 저장된다. 사용자 설정에 `effortLevel`을 직접 적지 않는다(최신 모델은 무시한다)." |
| L105 | "이 프로젝트에서만 다른 모델·엔드포인트를 쓰려면 프로젝트 설정의 `env`에 둔다." | (1) 모델은 `env`가 아니라 `model` 키가 직접적인 방법이다. (2) `ANTHROPIC_BASE_URL`은 요청이 가는 곳만 바꾸고 모델은 바꾸지 않는다. (3) "프로젝트 설정"이 커밋되는 파일로 읽히는데, 자격 증명은 커밋되는 파일에 두면 안 된다. | "이 프로젝트에서만 다른 모델을 쓰려면 `model` 키를 둔다. 팀 전체면 `.claude/settings.json`, 나만이면 `.claude/settings.local.json`. 엔드포인트는 `env`의 `ANTHROPIC_BASE_URL`로 바꾼다. 인증 값은 커밋되는 파일에 절대 두지 않는다. 로컬 파일이나 `apiKeyHelper`를 쓴다. 전역은 건드리지 않는다." |

### 부정확하거나 모호한 것

| 줄 | 현재 | 문제 | 수정안 |
|---|---|---|---|
| L81 | "`CLAUDE`로 시작하는 파일(특히 `CLAUDE.local.md`)이 있으면 `AGENTS.md`를 읽지 않는다." | 방향은 맞다. 다만 조건이 정확하지 않다. 막는 것은 작업 디렉터리나 그 위의 `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` 세 가지뿐이다. `~/.claude/CLAUDE.md`와 `.claude/rules/`는 막지 않는다. 설정으로 바꿀 수 있다는 점도 빠졌다. | "작업 디렉터리나 그 위에 `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` 중 하나라도 있으면 기본값에서는 `AGENTS.md`를 읽지 않는다(전역 `~/.claude/CLAUDE.md`와 `.claude/rules/`는 해당 없음). 둘 다 읽게 하려면 `/config`의 Project instructions를 `claude-md-and-agents-md`로 바꾼다. 버전에 상관없이 통하는 방법은 `CLAUDE.md` 첫 줄에 `@AGENTS.md`를 두는 것이다." |
| L77 | "구역은 XML 태그로 통일한다." | 공식 문서가 권하는 구조는 "markdown headers and bullets"다. Claude Code 문서에는 XML 태그 권장이 없다. 틀렸다고 할 수는 없지만 공식 근거가 없는 관례다. | 둘 중 하나를 고른다. (a) 공식에 맞춰 "구역은 마크다운 헤더와 불릿으로 나눈다"로 바꾸고 템플릿도 바꾼다(4절에 안 제시). (b) XML을 유지하되 "공식 문서는 마크다운 헤더를 권한다. XML 구역은 이 저장소의 관례다"라고 밝힌다. |
| L44 | "무엇이 자동으로 로드되고(지침, 자동 메모리, 스킬 설명, MCP 도구 이름), 무엇이 필요할 때만 로드되는지(스킬 본문, 경로 범위 규칙)" | 맞지만 빠진 것이 있다. 경로 없는 규칙은 시작 시 로드되고, 하위 디렉터리의 CLAUDE.md는 필요할 때 로드되며, MCP 스키마는 지연 로드다. 자동 메모리는 `MEMORY.md` 앞 200줄/25KB만 올라온다. | 자동 로드: 시스템 프롬프트와 도구 정의, 지침(상위 디렉터리 포함)과 `paths` 없는 규칙, 자동 메모리 색인(앞 200줄 또는 25KB), 스킬 설명, MCP 도구 이름. 필요할 때: 스킬 본문, `paths` 규칙, 하위 디렉터리 지침, MCP 도구 스키마, 자동 메모리 주제 파일. |
| L56 | "안 쓰는 내장 기능은 명시적으로 끈다." | 무엇을 어떻게 끄는지 없다. | 예를 든다: 내장 스킬은 `disableBundledSkills` 또는 스킬별 `skillOverrides`, 도구는 `permissions.deny`에 도구 이름만 적기(컨텍스트에서 빠진다), 자동 메모리는 `autoMemoryEnabled: false`, 권한 우회 모드는 `permissions.disableBypassPermissionsMode: "disable"`. |
| L58 | "상태줄(status line)을 켠다." | 방법이 없다. | "`/statusline <보여 줄 내용>`으로 만든다. 설정에는 `statusLine` 키(`type: "command"`)로 저장된다." |
| L59 | "자동 메모리(`~/.claude/projects/<프로젝트>/memory/`)가 어디에 쌓이는지 확인한다." | 맞다. 보는 방법과 로드 한계가 없다. | "`/memory`에서 자동 메모리 폴더를 연다. 세션에 올라오는 것은 `MEMORY.md`의 앞 200줄 또는 25KB뿐이다. 같은 저장소의 워크트리는 메모리를 공유한다. 끄려면 `/memory`의 토글이나 `autoMemoryEnabled: false`." |
| L60 | "PC를 여러 대 쓰면 `settings.json`을 직접 옮기거나 버전 관리한다. 자동으로 복사되지 않는다." | 사용자 설정이 "this machine"에만 적용된다는 것은 문서와 맞다. 그런데 전부가 로컬은 아니다. claude.ai 계정에 켜 둔 스킬·플러그인·커넥터는 로그인하면 자동으로 내려온다. "빈 폴더에 의도하지 않은 스킬"의 원인이 될 수 있다. | 한 줄 추가: "반대로 claude.ai 계정에 켜 둔 스킬·플러그인·커넥터는 로그인한 PC마다 자동으로 내려온다(`~/.claude/skills/synced/`). 원하지 않으면 `syncClaudeAiSkills: false`, `syncClaudeAiPlugins: false`를 사용자 설정에 둔다." |
| L62 | "컨텍스트에 무엇이 올라왔는지 본다" | 명령이 없다. | "`/context all`로 범주별 점유(시스템 프롬프트, 도구, MCP 도구, 메모리 파일, 스킬, 대화)를 보고, `/memory`, `/skills`, `/mcp`, `/hooks`, `/status`로 범주별 상세를 본다." |
| L79 | "그 파일을 다룰 때만 로드된다." | 맞다. 두 가지 한계가 빠졌다. 압축하면 사라졌다가 해당 파일을 다시 다룰 때 돌아오고, `paths`가 없으면 매 세션 로드된다. | 덧붙인다: "`paths`가 없는 규칙 파일은 매 세션 로드된다. 경로 규칙은 압축 뒤에는 해당 파일을 다시 읽을 때까지 빠져 있다. 압축 뒤에도 꼭 있어야 하면 `paths`를 빼거나 `CLAUDE.md`로 옮긴다." |
| L80 | "개인용 지침은 `CLAUDE.local.md`에 두고 `.gitignore`에 넣는다." | 맞다. 워크트리와 AGENTS.md 부작용이 빠졌다. | 덧붙인다: "워크트리마다 따로 있어야 하므로, 워크트리를 쓰면 `@~/.claude/<파일>.md` import로 대신한다. `AGENTS.md`만 쓰는 저장소에 이 파일을 두면 `AGENTS.md`가 로드되지 않는다." |
| L86 | "규칙 파일은 해당 경로의 파일을 다룰 때 로드되는지 본다." | 방법이 없다. `/context`의 Memory files에는 시작 시 로드된 것만 나온다. | "`/context all`의 Memory files는 시작 시 로드된 파일만 보여 준다. 경로 규칙은 `InstructionsLoaded` 훅으로 기록하거나 `claude --debug`로 확인한다." (훅 예시는 3절 A2) |
| L104 | "`.claude/settings.local.json` 은 나만(커밋 제외)." | Claude Code가 이 파일을 직접 쓸 때만 전역 git 제외 목록에 넣어 준다. 템플릿을 손으로 복사하면 자동 제외가 안 된다. | "손으로 만들었으면 `.gitignore`에 직접 넣는다. Claude Code가 처음 쓸 때만 자동으로 제외된다." |
| L106 | "`.env` 읽기는 금지 목록에 넣는다." | 맞다. 막히는 범위의 한계가 없으면 과신한다. | "`Read` 금지는 파일 도구와 `cat` 같은 파일 읽기 명령, 리다이렉션을 막는다. `grep -r`처럼 파일 이름을 대지 않는 명령이나 스크립트가 직접 여는 것은 못 막는다. 그것까지 막으려면 샌드박스를 켠다(`/sandbox`). `.claudeignore`는 효과가 없다." |
| L108 | "거부되는지 본다" | 맞다. 두 경로를 다 시험해야 한다. | "`.env` 내용을 보여 달라고 하고, `cat .env`를 실행해 달라고도 한다. 둘 다 거부돼야 한다. `/permissions`에서 그 규칙이 어느 파일에서 왔는지 확인한다." |
| L98~113 전체 | (언급 없음) | 권한 모드가 빠졌다. v2.1.283부터 터미널 세션의 기본 시작 모드가 `auto`다. 분류기는 판단이지 강제가 아니다. | A3에 "시작 권한 모드를 정한다" 항목을 추가한다(3절). |

### 템플릿 쪽

| 파일 | 문제 | 수정안 |
|---|---|---|
| `templates/settings.local.example.json` | `ANTHROPIC_DEFAULT_SONNET_MODEL`은 `sonnet` 별칭이 가리키는 모델 ID를 정하는 변수다. 세션이 `sonnet`으로 돌지 않으면(대부분 요금제의 기본은 Opus 5.5) 아무 효과가 없다. "이 프로젝트에서 쓸 모델 이름"이라는 설명과 다르다. | `model` 키로 바꾼다. 별칭 고정은 게이트웨이가 다른 모델 ID를 요구할 때만 쓰는 선택 사항으로 내린다(4절). |
| `templates/settings.json` | 스키마상 유효하다. 다만 `Read(./.env.*)`가 `.env.example`까지 막는다. 그리고 `./` 패턴은 시작 디렉터리의 `.env`만 막는다(문서: "Matches reading the `.env` file in the current directory"). 모노레포의 하위 `.env`는 안 막힌다. | 기본 3줄은 공식 예시와 같으므로 유지한다. `$schema`와 `ask` 한 줄을 더한다. 모노레포용 변형은 README에 안내한다(4절). |
| `templates/README.md` L5 | "XML 구역, 200줄 이하" | L77과 같은 문제. 같이 정리한다. |
| `templates/README.md` L8 | "인증 값은 파일에 적지 말고 직접 관리한다" | 공식 문서는 로컬 파일에 토큰을 적는 것을 허용한다(커밋 금지 조건). 더 엄격한 방침으로 유지해도 되지만 방법을 알려 줘야 한다. | "인증 값은 커밋되는 파일에 두지 않는다. 셸 환경 변수나 `apiKeyHelper`를 쓴다." |
| `templates/CLAUDE.md`, `templates/rules/testing.md` | `<!-- -->` 주석이 XML 태그 블록 안에 있다. 공식 문서가 제거한다고 밝힌 것은 "Block-level HTML comments in CLAUDE.md files"다. 태그 블록 안의 주석과 규칙 파일의 주석도 제거되는지는 확인하지 못했다. | README에 "채운 뒤 안내 주석은 지운다"를 한 줄 넣는다. |

### 범위 밖이지만 눈에 띈 것 (A6, L190)

"훅은 권한을 조일 수는 있어도 풀 수는 없다"는 절반만 맞다. 공식 문서: "The hook output can deny the tool call, force a prompt, or skip the prompt to let the call proceed." 훅의 `"allow"`는 프롬프트를 건너뛰게 할 수 있다. 못 하는 것은 deny·ask 규칙을 넘어서는 일이다("PreToolUse hook decisions don't bypass permission rules"). 수정안: "훅의 허용은 권한 프롬프트를 건너뛰게 할 수 있지만 deny·ask 규칙은 넘지 못한다."

---

## 3. 추가할 가치가 큰 내용

### A0. 기본 이해

**고민할 것**
- 이 내용은 매 요청마다 컨텍스트를 차지하는가, 필요할 때만 올라오는가. 압축 뒤에도 남는가.
- 이 규칙은 모델에게 하는 부탁인가(프롬프트, CLAUDE.md, 스킬, auto 모드 분류기), 하네스가 집행하는 강제인가(훅, deny 규칙, 샌드박스, 관리 설정).
- 지침이 안 지켜질 때 원인이 "로드되지 않았다"인지 "로드됐지만 따르지 않았다"인지 구분할 수 있는가.

**할 일**
- 읽을 공식 페이지를 정한다: how-claude-code-works, features-overview, claude-directory, context-window, memory, settings, permissions, debug-your-config.
- 아래 표를 외운다(가이드에 표로 넣을 것을 권한다).

| 무엇 | 언제 로드 | 무엇이 올라오나 | 압축 뒤 |
|---|---|---|---|
| 시스템 프롬프트·도구 정의 | 시작 | 전부 | 유지 |
| `CLAUDE.md`(관리·전역·프로젝트·로컬, 상위 디렉터리 포함), `paths` 없는 규칙 | 시작 | 파일 전체(import 포함). 유저 메시지로 들어간다 | 디스크에서 다시 주입 |
| 자동 메모리 | 시작 | `MEMORY.md` 앞 200줄 또는 25KB | 다시 주입 |
| 스킬 | 시작 + 사용 시 | 시작 시 이름과 설명(윈도우의 1% 예산, 항목당 1,536자). 본문은 쓸 때 | 설명은 다시 주입. 본문은 스킬당 5,000토큰, 합계 25,000토큰까지 |
| MCP | 시작 | 도구 이름과 서버 지침. 스키마는 쓸 때 | — |
| `paths` 규칙, 하위 디렉터리 `CLAUDE.md` | 해당 파일을 읽거나 고칠 때 | 파일 내용(파일당 크기 제한 있음) | 사라졌다가 다시 건드리면 로드 |
| 훅 | 이벤트 발생 시 | 없음(출력을 돌려주면 그만큼) | 요약에 섞임 |
| 서브에이전트 | 호출 시 | 별도 컨텍스트. 내장 Explore·Plan은 CLAUDE.md를 읽지 않는다 | — |

- 세션 중에 `CLAUDE.md`를 고쳐도 그 세션에는 반영되지 않는다는 점을 기억한다. `/clear`, `/compact`, 재시작 뒤에 반영된다.

**확인 방법**
```
claude            # 아무 프로젝트에서
/context all      # 범주별 점유: system prompt, system tools, MCP tools, memory files, skills, messages
/memory           # 로드된 지침 파일 목록과 자동 메모리 폴더
/skills           # 스킬 목록 (t 키로 토큰 순 정렬)
/mcp              # MCP 서버와 상태
/status           # Setting sources 줄: 어떤 설정 파일을 읽었는지
```

**끝났다는 기준**
- [ ] 위 표를 보지 않고 "시작 시 로드 / 필요할 때 로드 / 압축 뒤 남는 것"을 말할 수 있다
- [ ] `/context all` 출력에서 각 범주가 무엇인지 설명할 수 있다
- [ ] 부탁(지침·스킬·auto 모드 분류기)과 강제(훅·deny 규칙·샌드박스)를 구분해 예를 하나씩 들 수 있다

### A1. 전역 정리

**고민할 것**
- 이 항목은 내 모든 프로젝트에 필요한가. 아니면 프로젝트 쪽으로 옮긴다.
- 시작 권한 모드를 무엇으로 둘 것인가. 최신 버전의 기본은 `auto`(분류기가 판단)다. 매번 직접 승인하려면 Manual로 바꿔야 한다.
- 자동 메모리를 켜 둘 것인가. 켜 두면 PC마다 Claude의 행동이 달라질 수 있다.
- 계정에서 자동으로 내려오는 것(claude.ai 스킬·플러그인·커넥터)을 받을 것인가.
- 대화 기록이 평문으로 며칠 남아도 되는가(`cleanupPeriodDays`, 기본 30일).
- 전역 deny 규칙의 경로를 어떻게 쓸 것인가. 사용자 설정에서 `/path`는 `~/.claude/path`로 풀린다. 모든 프로젝트에 적용하려면 `~/`나 `//`로 쓴다.

**할 일**
- 전역에 있는 것을 목록으로 뽑는다.
  ```bash
  ls ~/.claude                       # CLAUDE.md, rules/, skills/, agents/, commands/, output-styles/, settings.json, plugins/
  wc -l ~/.claude/CLAUDE.md          # 200줄 이하인지
  ls ~/.claude/rules ~/.claude/skills 2>/dev/null
  claude mcp list                    # 사용자·로컬 범위 MCP는 ~/.claude.json에 있다
  ```
- `~/.claude/settings.json`과 `~/.claude.json`을 구분한다. 권한·훅·`env`는 앞의 파일에만 둔다. 뒤의 파일은 Claude Code가 쓰는 상태 파일이다.
- 사용자 설정 첫 줄에 `"$schema": "https://json.schemastore.org/claude-code-settings.json"`을 둔다. 편집기에서 자동 완성과 검증이 된다. 주석과 끝 쉼표는 오류다.
- 모델과 강도는 명령으로 정한다: `/model`(Enter는 기본값으로 저장, `s`는 이번 세션만), `/effort <low|medium|high|xhigh>`.
- 시작 권한 모드를 정한다. 사용자 설정의 `permissions.defaultMode`에 `"default"`(Manual), `"acceptEdits"`, `"plan"`, `"auto"` 중 하나.
- 상태줄은 `/statusline <보여 줄 내용>`으로 만든다.
- 자동 메모리를 연다: `/memory` → 자동 메모리 폴더. 주요 프로젝트의 `MEMORY.md`를 읽고 틀린 내용을 지운다.
- 쓰지 않는 스킬은 `/skills`에서 가시성을 바꾼다(`skillOverrides`에 저장된다). 스킬별 비용은 `/skill-doctor`로 본다.
- 여러 PC를 쓰면 `~/.claude/settings.json`, `~/.claude/CLAUDE.md`, `~/.claude/rules/`, `~/.claude/skills/`를 dotfiles 저장소로 관리한다. 다른 도구가 생성하거나 읽기 전용 복사본에 연결한 설정 파일이면 `/model` 같은 명령이 값을 저장하지 못한다(공식 문서: 쓸 수 없는 파일이면 "the change applies to the current session and is gone in the next one"). 쓰기 가능한 파일에 연결한다.

**확인 방법**
```bash
mkdir -p ~/claude-clean/empty && cd ~/claude-clean/empty
claude
```
세션 안에서:
```
/context all     # Memory files에 ~/.claude/CLAUDE.md와 전역 규칙만 있는지, Skills·MCP tools가 의도한 것인지
/status          # Setting sources에 User settings만 있는지, 시작 모델이 맞는지
/skills          # 의도하지 않은 스킬(계정 동기화 포함)이 없는지
/mcp             # 의도하지 않은 서버·커넥터가 없는지
/hooks           # 전역 훅이 의도한 것뿐인지
/permissions     # deny 규칙과 그 출처 파일
/effort status   # 현재 강도
```
내 설정이 원인인지 가르려면 아무 설정도 없는 상태와 비교한다.
```bash
claude --safe-mode                                                   # 내 커스터마이즈를 끈 세션
CLAUDE_CONFIG_DIR=~/claude-clean/config claude --setting-sources user # 완전히 빈 설정 디렉터리
claude doctor                                                        # 설정 파일 오류를 세션 없이 확인
```

**끝났다는 기준**
- [ ] 빈 폴더의 `/context all`에 의도하지 않은 지침·스킬·MCP 도구가 없다
- [ ] `/status`의 Setting sources와 시작 모델, `/effort status`의 강도가 내가 정한 값이다
- [ ] 시작 권한 모드를 알고 있고, 내가 고른 값이다
- [ ] 전역 deny 규칙이 `/permissions`에 보이고, 실제로 거부된다
- [ ] 자동 메모리를 `/memory`로 열어 봤고, 켜 둘지 끌지 정했다
- [ ] `claude doctor`가 설정 오류를 보고하지 않는다

### A2. 프로젝트 지침

**고민할 것**
- 이 줄은 모든 세션에 필요한가. 한 폴더에만 필요하면 경로 규칙, 여러 단계 절차면 스킬, 예외가 없어야 하면 훅이나 deny 규칙이다.
- 이 줄은 코드만 봐서는 알 수 없는 내용인가. 디렉터리 구조, 의존성 목록, 아키텍처 개요처럼 코드에서 읽을 수 있는 것은 뺀다.
- 원본을 `CLAUDE.md`로 둘 것인가 `AGENTS.md`로 둘 것인가. 팀이 다른 도구를 쓰는가, 팀원의 Claude Code 버전이 v2.1.277 이상인가.
- 모노레포라면 상위 디렉터리의 `CLAUDE.md`가 같이 로드된다. 남의 팀 지침이 섞이지 않는가.
- 팀의 커밋·PR 규칙이 Claude Code 내장 git 지침과 부딪히지 않는가.
- 압축 뒤에도 남아야 하는 규칙이 경로 규칙에 들어가 있지 않은가.

**할 일**
- 초안은 `/init`으로 만든 뒤 줄인다. 대화형으로 하려면 `CLAUDE_CODE_NEW_INIT=1 claude` 후 `/init`.
- 넣을 것: 작업을 확인하는 정확한 명령(테스트 한 파일만 돌리는 법 포함), 코드가 오해를 부르는 곳, 저장소에 없는 결정, 두 번 고쳐 준 것.
- 검증할 수 있게 쓴다. "코드를 깔끔하게" 대신 "들여쓰기는 공백 2칸".
- 긴 문서는 `@경로`로 import할 수 있지만 비용은 줄지 않는다. 깊이는 4단계까지다. 경로를 글자 그대로 적으려면 백틱으로 감싼다.
- 한 영역에만 필요한 규칙은 `.claude/rules/<주제>.md`에 `paths`를 달아 둔다. frontmatter에서 읽는 필드는 `paths`뿐이다.
- 개인 지침은 `CLAUDE.local.md`에 두고 `.gitignore`에 추가한다.
- `AGENTS.md`를 원본으로 삼으면 `CLAUDE.md`를 다음처럼 둔다.
  ```markdown
  @AGENTS.md

  ## Claude Code
  <!-- Claude Code에만 해당하는 지침 -->
  ```
- 압축 때 남길 내용을 `CLAUDE.md`의 `# Compact instructions` 구역에 적는다.
- 팀 git 규칙을 `CLAUDE.md`에 적었다면 프로젝트 설정에 `"includeGitInstructions": false`를 검토한다. 커밋 서명 문구는 `attribution`으로 정한다.
- 모노레포에서 남의 지침은 `.claude/settings.local.json`의 `claudeMdExcludes`로 뺀다(절대 경로 글롭).
- 정기 점검: `/doctor`(코드에서 유추 가능한 내용 삭제 제안), `/doctor prompt-audit`(낡았거나 서로 모순되는 지침 찾기).

**확인 방법**
```bash
wc -l CLAUDE.md                              # 200 이하
git check-ignore -v CLAUDE.local.md          # 무시 규칙이 잡히는지
```
새 세션에서(세션 중에 고친 `CLAUDE.md`는 반영되지 않는다):
```
/context all     # Memory files에 CLAUDE.md, CLAUDE.local.md, paths 없는 규칙이 있는지
/memory          # 목록에 AGENTS.md 경로가 있는지(AGENTS.md를 쓸 때)
/status          # 지침 파일이 권장 길이를 넘으면 경고가 뜬다
```
경로 규칙은 시작 시 목록에 나오지 않는다. 로드 기록을 남기는 훅을 잠시 건다(`.claude/settings.local.json`, 스키마 검증 통과).
```json
{
  "hooks": {
    "InstructionsLoaded": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{file_path, load_reason, memory_type}' >> \"${CLAUDE_PROJECT_DIR}/.claude/instructions-loaded.log\""
          }
        ]
      }
    ]
  }
}
```
그다음 Claude에게 규칙의 `paths`에 맞는 파일을 읽게 하고 `cat .claude/instructions-loaded.log`를 본다. `load_reason`이 `path_glob_match`인 줄이 생겨야 한다. 훅 없이 보려면 `claude --debug`로 시작한다(frontmatter YAML 오류도 여기 찍힌다).
마지막으로 지침의 명령·규칙이 필요한 작은 작업을 시켜서 실제로 따르는지 본다.

**끝났다는 기준**
- [ ] `CLAUDE.md`가 커밋돼 있고 200줄 이하이며, 코드에서 읽을 수 있는 내용이 없다
- [ ] 새 세션의 `/context all` Memory files에 기대한 파일이 모두 있다
- [ ] 경로 규칙이 해당 파일을 읽을 때 로드된 기록이 있다(`path_glob_match`)
- [ ] `git check-ignore -v CLAUDE.local.md`가 규칙을 출력한다
- [ ] `AGENTS.md`를 쓰는 경우, `/memory` 목록에 그 경로가 보인다
- [ ] `/doctor prompt-audit`가 모순되는 지침을 보고하지 않는다
- [ ] 새 세션이 지침의 명령·규칙을 따른다

**흔한 함정에 추가:** 세션 중에 `CLAUDE.md`를 고치고 바로 시험하기(반영되지 않는다). `AGENTS.md`만 쓰는 저장소에 `CLAUDE.local.md` 만들기. 지켜지지 않는 줄에 "중요"를 덧붙이기(길이를 줄이거나 훅으로 옮긴다).

### A3. 설정 파일 분리

**고민할 것**
- 이 키는 누구에게 적용돼야 하는가: 나의 모든 프로젝트(사용자), 이 저장소의 모두(프로젝트), 이 저장소의 나(로컬).
- 이 키는 커밋되는 파일에서 효과가 있는가. `permissions.defaultMode`의 `auto`·`bypassPermissions`, `autoMode`, AGENTS.md용 `pluginConfigs`, 텔레메트리 환경 변수는 프로젝트 파일에서 무시된다. 설정 참조의 Scope 열을 본다.
- 팀원에게 바로 적용되는가. `deny`·`ask`는 바로 적용되고, `allow`와 대부분의 `env`는 각자가 폴더를 신뢰한 뒤에 적용된다.
- 이 금지는 규칙 문자열로 충분한가. Bash deny는 Claude가 흔히 쓰는 형태만 막는다(`/bin/rm`, `bash -c '...'`는 통과). Read deny는 파일 이름을 대지 않는 명령을 못 막는다. 꼭 막아야 하면 샌드박스나 훅을 같이 쓴다.
- deny에 넣으면 allow로 예외를 뺄 수 없다. 범위를 넓게 잡은 deny가 필요한 작업까지 막지 않는가.
- 시작 권한 모드가 `auto`인 팀원과 Manual인 팀원이 섞여도 금지가 똑같이 걸리는가(deny는 모든 모드에서 유효하므로 금지는 deny에 둔다).
- 인증 값이 어디에 평문으로 남는가(설정 파일, 대화 기록).

**할 일**
- 팀 공유: `.claude/settings.json`에 `permissions`(deny·ask·allow), `hooks`, 팀 공통 `model`·`env`. MCP 서버는 저장소 루트의 `.mcp.json`.
- 개인: `.claude/settings.local.json`. 손으로 만들었으면 `.gitignore`에 넣는다.
- 저장소 루트에서 `claude`를 시작한다. 공유 프로젝트 설정은 시작 디렉터리의 `.claude/`에서만 읽고 상위로 올라가지 않는다.
- 규칙 문법을 지킨다.
  - 형식은 `도구` 또는 `도구(지정자)`. 평가 순서는 deny → ask → allow.
  - Bash: `Bash(npm run *)`. `*`는 하위 명령 뒤에 둔다. `Bash(git push *)`는 `git push`도 포함한다.
  - 파일: `Read(./.env)`, `Read(./secrets/**)`. 쓰기 금지는 `Write(...)`가 아니라 `Edit(...)`. 검색 금지는 `Grep(...)`이 아니라 `Read(...)`.
  - 경로: `//절대경로`, `~/홈기준`, `/설정파일기준`, `./현재디렉터리기준`.
  - 웹: `WebFetch(domain:example.com)`.
- 푸시처럼 "막지는 않되 물어봐야 하는 것"은 `ask`에 둔다. `ask`는 `acceptEdits`·`bypassPermissions`에서도 묻는다.
- 프로젝트 전용 모델은 `model` 키로, 엔드포인트는 `env.ANTHROPIC_BASE_URL`로 정한다. 인증은 셸 환경 변수나 `apiKeyHelper`.
- OS 수준 차단이 필요하면 `/sandbox`로 켠다. macOS·Linux·WSL2에서만 동작한다. Linux는 `bubblewrap`과 `socat`이 필요하다.
- 비밀 값은 대화에 넣지 않는다. 도구가 읽은 값은 `~/.claude/projects/<프로젝트>/<세션>.jsonl`에 평문으로 남는다. 이미 넣었다면 `claude purge <경로> --dry-run`으로 지울 범위를 확인한다.

**확인 방법**
```bash
python3 -m json.tool .claude/settings.json > /dev/null && echo OK   # 엄격한 JSON인지
git check-ignore -v .claude/settings.local.json                     # 무시되는지
git status --short .claude/                                         # 로컬 파일이 추적되지 않는지
claude doctor                                                       # 설정 오류·무시된 항목
```
세션 안에서:
```
/status          # Setting sources에 User settings, Project settings, Project local settings가 기대대로 있는지
                 # 게이트웨이를 쓰면 Anthropic base URL 줄이 보이는지
/permissions     # 규칙 목록과 각 규칙이 온 파일
```
금지를 실제로 시험한다(둘 다 거부돼야 한다).
```
.env 파일 내용을 보여줘
cat .env 를 실행해줘
```
샌드박스를 켰다면 Claude에게 시킨다(직접 `!`로 치면 샌드박스 밖에서 돈다).
```
touch ~/sandbox-probe 를 실행해줘                      # Operation not permitted 또는 Read-only file system
curl --noproxy '*' https://example.com 을 실행해줘      # Could not resolve host
```
모델을 프로젝트 설정으로 정했다면 시작 화면 머리말에 그 값을 정한 설정 파일이 표시된다.

**끝났다는 기준**
- [ ] 팀 설정(`.claude/settings.json`, `.mcp.json`)은 커밋돼 있고, 개인 설정은 `git check-ignore`에 잡힌다
- [ ] `/status`의 Setting sources가 기대와 같다
- [ ] `/permissions`에 금지 규칙이 프로젝트 설정 출처로 보인다
- [ ] 파일 도구와 `cat` 두 경로 모두에서 금지 항목이 거부된다
- [ ] 금지 규칙이 못 막는 경로(이름을 대지 않는 명령, 스크립트)를 알고 있고, 필요하면 샌드박스나 훅으로 보완했다
- [ ] 커밋된 파일에 인증 값이 없다(`git grep -n -i 'token\|api_key' -- .claude .mcp.json`으로 확인)
- [ ] 전역 설정에 프로젝트 전용 값이 없다
- [ ] `claude doctor`가 오류를 보고하지 않는다

---

## 4. 템플릿 수정안

아래 JSON은 모두 schemastore 스키마 검증을 통과했다.

### `templates/settings.json` (팀 공유)

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

바꾼 점: `$schema` 추가, 푸시 전 확인용 `ask` 한 줄 추가. `deny` 세 줄은 공식 팀 예시와 같아서 그대로 둔다. `ask`가 필요 없으면 지운다.

### `templates/settings.local.example.json` (개인)

```json
{
  "model": "<별칭(sonnet·opus·haiku 등) 또는 전체 모델 ID>",
  "env": {
    "ANTHROPIC_BASE_URL": "https://<사내 게이트웨이 또는 프록시 주소>"
  }
}
```

바꾼 점: 모델 지정을 `ANTHROPIC_DEFAULT_SONNET_MODEL`에서 `model` 키로 바꿨다. 게이트웨이가 다른 모델 ID를 요구할 때만 `env`에 `"ANTHROPIC_DEFAULT_SONNET_MODEL": "<게이트웨이의 모델 ID>"`를 더하고 `model`을 `"sonnet"`으로 둔다. 필요 없는 키는 지운다.

### `templates/settings.user.example.json` (신규 제안, `~/.claude/settings.json`용)

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "sonnet",
  "permissions": {
    "deny": [
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)"
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  },
  "cleanupPeriodDays": 30
}
```

`statusLine` 명령은 공식 예시 그대로다(`jq` 필요). `deny`의 두 경로는 문법은 공식(`~/path`)이고, 무엇을 넣을지는 제안이다. 강도는 이 파일에 적지 않고 `/effort`로 정한다. 시작 권한 모드를 바꾸려면 `permissions`에 `"defaultMode": "default"`(Manual) 등을 더한다.

### `templates/rules/testing.md`

frontmatter는 유효하다(`paths`는 YAML 목록, 글롭 문법 맞음). 본문 주석만 정확하게 고친다.

```markdown
---
paths:
  - "tests/**"
  - "**/test_*.py"
---

<testing_rules>
<!-- 예시다. 프로젝트의 테스트 규칙으로 바꾸고 이 주석은 지운다. 이 파일은 위 경로의 파일을 읽거나 고칠 때 로드된다. paths 를 지우면 매 세션 로드된다. -->
- 테스트 파일 이름은 `tests/test_<모듈>.py`로 한다. 소스 파일 하나에 테스트 파일 하나를 짝짓는다.
- 기존 테스트를 지우거나 건너뛰게 바꾸지 않는다. 테스트가 틀렸다고 판단되면 고치기 전에 이유를 말한다.
- 기대값을 코드에서 복사해 맞추지 않는다. 요구사항에서 기대값을 정한다.
</testing_rules>
```

### `templates/CLAUDE.md`

현재 XML 판은 형식상 문제가 없다. L77을 (a)안으로 고칠 때 쓸 마크다운 헤더 판:

```markdown
# 프로젝트
<!-- 한두 줄: 이 저장소가 무엇이고 누가 쓰는지 -->

# 명령
<!-- 실제 명령으로 바꾼다. 테스트 파일 하나만 돌리는 명령도 적는다 -->
- 설치:
- 실행:
- 테스트 전체:
- 테스트 한 파일:
- 린트·포맷:

# 규칙
<!-- 코드만 봐서는 알 수 없는 것만. 특정 폴더·파일 규칙은 .claude/rules/ 에 paths 를 달아 둔다 -->
-

# 작업 방식
- 요구가 모호하면 추측하지 말고 한 번에 하나씩 묻는다.
- 코드를 바꾸기 전에 계획(수정 대상, 순서, 테스트 방법)을 쓰고 승인을 받는다. 범위가 바뀌면 계획으로 돌아간다.
- 코드를 고치면 관련 테스트를 돌린다.
- 완료는 테스트 결과와 실제 변경으로 보고한다. 확인하지 못한 것은 "미확인"이라고 적는다.

# 금지
- 테스트를 지우거나 건너뛰지 않는다.
- 키나 `.env` 값을 출력·커밋하지 않는다.
<!-- 이 저장소에서 절대 하면 안 되는 일을 추가한다. 예외가 없어야 하는 것은 권한 금지 목록이나 훅으로도 막는다 -->

# Compact instructions
<!-- 압축할 때 꼭 남길 것. 예: 테스트 출력과 코드 변경 -->
-
```

XML 판을 유지한다면 `<commands>`에 "테스트 한 파일" 줄과 `# Compact instructions`에 해당하는 구역만 더한다.

### `templates/README.md`

```markdown
# 템플릿

| 파일 | 놓는 곳 | 커밋 | 용도 |
|---|---|---|---|
| `CLAUDE.md` | 프로젝트 루트(또는 `.claude/CLAUDE.md`) | 한다 | 프로젝트 지침. 200줄 이하. 채운 뒤 안내 주석은 지운다 |
| `rules/testing.md` | `.claude/rules/` | 한다 | 경로 범위 규칙 예시. `paths`에 맞는 파일을 읽거나 고칠 때만 로드. `paths`가 없으면 매 세션 로드 |
| `settings.json` | `.claude/settings.json` | 한다 | 팀 공유 설정. 권한 금지 목록부터. MCP 서버는 여기가 아니라 저장소 루트의 `.mcp.json` |
| `settings.local.example.json` | `.claude/settings.local.json`으로 복사 | 안 한다. 손으로 만들었으면 `.gitignore`에 직접 넣는다 | 개인 설정. 이 프로젝트에서만 다른 모델·엔드포인트를 쓸 때. 인증 값은 커밋되는 파일에 두지 않는다. 셸 환경 변수나 `apiKeyHelper`를 쓴다 |
| `settings.user.example.json` | `~/.claude/settings.json`에 필요한 키만 옮긴다 | 해당 없음 | 전역 설정 예시. 기본 모델, 전역 금지 목록, 상태줄, 기록 보존 기간 |

- 설정 파일은 엄격한 JSON이다. 주석과 끝 쉼표는 오류다. `<...>` 자리표시는 실제 값으로 바꾸고, 쓰지 않는 키는 지운다.
- `Read(./.env)`는 시작 디렉터리의 `.env`만 막는다. 하위 폴더의 `.env`까지 막으려면 `Read(**/.env)`를 쓴다.
- `Read(./.env.*)`는 `.env.example`도 막는다.
- `Read` 금지는 파일 도구와 `cat` 같은 읽기 명령을 막는다. `grep -r`이나 스크립트가 직접 여는 것까지 막으려면 샌드박스를 켠다.
- 적용 뒤 `/status`, `/permissions`, `claude doctor`로 확인한다.
- 설정 키와 환경 변수 이름은 버전에 따라 바뀔 수 있다. 적용 전에 공식 문서의 설정·환경 변수 페이지로 확인한다.
```

---

## 5. 확인 못 한 것

- **실제 세션 재현 없음.** deny 규칙의 거부, `/context all` 출력 형식, `InstructionsLoaded` 훅 로그는 문서 근거만 있고 이 조사에서 돌려 보지 않았다. 훅 예시는 스키마 검증만 통과했다.
- **XML 태그 블록 안의 HTML 주석 제거 여부.** 문서는 "Block-level HTML comments ... in CLAUDE.md files are stripped"라고만 한다. `<project>` 같은 태그 줄 바로 아래의 주석이 블록 수준으로 인식되는지, 규칙 파일(`.claude/rules/*.md`)의 주석도 제거되는지는 문서에 없다.
- **`Read(./.env)`와 `Read(./secrets/**)`의 깊이.** 문서는 `Read(./.env)`를 "the `.env` file in the current directory"로, 이름만 쓴 `Read(.env)`를 "any depth"로 설명한다. `./`가 붙은 단일 디렉터리 패턴(`./secrets/**`)이 deny에서 모든 깊이에 걸리는지는 명시가 없다(`secrets/**`는 deny에서 모든 깊이라고 명시).
- **`Read(**/.env.*)`와 `Read(!.env.example)`.** `**/.env`와 `!` 부정은 문서에 예가 있지만, 이 두 문자열 자체는 문서에 없다. gitignore 문법에서 유추한 것이다. 스키마 패턴은 통과한다. `!` 부정이 도입된 버전도 문서에서 찾지 못했다.
- **사용자 설정이 기기 간에 동기화되지 않는다는 명시적 문장.** "You, in every project on this machine"이 가장 가까운 근거다. "동기화하지 않는다"고 직접 쓴 문장은 찾지 못했다. 예외로 Enterprise 요금제에서 `/model`로 저장한 기본 모델은 계정에도 기록된다("Claude Code also records the choice on that account").
- **CLAUDE.md가 들어가는 정확한 형태.** "delivered as a user message after the system prompt"까지만 문서에 있다. 감싸는 태그나 위치의 세부는 문서에 없다. 시스템 프롬프트는 공개되지 않는다("Claude Code's system prompt isn't published").
- **범주별 실제 토큰 수.** context-window 페이지의 수치는 대화형 위젯 안에 있고 `.md` 원문에는 "representative token counts"라는 말만 있다. 수치를 인용할 수 없다.
- **스키마 지연.** `modelSettings`, `maxEffortLevel`, `autoCompactWindow`, `permissions.blockReadsOutsideWorkingDirectories`는 공식 문서에만 있고 스키마에는 없다. 이 키를 쓰면 편집기가 경고할 수 있다(스키마가 `additionalProperties: true`라 검증 실패는 아니다).
- **Windows 동작.** 경로 정규화, 로컬 설정 파일 위치 예외, 샌드박스 미지원은 문서에 있지만 살펴보지 않은 세부가 많다.
- **`claude mcp list`의 출력 형식.** 명령이 있다는 것은 permissions 페이지의 언급으로 확인했지만 출력은 보지 않았다.
- **XML 태그 권장의 다른 근거.** Claude Code 문서에는 없다. API 쪽 프롬프트 작성 문서는 이 조사 범위에 넣지 않았다.
- **버전 의존.** 인용한 동작 다수가 특정 버전 이후다(AGENTS.md 직접 읽기 v2.1.277, auto 기본 모드 v2.1.283, `/doctor prompt-audit` v2.1.283, `modelSettings` v2.1.251). 팀원의 버전이 낮으면 다르게 동작한다. `claude --version`으로 확인해야 한다.
