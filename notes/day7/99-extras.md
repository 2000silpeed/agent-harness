## Day7 부가 자료

강의 저장소 `sds_ax_advanced_2026`의 `Day07/`, `Day07_new/`를 읽기 전용으로 확인해 판서 이미지 3장과 실습 위치를 정리했다. 경로는 저장소 루트 기준이다. 판서는 손글씨라 읽은 그대로 옮겼고, 계산이 맞지 않아 보이는 곳은 원문을 유지했다.

### 1. 판서 이미지

**`Day07/Day07_01.png` — 모델 기초·정밀도·로컬 런타임**
- 좌상: "Transformers", "Attention" → Neural Network Block(블록 두 개가 화살표로 연결) → "Deep Learning", "역전파(BackPropagation)".
- 우중: **Chat Template** 상자에 `Multi modal / system / user / tool` 네 칸.
- 좌하: 정밀도 축 `Float32 → [Float16, 'B'Float16](박스) → Float8 → INT4`, 오른쪽에 "성능" 화살표. INT4 쪽 메모: "말이 깨진다 = 괅궭...중국어..일본어.." (저정밀 양자화 시 출력이 깨지거나 다른 언어가 섞임).
- 중하: "Fable / Astra 출시되면 기가막혀요...", "?? 왜이래", "128GB / 700B GLM-5.3".
- 우하(녹색): **GGUF** — `**llama.cpp**`, Ollama, LMStudio.

**`Day07/Day07_02.png` — KV 메모리 회계와 Concurrency (H200 144GB 1장 기준)**
```
144GB = *56GB(weights) + 4GB(Runtime)
  => 71GB(0.85)
  = *KV Cache
  = 15GB(262K)
  >> 15GB * 4EA = 60GB
  = '동시에' 받을 수 있는 요청의 개수 = Concurrency
  = 4.88x
```
- 녹색 화살표: "BF16(56GB) -> FP8 = 28GB" → "= 6.6x" (가중치 FP8로 동시성 증가).
- 빨강: "KV Cache 는 Dtype 이 뭘까요? BF16", "K(BF 16) * V(BF 16) = Q(BF 16)" → "= 9.6x".
- 빨강 박스 "[모델 정밀도 포기x] 1. KV Cache 의 정밀도를 포기 BF16 -> FP8 / 1) 연산(BF16) -> 정밀도 낮추는 '연산' -> FP8 저장 / 2) FP8 꺼내서 -> 정밀도 높이는 '연산' -> BF16 / --- 정밀도 포기 --- / BF16 ~ FP8 5% 이하".
- 검정 화살표: "= 11.6x" (가중치 FP8 + KV FP8 조합으로 보임).
- 요지: 덱 PART 2 "GPU 메모리 회계"와 같은 계산을 강의 Pod(H200)로 판서한 것. 모델 정밀도는 유지하고 KV만 FP8로 낮추는 선택지를 강조했다.

**`Day07/Day07_03.png` — 1노드 4 GPU 배치와 TP/DP**
- "GPU = 144 * 4 = 576GB", 1 Node 안에 144GB × 4.
- "1. 모델을 몇개 올릴까요? 1) FP8 = 763GB Weight, *FP4 = 376GB Weight*, 576 - 376 = 200GB / 2) BF16 = 56GB(weights)", "PCI-E (X) NVL(O)" (TP는 NVLink에서).
- "모델을 '쪼개서' 올리자 — T(ensor) P(arallel)": GPU 4장 각각에 [가중치 조각 | KV Cache].
- "데이터를 쪼개자 — D(ata) P(arallel)": "Model * 3" + Model, Model, Model (복제).
- 하단: "1M = 262K * 4(rope)" (RoPE 스케일링으로 컨텍스트 4배 확장).
- 덱 PART 8 "병렬화 전략"·멀티노드와 연결. README의 강사 Pod(H200 SXM ×4, TP4)와 같은 구성이다.

### 2. 주제 → 저장소 위치 → 볼 것

| 주제 | 저장소 위치 | 볼 것 |
|---|---|---|
| Day7 개요·교재 | `Day07/README.md:1-5` | RunPod vLLM(GLM-5.3-Flash) 호출 + 자유 실습 2개, 교재 PDF, 채점 없음 |
| 준비·환경변수 | `Day07/README.md:18-28` | 루트 `uv sync`만, `RUNPOD_BASE_URL` 필수(`https://<POD_ID>-8000.proxy.runpod.net/v1`), EXA·OpenRouter 키 |
| 실행 방법 | `Day07/README.md:30-43` | `uv run python …` 두 개, CLI 플래그 없음, effort low / max |
| 프록시 100초·reasoning 필드명 | `Day07/README.md:64-68` | timeout 95, 필드 `reasoning`/`reasoning_content`, ChatOpenAI는 비표준 필드를 버림 |
| 강사 Pod 기동 메모 | `Day07/README.md:70-82` | H200 SXM×4, `vllm/vllm-openai:glm53-flash`(v0.28.1rc1), TP4+MTP(5), `NCCL_NVLS_ENABLE=0` 필수, 기동 15~20분(가중치 ~306GiB, CUDA graph ~215초) |
| 에이전트 도움 규칙 | `Day07/AGENTS.md:5-8`, `:12`, `:16-19`, `:23-29` | 힌트 정책 미적용(끝까지 도움 허용), 플래그 지어내지 않기, `.env` 내용 출력 금지, 3사 모델 금지, 유료 호출 전 규모 고지 |
| CLAUDE.md 포인터 | `Day07/CLAUDE.md:1-4` | `@AGENTS.md` 한 곳에만 내용 |
| LangChain 호출 | `Day07/runpod_model_call.py:28-39` | `ChatOpenAI(model="GLM-5.3-Flash", api_key="EMPTY", timeout=95, extra_body={"chat_template_kwargs": {"reasoning_effort": "low", "clear_thinking": True}})` — 모델마다 chat template이 달라 reasoning on/off 전달 방식도 다름(`:35-36` 주석) |
| reasoning 분리(openai SDK) | `Day07/runpod_openai_reasoning.py:40`, `:43-45` | `EXTRA_BODY`(effort max), `reasoning_of()`로 필드명 차이 흡수 |
| 비스트리밍 / 스트리밍 | `Day07/runpod_openai_reasoning.py:48-59`, `:62-84` | `message.reasoning`·`content`·`usage`, `stream_options={"include_usage": True}`(`:68`), delta 단위 분리 출력 |
| 활동 1 DeepAgents | `Day07/task.md:2-8` | GLM-5.3-flash(RunPod) + EXA Tool 1개, 입력 "GLM-5.3-Flash 라는 모델의 분석 보고서를 작성할 것." |
| 활동 2 dcode | `Day07/dcode_task.md:2-20` | OpenRouter, 3사 금지(`:7`), WSL 전용(`:15`), 설치 `curl -LsSf https://langch.in/dcode \| bash`(`:20`) |
| dcode 과제 4개 | `Day07/dcode_task.md:27-33` | Prompt Caching 고려 구성, 모델별 Harness Profile, 메모리 구성 테스트, Middleware Self-Improving |
| PJT 예고 | `Day07/dcode_task.md:37` | 목-금 PJT용 dcode 소스는 Day08에서 제공(주석·소스맵) |
| 신규 과제(자유 챗봇) | `Day07_new/task.md:1-14` | 3사 주요 모델 X, 이미지 3~4장, 비디오 X, STT·TTS 적당히, LLM 200B 이하, DeepAgents 기반 권장 |
| 교재 PDF(저장소본) | `Day07/Day7_vLLM_기초와_추론_속도_최적화.pdf` | 71쪽 6 Chapter. Drive본(84쪽 "vLLM 이론에서 추론까지")과 다른 덱 → `00-deck.md` 부록 |
| 판서 | `Day07/Day07_01.png`~`03.png` | 위 1절 |
