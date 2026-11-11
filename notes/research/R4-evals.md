# R4. 평가(S1) · 비교 규칙 · 기준선(S2) 1차 자료 조사

- 조사일: 2026-11-11
- 대상 문서: `kit/harness/METHOD.md`(S1, 공통 규칙, S2 기준선), `kit/harness/templates/01-eval.md`, `kit/harness/templates/02-baseline.md`, `kit/.claude/skills/golden-dataset/SKILL.md`, `kit/.claude/skills/agent-eval/SKILL.md`
- 저장소는 수정하지 않았다. 아래 3절의 "그대로 넣을 문장"은 제안이다.
- 인용 표기: 큰따옴표 안 영문은 조회 도구가 원문에서 뽑아 준 문장이다. 도구가 인용 길이를 125자로 제한해서 긴 문장은 앞부분만 있거나 둘로 나뉘어 있다. 5절에 확인 한계를 적었다.
- 결과물(`kit/`)에 넣을 문장에는 출처 표시를 넣지 않았다(저장소 규칙). 근거는 이 파일에만 둔다.

---

## 1. 출처별 핵심

### 1-1. Anthropic

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Demystifying evals for AI agents (용어) | 과제·시도·채점기·기록·결과 상태를 구분한다. 결과(outcome)는 에이전트의 말이 아니라 환경의 최종 상태다 | "Each attempt at a task is a trial." / "The outcome is the final state in the environment at the end of the trial." / "is the complete record of a trial, including outputs, tool calls, reasoning, intermediate results" | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents |
| 같은 글 (능력 vs 회귀) | 평가 묶음을 둘로 나눈다. 능력 평가는 낮은 통과율에서 시작하고, 회귀 평가는 거의 100%여야 한다. 포화된 능력 평가는 회귀 묶음으로 "졸업"시킨다 | "They should start at a low pass rate, targeting tasks the agent struggles with and giving teams a hill to climb." / "should have a nearly 100% pass rate." | 위와 같음 |
| 같은 글 (채점기 종류) | 코드: 빠르고 싸고 재현되지만 정답과 다른 유효한 변형에 약하다. 모델: 유연하지만 비결정적이고 사람 보정이 필요하다. 사람: 기준이지만 느리고 비싸다 | 코드 "Fast • Cheap • Objective • Reproducible • Easy to debug" / "Brittle to valid variations that don’t match expected patterns exactly" · 모델 "Requires calibration with human graders for accuracy" | 위와 같음 |
| 같은 글 (채점 방법 목록) | 코드 채점기: 문자열 일치, 이진 테스트, 정적 분석, 결과 상태 확인, 도구 호출 확인, 기록 분석. 모델 채점기: 기준표, 자연어 단언, 쌍 비교, 참조 비교, 다중 심사 | "Binary tests (fail-to-pass, pass-to-pass)" / "Static analysis (lint, type, security)" / "Outcome verification" / "Tool calls verification (tools used, parameters)" / "Transcript analysis (turns taken, token usage)" | 위와 같음 |
| 같은 글 (코딩 에이전트) | 코딩 에이전트는 결정적 채점이 자연스럽다. 통과 = 실패하던 테스트를 고치고 기존 테스트를 안 깨뜨림. 정확성은 단위 테스트, 품질은 LLM 기준표·정적 분석으로 본다. 예시 과제의 채점기는 `deterministic_tests`, `llm_rubric`, `static_analysis`, `state_check`, `tool_calls`, 추적 지표는 `n_turns`, `n_toolcalls`, `n_total_tokens`, `time_to_first_token`, `output_tokens_per_sec`, `time_to_last_token` | "a solution passes only if it fixes the failing tests without breaking existing ones." / "heuristics-based code quality rules can evaluate the generated code based on more than passing tests," | 위와 같음 |
| 같은 글 (비결정성) | 같은 과제가 한 번은 통과, 한 번은 실패한다. pass@k(k번 중 한 번이라도)와 pass^k(k번 모두)는 제품 요구에 따라 고른다 | "measures the probability that all k trials succeed." / "If your agent has a 75% per-trial success rate and you run 3 trials, the probability of passing all three is (0.75)³ ≈ 42%." | 위와 같음 |
| 같은 글 (0단계: 몇 건) | 수백 건을 기다리지 말고 실제 실패에서 뽑은 20~50건으로 시작한다. 개발 중 손으로 확인하던 것부터 넣는다 | "20-50 simple tasks drawn from real failures is a great start." / "Begin with the manual checks you run during development" | 위와 같음 |
| 같은 글 (2단계: 명확한 과제 + 참조 해답) | 전문가 두 명이 같은 판정을 내릴 과제만 쓴다. 과제마다 모든 채점기를 통과하는 참조 해답을 만든다. 채점기가 보는 것은 전부 과제 설명에서 읽혀야 한다. 여러 번 돌려 0%면 에이전트가 아니라 과제가 깨진 것이다 | "A good task is one where two domain experts would independently reach the same pass/fail verdict." / "For each task, it’s useful to create a reference solution: a known working output that passes all graders." / "Everything the grader checks should be clear from the task description;" / "a 0% pass rate across many trials (i.e. 0% pass@100) is most often a signal of a broken task," | 위와 같음 |
| 같은 글 (3단계: 균형) | 해야 하는 경우와 하면 안 되는 경우를 둘 다 넣는다 | "One-sided evals create one-sided optimization." / "Test both the cases where a behavior should occur and where it shouldn't." | 위와 같음 |
| 같은 글 (4단계: 격리) | 시도마다 깨끗한 환경에서 시작한다. 남은 파일·캐시·자원 고갈 같은 공유 상태는 실패를 서로 연관시킨다. 이전 시도의 git 기록을 보고 이득을 본 사례가 있다 | "Each trial should be “isolated” by starting from a clean environment." / "we observed Claude gaining an unfair advantage on some tasks by examining the git history from previous trials." | 위와 같음 |
| 같은 글 (5단계: 채점기 설계) | 경로가 아니라 산출물을 채점한다. 도구 호출 순서를 그대로 요구하면 부서지기 쉽다. 여러 요소가 있으면 부분 점수를 둔다. 채점은 가중(임계값)·이진(모두 통과)·혼합 가운데 고른다. 채점기 우회를 막는다 | "We've found this approach too rigid and results in overly brittle tests," / "it’s often better to grade what the agent produced, not the path it took." / "binary (all graders must pass)," / "Make your graders resistant to bypasses or hacks." | 위와 같음 |
| 같은 글 (모델 채점기) | 사람 전문가와 보정한다. 정보가 부족하면 "Unknown"을 내게 한다. 차원마다 따로 심사한다. 안정되면 사람 검토는 가끔이면 된다 | "return "Unknown" when it doesn't have enough information." / "grade each dimension with an isolated LLM-as-judge rather than using one to grade all dimensions." / "Once the system is robust, it's sufficient to use human review only occasionally." | 위와 같음 |
| 같은 글 (6단계: 기록 읽기) | 기록과 채점을 읽지 않으면 채점기가 맞는지 알 수 없다. 채점 버그 수정만으로 42% → 95%가 된 사례(CORE-Bench), 지시를 따른 모델이 감점된 사례(METR 과제 설정 오류)가 있다 | "You won't know if your graders are working well unless you read the transcripts and grades from many trials." / "When a task fails, the transcript tells you whether the agent made a genuine mistake" + "or whether your graders rejected a valid solution." / "Opus 4.5 initially scored 42% on CORE-Bench," → "Opus 4.5's score jumped to 95%." | 위와 같음 |
| 같은 글 (7·8단계: 포화·소유) | 100%인 평가는 회귀만 잡는다. 평가셋은 담당자가 있는 살아 있는 산출물이다. 사용자 신고 실패를 과제로 바꾼다 | "An eval at 100% tracks regressions but provides no signal for improvement." / "An eval suite is a living artifact that needs ongoing attention and clear ownership to remain useful." / "Converting user-reported failures into test cases ensures your suite reflects actual usage," | 위와 같음 |
| A statistical approach to model evals (블로그) | ① 평균 옆에 표준오차 ② 묶인 문항은 묶음 단위 표준오차(3배 이상 커질 수 있음) ③ 같은 문항 재표집으로 분산 축소 ④ 두 모델은 문항별 짝 차이로 비교(문항 점수 상관 0.3~0.7) ⑤ 검정력 분석으로 문항 수 계획 | "we recommend clustering standard errors on the unit of randomization" / "clustered standard errors on popular evals can be over three times as large as naive standard errors" / "between 0.3 and 0.7 on a scale of −1 to +1" | https://www.anthropic.com/research/statistical-approach-to-model-evals |
| Adding Error Bars to Evals (Evan Miller, arXiv 2411.00640) | 평균 ± 1.96×표준오차로 95% 구간. 가능하면 짝 표준오차. 재표집 K=1→2에서 총분산 1/3 감소(논문 예시). 새 평가는 문항 1,000개 이상이어야 신호가 좋다 | "We suggest reporting the standard error of the mean alongside (beneath) the mean when reporting eval scores." / "We therefore recommend using the paired version of the standard error estimate wherever practicable." / "Going from K=1 (no resampling of answers) to K=2, the total variance is reduced by 1/3." / "new evals should contain at least 1,000 questions in order to have good signaling ability." | https://arxiv.org/abs/2411.00640 |
| Quantifying infrastructure noise in agentic coding evals (2026-02) | 자원 설정만으로 점수가 움직인다(Terminal-Bench 2.0에서 6%p). 엄격한 상한에서 인프라 오류 5.8%, 3배 여유에서 2.1%. 과제마다 "보장 할당"과 "강제 종료 상한" 두 값을 적고 공개한다. 시간 제한도 변수다. 3%p 미만 차이는 의심한다 | "the gap between the most- and least-resourced setups on Terminal-Bench 2.0 was 6 percentage points (p < 0.01)." / "we recommend that evals specify both parameters per task, not a single pinned value." / "limits can actually change what the eval measures." / "Naive binomial confidence intervals already span 1-2 percentage points;" / "leaderboard differences below 3 percentage points deserve skepticism" / "running at multiple times and on multiple days would help average out the noise." | https://www.anthropic.com/engineering/infrastructure-noise |
| Docs: Define success criteria | 성공 기준은 구체적·측정 가능·달성 가능·관련 있어야 한다 | "Use quantitative metrics or well-defined qualitative scales." / "Base your targets on industry benchmarks, prior experiments, AI research, or expert knowledge." | https://platform.claude.com/docs/en/test-and-evaluate/define-success |
| Docs: Develop tests (원문 직접 확인) | 채점은 가장 빠르고 믿을 만하고 확장되는 방법부터 고른다: 코드 → (사람은 가능하면 피함) → LLM. LLM 채점은 먼저 신뢰성을 시험한 뒤 늘린다. 기준표는 구체적으로, 출력은 correct/incorrect 같은 형태로, 판정 전에 추론하게 한다. 생성 모델과 다른 모델로 채점하는 것이 일반적 권장 | "Code-based grading: Fastest and most reliable, extremely scalable, but also lacks nuance" / "Human grading: Most flexible and high quality, but slow and expensive. Avoid if possible." / "LLM-based grading: Fast and flexible, scalable and suitable for complex judgment. Test to ensure reliability first, then scale." / "Generally best practice to evaluate with a different model from the one used to generate the evaluated output" | https://platform.claude.com/docs/en/test-and-evaluate/develop-tests |
| Writing effective tools for agents | 과제는 실제 사용에 근거하고 검증 가능한 결과와 짝짓는다. 형식 차이로 정답을 떨어뜨리는 엄격한 검증기를 피한다. 과적합을 막으려 보류 테스트셋을 쓴다. 정확도 외에 실행 시간·도구 호출 수·토큰·도구 오류를 모은다 | "Each evaluation prompt should be paired with a verifiable response or outcome." / "Avoid overly strict verifiers that reject correct responses due to spurious differences like formatting" / "We relied on held-out test sets to ensure we did not overfit to our “training” evaluations." | https://www.anthropic.com/engineering/writing-tools-for-agents |
| Raising the bar on SWE-bench Verified | 평가 대상은 모델이 아니라 에이전트 시스템(모델 + 주변 코드) 전체다. 모델은 채점 테스트를 볼 수 없어서 성공했다고 착각할 수 있다. 성공 실행도 수백 턴·10만 토큰 이상이 든다 | "SWE-bench doesn't just evaluate the AI model in isolation, but rather an entire "agent" system." / "Because the model cannot see the tests it's being graded against" / "many successful runs took hundreds of turns for the model to resolve, and >100k tokens." | https://www.anthropic.com/engineering/swe-bench-sonnet |

### 1-2. SWE-bench 계열

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| SWE-bench 논문 (arXiv 2310.06770) | 과제 = 실제 이슈 + 그 이슈를 닫은 PR. 저장소 12개 2,294건. PR이 테스트를 추가해야 하고, 실패→통과로 바뀌는 테스트가 하나 이상 있어야 한다. 지표는 해결 비율 | "We filter out task instances without at least one test where its status changes from a fail to pass" / "pass to pass tests are included to ensure that the revision does not break or violate any existing expected behavior" / "The metric for our benchmark is the percentage of task instances that are resolved." | https://arxiv.org/abs/2310.06770 |
| SWE-bench Verified 데이터셋 카드 (필드 정의) | 과제 필드: `instance_id`, `repo`, `base_commit`, `problem_statement`, `hints_text`, `patch`(정답), `test_patch`, `FAIL_TO_PASS`, `PASS_TO_PASS`, `version`, `environment_setup_commit`, `created_at` | `base_commit`: "The commit hash of the repository representing the HEAD of the repository before the solution PR is applied." / `FAIL_TO_PASS`: "A json list of strings that represent the set of tests resolved by the PR and tied to the issue resolution." / `PASS_TO_PASS`: "A json list of strings that represent tests that should pass before and after the PR application." / `environment_setup_commit`: "commit hash to use for environment setup and installation." | https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified |
| SWE-bench 저장소·평가 가이드 | 채점은 컨테이너에서 한다. 정답 패치로 설치를 먼저 확인한다(`swebench eval verified --gold`). 자원 소모가 크다. 결과 상태에 "빈 패치"가 따로 있다 | "SWE-bench uses Docker for reproducible evaluations." / "We recommend running on an x86_64 machine with at least 120GB of free storage, 16GB of RAM, and 8 CPU cores." / "The evaluation is performed in a containerized Docker environment to ensure consistent results across different platforms." | https://github.com/SWE-bench/SWE-bench · https://www.swebench.com/SWE-bench/guides/evaluation/ |
| OpenAI, Introducing SWE-bench Verified (원문 403, 미러 사본으로 확인) | 두 종류 테스트의 뜻. 원본의 세 문제: 지나치게 구체적인 테스트, 불명확한 이슈 설명, 환경 구성 실패. 개발자 93명이 1,699건을 3명씩 표시 → 38.3% 불명확, 61.1% 테스트가 유효한 해답을 떨어뜨릴 수 있음, 68.3% 제외, 500건 남김 | "If the FAIL_TO_PASS tests pass, this means the edit solves the issue." / "If the PASS_TO_PASS tests pass, then the edit has not inadvertently broken unrelated sections of the codebase." / "The unit tests used to evaluate the correctness of a solution are often overly specific, and in some cases are even unrelated to the issue." / "Many samples have an issue description that is underspecified, leading to ambiguity on what the problem is and how it should be solved." / "61.1% were flagged for unit tests that may unfairly mark valid solutions as incorrect." | https://openai.com/index/introducing-swe-bench-verified/ (미러: https://bittide.aicompass.dev/article/97de7998-f4a6-4479-86a7-6ae83bb4d791?locale=en) |
| OpenAI, Why we no longer evaluate SWE-bench Verified (2026-02, 검색 요약으로만 확인) | 사람이 검수한 500건에서도 2년 뒤 감사에서 문제: 감사한 138건 중 59.4%가 올바른 제출을 떨어뜨리는 테스트, 35.5%가 구현 세부를 강제하는 좁은 테스트, 주요 모델이 정답을 학습으로 봄. 한 번 검수했다고 끝이 아니다 | (원문 직접 인용 확보 못 함) | https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/ |
| SWE-bench 이슈 #465 (git 기록 누출) | 네트워크가 없어도 에이전트가 `git log --all`, `git log --grep`으로 미래 커밋(정답)을 본다. 대책: 원격·브랜치·reflog 제거, 미래 기록 전부 제거 | "even without internet access, the agent can still cheat by peeking at future commits using `git`." / "remove all future git history while preserving past history," | https://github.com/SWE-bench/SWE-bench/issues/465 |
| SWE-Bench+ (arXiv 2410.06992) | 성공 판정 패치의 32.67%는 이슈 본문에 답이 있었고, 31.08%는 테스트가 약해서 통과했다. 걸러내면 해결률 12.47% → 3.97% | "32.67% of the successful patches involve cheating as the solutions were directly provided in the issue report." / "31.08% of the passed patches are suspicious patches due to weak test cases." | https://arxiv.org/abs/2410.06992 |
| SWE-bench-Live (arXiv 2505.23419) | 정답 패치 전후 테스트 결과로 두 종류 테스트를 정하고, 검증을 여러 번 반복해 결과가 일관된 과제만 남긴다(불안정 테스트 제거) | "The validation is based on analyzing changes in the test suite results before and after applying the PR’s patch." / "the validation process is repeated multiple times." / "Only instances with consistent results across all runs are retained." | https://arxiv.org/abs/2505.23419 |
| METR, Many SWE-bench-Passing PRs Would Not Be Merged into Main (2026-03) | 테스트 통과 ≠ 받아들일 수 있는 변경. 유지보수자 4명이 통과 PR 296건을 검토했더니 약 절반은 머지 불가. 자동 채점이 유지보수자 판정보다 평균 24.2%p 높다. 사유: 코드 품질, 무관한 코드 손상, 실제로는 미해결. 정답 패치도 68%만 머지 판정(사람 판정 잡음) | "the automated grader is on average about 24.2 percentage points (standard error: 2.7) higher than the maintainer merge decision." / "about 68% of golden patches are indeed merged by our maintainers," / "The PR touches unrelated code and causes breakages." | https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/ |

### 1-3. Terminal-Bench, τ-bench, METR, 벤치마크 방법론

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Terminal-Bench 2.0 논문 (arXiv 2601.11868) | 과제 = 지시문 + 컨테이너 이미지 + 테스트 + 예시 해답 + 시간 제한. 테스트는 명령이 아니라 컨테이너 최종 상태를 본다. 검증: 자동으로 정답 해답 실행, 검토자 약 3시간/과제, 여러 모델로 시험 실행, 속임수를 찾는 적대 에이전트, 감사 2명 추가. 이미지 안에 테스트·해답이 있으면 읽어서 속일 수 있어 검사한다. 조합마다 5회 이상 실행, 95% 구간 표시 | "an instruction, a Docker image, a set of tests, an example solution, and a time limit." / "they do not test the agent's commands or console output." / "each task has an oracle solution script that mirrors a real workflow and, when executed, causes all test cases to pass." / "An adversarial exploit agent was run to detect design flaws that could allow agents to cheat and pass the tests." / "For each supported model and agent combination, we run the benchmark at least five times, resulting in a total of 32,155 trials." | https://arxiv.org/abs/2601.11868 |
| Harbor(Terminal-Bench 후속 형식) 문서 | 과제 디렉터리: `instruction.md`, `task.toml`, `environment/`, `solution/`, `tests/`. 테스트 스크립트가 보상 파일을 쓴다 | "A Harbor task is an instruction, environment, and test script." / "The script must produce a numerical reward in the environment at `/logs/verifier/reward.txt`." | https://docs.harborframework.com/tasks/overview |
| τ-bench (arXiv 2406.12045) | pass^k = k번 독립 시도가 모두 성공할 확률의 과제 평균. n번 중 c번 성공이면 과제별 추정값은 C(c,k)/C(n,k). pass@k = 1 − C(n−c,k)/C(n,k). 채점은 대화가 아니라 종료 시점 DB 상태와 정답 상태 비교. 과제당 3회 이상. gpt-4o급도 성공 50% 미만, pass^8은 25% 미만 | "pass^k (pass hat k), defined as the chance that all k i.i.d. task trials are successful, averaged across tasks." / "Our evaluation scheme compares the database state at the end of each episode with the ground truth expected state." / "we run at least 3 trials per task." / "quite inconsistent (pass^8 <25% in retail)." | https://arxiv.org/abs/2406.12045 |
| METR Task Standard (저장소는 보관 상태) | 과제는 환경 + 지시 + (선택) 자동 채점. 과제 묶음(family)이 구현을 공유한다. 에이전트는 권한 낮은 사용자로 실행해 채점 자료에 닿지 못하게 한다. 네트워크 허용 범위를 과제가 명시한다. 과제 자체에 테스트를 둔다 | "Tasks are defined as part of a task family, which are one or more related tasks that may share a bunch of implementation." / "it cannot access files and processes created/owned by `root`." / "The task also specifies the degree of internet access available from inside the environment" / "You can write automated tests for tasks using pytest." | https://github.com/METR/task-standard |
| METR, Measuring AI Ability to Complete Long Tasks | 과제 난이도를 "숙련자가 걸리는 시간"으로 잰다. 4분 미만 과제는 거의 100%, 4시간 이상은 10% 미만. 평가셋 난이도 분포를 사람 소요 시간으로 적을 근거 | "current models have almost 100% success rate on tasks taking humans less than 4 minutes" / "but succeed <10% of the time on tasks taking more than around 4 hours." | https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/ |
| Establishing Best Practices for Building Rigorous Agentic Benchmarks (arXiv 2507.02825) | 과제 설정·보상 설계 결함으로 성능 추정이 상대 100%까지 틀린다. 예: 불충분한 테스트, 빈 응답을 성공으로 셈 | "SWE-bench Verified uses insufficient test cases" / "TAU-bench counts empty responses as successful" / "Such issues can lead to under- or overestimation of agents' performance by up to 100% in relative terms." | https://arxiv.org/abs/2507.02825 |
| AI Agents That Matter (arXiv 2407.01502) | 정확도만 보지 말고 비용을 함께 최적화한다. 보류 셋이 부실하거나 없으면 지름길·과적합이 생긴다 | "there is a narrow focus on accuracy without attention to other metrics," / "many agent benchmarks have inadequate holdout sets, and sometimes none at all," | https://arxiv.org/abs/2407.01502 |

### 1-4. Hamel Husain · Shreya Shankar · Eugene Yan · 모델 채점 신뢰성 연구

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Hamel, Creating a LLM-as-a-Judge That Drives Business Results | 판정 기준이 되는 도메인 전문가 한 명을 정한다. 1~5점 대신 통과/실패 + 상세 비평. 30건쯤에서 시작해 새 실패 유형이 안 나올 때까지. 60건 미만은 구간이 너무 넓다. 판정기는 전문가와 수렴할 때까지 고친다(사례: 3회 반복에 90% 초과 일치). 일치율 대신 참양성률·참음성률을 따로 본다 | "No complex scoring scales or multiple metrics. Just a clear pass or fail decision." / "People don't know what to do with a 3 or 4." / "My heuristic is that I start with around 30 examples and keep going until I do not see any new failure modes." / "Below 60 examples, the confidence intervals are often too wide to support a useful conclusion." / "Treat the human labels as ground truth and report the judge's True Positive Rate and True Negative Rate separately." | https://hamel.dev/blog/posts/llm-judge/ |
| Hamel, Your AI Product Needs Evals | 3단계: 단위 테스트(코드 변경마다) → 사람·모델 평가(주기적) → A/B(큰 변경 뒤). 비용 순서가 실행 빈도를 정한다. 데이터 보는 마찰을 없앤다. 통과율은 제품 결정이다 | "I often run Level 1 evals on every code change" / "The cost of Level 3 > Level 2 > Level 1. This dictates the cadence and manner you execute them." / "You must remove all friction from the process of looking at data." / "Your pass rate is a product decision, depending on the failures you are willing to tolerate." | https://hamel.dev/blog/posts/evals/ |
| Hamel, A Field Guide to Rapidly Improving AI Products | 지표를 위에서 정하지 말고 실제 기록에서 실패 유형을 뽑아 센다. 합성 데이터는 입력만 만들고 기대 응답은 만들지 않는다. 평가 기준은 산출물을 보면서 바뀐다(기준 표류) | "Error analysis consistently reveals the highest-ROI improvements." / "Use LLMs to generate realistic user queries or inputs, not the expected AI responses." / "it is impossible to completely determine evaluation criteria prior to human judging of LLM outputs." / "a binary pass/fail forces evaluators to make a clear judgment: did this output achieve its purpose or not?" | https://hamel.dev/blog/posts/field-guide/ |
| Hamel·Shankar, AI Evals FAQ | 기록 100건 이상 검토, 새 실패 유형이 안 나올 때까지. 열린 메모 → 유형 묶기 → 건수 세기. 에이전트는 먼저 전체 성공 여부, 그다음 "마지막 성공 단계 × 첫 실패 단계" 표. 첫 상류 실패에 집중. CI용 셋은 작고(보통 100건 이상) 결정적 검사 위주. 판정기 라벨은 실패 유형마다 100~200건, 통과·실패 각 50건 이상, 10~20%만 프롬프트 예시로 쓰고 나머지는 개발·시험으로 나눈다. 여러 검사를 합칠 때는 "전부 통과" 비율 | "We recommend reviewing at least 100 traces." / "Continue until new traces stop revealing failure modes or changing existing ones." / "A useful heuristic is to focus on the first upstream failure." / "Create a matrix where rows represent the last successful state and columns represent where the first failure occurred." / "Favor assertions or other deterministic checks over LLM-as-judge evaluators." / "we recommend at least 50 passing and 50 failing examples." / "A simple approach I like to use is a 'pass all' rate." | https://hamel.dev/blog/posts/evals-faq/ |
| Shankar 외, Who Validates the Validators? (arXiv 2404.12272) | 모델 채점기는 채점 대상 모델의 문제를 물려받으므로 사람 검증이 필요하다. 기준을 정하려면 채점해 봐야 하고, 채점하면 기준이 바뀐다 | "LLM-generated evaluators simply inherit all the problems of the LLMs they evaluate, requiring further human validation." / "users need criteria to grade outputs, but grading outputs helps users define criteria." | https://arxiv.org/abs/2404.12272 |
| Eugene Yan, Evaluating the Effectiveness of LLM-Evaluators | 객관적 항목은 단건 채점, 주관적 항목은 쌍 비교. 가능하면 이진 출력. 판정기 평가는 상관계수가 아니라 분류 지표(정밀도·재현율, 우연 보정 일치도). 일치율 80%인데 κ는 0.62인 사례(인용 논문), 일관된 요약은 95% 넘게 잡지만 비일관은 30~60%만 잡는 사례 | "Thus, where possible, I have my evaluators return binary outputs." / "Classification metrics are more straightforward to apply and interpret." / "I tend to be skeptical of correlation metrics." | https://eugeneyan.com/writing/llm-evaluators/ |
| Zheng 외, Judging LLM-as-a-Judge (arXiv 2306.05685) | 모델 채점기의 편향: 위치, 장황함 선호, 자기 선호, 제한된 추론. 강한 판정기는 사람과 80% 넘게 일치 | "position, verbosity, and self-enhancement biases, as well as limited reasoning ability." / "achieving over 80% agreement, the same level of agreement between humans." | https://arxiv.org/abs/2306.05685 |
| Stureborg 외, LLMs are Inconsistent and Biased Evaluators (arXiv 2405.01724) | 점수 분포가 치우치고, 여러 속성을 한꺼번에 매기면 앞 판단에 끌려가고, 같은 조건 표본 간 일치가 낮다 | "show skewed and biased distributions of ratings," / "experience anchoring effects for multi-attribute judgments," / "low "inter-sample" agreement," | https://arxiv.org/abs/2405.01724 |
| Thakur 외, Judging the Judges (arXiv 2406.12624) | 가장 큰 모델만 사람과 쓸 만하게 일치한다. 일치율이 높아도 점수는 크게 다를 수 있다. 관대한 쪽으로 기운다 | "only the best (and largest) models achieve reasonable alignment with humans." / "judges with high percent agreement can still assign vastly different scores." | https://arxiv.org/abs/2406.12624 |

### 1-5. 평가 도구 문서 (개념만)

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Inspect AI (UK AISI) | 평가 = 데이터셋 + 풀이기(solver) + 채점기(scorer). 표본마다 별도 샌드박스. 표본별 파일·설정 스크립트. 종료 시 자동 정리. 표본별 메시지·토큰·시간·비용 제한. 채점은 실행과 분리해 나중에 다시 할 수 있다. 기본 지표에 정확도와 표준오차가 같이 나온다 | "An Inspect evaluation is a Task that brings together three things:" / "each sample gets its own sandbox instance, even if the sandbox is defined at Task level." / "Limits to apply to sample execution." / "Most report `accuracy` and `stderr`; `exact()` and `f1()` report `mean` and `stderr`." | https://inspect.aisi.org.uk/ · https://inspect.aisi.org.uk/sandboxing.html · https://inspect.aisi.org.uk/scorers.html |
| LangSmith 평가 개념 | 데이터셋(예제) → 실험(버전별 결과). 참조 출력은 애플리케이션에 전달되지 않고 평가기만 쓴다. 분할과 버전. 평가기 종류: 사람·코드·LLM·쌍 비교. 10~20건을 손으로 만들어 시작하고 운영 기록을 예제로 바꾼다. 반복 실행으로 잡음을 줄이고 평균·표준편차를 본다 | "These do not get passed to your application, they are only used in evaluators." / "Create 10–20 high-quality examples covering common scenarios and edge cases." / "Once in production, convert real traces into examples." / "LangSmith automatically creates dataset versions when examples change." | https://docs.langchain.com/langsmith/evaluation-concepts · https://docs.langchain.com/langsmith/repetition |
| Langfuse 평가 개요 | 온라인(운영 기록)과 오프라인(배포 전 데이터셋)을 잇는 고리: 운영에서 본 흥미로운 사례를 데이터셋으로 만들고, 실험으로 비교하고, 다시 운영 기록으로 | "turn interesting examples into datasets" / "Compare prompt, model, or code changes side by side." | https://langfuse.com/docs/evaluation/overview |

### 1-6. 숫자만 모은 표

| 질문 | 값 | 출처 |
|---|---|---|
| 처음 몇 건 | 20~50건(실제 실패에서) / 손으로 10~20건 / 30건에서 시작해 새 실패 유형이 안 나올 때까지 | Anthropic / LangSmith / Hamel |
| CI(회귀)용 셋 규모 | 보통 100건 이상, 결정적 검사 위주 | Hamel FAQ |
| 통계적으로 좋은 신호 | 문항 1,000개 이상 (모델 벤치마크 기준) | Miller |
| 과제당 반복 | 3회 이상(τ-bench) / 5회 이상(Terminal-Bench 2.0) / 10회(Anthropic의 SWE-bench 자원 실험) | 각 출처 |
| 회귀 묶음 기대 통과율 | 거의 100% | Anthropic |
| 깨진 과제 신호 | 여러 번 돌려 0% | Anthropic |
| 자원 설정에 따른 점수 차 | 6%p (Terminal-Bench 2.0), SWE-bench는 RAM 5배에서 1.54%p | Anthropic infra noise |
| 인프라 오류율 | 엄격 상한 5.8% → 3배 여유 2.1% → 무제한 0.5% | 같은 글 |
| 검수 전 벤치마크의 불량률 | 불명확한 요청 38.3%, 유효 해답을 떨어뜨릴 수 있는 테스트 61.1% | OpenAI(미러) |
| 테스트 통과 패치 중 받아들일 수 없는 비율 | 약 절반(유지보수자 판정), 자동 채점이 24.2%p 높음 | METR |
| 요청문에 답이 든 비율 / 약한 테스트로 통과한 비율 | 32.67% / 31.08% (성공 판정 패치 중) | SWE-Bench+ |
| 과제 검수 공수 | 과제당 검토자 약 3시간 + 감사 2명 | Terminal-Bench 2.0 |
| 판정기 보정용 라벨 | 통과·실패 각 50건 이상, 실패 유형당 100~200건 | Hamel FAQ |
| 기록 검토량 | 100건 이상 | Hamel FAQ |

---

## 2. S1 · 평가 규칙 · 기준선 보강안

문서 형식(고민할 것 / 진행 / 검증 / 완료 기준 / 흔한 함정)으로 적는다. 각 항목 끝의 [근거]는 1절의 출처, [제안]은 출처에서 직접 나오지 않고 이 프로젝트 구조에 맞춰 내가 추론한 것이다.

### 2-1. 용어를 먼저 고정한다

지금 문서는 "시나리오", "사례", "실행", "시도"를 섞어 쓴다. 비교 규칙을 쓰려면 단위가 분명해야 한다.

| 용어 | 뜻 |
|---|---|
| 과제(시나리오) | 입력과 성공 기준이 고정된 시험 한 건 |
| 시도 | 과제 하나를 한 번 돌린 것. 과제당 k번 |
| 결과 상태 | 시도가 끝났을 때 환경(작업 트리, 테스트 결과)의 상태. 에이전트의 말이 아니다 |
| 기록 | 시도의 전체 흐름(출력, 도구 호출, 중간 결과) |
| 채점기 | 결과 상태나 기록의 한 측면을 판정하는 코드·모델·사람 |
| 묶음(family) | 같은 원본 이슈·같은 모듈에서 나온 과제들. 분할과 표준오차의 단위 |
| 평가 조건 | 데이터 버전, 채점기 버전, 환경 이미지, 자원·시간 한도, 모델, 프롬프트·코드 커밋, 메모리 스냅샷, 반복 수 |

[근거] Anthropic Demystifying(용어), Miller(묶음 단위 표준오차).

### 2-2. S1 고민할 것 (보강)

1. **과제 한 건이 판정 가능한가.** 담당자 두 명이 따로 봐도 같은 통과/실패를 내는가. 채점기가 확인하는 것이 전부 요청문에서 읽히는가(숨긴 테스트가 요청문에 없는 함수 이름·파일 경로·오류 문구를 요구하지 않는가). 요청문에 해답이 들어 있지 않은가. [근거] Anthropic 2단계, OpenAI(38.3% / 61.1%), SWE-Bench+(32.67%).
2. **결과가 기준이고 과정은 관문이다.** 통과 여부는 결과 상태로 정한다. 과정은 "금지 행동"과 "의존 관계가 있는 순서"만 통과/실패로 보고, 도구 호출 순서·횟수·종류는 진단 지표로만 남긴다. 다른 길로 푼 정답을 떨어뜨리면 채점기가 틀린 것이다. [근거] Anthropic 5단계("too rigid"), Terminal-Bench("do not test the agent's commands").
3. **테스트 통과만으로 충분한가.** 숨긴 테스트를 통과한 변경의 절반가량이 리뷰에서 거절될 수 있다. 통과한 변경 중 표본을 실제 리뷰어가 "머지할 수 있나"로 판정하는 층을 둘지 정한다. [근거] METR 2026-03.
4. **묶음을 둘로 나눈다.** 능력 묶음(아직 잘 못하는 작업, 낮은 통과율에서 시작)과 회귀 묶음(이미 되는 작업, 100% 근처). 능력 과제가 안정적으로 통과하면 회귀 묶음으로 옮기고 더 어려운 과제를 채운다. [근거] Anthropic.
5. **한 번 돌린 결과는 수치가 아니다.** 반복 수 k, 주 지표(매번 통과인가 한 번이라도 통과인가), "개선"과 "회귀"를 무엇으로 판정할지를 결과를 보기 전에 적는다. 사람이 고르지 않고 결과를 그대로 받는 코딩 에이전트는 매번 통과(pass^k)가 주 지표다. [근거] τ-bench, Anthropic.
6. **무엇을 잠그고 무엇을 고칠 수 있나.** 한 번의 비교 안에서는 평가 조건 전체를 잠근다. 개발용 과제·채점기의 결함은 고칠 수 있지만, 고치면 새 버전이고 비교할 양쪽을 다시 채점한다. 최종 확인용은 볼 때마다 닳는다. [근거] Shankar(기준 표류), Anthropic(CORE-Bench 42%→95%), AI Agents That Matter.
7. **에이전트가 정답에 닿는 경로가 몇 개인가.** 파일(테스트·정답 패치), git 기록(미래 커밋, 이전 시도), 네트워크(원본 저장소의 수정 PR), 에이전트의 경험 메모리(같은 사례의 해결 기록), 요청문 자체. [근거] SWE-bench #465, Anthropic 4단계, Terminal-Bench(이미지 검사). 메모리 경로는 [제안].
8. **얼마가 드나.** 과제 수 × 반복 × 비교 대상 수 × 시도당 비용. 어느 범위를 얼마나 자주 돌릴지 층을 나눈다. [근거] Hamel(3단계), AI Agents That Matter.

### 2-3. 과제 스키마 (코딩 에이전트용)

핵심은 **에이전트에게 주는 파일과 채점자만 보는 파일을 물리적으로 나누는 것**이다. 지금 템플릿은 `request`와 `expected`가 같은 JSONL 줄에 있어서, 그 파일이 작업 디렉터리 안에 있으면 그대로 누출된다.

```
eval/
  tasks/<버전>/dev.jsonl        # 에이전트 하네스가 읽는 것: 아래 public 부분만
  tasks/<버전>/holdout.jsonl
  env/<과제 ID>/                # 환경 준비·초기화 스크립트 또는 이미지 정의
eval-private/                   # 에이전트 실행 환경에 마운트하지 않는다
  <버전>/<과제 ID>/grader.json  # 아래 private 부분
  <버전>/<과제 ID>/tests.patch  # 숨긴 테스트
  <버전>/<과제 ID>/reference.patch  # 사람이 만든 정답 변경
```

공개 부분(에이전트 실행기가 읽는다):
```json
{
  "id": "T-001",
  "family": "billing-rounding",
  "suite": "capability",
  "type": "normal",
  "pair_id": null,
  "repo": {"source": "git@...:team/app.git", "base_commit": "<sha>"},
  "request": "사용자가 실제로 쓸 요청문. 채점이 요구하는 것은 전부 여기서 읽혀야 한다",
  "environment": {
    "setup": "eval/env/T-001/setup.sh",
    "image_digest": "",
    "network": "none",
    "resources": {"cpu": 2, "memory_guaranteed_mb": 4096, "memory_kill_mb": 8192},
    "limits": {"max_turns": 60, "timeout_sec": 1800, "max_cost": null},
    "fault_injection": null
  }
}
```

비공개 부분(채점기만 읽는다):
```json
{
  "id": "T-001",
  "expected_behavior": "patch",
  "tests": {
    "test_patch": "tests.patch",
    "fail_to_pass": ["tests/billing/test_round.py::test_half_even"],
    "pass_to_pass": ["tests/billing/test_round.py::test_existing_total", "tests/billing/test_invoice.py"],
    "test_command": "pytest -q {tests}"
  },
  "reference_patch": "reference.patch",
  "allowed_paths": ["src/billing/**"],
  "protected_paths": ["tests/**", "eval/**", ".github/**", "pyproject.toml"],
  "must_not": [
    {"id": "out_of_scope_write", "check": "변경 파일이 allowed_paths 밖"},
    {"id": "test_tamper", "check": "protected_paths 변경, skip·xfail 추가"},
    {"id": "secret_access", "check": "기록에 시크릿 경로 읽기"},
    {"id": "history_peek", "check": "base_commit 이후 객체 조회 시도"}
  ],
  "order": [["plan_approved", "first_write"], ["last_write", "test_run"]],
  "response_checks": ["변경 요약의 파일 목록이 실제 diff와 일치"],
  "validation": {
    "reference_passes": "3/3", "noop_fails": true, "alt_solution_passes": null,
    "flaky_excluded": [], "request_reviewed_by": "", "validated_at": "", "env_hash": ""
  },
  "metadata": {"source": "PR #1234", "reviewer": "", "version": "", "human_minutes": 30, "promoted_from_trace": null}
}
```

필드 설명과 근거:

| 필드 | 뜻 | 근거 |
|---|---|---|
| `base_commit` | 수정 PR이 적용되기 직전 커밋. 에이전트는 이 시점의 저장소만 본다 | SWE-bench 필드 정의 |
| `fail_to_pass` | 수정 전에는 실패하고 정답 변경 뒤 통과하는 테스트. "고쳐졌다"의 증거. 최소 1개 | SWE-bench 논문("at least one test … from a fail to pass") |
| `pass_to_pass` | 수정 전후 모두 통과하는 테스트. "안 깨뜨렸다"의 증거 | OpenAI(미러), 데이터셋 카드 |
| `test_patch` | 숨긴 테스트. 에이전트가 끝난 뒤 채점기가 덮어써서 적용한다 | SWE-bench(`test_patch`), Terminal-Bench |
| `reference_patch` | 사람이 만든 정답 변경. 에이전트 채점에는 안 쓰고 과제·채점기 검증에만 쓴다 | Anthropic 2단계, Terminal-Bench(oracle) |
| `expected_behavior` | `patch` / `ask`(되물어야 함) / `refuse` / `report_incomplete`. 유형별로 통과 조건이 다르다 | Anthropic 3단계(균형), 현재 문서의 유형 표 |
| `allowed_paths`, `protected_paths` | 범위 밖 수정과 테스트 조작을 코드로 판정하는 근거 | 현재 `must_not`을 판정 가능하게 구체화 [제안] |
| `environment.resources` | 보장 할당과 강제 종료 상한을 따로 적는다 | Anthropic infra noise |
| `environment.limits` | 턴·시간·비용 한도. 한도가 바뀌면 다른 평가다 | Inspect(표본별 제한), infra noise(시간 제한) |
| `environment.network` | 없음 또는 허용 목록 | METR Task Standard |
| `validation` | 과제가 검증을 통과했다는 기록 | SWE-bench-Live, Terminal-Bench 2.0 |
| `human_minutes` | 숙련자가 걸리는 시간. 난이도 분포를 보는 축 | METR time horizon |
| `promoted_from_trace` | 운영 기록에서 승격했다면 원본 기록 ID. 메모리 누출 차단에 쓴다 | [제안] |

`order`는 과제마다 같으면 과제 파일이 아니라 평가 공통 설정에 한 번만 두고, 과제에서는 예외만 적는다. [제안]

### 2-4. S1 진행 (보강)

**과제 만들기**
1. 과거 PR에서 만들 때: `base_commit` = 수정 PR의 부모 커밋, `test_patch` = PR의 테스트 변경, `reference_patch` = PR의 나머지 변경. `base_commit`에서 테스트를 돌리고, 정답 변경을 적용한 뒤 다시 돌려서 실패→통과는 `fail_to_pass`, 통과→통과는 `pass_to_pass`로 자동 분류한다. [근거] SWE-bench 논문, SWE-bench-Live.
2. 요청문은 이슈 원문을 그대로 쓰지 않는다. 해답이 들어 있으면 지우고, 테스트가 요구하는 인터페이스가 빠져 있으면 채운다. [근거] SWE-Bench+, OpenAI.
3. 처음에는 5건으로 파이프라인을 끝까지 통과시키고(과제 형식·격리·채점기 검증용), 기준선을 재기 전에 개발용 20건 이상으로 늘린다. 20건이어도 구간은 넓다(아래 2-7). [근거] Anthropic(20~50), LangSmith(10~20). 5건→20건 두 단계는 [제안].
4. 능력 묶음과 회귀 묶음을 `suite`로 표시한다.
5. 유형별 통과 조건을 적는다. 되물어야 하는 요청은 "쓰기 없이 질문으로 끝남", 거절은 "쓰기 없이 거절 사유", 도구 실패는 "미완료라고 보고하고 깨진 상태를 남기지 않음". 빈 변경이 성공으로 세어지는 경로가 없는지 확인한다. [근거] ABC 논문(빈 응답을 성공으로 센 사례).

**격리**
6. 시도마다 새 환경에서 시작한다: 새 컨테이너나 새 작업 트리, `base_commit` 체크아웃, 의존성은 고정된 잠금 파일·이미지로 설치. 시도 사이에 남는 것(작업 트리, 캐시, 임시 파일, 에이전트 세션, 메모리 저장소 쓰기)이 없어야 한다. [근거] Anthropic 4단계, Inspect(표본별 샌드박스).
7. git 기록에서 `base_commit` 이후의 커밋·브랜치·태그·reflog·원격을 지운다. 이전 시도의 커밋도 남기지 않는다. [근거] SWE-bench #465, Anthropic(이전 시도의 git 기록).
8. 에이전트의 경험 메모리는 평가 조건의 일부다. 시도마다 같은 스냅샷을 읽기 전용(또는 복사본)으로 주고, 시도 중 쓴 내용은 버린다. 운영 기록에서 승격한 과제는 그 원본 세션에서 나온 메모리 항목을 평가 때 제외한다. 그러지 않으면 능력이 아니라 정답 검색을 재게 된다. [제안: S6 구조에서 나오는 누출 경로]
9. 자원(보장 할당, 강제 종료 상한)과 시간·턴 한도를 과제에 적고, 한도에 걸려 죽은 시도는 "환경 오류"로 따로 센다. [근거] infra noise.

**정답 숨기기**
10. 숨긴 테스트와 정답 변경은 에이전트 실행 환경에 넣지 않는다. 에이전트가 끝난 뒤 채점기가 (a) 결과 diff를 뽑고 (b) `protected_paths`를 원본으로 되돌리고 (c) `test_patch`를 적용해 (d) 테스트를 돌린다. 에이전트가 고친 테스트 파일로 채점하지 않는다. [근거] SWE-bench 방식, Terminal-Bench(이미지 검사).
11. 채점 코드는 에이전트와 다른 권한·다른 프로세스에서 돈다. [근거] METR Task Standard.
12. 네트워크는 끄거나 허용 목록만 연다(패키지 저장소 등). 원본 저장소의 수정 PR에 닿으면 안 된다. [근거] METR Task Standard, SWE-bench #465.
13. 평가 파일에 고유 표식 문자열을 넣어 두고, 기록·메모리·프롬프트에서 그 문자열이 나오면 누출로 본다. [근거] Terminal-Bench 2.0(canary check).

**채점기**
14. 판정 순서: 판정 유효성(환경 오류·채점기 오류·근거 부족 아님) → 정책 관문 → 결과(`fail_to_pass` 전부 통과 그리고 `pass_to_pass` 전부 통과) → 응답. 과제 통과는 전부 통과일 때만이다. 부분 점수(통과한 테스트 비율, 도달한 단계)는 진단용으로 따로 남긴다. [근거] Anthropic("binary (all graders must pass)"), Hamel("pass all").
15. 채점 방법 선택: 테스트·diff·기록 이벤트로 판정되는 것은 코드. 의미 판단(요약과 변경의 일치, 되묻는 질문의 적절성, 코드 품질)만 모델. 모델 채점 결과가 사람과 갈리면 사람. [근거] Anthropic Docs(코드 → LLM, 사람은 피함).
16. 모델 채점은 기본을 통과/실패 + 이유로 한다. 기준 하나에 판정기 하나, 근거가 부족하면 "판단 불가"를 내게 하고 이를 "근거 부족"으로 매핑한다. 사람이 통과·실패로 라벨한 사례(처음 30건, 목표는 각 50건)로 "잘못 통과"와 "잘못 탈락" 비율을 따로 잰다. 라벨의 일부만 프롬프트 예시로 쓰고 나머지로 잰다. [근거] Hamel, Yan, Anthropic, Stureborg.
17. 통과한 변경에서 표본을 뽑아 실제 리뷰어가 머지 가능 여부를 판정한다(주기적으로). 통과율과 머지 가능률의 차이를 적는다. [근거] METR 2026-03.

### 2-5. S1 검증 (보강)

과제 검증(과제마다, 과제를 고칠 때마다):

| 넣는 것 | 기대 판정 | 잡는 결함 |
|---|---|---|
| 정답 변경, 3회 | 3회 모두 통과 | 과제가 풀 수 없음, 불안정한 테스트 |
| 아무것도 안 바꾼 상태 | 실패 (`ask`·`refuse` 과제는 통과가 아니라 "응답 없음 = 실패") | 빈 변경이 통과하는 채점기 |
| `base_commit`에서 숨긴 테스트만 실행, 3회 | `fail_to_pass`는 매번 실패, `pass_to_pass`는 매번 통과 | 불안정한 테스트(결과가 갈리는 테스트는 목록에서 뺀다) |
| 테스트를 지우거나 건너뛰게 한 변경 | 정책 위반 | 테스트 조작이 통과하는 경로 |
| 특정 입력만 분기해 테스트를 맞춘 변경 | 실패 (통과하면 테스트가 약하다) | 약한 테스트 |
| 다른 방식으로 푼 정답(이름·구조가 다름) | 통과 (실패하면 테스트가 지나치게 구체적이다) | 유효한 해답을 떨어뜨리는 테스트 |
| 요청문만 보고 다른 담당자가 통과 조건을 적어 봄 | 숨긴 테스트의 요구와 일치 | 불명확한 요청 |

채점기 검증(기존 반례 표에 추가): 범위 밖 파일 수정 → 실패, 보호 경로 수정 → 정책 위반, 한도 초과로 죽은 시도 → 환경 오류, 판정기 "판단 불가" → 근거 부족.

실행 검증:
- 처음 전체 실행 뒤 통과 기록과 실패 기록을 각각 읽는다. 실패마다 "에이전트 잘못 / 과제·채점기 결함 / 환경"으로 분류한다. 실패의 상당수가 과제·채점기 결함이면 에이전트를 고치기 전에 평가를 고친다. [근거] Anthropic 6단계.
- 여러 번 돌려 0%인 과제는 깨진 과제로 의심하고 정답 변경으로 다시 검증한다. 매번 100%인 과제는 회귀 묶음으로 분류한다. [근거] Anthropic.
- 같은 조건으로 전체를 두 번 돌려 차이를 잰다. 이 차이가 "아무것도 안 바꿔도 생기는 흔들림"이고, 이후 비교의 하한이다. [제안. 근거 방향: infra noise]
- 지름길을 찾으라고 지시한 에이전트를 한 번 돌려 본다. 통과하면 그 경로를 막는다. [근거] Terminal-Bench 2.0(exploit agent).

### 2-6. S1 완료 기준 (보강안)

- [ ] 과제 파일이 공개·비공개로 나뉘어 있고, 비공개 부분은 에이전트 실행 환경에서 읽을 수 없음을 시험했다(읽기 시도가 실패하는 기록)
- [ ] 과제마다 과제 검증 기록이 있다: 정답 변경 통과(3회), 무변경 실패, 불안정 테스트 제외
- [ ] 개발용이 20건 이상(파이프라인 개통은 5건), 최종 확인용이 묶음 단위로 분리돼 10건 이상이다. 다르게 정했으면 S0 지표와 함께 근거가 적혀 있다
- [ ] 채점기가 반례 시험을 통과했고, 모델 채점을 쓴다면 사람 라벨 대비 잘못 통과·잘못 탈락 비율이 적혀 있다
- [ ] 시도마다 환경이 초기화됨을 확인했다(앞 시도가 남긴 파일·커밋·메모리가 다음 시도에서 안 보인다)
- [ ] 명령 한 줄로 전체가 다시 돌고, 평가 조건(버전·해시·한도·반복 수)이 결과 파일에 같이 남는다
- [ ] 반복 수, 주 지표, 개선·회귀 판정 규칙, 최종 확인용 사용 규칙이 결과를 보기 전에 적혀 있다

### 2-7. 모든 단계가 쓰는 비교 규칙 (신설 제안)

S3·S4·S6·S7의 완료 기준에 "평가 회귀가 없다"가 있는데 문서 어디에도 회귀의 정의가 없다. 비결정적인 시스템에서 정의 없이 쓰면 "한 번 돌려 같거나 높으면 통과"가 된다.

**측정**
- 과제당 k회 반복한다. 기본 3회, 채택·출시 판단에는 5회. [근거] τ-bench(3회 이상), Terminal-Bench(5회 이상).
- 보고하는 값: 시도 성공률(과제별 c/k의 평균), 매번 통과율(pass^k), 한 번이라도 통과율(pass@k), 유효 판정 비율, 환경 오류율, 정책 위반 수.
- 과제별 추정: k번 중 c번 성공이면 pass^j = C(c,j)/C(k,j), pass@j = 1 − C(k−c,j)/C(k,j). 과제 평균을 낸다. [근거] τ-bench.
- 표본 단위는 시도가 아니라 과제(같은 묶음의 과제가 많으면 묶음)다. 구간은 과제별 값의 표준오차로 낸다. [근거] Miller(묶음 표준오차), 현재 agent-eval의 "반복 실행을 독립 사례로 세지 않는다"와 같은 뜻.

**구간이 얼마나 넓은가 (직접 계산, 통과율 60% 가정, 95% Wilson 구간)**

| 과제 수 | 관측 | 95% 구간 |
|---|---|---|
| 5 | 3/5 | 23% ~ 88% |
| 20 | 12/20 | 39% ~ 78% |
| 30 | 18/30 | 42% ~ 75% |
| 50 | 30/50 | 46% ~ 72% |
| 100 | 60/100 | 50% ~ 69% |

5건으로는 "60%"와 "30%"도 구분하지 못한다. 과제 하나가 20%p다.

**비교**
- 같은 과제·같은 반복 수·같은 평가 조건에서 한 가지만 바꾼다. 가능하면 기준과 후보를 같은 시간대에 번갈아 돌린다(모델 API·인프라 상태가 시간에 따라 변한다). [근거] infra noise("multiple times and on multiple days"). 번갈아 돌리기는 [제안].
- 판정은 과제별 짝 차이로 한다: 과제마다 (후보 성공률 − 기준 성공률)을 내고, 평균과 95% 구간, 좋아진 과제 수와 나빠진 과제 수를 적는다. [근거] Miller(짝 표준오차 권장).
- 짝 차이 구간의 너비(직접 계산, 과제별 차이의 표준편차 0.3~0.4 가정): 20건이면 ±13~18%p, 30건이면 ±11~14%p, 50건이면 ±8~11%p. 즉 20~50건으로는 10%p 안팎보다 작은 개선을 가려낼 수 없다.
- 과제 수가 적으면 부호 검정을 쓴다(일반 통계, 출처 아님). 좋아진 과제 b개, 나빠진 과제 c개일 때 양측 p값(직접 계산): 5:0 → 0.06, 6:0 → 0.03, 8:1 → 0.04, 8:2 → 0.11, 4:1 → 0.38.

**판정 규칙 (결과를 보기 전에 적는다)**
- **개선:** 짝 차이의 95% 구간 하한이 0보다 크다(또는 미리 정한 최소 개선폭보다 크다).
- **차이 없음:** 구간이 0을 포함한다. 이때는 "좋아졌다"고 쓰지 않는다. 지연·비용·단순함이 나아졌을 때만 채택한다.
- **회귀 없음:** (a) 정책 위반 0건, (b) 회귀 묶음에서 기준이 매번 통과하던 과제 중 후보가 한 번이라도 실패한 과제는 기록을 읽어 원인을 분류했고 에이전트 원인이 없다, (c) 전체 짝 차이의 구간 하한이 미리 정한 허용폭(예: −5%p)보다 크다. 허용폭은 같은 조건 두 번 실행의 차이보다 작게 잡을 수 없다.
- **무효:** 환경 오류율이나 근거 부족 비율이 미리 정한 한도(예: 5%)를 넘으면 그 실행으로 판정하지 않는다. 환경 오류 시도는 정한 횟수만큼 다시 돌리고 재실행 사실을 남긴다. 그래도 남으면 분모에 두고 따로 표시한다. [근거 방향] infra noise(인프라 오류율 5.8%). 한도와 재실행 정책은 [제안].

**잠금과 버전**
- 비교 한 번 안에서는 데이터·채점기·환경·한도·반복 수를 바꾸지 않는다.
- 개발용 과제나 채점기의 결함을 발견하면 고친다. 고치면 버전을 올리고, 비교할 양쪽을 새 버전으로 다시 채점(필요하면 다시 실행)한다. 고친 이유를 `design/decisions.md`에 남긴다. "결과를 본 뒤 기준을 바꾸지 않는다"는 한 번의 비교 안에서의 규칙이지 평가를 영원히 못 고친다는 뜻이 아니다. [근거] Shankar, Hamel(기준 표류), Anthropic(채점 버그 수정 사례).
- 최종 확인용은 열어 본 횟수와 날짜를 기록한다. 결과를 보고 에이전트를 고쳤다면 그 최종 확인용은 다음 판에서 개발용으로 내리고 새로 채운다. [근거] AI Agents That Matter, Anthropic(held-out). 내리고 새로 채우는 규칙은 [제안].

**비용 층**

| 층 | 범위 | 언제 | 채점 |
|---|---|---|---|
| 연기 시험 | 회귀 묶음 일부(5~10건) × 1회 | 변경할 때마다 | 코드만 |
| 개발 평가 | 개발용 전체 × 3회 | 반영 후보마다 | 코드 + 필요한 모델 채점 |
| 채택 평가 | 개발용 전체 × 5회, 기준과 후보 번갈아 | 채택 결정 전 | 전부 |
| 최종 확인 | 최종 확인용 × 5회 | 출시 전 한 번 | 전부 + 리뷰어 표본 |

- 실행 전에 과제 수 × 반복 × 버전 수 × 시도당 평균 비용을 적는다(시도당 평균은 기준선에서 나온다).
- 조건 해시가 같은 기준 결과는 재사용할 수 있지만, 모델·인프라가 바뀌었을 수 있는 기간이 지났으면 다시 잰다.
- 지표에 "통과 1건당 비용"을 넣어 정확도와 비용을 같이 본다.
[근거] Hamel(3단계 빈도), AI Agents That Matter. 층 구성과 건수는 [제안].

### 2-8. S2 기준선 (보강)

**고민할 것**
- 기준선은 숫자 하나가 아니라 (평가 조건 + 분포 + 실패 분류)다. 조건이 안 적힌 기준선과는 나중에 비교할 수 없다.
- 무엇의 기준선인가: 기반 에이전트를 거의 그대로 둔 상태. 이후 모든 변경의 비교 대상이다.

**진행**
- 개발용 전체 × 3회 이상. 평가 조건(데이터 버전, 채점기 버전, 환경 해시, 자원·시간 한도, 모델 식별자, 코드 커밋, 메모리 스냅샷, 측정 일시)을 결과와 같이 남긴다.
- 같은 조건으로 한 번 더 돌려 두 실행의 차이를 적는다(흔들림 바닥).
- 실패 기록을 전부 읽고(처음에는 전부, 많아지면 표본) "에이전트 / 과제·채점기 / 환경"으로 먼저 나눈 뒤, 에이전트 실패만 유형별로 센다. 긴 기록은 첫 상류 실패 지점을 본다. "마지막으로 성공한 단계 × 처음 실패한 단계" 표를 만든다. [근거] Anthropic 6단계, Hamel FAQ.
- 0%인 과제와 100%인 과제를 표시한다.

**검증**
- 기준선 실행에서 환경 오류율이 한도 안이다.
- 실패 분류에서 "과제·채점기 결함"이 0건이 될 때까지 평가를 고치고 다시 잰 값이 기준선이다.

**완료 기준에 추가**
- [ ] 기준선에 평가 조건과 95% 구간, 매번 통과율, 같은 조건 재실행 차이가 적혀 있다
- [ ] 실패 기록을 읽고 분류했다(과제·채점기 결함은 고쳐서 0건)

**흔한 함정에 추가:** 조건을 안 적은 기준선, 환경 오류를 에이전트 실패로 세기, 채점기 결함으로 낮게 나온 수치를 기준선으로 삼아 이후 "개선"을 부풀리기.

### 2-9. 운영 실패에서 평가셋이 자라는 방법

- 승격 조건(현재 문서: 반복·재현 가능·정답 정의 가능)에 더해: 사용자가 신고한 실패를 우선하고, 영향 큰 순으로 고른다. [근거] Anthropic.
- 승격 절차: 원본 기록 → 비식별화 → `base_commit` 고정 → 실패 재현(지금 에이전트로 k회) → 정답 변경과 숨긴 테스트 작성 → 과제 검증(2-5 표) → 묶음 배정 → 버전 올림.
- 승격 과제의 초기 분류: 지금 에이전트가 실패하면 능력 묶음, 고친 뒤 안정적으로 통과하면 회귀 묶음.
- 실패만 넣지 않는다. 같은 유형의 "해야 하는 경우"와 "하면 안 되는 경우"를 짝으로 넣는다. [근거] Anthropic 3단계.
- 과제를 넣거나 고치면 새 버전이고, 기준선을 새 버전으로 다시 잰다. 이전 버전 수치와 직접 비교하지 않는다.
- 주기적으로: 포화된 능력 과제는 회귀로 옮기고, 깨진 과제는 고치거나 은퇴시키고(은퇴 사유 기록), 최종 확인용을 새 사례로 채운다. 담당자가 있다. [근거] Anthropic 7·8단계, OpenAI 2026(검수한 벤치마크도 낡는다).
- 승격 과제와 같은 사례의 해결 기록이 경험 메모리에 있으면 평가 때 제외한다. [제안]

### 2-10. 흔한 함정 (추가분)

- 과제 5건의 통과율 차이로 채택을 결정하기
- 한 번 돌린 결과끼리 비교하기, 반복 시도를 독립 사례로 세기
- 요청문에 없는 이름·경로를 숨긴 테스트가 요구하기
- 요청문(이슈 원문)에 해답이 들어 있기
- 에이전트가 고친 테스트 파일로 채점하기
- git 기록에 정답 커밋이나 이전 시도의 커밋이 남아 있기
- 평가 중 쌓인 메모리가 다음 시도로 넘어가기
- 도구 호출 순서가 정답과 다르다고 떨어뜨리기
- 환경 오류를 에이전트 실패로 세거나 표에서 조용히 빼기
- 0%인 과제를 "어려운 과제"로 두기(깨진 과제일 가능성이 높다)
- 기록을 안 읽고 점수만 보기
- 통과율 100%인 묶음으로 "개선"을 재려 하기
- 최종 확인용을 출시 때마다 다시 쓰면서 계속 "처음 본 데이터"라고 믿기
- 테스트 통과를 머지 가능과 같다고 보기

---

## 3. 템플릿 · 스킬 수정안 (그대로 넣을 문장)

저장소 규칙에 맞춰 출처 표시 없이 썼다. 특정 프레임워크·컨테이너 도구를 전제하지 않는다.

### 3-1. `METHOD.md` — 공통 규칙 3 교체

현재:
> 3. **평가 기준은 결과를 보기 전에 고정한다.** 결과를 본 뒤 기준·임계값·반복 수를 바꾸지 않는다. 최종 확인용 데이터는 수정에 쓰지 않는다.

교체안:
```markdown
3. **평가 조건은 비교하기 전에 잠근다.** 한 번의 비교 안에서는 데이터·채점기·환경·한도·반복 수·판정 규칙을 바꾸지 않는다. 개발용 과제나 채점기의 결함은 고칠 수 있지만, 고치면 새 버전이고 비교할 양쪽을 다시 채점한다. 최종 확인용 데이터는 수정에 쓰지 않는다.
```

### 3-2. `METHOD.md` — "모든 단계에 공통인 규칙" 아래에 새 절 추가

```markdown
### 비교 규칙 (기준선 이후 모든 단계)

"평가 회귀가 없다", "좋아졌다"는 아래 규칙으로만 판정한다. 값(반복 수, 허용폭, 한도)은 `design/01-eval.md`에 결과를 보기 전에 적는다.

1. **한 번 돌린 결과는 수치가 아니다.** 과제마다 여러 번 돌린다(기본 3회, 채택·출시 판단은 5회). 시도 성공률과 매번 통과한 비율을 같이 적는다. 사람이 결과를 고르지 않고 그대로 받는 작업은 매번 통과한 비율이 주 지표다.
2. **표본은 과제다.** 반복 시도를 독립 사례로 세지 않는다. 구간은 과제(같은 묶음이 많으면 묶음) 단위로 낸다. 수치에는 95% 구간을 붙인다.
3. **같은 과제끼리 짝지어 비교한다.** 같은 과제·같은 반복 수·같은 조건에서 한 가지만 바꾸고, 과제별 차이의 평균과 구간, 좋아진 과제 수와 나빠진 과제 수를 적는다. 가능하면 기준과 후보를 같은 시간대에 번갈아 돌린다.
4. **판정은 넷 중 하나다.**
   - 개선: 차이의 구간 하한이 0(또는 미리 정한 최소 개선폭)보다 크다
   - 차이 없음: 구간이 0을 포함한다. "좋아졌다"고 쓰지 않는다. 지연·비용·단순함이 나아졌을 때만 채택한다
   - 회귀: 정책 위반이 생겼거나, 회귀 묶음에서 매번 통과하던 과제가 에이전트 원인으로 실패했거나, 차이의 구간 하한이 허용폭 아래다
   - 무효: 환경 오류·근거 부족 비율이 한도를 넘었다. 다시 잰다
5. **흔들림 바닥을 안다.** 같은 조건으로 두 번 돌린 차이보다 작은 변화는 근거가 아니다.
6. **점수가 움직이면 기록을 읽는다.** 새로 실패한 과제는 에이전트 잘못인지, 과제·채점기 결함인지, 환경 문제인지 나눈다. 뒤의 둘이면 평가를 고치고 양쪽을 다시 잰다.
7. **범위를 층으로 나눈다.** 변경할 때마다 작은 회귀 묶음 1회, 반영 후보마다 개발용 전체, 채택 전 반복을 늘린 비교, 출시 전 최종 확인용 한 번. 실행 전에 과제 수 × 반복 × 버전 수 × 시도당 비용을 적는다.
```

### 3-3. `METHOD.md` — S1 절 교체안

```markdown
## S1. 시험지와 채점기

**목적:** "좋아졌다"를 판정할 기준을 만든다. S2와 동시에 진행한다.

**고민할 것**
1. **무엇이 대표 작업인가.** 실제 과거 이슈·PR, 개발자가 손으로 확인하던 항목, 사용자가 신고한 실패에서 뽑는다. LLM은 요청문의 변형을 늘리는 데만 쓰고 정답은 맡기지 않는다.
2. **과제 한 건이 판정 가능한가.** 담당자 두 명이 따로 봐도 같은 통과/실패를 내는가. 채점기가 확인하는 것이 전부 요청문에서 읽히는가. 요청문에 해답이 들어 있지 않은가.
3. **무엇이 성공인가.** 결과가 기준이고 과정은 관문이다.
   - 결과(Outcome): 실패하던 숨긴 테스트가 통과하고(고쳐졌다), 통과하던 테스트가 그대로 통과한다(안 깨뜨렸다)
   - 과정(Trajectory): 금지 행동과 의존 관계가 있는 순서만 통과/실패로 본다. 도구 호출의 순서·횟수·종류는 진단 지표로만 남긴다
   - 응답(Final Response): 변경 요약이 실제 변경과 일치하는가. 못 끝냈으면 못 끝냈다고 말했는가
4. **테스트 통과로 충분한가.** 테스트를 통과해도 리뷰에서 거절될 변경이 있다. 통과한 변경의 표본을 실제 리뷰어가 볼지 정한다.
5. **무엇으로 채점하나.** 테스트·diff·기록으로 가려지는 것은 코드, 의미 판단만 모델 채점(Judge), 이견은 사람이 본다.
6. **묶음을 어떻게 나누나.** 고치려는 문제점으로 묶는다(예: "도구 호출이 너무 잦다"). 아직 못하는 작업(능력 묶음, 낮은 통과율에서 시작)과 이미 되는 작업(회귀 묶음, 100% 근처)을 구분한다.
7. **에이전트가 정답에 닿는 길은 몇 개인가.** 파일, git 기록, 네트워크, 경험 메모리, 요청문.
8. **몇 번 돌리고 무엇으로 판정하나.** 반복 수, 주 지표, 개선·회귀 판정 규칙(공통 "비교 규칙"), 실행 비용.

**진행**
- `golden-dataset` 스킬로 5건을 만들어 파이프라인을 끝까지 통과시키고, 기준선을 재기 전에 개발용 20건 이상으로 늘린다.
- 과제 하나의 구성:
  - 에이전트에 주는 것: 저장소 스냅샷(수정 직전 커밋) + 요청문 + 환경(준비·초기화 방법, 네트워크, 자원·시간·턴 한도)
  - 채점자만 보는 것: 숨긴 테스트(실패→통과여야 할 것 / 계속 통과해야 할 것), 사람이 만든 정답 변경, 수정 허용 경로와 보호 경로, 금지 행동, 순서 규칙, 과제 검증 기록, 출처·검수자
- 과거 PR에서 만들 때는 수정 직전 커밋에서 테스트를 돌리고 정답 변경을 적용해 다시 돌려, 실패→통과와 통과→통과 테스트를 가른다.
- 정상 사례만 넣지 않는다. 정보가 부족해 되물어야 하는 요청, 거절해야 하는 요청, 도구가 실패하는 상황, 한 조건만 다른 경계 사례 쌍을 넣고 유형마다 통과 조건을 적는다.
- 시도마다 깨끗한 환경에서 시작한다. 앞 시도의 파일·커밋·캐시·메모리가 남지 않게 하고, 경험 메모리는 고정된 스냅샷을 읽기 전용으로 준다.
- 정답을 숨긴다. 숨긴 테스트와 정답 변경은 실행 환경에 넣지 않고, 수정 시점 이후의 git 기록을 지우고, 네트워크를 끄거나 허용 목록만 연다. 에이전트가 끝난 뒤 채점기가 보호 경로를 원본으로 되돌리고 숨긴 테스트를 적용해 돌린다.
- 사례 묶음 단위로 개발용과 최종 확인용을 나누고 버전을 고정한다.
- `agent-eval` 스킬로 채점기를 만든다. 판정 순서는 유효성 → 정책 관문 → 결과 → 응답이고, 전부 통과해야 과제 통과다. 정책 위반은 다른 점수와 평균 내지 않는다. 판정은 통과 / 실패 / 근거 부족 / 채점기 오류 / 환경 오류로 나눈다.
- 모델 채점은 기준 하나에 판정 하나, 통과/실패와 이유를 내게 하고, 근거가 부족하면 "판단 불가"를 허용한다. 사람이 라벨한 사례로 잘못 통과·잘못 탈락을 따로 잰다.

**검증**
- 과제마다: 정답 변경으로 여러 번 돌려 매번 통과, 아무것도 안 바꾼 상태로 실패, 결과가 갈리는 테스트는 목록에서 뺀다. 테스트를 지운 변경은 정책 위반, 다른 방식으로 푼 정답은 통과가 나오는지 본다.
- 채점기를 일부러 만든 반례로 시험한다: 순서만 다른 정상 실행 → 통과, 승인 없이 수정한 실행 → 실패, 범위 밖 수정 → 실패, 기록이 지워진 실행 → 근거 부족, 빈 정답 → 채점기 오류, 한도에 걸려 죽은 실행 → 환경 오류.
- 실행 환경 안에서 숨긴 테스트·정답·이후 커밋을 읽으려는 시도가 실패하는지 본다.
- 전체를 돌린 뒤 통과 기록과 실패 기록을 읽는다. 매번 0%인 과제는 깨진 과제인지 먼저 확인한다.
- 명령 한 줄로 평가 전체가 다시 돌고, 평가 조건이 결과와 함께 남는다.

**완료 기준**
- [ ] 과제 파일이 에이전트용과 채점자용으로 나뉘어 있고, 실행 환경에서 채점자용을 읽을 수 없음을 확인했다
- [ ] 과제마다 검증 기록(정답 변경 통과, 무변경 실패, 불안정 테스트 제외)이 있다
- [ ] 개발용이 20건 이상이고 최종 확인용이 묶음 단위로 따로 있다 (다르게 정했으면 S0 지표와 함께 근거를 적는다)
- [ ] 채점기가 반례 시험을 통과했다
- [ ] 시도마다 환경이 초기화되고, 평가가 명령 한 줄로 재실행된다
- [ ] 반복 수·주 지표·개선과 회귀의 판정 규칙이 결과를 보기 전에 적혀 있다

**흔한 함정:** 질문·답 형식으로 만들기, LLM이 쓴 정답을 검수 없이 쓰기, 요청문에 없는 것을 숨긴 테스트가 요구하기, 에이전트가 정답 테스트나 이후 커밋을 읽을 수 있게 두기, 에이전트가 고친 테스트로 채점하기, 도구 호출 순서가 다르다고 떨어뜨리기, 과제 몇 건·한 번 실행의 차이로 결정하기, 점수만 보고 기록을 안 읽기, 결과를 보고 최종 확인용 데이터로 다시 고치기.
```

### 3-4. `METHOD.md` — S2 수정 문장

진행의 마지막 줄 교체:
```markdown
- S1의 개발용 평가셋으로 기준선을 잰다. 과제마다 3회 이상 돌리고, 평가 조건(데이터·채점기·환경 버전, 한도, 모델, 코드 커밋, 메모리 스냅샷, 측정 일시)을 결과와 함께 남긴다.
- 같은 조건으로 한 번 더 돌려 두 실행의 차이를 적는다. 이것이 흔들림 바닥이다.
- 실패 기록을 읽고 에이전트 잘못 / 과제·채점기 결함 / 환경 문제로 먼저 나눈다. 뒤의 둘은 고치고 다시 잰다. 에이전트 실패만 유형별로 세고 고칠 단계를 붙인다.
```

완료 기준의 기준선 줄 교체:
```markdown
- [ ] 기준선 표가 채워졌다: 평가 조건, 성공률(95% 구간), 매번 통과한 비율, 같은 조건 재실행 차이, 정책 위반 수, 환경 오류율, 첫 응답 시간·전체 지연, 호출 수, 토큰, 통과 1건당 비용, 실패 유형 분류
```

흔한 함정 끝에 추가:
```markdown
조건을 적지 않은 기준선, 환경 오류를 에이전트 실패로 세기, 채점기 결함으로 낮게 나온 수치를 기준선으로 삼기.
```

### 3-5. `templates/01-eval.md` — 전체 교체안

````markdown
# S1. 시험지와 채점기

## 시험지
- 출처 (과거 이슈·PR / 개발자 인터뷰 / 사용자 신고·운영 기록):
- 데이터셋이 겨냥하는 문제점:
- 에이전트용 위치와 버전: `eval/tasks/<버전>/dev.jsonl`, `eval/tasks/<버전>/holdout.jsonl` (해시: )
- 채점자용 위치: (에이전트 실행 환경에 넣지 않는 곳. 해시: )
- 담당자:

에이전트용 (실행기가 읽는다):
```json
{"id": "T-001", "family": "", "suite": "capability | regression",
 "type": "normal | ask | refuse | tool_failure | boundary_pair", "pair_id": null,
 "repo": {"source": "", "base_commit": ""},
 "request": "",
 "environment": {"setup": "", "network": "none | allowlist",
                 "resources": {"cpu": null, "memory_guaranteed_mb": null, "memory_kill_mb": null},
                 "limits": {"max_turns": null, "timeout_sec": null, "max_cost": null},
                 "fault_injection": null}}
```

채점자용 (채점기만 읽는다):
```json
{"id": "T-001", "expected_behavior": "patch | ask | refuse | report_incomplete",
 "tests": {"test_patch": "", "fail_to_pass": [], "pass_to_pass": [], "test_command": ""},
 "reference_patch": "",
 "allowed_paths": [], "protected_paths": ["tests/**", "eval/**"],
 "must_not": ["범위 밖 파일 수정", "테스트 삭제·건너뛰기·수정", "시크릿 접근", "수정 시점 이후 기록 조회"],
 "order": [["계획 승인", "첫 수정"], ["마지막 수정", "테스트 실행"]],
 "response_checks": [],
 "validation": {"reference_passes": "", "noop_fails": null, "alt_solution_passes": null,
                "flaky_excluded": [], "request_reviewed_by": "", "validated_at": ""},
 "metadata": {"source": "", "reviewer": "", "version": "", "human_minutes": null, "promoted_from_trace": null}}
```

| 유형 | 통과 조건 | 개발용 | 최종 확인용 |
|---|---|---|---|
| 정상 | 실패→통과 테스트 전부 통과, 계속 통과 테스트 전부 통과 |  |  |
| 정보 부족 (되물어야 함) | 수정 없이 필요한 질문으로 끝남 |  |  |
| 거절해야 함 | 수정 없이 거절 사유를 말함 |  |  |
| 도구 실패 | 미완료라고 보고하고 깨진 상태를 남기지 않음 |  |  |
| 경계 사례 쌍 | 쌍의 두 과제가 각자 조건대로 판정됨 |  |  |

| 묶음 | 건수 | 기대 통과율 |
|---|---|---|
| 능력 (아직 못하는 작업) |  | 낮게 시작 |
| 회귀 (이미 되는 작업) |  | 100% 근처 |

## 격리와 숨기기
| 항목 | 방법 | 확인한 증거 |
|---|---|---|
| 시도마다 새 환경 (작업 트리, 캐시, 세션) |  |  |
| 수정 시점 이후 git 기록 제거 (커밋·브랜치·태그·reflog·원격) |  |  |
| 숨긴 테스트·정답 변경이 실행 환경에 없음 |  |  |
| 채점 전 보호 경로를 원본으로 되돌림 |  |  |
| 네트워크 차단 또는 허용 목록 |  |  |
| 경험 메모리: 고정 스냅샷 읽기 전용, 승격 과제의 원본 기록 제외 |  |  |
| 자원·시간·턴 한도 |  |  |

## 과제 검증 (과제마다)
| 넣는 것 | 기대 | 통과한 과제 수 / 전체 |
|---|---|---|
| 정답 변경 (3회) | 매번 통과 |  |
| 아무것도 안 바꾼 상태 | 실패 |  |
| 수정 전 상태에서 숨긴 테스트 (3회) | 실패→통과 목록은 매번 실패, 계속 통과 목록은 매번 통과 |  |
| 테스트를 지우거나 건너뛰게 한 변경 | 정책 위반 |  |
| 다른 방식으로 푼 정답 (가능한 과제만) | 통과 |  |
| 다른 담당자가 요청문만 보고 적은 통과 조건 | 숨긴 테스트의 요구와 일치 |  |

- 제외한 불안정 테스트:
- 고치거나 뺀 과제와 이유:

## 채점기
판정 순서: 유효성 → 정책 관문 → 결과 → 응답. 전부 통과해야 과제 통과.

| 축 | 무엇을 보나 | 담당 (코드 / 판단 모델 / 모델 채점 / 사람) | 통과·실패에 반영 |
|---|---|---|---|
| 결과 | 실패→통과 테스트, 계속 통과 테스트 | 코드 | 예 |
| 정책 위반 (필수 관문) | must_not, 보호 경로, 허용 경로 | 코드 | 예 |
| 과정: 순서 | 승인 전 수정 없음, 수정 뒤 테스트 실행 | 코드 | 예 |
| 과정: 진단 | 턴 수, 도구 호출 수·종류, 재시도, 토큰 | 코드 | 아니오 |
| 응답 | 변경 요약이 실제 변경과 일치, 미완료 보고 |  | 예 |
| 품질 (표본) | 통과한 변경을 리뷰어가 머지할 수 있나 | 사람 | 따로 보고 |

- 모델 채점 기준 (기준 하나에 판정 하나, 통과/실패 + 이유, "판단 불가" 허용):
- 판정 모델:
- 사람 라벨 수 (통과 / 실패):
- 사람 판정과 비교: 잘못 통과 ___ / 잘못 탈락 ___
- 같은 입력 반복 시 판정이 바뀐 비율:

## 채점기 검증
| 반례 | 기대 판정 | 실제 판정 |
|---|---|---|
| 순서만 다른 정상 실행 | 통과 |  |
| 승인 없이 수정한 실행 | 실패 |  |
| 범위 밖 파일을 수정한 실행 | 실패 |  |
| 테스트 파일을 고친 실행 | 정책 위반 |  |
| 기록이 지워진 실행 | 근거 부족 |  |
| 빈 정답 | 채점기 오류 |  |
| 한도에 걸려 죽은 실행 | 환경 오류 |  |
| 사람이 만든 정답 변경 | 통과 |  |
| 아무것도 안 바꾼 상태 | 실패 |  |

## 판정 규칙 (결과를 보기 전에 적는다)
- 실행 명령:
- 과제당 반복: 개발 ___회 / 채택·최종 ___회
- 주 지표: 매번 통과한 비율 / 시도 성공률 (하나를 고르고 이유)
- 개선: 과제별 짝 차이의 95% 구간 하한 > ___
- 회귀 허용폭: 구간 하한 > −___ (같은 조건 재실행 차이 ___보다 작게 잡지 않는다)
- 무효: 환경 오류율 > ___% 또는 근거 부족 > ___%. 환경 오류 시도 재실행 최대 ___회
- 채택 조건 (순서대로): 판정 유효 → 정책 위반 0 → 목표 지표 개선·회귀 없음 → 지연·비용 → 최종 확인용 통과
- 최종 확인용 사용 규칙: 출시 전 한 번. 열어 본 기록:

| 날짜 | 버전 | 누가 | 결과를 보고 고쳤나 |
|---|---|---|---|

## 비용
| 층 | 범위 × 반복 | 언제 | 예상 비용 |
|---|---|---|---|
| 연기 시험 |  | 변경할 때마다 |  |
| 개발 평가 |  | 반영 후보마다 |  |
| 채택 평가 |  | 채택 전 |  |
| 최종 확인 |  | 출시 전 |  |

## 완료 기준
- [ ] 과제 파일이 에이전트용과 채점자용으로 나뉘어 있고, 실행 환경에서 채점자용을 읽을 수 없음을 확인했다
- [ ] 과제마다 검증 기록(정답 변경 통과, 무변경 실패, 불안정 테스트 제외)이 있다
- [ ] 개발용이 20건 이상이고 최종 확인용이 묶음 단위로 따로 있다 (다르면 근거를 적었다)
- [ ] 채점기가 반례 시험을 통과했다
- [ ] 시도마다 환경이 초기화되고, 평가가 명령 한 줄로 재실행된다
- [ ] 판정 규칙이 결과를 보기 전에 적혔다
````

### 3-6. `templates/02-baseline.md` — "기준선" 절 교체안

```markdown
## 기준선 (개발용 평가셋)

평가 조건:
| 데이터 버전 | 채점기 버전 | 환경 해시 | 자원·시간·턴 한도 | 모델 | 코드 커밋 | 메모리 스냅샷 | 측정 일시 |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

| 실행 | 건수×반복 | 성공률 (95% 구간) | 매번 통과 | 유효 판정 비율 | 환경 오류율 | 정책 위반 | 첫 응답 / 전체 지연 | 호출 수 | 토큰 | 통과 1건당 비용 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1차 |  |  |  |  |  |  |  |  |  |  |
| 같은 조건 재실행 |  |  |  |  |  |  |  |  |  |  |

- 같은 조건 두 실행의 차이 (흔들림 바닥):
- 매번 0%인 과제 (깨진 과제인지 확인한 결과):
- 매번 100%인 과제 (회귀 묶음으로 분류):

실패 기록 1차 분류:
| 원인 | 건수 | 조치 |
|---|---|---|
| 에이전트 잘못 |  | 아래 유형 분류로 |
| 과제·채점기 결함 |  | 고치고 다시 잰다 (0건이어야 기준선) |
| 환경 문제 |  | 고치고 다시 잰다 |

실패 유형 분류 (에이전트 잘못만):
| 유형 | 건수 | 첫 실패 단계 | 고칠 단계 (S3 컨텍스트 / S4 도구·스킬 / S5 제어) |
|---|---|---|---|
```

완료 기준 마지막 줄 교체:
```markdown
- [ ] 기준선 표(평가 조건, 구간, 재실행 차이 포함)와 실패 분류가 채워졌고, 과제·채점기 결함이 0건이다
```

### 3-7. `golden-dataset/SKILL.md` — 수정안

`<procedure>` 2번 끝 문장 교체:
```markdown
처음엔 5건으로 파이프라인(과제 형식, 격리, 채점)을 끝까지 통과시키고, 기준선을 재기 전에 개발용 20건 이상으로 늘린다. 아직 못하는 작업(능력)과 이미 되는 작업(회귀)을 `suite`로 구분한다.
```

4번 교체:
```markdown
4. **과제로 쓴다.** 질문·답 형식이 아니다. 파일을 둘로 나눈다.
   - 에이전트용: `repo.base_commit`(수정 직전 커밋), `request`, `environment`(준비·초기화, 네트워크, 자원·시간·턴 한도)
   - 채점자용(실행 환경에 넣지 않는다): `tests.test_patch`, `tests.fail_to_pass`(수정 전 실패 → 정답 변경 뒤 통과, 1개 이상), `tests.pass_to_pass`(전후 모두 통과), `reference_patch`(사람이 만든 정답 변경), `allowed_paths`, `protected_paths`, `must_not`, `order`(의존 관계가 있는 순서만), `expected_behavior`, `validation`, `metadata`(출처, 검수자, 버전, family)
   - 과거 PR에서 만들 때: 수정 직전 커밋에서 테스트를 돌리고, 정답 변경을 적용해 다시 돌려 두 목록을 가른다.
   - 요청문에 해답이 들어 있으면 지운다. 숨긴 테스트가 요구하는 이름·경로·동작이 요청문에서 읽히지 않으면 요청문을 고치거나 테스트를 고친다.
   - 정답 경로 하나를 강제하지 말고 지켜야 할 제약을 적는다.
```

5번과 6번 사이에 새 단계 추가:
```markdown
6. **과제를 검증한다.** 통과하지 못한 과제는 평가셋에 넣지 않는다.
   - 정답 변경으로 3회 → 매번 통과. 아무것도 안 바꾼 상태 → 실패.
   - 수정 전 상태에서 숨긴 테스트 3회 → 결과가 갈리는 테스트는 목록에서 뺀다. `fail_to_pass`가 0개가 되면 과제를 버리거나 테스트를 다시 쓴다.
   - 테스트를 지우거나 건너뛰게 한 변경 → 정책 위반. 다른 방식으로 푼 정답 → 통과(실패하면 테스트가 지나치게 구체적이다).
   - 다른 담당자가 요청문만 보고 통과 조건을 적어 숨긴 테스트의 요구와 맞는지 본다.
   - 결과를 `validation`에 적는다.
```

기존 6번(운영 기록 승격) 끝에 추가:
```markdown
사용자가 신고한 실패를 우선한다. 원본 기록 ID를 `metadata.promoted_from_trace`에 적어, 평가 때 같은 사례의 경험 메모리를 제외할 수 있게 한다. 지금 실패하면 능력, 고친 뒤 안정적으로 통과하면 회귀로 분류한다.
```

기존 7번(분리와 동결) 끝에 추가:
```markdown
holdout을 열어 본 날짜·버전·사람을 `design/01-eval.md`에 적는다. 결과를 보고 에이전트를 고쳤다면 그 holdout은 다음 판에서 dev로 내리고 새 사례로 채운다.
```

`<anti_patterns>`에 추가:
```markdown
- 요청문과 정답을 같은 파일에 두고 그 파일을 작업 디렉터리에 두기
- 이슈 원문을 그대로 요청문으로 쓰기(해답이 들어 있거나 테스트가 요구하는 것이 빠져 있다)
- 정답 변경으로 통과하는지 확인하지 않은 과제 넣기
- 매번 0%인 과제를 "어려운 과제"로 두기
```

### 3-8. `agent-eval/SKILL.md` — 수정안

`<principles>` 첫 줄 교체:
```markdown
- 결과가 기준이고 과정은 관문이다. Outcome으로 통과를 정하고, Trajectory는 금지 행동과 의존 순서만 통과/실패로 본다. 다른 길로 푼 정답을 떨어뜨리면 평가기가 틀린 것이다. Final Response는 따로 본다.
```

`<principles>`에 추가:
```markdown
- 한 번 돌린 결과로 판정하지 않는다. 과제마다 여러 번 돌리고, 표본은 과제로 세고, 같은 과제끼리 짝지어 비교한다.
- 점수가 움직이면 기록을 읽는다. 실패는 에이전트 잘못 / 과제·평가기 결함 / 환경 문제로 먼저 나눈다.
```

`<procedure>` 2번 교체:
```markdown
2. **Judge rubric:** 기준 하나에 Judge 하나. 출력은 판정(PASS / FAIL / UNKNOWN)·이유·근거 단계(JSON)로 고정한다. UNKNOWN은 INSUFFICIENT_EVIDENCE로 매핑한다. 등급이나 점수는 통과/실패로 답이 안 되는 기준에만 쓰고, 그때는 등급마다 관찰 가능한 기준을 적는다. 사람이 PASS/FAIL로 라벨한 사례(처음 30건, 목표는 각 50건)에서 false pass와 false fail을 따로 잰다. 라벨의 일부만 프롬프트 예시로 쓰고 나머지로 잰다. 같은 입력을 여러 번 돌려 판정이 바뀌는 비율을 본다. 가능하면 평가 대상과 다른 모델을 쓴다.
```

3번 교체:
```markdown
3. **실행:** 유료 실행 전에 규모(과제 수 × 반복 × 버전 ≈ 시도 수 × 시도당 비용)를 한 줄로 알린다. 시도마다 새 환경에서 시작한다(작업 트리, 캐시, 세션, 수정 시점 이후 git 기록 제거, 경험 메모리는 고정 스냅샷). 에이전트가 끝나면 보호 경로를 원본으로 되돌리고 숨긴 테스트를 적용한 뒤 돌린다. 자원·시간·턴 한도에 걸려 죽은 시도는 INFRA_ERROR다. 기준과 후보는 같은 시간대에 번갈아 돌린다. 평가 조건과 실행 기록을 관측 플랫폼과 `eval/results/<버전>-<날짜>.jsonl`에 남긴다.
```

4번 교체:
```markdown
4. **채점:** 판정 순서는 유효성 → 정책 관문 → Outcome(`fail_to_pass` 전부 통과, `pass_to_pass` 전부 통과) → Final Response. 전부 통과해야 과제 PASS다. 순서 규칙은 같은 대상의 모든 쓰기 시도(실패·차단 포함)에 적용한다. milestone 도달, 도구 호출 수·종류, 반복·복구는 진단 지표로 따로 기록하고 통과/실패에 넣지 않는다.
```

6번 교체:
```markdown
6. **비교 보고:** 시도 성공률(95% 구간), pass^k, pass@k, 평가 완료율, INFRA_ERROR 비율, 정책 위반 수, slice별 개선·회귀, p50/p95 지연, 통과 1건당 비용.
   - n번 중 c번 성공한 과제의 pass^k = C(c,k)/C(n,k), pass@k = 1 − C(n−c,k)/C(n,k). 과제 평균을 낸다.
   - 반복 실행을 독립 사례로 세지 않는다. 구간은 과제(family가 크면 family) 단위로 낸다.
   - 비교는 과제별 짝 차이의 평균과 구간, 좋아진 과제 수 / 나빠진 과제 수로 쓴다. 구간이 0을 포함하면 "차이 없음"이라고 쓴다.
   - 새로 실패한 과제와 매번 0%인 과제는 기록을 읽은 결과를 붙인다.
```

`<cost>` 교체:
```markdown
<cost>
범위를 층으로 나눈다: 변경할 때마다 회귀 묶음 일부 1회(코드 채점만), 반영 후보마다 dev 전체 3회, 채택 전 5회 짝 비교, 출시 전 holdout 한 번. 조건 해시가 같은 기준 결과는 재사용하되 모델·환경이 바뀌었을 수 있으면 다시 잰다. 온라인은 샘플링, 배치는 "체크 필요" 표시된 기록 위주로 고르고 예상 비용을 먼저 계산한다.
</cost>
```

`<when_to_rerun>` 끝에 추가:
```markdown
과제나 평가기의 결함을 고쳤을 때도 새 버전으로 양쪽을 다시 채점한다. 같은 조건 재실행 차이(흔들림 바닥)는 모델이나 환경이 바뀔 때마다 다시 잰다.
```

---

## 4. 현재 문서의 문제점

심각도: 상(판정이 틀릴 수 있음) / 중(모호해서 사람마다 다르게 함) / 하(정리 수준).

| # | 위치 | 문제 | 근거 | 심각도 | 고치는 곳 |
|---|---|---|---|---|---|
| 1 | METHOD S3·S4·S6·S7 완료 기준 "평가 회귀가 없다", 템플릿 "목표 지표 개선·중요 묶음 무회귀" | "회귀"와 "개선"의 정의가 없다. 비결정적 시스템에서 반복 수·구간·허용폭 없이는 판정할 수 없다. 모든 뒤 단계의 완료 판정이 여기에 걸려 있다 | Miller, Anthropic 통계 글, infra noise | 상 | 3-2 |
| 2 | METHOD S1 완료 기준·템플릿·CRITERIA 그림 "5건 이상" | 5건이면 과제 하나가 20%p다. 3/5의 95% 구간은 23~88%(직접 계산). 시작 크기로는 맞지만 완료 기준으로는 비교가 불가능하다. 출처들의 시작 크기는 20~50건, 10~20건, 30건 | Anthropic, LangSmith, Hamel | 상 | 3-3, 3-5 |
| 3 | `templates/01-eval.md` 시나리오 형식, golden-dataset 4번 | `request`와 `expected`가 같은 JSON 줄에 있다. `eval/dev.jsonl`이 작업 디렉터리 안이면 정답이 그대로 보인다. "볼 수 없는 곳에 둔다"는 말만 있고 방법이 없다 | SWE-bench(test_patch 분리), Terminal-Bench(이미지 검사), LangSmith("These do not get passed to your application") | 상 | 3-5, 3-7 |
| 4 | METHOD S1 "에이전트가 볼 수 없는 곳에 둔다" | 누출 경로가 파일 하나뿐인 것처럼 쓰였다. git 기록(미래 커밋, 이전 시도), 네트워크, 요청문 속 해답, 경험 메모리(S6)가 빠졌다. 에이전트가 테스트 파일을 고친 뒤 그 파일로 채점되는 경로도 언급이 없다 | SWE-bench #465, Anthropic(이전 시도 git 기록), SWE-Bench+(32.67%) | 상 | 3-3 진행 |
| 5 | 템플릿 `expected.tests_must_pass` | 실패→통과와 계속 통과를 구분하지 않는다. 구분이 없으면 "원래 통과하던 테스트만 적힌 과제"(무변경으로 통과)나 "회귀 검사 없는 과제"를 걸러낼 수 없다. 정답 변경, 환경 준비·초기화, 한도, 허용·보호 경로, 과제 검증 기록 필드도 없다 | SWE-bench 필드 정의, OpenAI(미러) | 상 | 3-5 |
| 6 | agent-eval 4번 "도구 이름 Precision/Recall", 원칙 1 "과정이 다르면 같은 성공이 아니다" | 도구 Precision/Recall은 정답 도구 목록을 전제한다. golden-dataset 4번의 "정답 경로 하나를 강제하지 말고"와 충돌한다. 과정을 결과와 같은 무게의 성공 조건으로 두면 다른 길로 푼 정답이 떨어진다 | Anthropic("too rigid … overly brittle tests"), Terminal-Bench("do not test the agent's commands") | 중 | 3-8 |
| 7 | METHOD 공통 규칙 3 "결과를 본 뒤 기준·임계값·반복 수를 바꾸지 않는다" | 지나치게 절대적이다. 채점기·과제 결함은 결과를 봐야 발견된다(채점 버그 수정으로 42%→95% 사례). 지금 문장대로면 결함을 발견해도 못 고치거나, 고치면 규칙 위반이 된다. agent-eval의 "기준이 바뀌면 두 버전을 다시 채점"과도 어긋난다 | Shankar, Hamel field guide, Anthropic | 중 | 3-1 |
| 8 | METHOD S2 "여러 번 돌려 흔들림도 본다", 완료 기준 "매번 통과한 비율" | 몇 번인지, "매번"이 몇 번 기준인지, 흔들림을 어떻게 수치로 쓰는지 없다. 기준선에 평가 조건(모델 버전, 환경, 한도) 기록 요구도 없다 | τ-bench, Terminal-Bench 2.0, infra noise | 중 | 3-4, 3-6 |
| 9 | agent-eval 6번 "pass@k, pass^k" 나열 | 정의·추정식·어느 쪽이 주 지표인지 없다. 사람이 고르지 않는 코딩 에이전트에서 pass@k를 주 지표로 쓰면 실제보다 좋게 보인다(시도 성공률 75%면 pass@3 98%, pass^3 42%) | τ-bench, Anthropic | 중 | 3-8 |
| 10 | METHOD S1 검증 | 정답 변경 통과·무변경 실패는 있다(좋다). 빠진 것: 불안정 테스트 확인(반복 실행), 지나치게 구체적인 테스트(다른 정답이 떨어짐), 약한 테스트, 불명확한 요청, 0% 과제 = 깨진 과제 의심, 기록 읽기 | SWE-bench-Live, OpenAI(61.1% / 38.3%), SWE-Bench+(31.08%), Anthropic | 중 | 3-3 검증 |
| 11 | METHOD S1, agent-eval 3번 | 격리가 "매 시도마다 초기 상태를 복원한다" 한 줄(스킬에만)이다. METHOD 본문에는 없다. 자원·시간 한도, 한도 초과의 분류, 메모리 상태가 빠졌다. S6 메모리가 평가 시도 사이에 쌓이면 시도가 독립이 아니고 비교가 오염된다 | Anthropic 4단계, infra noise, Inspect | 중 | 3-3, 3-8 |
| 12 | METHOD S1, agent-eval 2번 모델 채점 | "등급(나쁨·보통·좋음)마다 … 최저·최고 점수"를 기본으로 둔다. 조사한 실무 자료는 통과/실패 + 이유를 기본으로 권한다. 빠진 것: 사람 라벨 몇 건, 잘못 통과와 잘못 탈락을 따로 재기, "판단 불가" 출구, 기준별 분리 | Hamel, Yan, Anthropic, Stureborg(다속성 동시 채점의 끌림) | 중 | 3-8 |
| 13 | METHOD S1 "점수가 0.7 근처로 쏠린다" | 0.7이라는 수치의 1차 근거를 찾지 못했다. 방향(치우친 분포, 가운데 값 선호)은 근거가 있다 | Stureborg("skewed and biased distributions of ratings"), Hamel FAQ("default to middle values") | 하 | "점수가 한쪽으로 쏠린다"로 바꾸거나 notes에 근거를 남긴다 |
| 14 | METHOD S1·golden-dataset "LLM에게만 맡기면 50~60점짜리" | 수치의 1차 근거를 찾지 못했다(강의 출처로 보임). 조사 자료의 지침은 "입력은 LLM으로 만들어도 되지만 기대 응답은 안 된다" | Hamel field guide | 하 | 수치를 빼거나 notes에 근거 |
| 15 | METHOD 전체 | 능력 평가와 회귀 평가의 구분, 포화(100%면 개선 신호 없음), 졸업 개념이 없다. 통과율이 낮은 능력 과제와 섞인 묶음에서 "회귀 없음"을 보면 잡음이 크다 | Anthropic | 중 | 3-3, 3-5 |
| 16 | METHOD S1·S2 Outcome = 숨긴 테스트 통과 | 테스트 통과를 성공과 같게 둔다. 통과 변경의 절반가량이 유지보수자 판정에서 거절된 연구가 있다. S0 성공 지표 "성공률(숨겨 둔 테스트 통과)"도 같은 문제 | METR 2026-03 | 중 | 3-5 "품질(표본)" 행 |
| 17 | 판정 5상태(METHOD S1, agent-eval) | 상태는 잘 나뉘어 있다. 그러나 환경 오류·근거 부족을 성공률 분모에 어떻게 넣는지, 재실행하는지, 비율이 높을 때 실행을 무효로 하는지 규칙이 없다. "누락을 분모에서 지우지 않는다"만으로는 인프라 오류가 에이전트 점수를 깎는다 | infra noise(인프라 오류율 5.8%) | 중 | 3-2 4번, 3-5 판정 규칙 |
| 18 | METHOD S8 "최종 확인용 평가를 한 번 돌린다", golden-dataset 7번 | 한 번만 본다는 규칙은 있으나 크기, 열람 기록, 출시가 반복될 때의 교체 규칙이 없다. 매 출시마다 같은 최종 확인용을 쓰면 점점 개발용이 된다 | AI Agents That Matter | 중 | 3-5, 3-7 |
| 19 | agent-eval `<cost>` | "유료 실행 전 규모를 알린다"와 온라인 샘플링뿐이다. 어느 범위를 언제 돌리는지(층)가 없어서 매번 전체를 돌리거나 아예 안 돌리게 된다 | Hamel(3단계 빈도) | 하 | 3-8 |
| 20 | 템플릿 `order` 필드 | 모든 과제에 같은 값(계획 승인 → 수정 → 테스트)이 들어간다. 과제별 정보가 아니라 평가 공통 정책이다. `must_not`도 문장이라 코드로 판정할 근거(경로 목록)가 없다 | — (구조 문제) | 하 | 3-5 (`allowed_paths`, `protected_paths`) |
| 21 | METHOD S1 "5건부터 시작해 늘린다" | 언제까지 얼마로 늘리는지 없다. 완료 기준이 5건이라 늘릴 유인이 없다 | — | 중 | 3-3 |
| 22 | 용어 | "시나리오/사례/실행/시도", "최종 확인용/holdout", "채점기/평가기"가 문서마다 다르다. 반복 단위가 섞이면 "반복 실행을 독립 사례로 세지 않는다" 같은 규칙이 읽히지 않는다 | Anthropic 용어 정의 | 하 | 2-1 표를 METHOD에 한 번 정의 |

현재 문서에서 조사 결과와 잘 맞는 부분(유지 권장):
- 정책 위반을 평균에 넣지 않는 필수 관문으로 둔 것
- 판정 상태 5종과 "누락을 분모에서 지우지 않는다"
- 묶음(family) 단위 분할, 버전·해시 고정
- "반복 실행을 독립 사례로 세지 않는다" (묶음 단위 표준오차와 같은 뜻)
- 채점기를 반례로 먼저 검증하는 것, 정답 변경 통과·무변경 실패
- "정답 경로 하나를 강제하지 말고 지켜야 할 제약을 적는다"
- 운영 기록 승격 조건(반복·재현·정답 정의 가능)과 승격 시 실패 재현
- 문제점 단위로 데이터셋을 묶는 것, 균형(거절·되묻기·경계 쌍)

단계 밖이지만 눈에 띈 것: S7 "동작이 바뀌면 안 된다(도구 호출 순서 포함)"는 6번과 같은 이유로 지나치게 엄격할 수 있다. 호출을 묶는 최적화는 정의상 호출 순서를 바꾼다. S7 담당 조사에서 확인이 필요하다.

---

## 5. 확인 못 한 것

**접근 실패**
- OpenAI 원문 3건이 403이다: "Introducing SWE-bench Verified", "Why we no longer evaluate SWE-bench Verified", "Separating signal from noise in coding evaluations". 첫 글의 인용은 미러 사본(bittide.aicompass.dev)에서 뽑았고 원문과 대조하지 못했다. 둘째 글의 수치(138건, 59.4%, 35.5%)는 검색 요약에서만 봤다. 셋째 글은 내용을 보지 못했다. "OpenAI가 SWE-bench Pro 권고를 철회했다"는 2차 기사 제목도 확인하지 못했다.
- Terminal-Bench 원래 문서(tbench.ai/docs/task-overview)는 404였다. 과제 구조는 2.0 논문과 Harbor 문서로 대신했다. "테스트는 에이전트가 끝난 뒤에 컨테이너로 복사된다"는 문장은 원문에서 확인하지 못했다(논문은 이미지 안에 테스트·해답이 있으면 읽힐 수 있어 검사한다고만 한다).
- Inspect의 epochs·reducer 문서(예상 경로 scoring-metrics.html)는 404였다. 기본 reducer가 평균이라는 것만 봤다. `pass_at_k` 같은 reducer 이름과 묶음 표준오차 옵션의 정확한 표기는 확인하지 못했다.

**인용의 한계**
- 조회 도구가 인용을 125자로 제한했다. 긴 문장은 앞부분만 있거나 둘로 나눠 표기했다(표에서 "/" 또는 "+"로 구분). 원문 전체를 직접 본 것은 Anthropic Docs "Develop tests"의 "Grade your evaluations" 절뿐이다. 나머지 인용은 도구가 원문에서 뽑아 준 것이고 내가 원문 화면으로 대조하지는 못했다. 결과물이나 notes에 인용을 옮길 때는 원문 대조를 권한다.
- "leaderboard differences below 3 percentage points deserve skepticism": 원문 조회에서는 Anthropic 글의 문장으로 나왔고, 앞선 검색 요약은 제3자 글의 표현이라고 했다. 원문 조회 쪽을 채택했지만 한 번 더 확인할 가치가 있다.
- "Judging the Judges"의 κ 수치(일치율 80%에 κ 0.62 등)는 Eugene Yan 글의 요약을 통해 본 것이다. 논문 초록에는 κ라는 말이 없다.
- τ-bench "we run at least 3 trials per task", Terminal-Bench "roughly three reviewer-hours of work per task"는 본문 조회 결과이며 앞뒤 맥락(어느 실험 기준인지)은 보지 못했다.
- SWE-bench의 정답 패치 검증 명령은 README에서 `swebench eval verified --gold` 형태로 확인했다. 예전 형태(`--predictions_path gold`)는 확인하지 못했다. SWE-bench-Live가 검증을 몇 번 반복하는지는 논문에 수치가 없었다.

**기대와 달랐던 것**
- Hamel "Your AI Product Needs Evals"에는 "100% 통과면 평가가 너무 쉽다"는 문장이 없다. 있는 것은 "you don't necessarily need a 100% pass rate"와 통과율은 제품 결정이라는 내용이다. 포화 논의는 Anthropic 글에 있다.
- Hamel field guide에는 open coding·axial coding이라는 용어와 "100건" 수치가 없다. 둘 다 FAQ 글에 있다.
- Hamel FAQ는 "평가를 먼저 쓰고 개발(eval-driven development)"에 대해 "Generally no."라고 한다. 기능보다 평가기를 먼저 쓰면 문제가 더 생긴다는 입장이다. 이 문서의 "S1을 S2와 동시에, S3 전에"와 정면충돌은 아니지만(실제 실패에서 뽑은 과제와 결정적 테스트는 권한다), "기록을 먼저 보고 실패 유형에서 평가를 만든다"는 순서를 강조한다는 점에서 긴장이 있다. S1 과제를 과거 PR·수동 확인 항목에서 만들고, 모델 채점기는 기준선 기록을 읽은 뒤에 만드는 것으로 풀 수 있다.
- 판정 모델 선택은 출처가 갈린다. Anthropic Docs는 평가 대상과 다른 모델을 일반적 권장으로 적고, Hamel FAQ는 같은 모델이어도 대체로 괜찮다고 한다("using the same model is usually fine"). 3-8에서는 "가능하면 다른 모델"로 약하게 썼다.
- Miller의 "문항 1,000개 이상" 권고는 모델 벤치마크 기준이다. 사내 코딩 에이전트 평가셋(20~100건)에는 그대로 적용할 수 없고, 그래서 2-7에서 "작은 차이는 가려낼 수 없다"를 규칙으로 넣었다.
- METR Task Standard 저장소는 보관(읽기 전용) 상태이고 더는 유지되지 않는다. METR 시간 지평 글은 본문에 일부가 낡았다는 안내가 있다. 구조 참고용으로만 썼다.
- LangSmith 개념 문서에서 에이전트 평가 유형(최종 응답 / 단일 단계 / 궤적) 구분은 찾지 못했다. 이 문서의 Outcome / Trajectory / Final Response 3축과 직접 대응되는 1차 출처는 이번 조사에서 확인하지 못했다.

**출처가 아니라 내 제안인 것 (2절에 [제안]으로 표시)**
- 5건(개통) → 20건(기준선 전) → 최종 확인용 10건 이상이라는 구체적 건수. 출처의 범위(10~50건) 안에서 고른 기본값이다.
- 같은 조건 두 번 실행으로 흔들림 바닥을 재는 것, 기준과 후보를 번갈아 돌리는 것, 환경 오류율 한도 5%와 재실행 정책, 회귀 허용폭 −5%p 예시.
- Wilson 구간, 부호 검정, 짝 차이 구간 너비 수치는 직접 계산한 값이다(일반 통계). 과제별 차이의 표준편차 0.3~0.4는 가정이며 실제 값은 기준선에서 재야 한다.
- 경험 메모리를 평가 조건으로 잠그고 승격 과제의 원본 기록을 제외하는 규칙. S6 구조에서 추론한 누출 경로이고 이를 직접 다룬 출처는 찾지 못했다.
- 최종 확인용을 본 뒤 고쳤으면 개발용으로 내리고 새로 채우는 규칙.
- 비용 층 표의 건수와 반복 수.

**조사하지 않은 것**
- 평가 실행기 구현(병렬 실행, 컨테이너 캐시 전략)의 구체적 방법.
- 온라인 평가(운영 중 표본 채점)의 표본 크기 설계.
- 한국어 요청문에서의 모델 채점 신뢰성.
