## Day7 교재 — vLLM: 이론에서 추론까지

- 원본: Google Drive `Day7_vLLM_이론자료.pdf` (fileId `1tdkUS6-hG9UWHhWfFTBdGpbeMsftcPyR`, 84쪽, 4.1MB, 16:9, 2026-11-09 생성). `download_file_content`로 원본 전체를 받아 `pdftotext -layout`으로 추출했다(잘림 없음, 84쪽 전부 확인).
- 덱 제목: **vLLM — 이론에서 추론까지** (표지에 강사명 없음). 8개 PART + 마무리.
- **저장소 사본과 다른 덱이다.** 강의 저장소 `Day07/Day7_vLLM_기초와_추론_속도_최적화.pdf`는 제목 "vLLM 기초와 추론 속도 최적화"(전현준), 71쪽, 6개 Chapter로 구성이 다르다(md5 다름, 추출 텍스트 유사도 약 0.01). 주제(KV 메모리·PagedAttention·배칭·CUDA Graph·양자화·Spec decoding·병렬화)는 상당 부분 겹치지만 슬라이드와 예시가 다르다. 저장소 덱 목차는 맨 아래 "부록"에 적었다.
- 주의:
  - PDF 추출 과정에서 하이픈·밑줄·`%`·`~`·화살표가 상당수 사라졌다(예: "gpu memory utilization", "Qwen3.5 9B", "llm d", "TTFT 2 22배"). 아래에서는 vLLM의 실제 표기(`--gpu-memory-utilization`, `Qwen3.5-9B`, `llm-d`)와 범위 표기(2~22배)로 복원했다. 복원이 애매한 수치는 원문 그대로 적고 "(추출본)"이라고 표시했다.
  - 덱 안에 "A 덱", "B 덱", "C1·C2 예시"라는 표현이 나온다. 이 덱이 이전 자료 여러 개를 합친 통합본임을 뜻한다.
  - 버전·날짜(v0.33.0, 2026-11, MRV2 기본화 등)와 벤치마크 배수는 **덱 작성 시점 기준 값과 출처별 보고치**다. 보장값이 아니다. 로드맵 슬라이드도 "계획이며 출시된 기능이 아님"이라고 직접 밝힌다.

---

### 목차 (덱 구조, 쪽 번호)

| PART | 제목 · 부제 | 쪽 |
|---|---|---|
| 1 | Introduction — 왜 직접 서빙하나, 2026년 vLLM | 3~7 (셀프 호스팅 이유, HF generate 한계, 연혁, 2025→2026 변경점) |
| 2 | LLM 추론 기초 — Prefill·Decode, KV 원리, 메모리 회계 | 8~16 (요청의 여정, Prefill/Decode, Attention과 KV, Roofline, KV 메모리 계산, GPU 메모리 회계, 어텐션 구조, 핵심 지표) |
| 3 | 메모리와 스케줄링 — PagedAttention, 블록 해시, 배칭 | 17~28 (기존 KV 관리, 단편화, PagedAttention, 블록 할당, Prefix caching, 해시 체인, 회수 순서, 배칭 진화, Continuous batching, 토큰 예산 스케줄러, Preemption) |
| 4 | 엔진 아키텍처 — EngineCore, MRV2, CUDA Graph | 29~37 (엔진 계층, V0/V1/MRV2, 비동기 스케줄링, Attention 백엔드, CUDA Graph·torch.compile, 요청 한 건의 경로) |
| 5 | 서빙 인터페이스 — OpenAI·Anthropic 호환 API | 38~44 (`vllm serve`/`LLM`, 엔드포인트, Tool calling, Reasoning·Chat template, 에이전트 서빙, LoRA·Structured outputs) |
| 6 | 성능 최적화 — 양자화, Speculative decoding | 45~50 (최적화 포인트 표, 양자화, Spec decoding 원리·현황, 목표별 튜닝) |
| 7 | KV Cache 확장 — 오프로드, LMCache, Mooncake | 51~69 (VRAM 한계, 줄이기·옮기기·공유하기, 재계산 vs 불러오기, KV 계층, KV Connector API, 네이티브 CPU 오프로드, 계층형 오프로드, LMCache, CacheBlend/CacheGen, Mooncake, 솔루션 비교, 클러스터 공유, 관측 지표, 효과 조건) |
| 8 | 확장과 운영 — 병렬화, P/D, llm-d, 진단 | 70~80 (TP/PP/DP/EP, 멀티노드, Wide EP·Context parallel, P/D 분리, Kubernetes, llm-d, 메트릭, 벤치마크, 증상별 진단, 엔진 비교) |
| 마무리 | RL과 로드맵 — 롤아웃 엔진, Agent Lightning | 81~84 |

모든 PART 표지에 같은 파이프라인 띠가 붙는다: **요청 → 토큰화 → 스케줄링 → Prefill → KV Cache → Decode → 스트리밍**.

---

### 섹션별 핵심 내용

#### PART 1. Introduction (3~7쪽)

- **셀프 호스팅 이유 4가지:** 비용(트래픽이 커지면 토큰 과금이 그대로 누적되고, 일정 규모를 넘으면 고정 GPU 비용이 유리), 보안·프라이버시(망분리·규제 환경에서는 사실상 유일한 선택지), 커스터마이징(프롬프트·샘플링·응답 형식·LoRA 직접 통제), 가용성(외부 API의 속도·장애·국가별 접근 제한에서 벗어남). → "가중치 파일만으로는 서빙이 되지 않는다. 동시 요청, GPU 메모리, 스케줄링을 책임질 **추론 엔진**이 필요하다."
- **HF generate vs vLLM:** 코드는 비슷하지만 아래가 다르다(`# static batch · padding · per-request KV` vs `# continuous batching · paged KV · kernels`).

  ```python
  # Transformers
  model = AutoModelForCausalLM.from_pretrained(name)
  inputs = tok(prompts, padding=True, return_tensors="pt")
  out = model.generate(**inputs, max_new_tokens=256)
  # vLLM
  from vllm import LLM, SamplingParams
  llm = LLM(model=name)
  params = SamplingParams(max_tokens=256)
  outs = llm.generate(prompts, params)
  ```

  | 배치 크기 | HF TTFT | HF 처리량 | vLLM TTFT | vLLM 처리량 |
  |---|---|---|---|---|
  | 1 | 0.578 s | 10.96 tok/s | 0.543 s | 12.42 tok/s |
  | 2 | 1.147 s | 5.54 tok/s | 1.211 s | 22.13 tok/s |
  | 3 이상(vLLM은 5) | 처리 불가 | 처리 불가 | 2.32 s | 33.71 tok/s |

- **연혁:** 2023.02 CacheFlow로 첫 커밋 → 2023.06 vLLM 공개 → 2023.09 PagedAttention 논문(SOSP 2023) → 2025.01 V1 엔진 알파 → 2025.05 PyTorch Foundation 호스팅 → 2025.10 v0.11 V0 완전 제거 → 2026.01 핵심 메인테이너들이 Inferact 설립 → 2026.07 v0.25 MRV2 기본, 레거시 커널 삭제 → 2026.11 현재 v0.33.0(CUDA 13, PyTorch 2.14). GitHub 스타 96.5k, 기여자 2,000, 지원 아키텍처 500, 릴리스 주기 약 2주.
- **2025 → 2026 변경점:**

  | 영역 | 2025 (v0.9~v0.11) | 2026-11 (v0.33.0) |
  |---|---|---|
  | 엔진 | V1 엔진 + 기존 GPU Model Runner | V1 엔진 + Model Runner V2 (v0.29부터 전 모델 기본) |
  | Attention | PagedAttention 커널 + FlashAttention·FlashInfer | 레거시 커널 삭제(v0.25), 블록 기반 KV 관리는 그대로 |
  | API | Chat·Completions 중심 | Responses API, Anthropic `/v1/messages`, 토큰 입출력 API |
  | CUDA Graph | FULL_AND_PIECEWISE 도입 | O2 기본값 FULL_AND_PIECEWISE |
  | Spec decoding | EAGLE·MTP·n-gram·Medusa | EAGLE-3/3.1·DFlash 등 추가, Medusa 제거(v0.33) |
  | KV Cache | GPU, KV 커넥터 초기 단계 | CPU·디스크 계층 오프로드, NIXL 기반 P/D 분리 |
  | RL | sleep mode, 임시 가중치 동기화 | 네이티브 RL API(weight transfer, pause/resume) |
  | 배포 | production-stack, AIBrix | llm-d v1.0(2026-10)이 레퍼런스 경로로 |
  | 빌드 | CUDA 12.8 / 12.9 | CUDA 13.0 전용 휠·이미지, PyTorch 2.14 |

#### PART 2. LLM 추론 기초 (8~16쪽)

- **요청의 여정(강의 전체의 지도):** 요청(프롬프트·샘플링 파라미터) → 토큰화(채팅 템플릿 적용 후 토큰 ID) → 스케줄러(대기열 관리, 매 스텝 배치 구성) → Prefill(프롬프트 전체 병렬 처리, 첫 토큰 생성) → Decode 루프(스텝마다 1토큰, KV를 읽고 추가하며 반복) → 스트리밍(생성 즉시 전송). TTFT = 큐 대기 + Prefill, ITL = Decode.
- **Prefill vs Decode:** Prefill은 보통 **연산(compute) 한계**다. 같은 가중치를 수천 토큰이 재사용하므로 연산 강도가 높고 TTFT를 결정한다. 어텐션 비용은 길이의 제곱으로 는다. Decode는 보통 **메모리 대역폭 한계**다. 토큰 하나를 위해 가중치와 KV를 매번 HBM에서 읽고, ITL을 결정한다. 배치를 키우면 읽은 가중치를 여러 요청이 나눠 쓴다. 병목은 고정이 아니다. 배치를 키우면 Decode도 연산 쪽으로 이동하고, 아주 짧은 요청은 커널 실행·스케줄링 오버헤드가 지배하기도 한다.
- **Attention과 KV Cache:** 캐시가 없으면 토큰 1개를 만드는 비용이 O(n²·d)이고, KV 캐시를 쓰면 새 쿼리 1개만 계산해 O(n·d)가 된다. 대신 KV를 계속 들고 있어야 한다. → "KV Cache 이후 추론은 **메모리 문제**가 된다. 그 메모리를 어떻게 관리하느냐가 엔진의 경쟁력이다."
- **Roofline:** 달성 성능 = min(최대 연산, 대역폭 × 연산 강도). Decode는 기울기 구간, Prefill은 평탄한 연산 한계 구간에 놓인다. "잘 최적화된 Decode도 FLOP 사용률은 낮게 나온다. 정상이다." 배치를 키우면 Decode가 오른쪽으로 이동하지만 요청당 지연이 는다.
- **KV 메모리 공식:** `KV bytes = 2 × L × H_kv × D_head × b × T` (2 = K와 V, L = full attention 레이어 수, H_kv = KV 헤드 수, D_head = 헤드 차원, b = 원소당 바이트(BF16 = 2), T = 토큰 수(프롬프트+생성)).
  - Qwen3.8-27B(하이브리드 GQA): 2 × 16 × 4 × 256 × 2 B = **64 KiB/토큰** × 262,144 = **16 GiB/시퀀스**. 배치 10이면 KV 160 GiB(+GDN 상태 1.4 GiB)로 가중치 52 GiB의 약 3배.
  - Qwen3.5-9B: 2 × 8 × 4 × 256 × 2 B = **32 KiB/토큰** → 8 GiB/시퀀스. 독립 시퀀스 16개면 KV 128 GiB(+GDN 0.75 GiB, 오버헤드 제외).
  - 함정: L은 full attention 레이어 수다. 하이브리드 모델은 4층 중 1층만 KV를 쌓는다. 전체 레이어로 계산하면 4배, hidden size까지 쓰면 다시 4~5배 과대 추정한다.
- **GPU 메모리 회계 (H100 80GB + Qwen3.8-27B BF16):** `--gpu-memory-utilization 0.92` → 73.6 GB까지 사용. 73.6 − 55.6(가중치) − 4(활성화 피크·CUDA Graph 가정) ≈ **14.0 GB** → 14.0 GB ÷ 64 KiB ≈ **214,000 토큰** → 214,000 ÷ 262,144 ≈ **0.82**. 시작 로그의 `GPU KV cache size: ~214K tokens`, `Maximum concurrency ...: 0.82x`가 이 계산 결과다. 최대 길이 262K 요청 1개도 다 들어가지 않으므로 vLLM이 **기동 시 에러**를 낸다. 활성화 메모리는 기동 시 프로파일링으로 실측하므로 가정값과 다를 수 있다. KV fp8이면 토큰 수가 약 2배가 된다. 실제 요청이 짧으면 동시 처리 수가 더 는다.
- **어텐션 구조와 KV 크기:** MHA(KV 1) / GQA(쿼리 헤드를 그룹으로 묶어 KV 공유, 예시 1/4, 품질과 크기의 절충으로 현재 표준) / MQA(1/8, 가장 작지만 품질 저하 가능) / MLA(저차원 잠재 벡터로 압축, DeepSeek). Qwen3.8-27B는 쿼리 24·KV 4 GQA이고 4층 중 1층만 KV를 저장한다. **Hybrid KV Cache Manager:** full·sliding window·Mamba/선형 어텐션 층이 섞이면 층 종류별로 KV 캐시 그룹과 블록을 따로 할당하고, sliding window 층은 창 밖 블록을 일찍 해제한다.
- **핵심 지표:**

  | 지표 | 정의 | 주로 결정하는 곳 |
  |---|---|---|
  | TTFT | 요청 도착 → 첫 토큰 | 큐 대기 + Prefill |
  | ITL | 스트리밍 토큰 사이 간격 | Decode |
  | TPOT | (E2E − TTFT) / (출력 토큰 수 − 1) | Decode |
  | Throughput | 모든 요청 합산 초당 출력 토큰 | 배치 크기·스케줄링 |
  | Goodput | 지연 SLO를 지키며 처리한 초당 요청 수 | 전체 시스템 |

  "처리량이 높아도 SLO를 넘긴 요청은 사용자에게 쓸모없는 처리량이다." (Throughput ≠ Goodput)

#### PART 3. 메모리와 스케줄링 (17~28쪽)

- **기존 KV 관리(HF):** Dynamic Cache(기본)는 `torch.cat`으로 매번 재할당·복사하므로 길수록 메모리 I/O 병목이 된다. Static Cache는 max_length만큼 미리 예약해 복사는 없지만 내부 단편화가 생기고 동시 처리 수가 급감한다. 공통 문제는 요청마다 연속된 큰 공간이 필요하고 요청끼리 메모리를 공유하지 못한다는 점이다.
- **단편화:** 내부(예약했지만 덜 쓰는 공간)와 외부(빈틈 합계 420이 충분해도 가장 큰 빈틈이 160이라 연속 360 할당 불가). 기존 시스템은 KV 메모리의 **20.4~38.2%만** 실제 토큰 저장에 썼다(PagedAttention 논문).
- **PagedAttention:** OS 가상 메모리처럼 논리 KV 블록 → 블록 테이블 → 비연속 물리 블록으로 매핑한다. 블록 크기는 고정(**기본 16토큰**, 그림은 4)이고 필요할 때 한 블록씩 할당하며 끝나면 즉시 반환한다. 낭비는 마지막 블록 안으로 제한된다(4 미만).
- **Prefix caching(자동) / Copy-on-Write:** 블록 해시 = hash(앞 블록 해시 + 이 블록의 토큰)라 앞부분이 모두 같아야 적중한다. 새 요청은 블록 단위로 해시를 조회하고 적중한 블록은 Prefill을 건너뛴다(TTFT↓). 참조 수가 0이 된 블록도 LRU로 회수되기 전까지는 재사용된다. **V1부터 기본 활성**, 지표 `vllm:prefix_cache_hits / queries`. 같은 프롬프트로 n개를 샘플링하면 프롬프트 블록을 공유하고 참조 수만 올린다. 쓰려 할 때만 복사한다. "**공통 부분을 프롬프트 앞쪽에 두세요.**"
- **블록 해시 체인:** `h0 = H(None, 토큰, 추가키)`, `h1 = H(h0, 토큰)`. 가득 찬 블록만 캐시한다. 추가 키는 LoRA ID, 멀티모달 입력 해시, `cache_salt`. 요청에 `cache_salt`를 넣으면 같은 salt를 쓴 요청끼리만 캐시를 공유한다. 응답 지연 차이로 남의 프롬프트를 추측하는 **타이밍 공격을 막는다. 멀티테넌트 서비스라면 필수.** `--prefix-caching-hash-algo`(기본 sha256).
- **블록 회수 순서:** free 블록 큐(LRU, 이중 연결 리스트). 요청이 끝나면 블록을 **역순(A2→A1→A0)으로 tail에 붙인다**. 그래서 접두사가 가장 긴 마지막 블록이 먼저 회수된다. ① 반환(ref_cnt 0, 해시 유지) ② 재사용 touch(free 큐에서 빼고 ref_cnt+1) ③ 회수 evict(head에서 꺼내며 해시 삭제).
- **배칭 진화:** Static(가장 긴 요청이 끝나야 다음 배치) / Dynamic(시간 창으로 모으지만 실행 중 한계 동일). 낭비 3가지: ① 패딩 ② 먼저 끝난 요청의 빈 슬롯 ③ 새 요청 대기.
- **Continuous batching:** 스텝(iteration)마다 배치를 다시 구성한다(iteration-level scheduling). 끝난 요청은 즉시 반환되고 빈 자리에 대기 요청이 바로 들어온다. 패딩 없는 1차원 flatten 배치이고, Linear·LayerNorm은 한 번에, 어텐션만 요청별로 계산한다. PagedAttention과 결합해야 메모리가 버틴다.
- **토큰 예산 스케줄러(V1):** 예시 `max_num_batched_tokens` 2,048. 스텝 3 출력 예 `{"r1": 1, ... "r12": 1, "X": 928, "Y": 1108}  # sum = 2,048 tokens`.
  1. 실행 중 요청의 Decode 토큰을 먼저 넣는다(요청당 1, spec decoding이면 더).
  2. 남은 예산을 대기 요청의 Prefill로 채우고, 넘치면 자동 청크 분할(**Chunked prefill, 기본 활성**).
  3. 상한은 토큰 예산 · `max_num_seqs` · 남은 KV 블록 세 가지.
  4. Prefill·Decode 단계를 따로 두지 않는다. 요청마다 "계산된 토큰 수"가 목표 길이를 따라잡게 할 뿐이다.
  - 예산을 작게(2k) 잡으면 ITL이 안정되고 TTFT·처리량이 떨어진다. 크게(8k~16k) 잡으면 TTFT·처리량이 좋아지고 ITL이 흔들린다.
- **Preemption(선점):** KV 블록 부족 → 우선순위가 가장 낮은 요청(FCFS면 가장 늦게 온 요청)을 선점 → 블록 해제, 대기열 앞으로 → 여유가 생기면 recompute(prefix 캐시가 남아 있으면 일부 재사용). V0에는 CPU swap이 있었지만 **V1은 recompute만** 쓴다. 징후 `vllm:num_preemptions`↑ → 대응: `--gpu-memory-utilization`↑, `--max-num-seqs`↓, `--max-model-len`↓, `--kv-cache-dtype fp8`, TP로 GPU 늘리기.

#### PART 4. 엔진 아키텍처 (29~37쪽)

- **엔진 계층:** 클라이언트(OpenAI SDK·Claude Code·curl) → API 서버(HTTP·채팅 템플릿·토큰화·스트리밍) → AsyncLLM(요청 등록, 출력 조립·디토큰화) ═ **ZMQ 프로세스 경계** ═ EngineCore busy loop(Scheduler + KV Cache Manager) → Executor·Worker(GPU마다 워커 프로세스 1개) → Model Runner V2(GPU 입력 준비·CUDA Graph 실행·샘플링). 프로세스를 나눈 이유: CPU 일(HTTP·토큰화·디토큰화·파서)과 GPU 스케줄 루프를 분리해 GPU가 CPU를 기다리지 않게 하려는 것이다. TP면 스케줄러 1개 + 워커는 GPU 수만큼, DP면 EngineCore 여러 개 + 앞단 로드밸런서. Rust 프론트엔드(옵션)가 같은 경계 위에서 Python API 서버를 대체하도록 테스트 중이다.
- **V0 → V1 → MRV2:** V0(2023~, v0.11에서 제거)는 한 프로세스에 얽혀 있었고 Prefill/Decode를 나눠 스케줄했으며 입력 준비 중 GPU가 쉬었다. V1(2025.01 알파, v0.8부터 기본)은 EngineCore 분리(ZMQ), 통합 토큰 예산 스케줄러, chunked prefill·prefix caching 기본, persistent batch, torch.compile piecewise CUDA Graph를 갖췄다. MRV2(2026.03 실험, v0.25 dense 기본, v0.29 전 모델)는 입력 준비를 GPU Triton 커널로 옮겨 CPU↔GPU 동기화 제거를 노린다. 비동기 우선(스텝 N 실행 중 N+1 준비), ModelState로 모델별 로직 분리, Triton 기반 샘플러를 쓴다. **사용자 API(`vllm serve`, `LLM`, OpenAI API)는 그대로다.** 보고치: GB200·Qwen3-0.6B 처리량 56%↑(자체 측정, 추출본). MRV1은 v0.29에서 deprecated, 2026-11-07 main에서 제거(#63373), v0.34부터 적용.
- **비동기 스케줄링:** CPU가 스텝 N+1을 준비하는 동안 GPU가 스텝 N을 실행해 버블을 없앤다(같은 시간에 실행 3번 → 5번). 플래그 `--async-scheduling`. 작은 모델·짧은 스텝일수록 효과가 크다.
- **Attention 백엔드:** 커널을 가르는 4조건은 KV 구조(블록 분산, 일반 SDPA는 연속 텐서 가정), Prefill/Decode, 하드웨어(Hopper·Blackwell·AMD·Intel), 모델 구조(GQA·MLA·sliding window)다. 해법은 인터페이스 분리다. 모델은 `Attention(q, k, v)`만 호출하고 `AttentionBackend`가 메타데이터(블록 테이블·시퀀스 길이·슬롯 매핑)를 빌드해 커널을 고른다. 백엔드 예: FlashAttention 3(Hopper)·4(Blackwell), FlashInfer(NVIDIA 전반), Triton Attention(AMD·Intel, 하드웨어 독립), FlashMLA(DeepSeek 계열). 자동 선택되며 설정으로 강제할 수 있고, 모든 백엔드가 같은 블록 테이블을 읽는다. **개념으로서의 PagedAttention은 유지**되고, 2023년 PagedAttention 커널은 v0.25에서 삭제됐다. FlashAttention ≠ PagedAttention: HBM 트래픽을 줄이는 정확한(exact) 커널일 뿐 연산량은 여전히 O(n²)다.
- **CUDA Graph · torch.compile:** CUDA Graph는 커널 런치 오버헤드를 없앤다. PIECEWISE는 어텐션 밖만 캡처하고, FULL은 어텐션까지 캡처한다. **O2 기본값 FULL_AND_PIECEWISE**: 모양이 고정된 Decode 배치는 FULL, Prefill이 섞인 배치는 PIECEWISE. O2 = torch.compile 커널 융합 + CUDA Graph로, 캡처 때문에 기동이 느리고 메모리를 조금 쓴다. `--enforce-eager`는 CUDA Graph를 끈다(디버깅·빠른 기동·메모리 빠듯할 때). 작은 배치 Decode가 느려진다. 현장 사례(B 덱): Eager 모드에 양자화·LoRA를 붙였다가 성능이 떨어졌고, 그래프를 쓰자 해결됐다.
- **요청 한 건의 경로(`/v1/chat/completions`):** ① POST → ② 템플릿·토큰화 → ③ 스케줄·KV 할당 → ④ 배치 실행(forward·샘플링) → ⑤ 새 토큰 ID 반환 → ⑥ 출력 전달(ZMQ) → ⑦ 디토큰화·파서·SSE. Decode 루프에서는 EOS까지 ③~⑦을 반복한다. Prefill은 요청당 1회다(N토큰 계산, 마지막 위치만 샘플링, 첫 청크 = 체감 TTFT). Decode는 토큰마다 반복한다(1토큰분 슬롯 추가, 16토큰 블록이 차면 새 블록, 모자라면 선점, CUDA Graph FULL, EOS·max_tokens에서 KV 해제). V1은 한 스텝 배치에 Prefill 요청과 Decode 요청을 섞는다.

#### PART 5. 서빙 인터페이스 (38~44쪽)

- **실행 형태 두 가지:**

  ```bash
  # Docker image (CUDA 13)
  docker run --gpus all --ipc=host -p 8000:8000 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    vllm/vllm-openai:v0.33.0 --model Qwen/Qwen3.5-9B
  # or pip
  pip install vllm
  vllm serve Qwen/Qwen3.5-9B --max-model-len 32768
  ```

  ```python
  from vllm import LLM, SamplingParams
  llm = LLM(model="Qwen/Qwen3.5-9B")
  params = SamplingParams(temperature=0.7, max_tokens=512)
  outs = llm.generate(prompts, params)
  # llm.chat(messages) applies the template
  ```

  시작 로그에서 볼 세 줄: `Model loading took [N] GiB`, `GPU KV cache size: [N] tokens`, `Maximum concurrency for 32,768 tokens per request: [M]x`. PART 2의 KV 계산이 여기서 확인된다.
- **엔드포인트(기본 포트 8000, 한 서버가 여러 API 규격을 동시에):** 생성(OpenAI) `/v1/chat/completions`, `/v1/completions`, `/v1/responses` · Anthropic `/v1/messages`, `/v1/messages/count_tokens`("Claude Code를 바로 연결") · 토큰 단위 `/tokenize`, `/detokenize`, `/inference/v1/generate`(토큰 ID 입출력, scale-out 모드) · 운영 `/health`, `/metrics`, `/v1/models`, `/version`, `/load`, `/ping` · 임베딩·풀링 `/v1/embeddings`, `/pooling`, `/classify`, `/score`, `/rerank`(Cohere) · LoRA·음성 `/v1/load_lora_adapter`, `/v1/audio/transcriptions`, `/v1/realtime`.
- **Tool calling:** ① 요청(messages + tools JSON Schema) → ② 채팅 템플릿이 tools 정의를 프롬프트에 주입 → ③ 모델 출력 `<tool_call>{name, arguments}` → ④ 모델 계열별 Tool Parser가 추출 → ⑤ OpenAI 형식 `tool_calls`.

  ```bash
  vllm serve Qwen/Qwen3.5-9B \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder
  ```

  `tool_choice: auto`는 파서가 찾아낸다(`--enable-auto-tool-choice` 필요). `required`나 특정 함수 지정은 구조화 출력으로 형식 자체를 강제한다. v0.25 Streaming Parser Engine이 모델별 파서를 스트리밍 공통 엔진으로 통합했다(플래그는 그대로). 파서 예: `qwen3_coder`(Qwen3.5 이후), `hermes`(Qwen3 이전), `llama3_json`, `mistral`, `openai`(gpt-oss). 모델별 값은 recipes 문서로 확인한다.
- **Reasoning · Chat template:** 입력 쪽은 messages → Chat Template(Jinja, `tokenizer_config.json`) → `<|im_start|>user …` → 토큰 ID다. 출력 쪽은 `<think>…</think> 답변` → Reasoning Parser → `reasoning` + `content`다. `--chat-template ./my.jinja`(템플릿이 없거나 잘못된 모델), 요청별 `chat_template_kwargs` 예 `{"enable_thinking": false}`, `--reasoning-parser qwen3`(deepseek_r1 등). 이전 "enable reasoning" 플래그는 폐기됐고 파서 지정만으로 동작한다.
- **에이전트 서빙:** Claude Code → `/v1/messages`(count_tokens 포함), Codex·Agents SDK → `/v1/responses`, LangChain 등 → `/v1/chat/completions`(가장 넓은 호환성). 프론트엔드(Python 기본/Rust 옵션)와 툴·리즈닝 파서가 앞에 있고, EngineCore는 stateless다. "**상태는 엔진 바깥에**": 대화 저장·내장 도구는 별도 Rust 게이트웨이(vllm-project/agentic-api)가 맡는다. llm-d v1.0의 세션 인식 라우팅과 로드맵의 에이전트 힌트(Session ID)도 같은 방향이다.
- **Multi-LoRA · Structured outputs:** 기본 가중치 W를 공유하고 요청의 `model` 이름으로 어댑터(ΔW = B·A 저랭크)를 고른다. 한 배치에서 함께 실행한다. `vllm serve Qwen/Qwen3.5-9B --enable-lora --lora-modules sql-lora=./adapters/sql`, 런타임에 `POST /v1/load_lora_adapter`. Structured outputs는 JSON Schema·정규식·선택지를 문법 상태 기계로 변환하고 허용 토큰만 남겨 샘플링한다. 요청은 `response_format: json_schema`, 백엔드는 xgrammar·guidance이고 LM Format Enforcer는 v0.33에서 deprecated다. `tool_choice: required`도 같은 장치로 형식을 강제한다.

#### PART 6. 성능 최적화 (45~50쪽)

- **최적화 포인트 표:**

  | 기법 | 줄이는 것 | 줄이지 못하는 것 | 주로 좋아지는 지표 |
  |---|---|---|---|
  | PagedAttention | KV 할당 낭비(단편화) | 토큰당 KV 바이트 | 동시 처리 수·처리량 |
  | Prefix caching | 같은 접두사 Prefill 재계산 | 새 출력 토큰 Decode | TTFT |
  | Chunked prefill | 긴 Prefill이 Decode를 막는 시간 | 전체 연산량 | ITL 안정성 |
  | FlashAttention | 어텐션 HBM 트래픽 | Dense 어텐션 O(n²) 연산 | Prefill 속도·긴 문맥 |
  | 가중치 양자화 | 가중치 메모리·읽기 대역폭 | KV 크기(별도 선택) | Decode ITL·적재 가능 모델 |
  | KV 양자화 | KV 메모리·대역폭 | 가중치 크기 | 동시 처리 수·긴 문맥 |
  | Spec decoding | Decode 스텝 수 | Target 검증 비용 | 저동시성 ITL |
  | CUDA Graph | 커널 런치 오버헤드 | 연산 자체 | 작은 배치 Decode |

- **양자화:** Qwen3.8-27B 가중치는 BF16(2 B) 약 56 GB, FP8(1 B) 약 28 GB, INT4·FP4(0.5 B) 약 14 GB.

  | 대상 | 형식 | 하드웨어 | 메모 |
  |---|---|---|---|
  | 가중치 8bit | FP8 W8A8, 블록 FP8 | Hopper·Ada·Blackwell·MI300 이상 | 품질 손실이 작아 **기본 추천** |
  | 가중치 4bit | AWQ·GPTQ INT4, Marlin 커널 | Ampere 이상 NVIDIA 등 | 메모리 최우선, **품질 확인 필수** |
  | 가중치 FP4 | NVFP4·MXFP4 | Blackwell(MXFP4는 MI355X도) | gpt-oss는 MXFP4로 배포 |
  | KV Cache | `--kv-cache-dtype fp8`(그 외 nvfp4 등) | FP8 지원 GPU | 동시 처리 수·긴 문맥 |

  "속도와 품질은 커널에 달려 있다. **양자화 후에는 평가셋으로 품질을 다시 확인하라.**"
- **Speculative decoding:** "The square root of 7 is 2.646"에서 뒤의 7은 베끼면 되는 쉬운 토큰이다. ① Draft가 k개 제안 → ② Target이 k개 위치를 한 번의 forward로 채점 → ③ 앞에서부터 rejection sampling으로 수락·거절 → ④ 수락된 접두사 + 보정 토큰 1개. 정확한 rejection sampling은 Target 분포를 그대로 유지한다(수치 오차 제외). 이득은 수락률·제안 수가 높고 Draft 비용이 낮을수록 크다. 배치가 크면 GPU가 이미 바빠 이득이 줄어든다. **저동시성·지연 민감 트래픽용.**
  - 방식: EAGLE-3/3.1(Target 히든 상태로 학습한 draft 헤드, 가장 널리 쓰임), MTP(모델 내장 다중 토큰 예측 헤드, DeepSeek 등), n-gram(프롬프트에서 같은 n-gram을 찾아 복사, 학습 불필요, 요약·코드 수정에 강함), Draft model(같은 토크나이저 작은 모델), DFlash·DSpark(블록 단위 초안, v0.25부터). 제거됨: Medusa, MLP speculator(v0.33).

  ```bash
  vllm serve <model> --speculative-config \
    '{"method": "eagle3", "model": "<draft-head>",
      "num_speculative_tokens": 3}'
  ```

  기본값은 꺼짐이다(기본 활성화는 Q4 2026 로드맵의 "목표"일 뿐). 지표 `vllm:spec_decode_*`(위치별 수락 토큰 수)로 효과를 확인한다.
- **목표별 튜닝:**

  | 처리량 우선 | 지연 우선 |
  |---|---|
  | `--gpu-memory-utilization 0.95`(KV에 VRAM 더) | `--max-num-batched-tokens` 약 2k(ITL 안정) |
  | `--max-num-seqs`↑(동시 시퀀스 더) | `--max-num-seqs`↓(배칭 경쟁 줄이기) |
  | `--max-num-batched-tokens` 8k~16k | Speculative decoding(저동시성 ITL) |
  | 양자화(FP8·AWQ 가중치, KV fp8) | 작은·양자화 모델(스텝 자체를 짧게) |
  | 복제(DP·TP, 규모 키우기) | 큐 대기 줄이기(복제·라우팅 확대) |

  ```bash
  # baseline — adjust per model recipe
  vllm serve <model> --max-model-len 32768 \
    --gpu-memory-utilization 0.92 --kv-cache-dtype fp8 \
    --max-num-batched-tokens 8192 \
    --enable-auto-tool-choice --tool-call-parser <family> \
    --reasoning-parser <family>
  ```

  헷갈리기 쉬운 설정: 지연 쪽 `max_num_seqs`는 더 작게(원본 표기가 2048과 같다고 적혀 있음, 추출본), prefix caching은 이미 기본 활성, `--gpu-memory-utilization` 기본값은 0.92.

#### PART 7. KV Cache 확장 (51~69쪽)

- **VRAM 한계(모델 설정 파일 기준, BF16 토큰당 KV / 262K 시퀀스 1개):** Qwen3.5-9B(32층 중 8층, KV 헤드 4, 256차원) 32 KiB / 8 GiB · Qwen3.8-27B(64층 중 16층) 64 KiB / 16 GiB · Qwen3.5-397B-A17B(60층 중 15층, KV 헤드 2) 30 KiB / 7.5 GiB · DeepSeek-V3(MLA, 61층, 잠재 576차원) 약 69 KiB / 약 8.6 GiB(128K). 27B 262K 시퀀스 하나의 KV(16 GiB)는 H100에 가중치를 올리고 남는 약 14 GB보다 크다. 에이전트는 도구 결과까지 문맥에 쌓고, GPU에서 밀려난 KV는 다음 턴에 다시 Prefill해야 한다. LMCache 사용자들이 저장한 KV 총량은 GPU 메모리를 훨씬 넘어섰다(MLSys 2026).
- **한계를 넘는 3가지:** ① 줄이기(GQA·MLA 모델, KV fp8·fp4로 2~4배, sliding window 층) ② 옮기기(CPU DRAM·NVMe·원격, 다시 쓰일 때 GPU로 승격: vLLM 오프로드, LMCache, Dynamo KVBM) ③ 공유하기(인스턴스 간 공유 저장소·P2P, KV 위치를 아는 라우팅: LMCache, Mooncake, llm-d). 판단의 출발점은 하나다. "**다시 계산할까, 불러올까?**"
- **재계산 vs 불러오기:** 불러오기가 이기는 조건은 `토큰당 KV 바이트 / 대역폭 < 2 × 파라미터 수 / 실효 FLOP/s`(어텐션 비용 제외). Qwen3.8-27B, 실효 500 TFLOPS, KV 64 KiB 가정으로 토큰 하나당 재계산(56 GFLOP) 약 111 µs 대비 CPU DRAM·PCIe(약 50 GB/s) 1.3 µs(85배 빠름), RDMA 200 Gbps(25 GB/s) 2.6 µs(42배), 이더넷 32 Gbps(4 GB/s) 16 µs(7배). 단위는 추출본에서 "s"로만 보이며 수치상 µs다. 긴 문맥일수록 불러오기가 유리하다(재계산에는 어텐션 O(n²)가 더해짐). LMCache 논문 실측으로는 32 Gbps에서 약 256K 토큰 이상에서만, 64·128 Gbps에서는 모든 길이에서 불러오기가 이겼다. 결론: "KV를 어디에 두느냐가 곧 얼마나 빨리 가져오느냐. 계층 설계가 필요하다."
- **KV 계층(G1~G4, NVIDIA Dynamo KVBM 용어):** G1 GPU HBM(수십~수백 GB, 수 TB/s, 지금 연산 중인 KV) / G2 CPU DRAM(수백 GB~수 TB, PCIe 수십 GB/s, 핫 캐시, pinned) / G3 로컬 NVMe(수 TB 이상, 수~수십 GB/s, 긴 문서·세션, GPUDirect Storage) / G4 원격·공유(Redis/Valkey·Mooncake Store·S3 호환). 내리기는 비동기 복사, 올리기는 요청 전 미리 가져와 지연을 숨긴다.
- **KV Connector API:** 스케줄러(EngineCore) 쪽은 ① `get_num_new_matched_tokens()`(외부 저장소에 이 요청의 토큰이 몇 개?) ② `update_state_after_alloc()` ③ `build_connector_meta()`이고, 워커(GPU, 레이어마다) 쪽은 ④ `start_load_kv()` ⑤ `wait_for_layer_load()` / `save_kv_layer()` / `wait_for_save()` ⑥ `get_finished()`. 구현체는 `--kv-transfer-config`로 고른다: OffloadingConnector, LMCacheConnectorV1, LMCacheMPConnector, NixlConnector, MooncakeConnector, MultiConnector.
- **vLLM 네이티브 CPU 오프로드(v0.11 OffloadingConnector):** 별도 설치 없이, 완성된 KV 블록을 생기는 즉시 CPU에 비동기 DMA로 복사한다(기본은 프롬프트만, pinned 메모리, LRU/ARC).

  ```bash
  vllm serve <model> \
    --kv-offloading-backend native \
    --kv-offloading-size 64
  # GiB 단위, TP 전체 합계
  # = OffloadingConnector + cpu_bytes_to_use
  ```

  빠른 이유: 비동기 커넥터 API(v0.9)라 저장이 응답 경로 밖에서 진행되고, DMA(`cudaMemcpyAsync`)는 GPU 코어를 쓰지 않으며, v0.12 레이아웃 변경으로 블록 하나에 전 레이어 KV를 담아 블록이 0.5~2.5 MB가 돼 DMA 효율이 올랐다. 측정(vLLM 블로그): TTFT 2~22배(단일 요청, 프롬프트가 길수록 큼), 처리량 최대 9배(512토큰 요청 1만 개, CPU 적중률에 비례). 조건은 Llama-3.1-8B·H100·GPU prefix 캐시 끔이다. 선점된 요청도 CPU에서 다시 불러온다. **CPU 계층 크기는 GPU KV보다 크게 잡는다.** 복사가 즉시 일어나므로 CPU 계층이 작으면 GPU에 있는 것을 복제할 뿐이다.
- **계층형 오프로드:** GPU HBM → 호스트(CPU DRAM, 모든 KV가 거침) → 2차 계층 fs(NVMe·공유 FS) / obj(S3 호환, NIXL) / p2p(다른 노드 CPU 계층, ZMQ·RDMA).

  ```json
  "spec_name": "TieringOffloadingSpec",
  "cpu_bytes_to_use": 107374182400,
  "secondary_tiers": [{"type": "fs", "root_dir": "/mnt/kv-cache"}]
  ```

  호스트 복사가 끝나면 GPU 블록을 바로 반환하고 2차 계층으로는 그 뒤에 내린다. 조회는 호스트 → 2차 순서이고, 승격 중이면 RETRY 후 다음 스텝에 재확인한다. `canonical_layout: true`일 때만 TP2·TP4 노드가 같은 청크를 공유한다(기본 false). 벤치마크(Qwen3.6-35B-A3B·H100×2·NVMe, 멀티턴 8라운드): 64개까지는 HBM 충분, 64~128개는 CPU가 처리량 유지, 128개 초과 시 스토리지가 처리량 2배 이상.
- **LMCache:** 추론 엔진 밖에 놓이는 KV 캐시 계층이다. 엔진 중립(vLLM·SGLang 커넥터)이며 저장(오프로드·재사용)과 전송(P/D에서 Prefill→Decode) 두 모드가 있다. 논문(arXiv 2510.09665): 처리량 최대 15배(멀티턴·문서 QA), CPU 오프로드 TTFT 1.9~8.1배 감소, P/D TTFT 1.53~1.84배 감소(vLLM 기본 대비). 백엔드 L1(CPU DRAM·Device DAX·NVMe GDS), L2(파일시스템·NIXL·S3·Redis/Valkey·Mooncake Store·3FS 등). 시카고대 Junchen Jiang 연구실, Apache 2.0, 2025-10 PyTorch Foundation 합류, 상용 지원 Tensormesh.
  - 아키텍처: **MP 모드(2026-04, 권장)**에서는 `lmcache server`가 노드당 1개 뜨고 vLLM은 LMCacheMPConnector로 GPU KV를 CUDA IPC로 공유한다. 캐시가 엔진 밖 프로세스라 캐시 문제가 엔진을 죽이지 않고, 노드의 여러 엔진이 L1 하나를 공유한다. 축출 LRU·ARC·IsolatedLRU(cache_salt별 할당량). 포트 ZMQ 5555 · HTTP 8080 · Prometheus 9090.
  - 흐름: 조회는 ① 프롬프트를 청크로(기본 256토큰) ② 청크마다 접두사 해시 ③ LOOKUP(L2에만 있으면 L1로 prefetch) ④ 적중만큼 블록 할당, Prefill 생략 ⑤ RETRIEVE L1→GPU 순이다. 저장은 ⑥ STORE GPU→L1 ⑦ Store 컨트롤러가 L2로 비동기 전송 ⑧ L1이 80% 차면 20% 축출 순이다. 레이어 단위 파이프라인으로 로드·계산·저장을 겹친다(인프로세스 모드에선 `use_layerwise`, 기본 꺼짐). 256토큰 청크인 이유: 작은 전송은 PCIe 효율이 낮다(논문 당시 vLLM 페이지는 레이어당 20~63 KB). 청크로 묶자 CPU 로드가 88→400 Gbps가 됐다. vLLM도 0.12에서 같은 이유로 블록을 키웠다.
  - **CacheBlend**(EuroSys'25 Best Paper): RAG처럼 문서 조각을 이어 붙이면 앞 문서만 접두사로 맞는다. 조각마다 KV를 재사용하되 편차 큰 토큰(HKVD, 보통 10~15%)만 다시 계산하고, 재계산은 KV 로드와 겹쳐 숨긴다. TTFT 2.2~3.3배 감소, 처리량 2.8~5배 증가. **CacheGen**(SIGCOMM'24): KV를 영상처럼 압축(차분·레이어별 양자화·산술 부호화, 대역폭에 맞춰 청크마다 압축 수준 선택). KV 크기 3.5~4.3배 감소, 가져오기·처리 지연 3.2~3.7배 감소.
  - 설정 3가지:

  ```bash
  # ① MP 모드(권장): 서버를 먼저 띄우고 vLLM은 연결만
  lmcache server --l1-size-gb 100 --eviction-policy LRU
  vllm serve <model> \
    --kv-offloading-backend lmcache --kv-offloading-size 100
  # ② MP 모드 명시형 (vLLM 0.20 이상이면 module_path 지정)
  --kv-transfer-config '{"kv_connector":"LMCacheMPConnector",
    "kv_connector_module_path":
    "lmcache.integration.vllm.lmcache_mp_connector",
    "kv_role":"kv_both"}'
  # ③ 인프로세스 (환경 변수 또는 YAML, LMCacheConnectorV1)
  LMCACHE_CHUNK_SIZE=256 LMCACHE_LOCAL_CPU=True \
  LMCACHE_MAX_LOCAL_CPU_SIZE=64 vllm serve <model> \
    --kv-transfer-config \
    '{"kv_connector":"LMCacheConnectorV1","kv_role":"kv_both"}'
  ```

  서버 옵션: `--l1-size-gb`·`--eviction-policy` 필수(LRU·ARC·IsolatedLRU·noop), `--l2-adapter` JSON 반복 지정(순서대로 사용), chunk size 256 최솟값, 원격 서버 `lmcache.mp.host`·`port`, 요청별 `kv_transfer_params`에 `lmcache.skip_load`.
  - **도입 점검:** "이 두 버전이면 된다"는 단일 조합은 없다. 버전 호환은 세 층으로 본다: ① 런타임·ABI(Python·PyTorch·CUDA 빌드 일치) ② 커넥터 로딩(의도한 커넥터가 실제로 로드되나) ③ 모델·기능(KV 레이아웃, 블록 크기, 하이브리드). **운영 전 5단계 확인:** 1) 서버 기동 후 의도한 커넥터 모듈이 로드됐는지 로그로 확인 2) 첫 요청으로 접두사 저장 3) 같은 접두사로 다시 요청해 적중 토큰 > 0 확인 4) vLLM 로컬 캐시만 비우거나 재시작한 뒤 LMCache에서 불러오는지 확인 5) 출력 정확도 비교(예: lm-eval 점수), 서버 로그의 레이아웃·전송 오류 확인. Docker라면 `--network host`, `--ipc host`(CUDA IPC). 하이브리드 모델(SWA·Mamba 혼합)에 HMA 미지원 커넥터가 붙으면 vLLM이 하이브리드 KV 매니저를 끄고 페이지 크기를 하나로 합쳐 메모리 이득을 잃는다. LMCache MP 커넥터는 지원하므로 끌 필요가 없다.
- **Mooncake(Kimi):** KVCache 중심 설계다. Conductor가 KV 위치·부하·SLO로 노드를 고르고, Prefill 풀 → Transfer Engine(RDMA) → Decode 풀, Mooncake Store(클러스터 노드의 CPU DRAM·SSD를 묶은 분산 KV 풀, Put/Get/Remove)로 구성된다. 처리 요청 수 A800 +115%, H800 +107%(FAST'25, 추출본). Transfer Engine은 RDMA·NVLink·TCP를 한 API로 묶고 4×200 Gbps에서 87 GB/s, 8×400 Gbps에서 190 GB/s다. vLLM 연결은 MooncakeConnector(P/D)·LMCache 백엔드·SGLang HiCache·NIXL 플러그인.
- **KV 계층 솔루션 비교:**

  | 솔루션 | 무엇 | 계층·범위 | vLLM 연결 | 이런 경우 |
  |---|---|---|---|---|
  | vLLM 네이티브 | 엔진 내장 오프로드 | CPU(+fs·S3·p2p, v0.22) | OffloadingConnector | 별도 인프라 없이 시작 |
  | LMCache | 엔진 밖 KV 캐시 계층 + CacheBlend·CacheGen | CPU·SSD·Redis·S3·Mooncake, 노드~클러스터 | LMCacheMPConnector | 긴 문서·RAG, 여러 엔진 간 공유 |
  | Mooncake | 분산 KV 풀 + RDMA 전송 엔진 | 클러스터 DRAM·SSD 풀 | MooncakeConnector·LMCache 백엔드 | RDMA 망, 대규모 P/D |
  | Dynamo KVBM | NVIDIA Dynamo의 KV 블록 관리자 | G1~G4 | DynamoConnector(kvbm 모듈) | NVIDIA 스택 전체를 쓸 때 |
  | SGLang HiCache | SGLang 계층형 Radix 캐시 | GPU·CPU·원격 | 해당 없음(SGLang 전용) | SGLang으로 서빙할 때 |
  | llm-d KV 인덱서 | 어느 Pod에 어떤 KV가 있나 추적 | 클러스터 라우팅(저장 안 함) | KV 이벤트(ZMQ) | 레플리카가 여럿일 때 적중률 높이기 |

  서로 배타적이지 않다. 예를 들어 llm-d가 라우팅하고, 각 Pod의 vLLM은 LMCache로 CPU·SSD에 KV를 두며, LMCache의 원격 백엔드로 Mooncake Store를 쓰는 조합이 가능하다.
- **클러스터 단위 KV 공유:** llm-d 라우터(EPP)의 KV 인덱서가 이벤트로 블록 키 → Pod 목록을 유지한다. Precise prefix scorer는 요청의 연속 접두사를 보고 계층 가중치(GPU 1.0 · CPU 0.8)로 점수를 매기고, 큐 길이·KV 사용률과 합쳐 0~1로 정규화한다. vLLM은 `kv_events_config`(publisher zmq)로 BlockStored·BlockRemoved·AllBlocksCleared 이벤트를 보낸다. 이벤트가 오기 전 공백은 추측 인덱싱(라우팅 직후 곧 생길 블록을 기본 2초 TTL로 기록)으로 메운다. Pod A가 바쁘면 B로 보내고, B가 A의 CPU 계층에서 블록을 P2P(NIXL)로 가져온다.
- **KV 캐시 관측 지표:**

  | 지표(`/metrics`) | 무엇을 세나 | 읽는 법 |
  |---|---|---|
  | `vllm:prefix_cache_hits / queries` | GPU 로컬 접두사 적중 토큰 | 로컬 적중률, 라우팅이 잘 되는지의 신호 |
  | `vllm:external_prefix_cache_hits / queries` | 커넥터(오프로드·LMCache) 적중 | 스케줄링 시점 집계라 실제 로드량과 함께 볼 것 |
  | `vllm:kv_offload_store_bytes / load_bytes` | GPU↔오프로드 계층 전송량 | load가 0에 가까우면 내리기만 하고 재사용이 없음 |
  | `vllm:kv_offload_store_time / load_time` | 전송 시간(초) | 바이트÷시간 = 실효 대역폭, 재계산과 비교 |
  | `vllm:kv_offload_allocation_failure` | CPU 계층 블록 할당 실패 | 계속 늘면 CPU 계층이 작음 |
  | `vllm:kv_offload_cpu_cache_usage_perc` | 전송 중 점유 비율(점유율 아님) | 1.0 근처가 지속되면 저장이 누락될 수 있음 |
  | `vllm:kv_cache_usage_perc` · `num_preemptions` | GPU KV 사용률·선점 횟수 | 오프로드 전후 비교의 기준선 |

  카운터는 Prometheus에서 `_total`이 붙는다. 오프로드 지표 이름은 v0.26 이후 기준이고, LMCache 서버 지표는 `:9090`에서 본다.
- **언제 효과가 있나:** 잘 맞는 경우는 멀티턴 대화·에이전트(이전 턴 전체 재사용), 긴 문서 QA·RAG(같은 문서 반복), 공통 시스템 프롬프트·few-shot, 코드 에이전트(같은 저장소 문맥)다. 효과가 작은 경우는 매번 다른 짧은 프롬프트, 출력이 긴 생성 위주(병목이 Decode), 동시성이 낮아 HBM이 넉넉함, 느린 네트워크 + 짧은 문맥(재계산이 더 빠름)이다.
- **도입 체크리스트(덱 원문):** 프롬프트는 뒤에 붙이기만 한다(중간을 잘라내는 truncation으로 적중률이 85%→45%로 떨어진 LMCache 실배포 사례). 캐시 키에 모델·LoRA·cache_salt를 넣는다(테넌트 간 재사용과 타이밍 공격 방지). 용량·대역폭 계산을 먼저 한다(토큰당 KV × 보관할 토큰 수, 재계산 vs 불러오기 비교). 지표로 확인한다(로컬·외부 적중률을 나눠 보고, 로드 바이트·TTFT p50/p99를 켜기 전과 비교).

#### PART 8. 확장과 운영 (70~80쪽)

- **병렬화 전략:** TP `--tensor-parallel-size`는 레이어 안의 행렬을 나눈다. 매 레이어 all-reduce가 일어나므로 노드 안(NVLink)에서 쓰고, KV도 나눠 담는다. PP `--pipeline-parallel-size`는 레이어 묶음을 단계로 나눈다. 통신이 적어 노드 간 확장에 유리하지만 파이프라인 버블이 생긴다. DP `--data-parallel-size`는 모델 전체를 복제해 처리량을 늘리며, 복제마다 가중치 메모리가 전부 필요하다. EP `--enable-expert-parallel`은 MoE 전문가를 GPU에 분산하고 all-to-all로 디스패치한다.
- **멀티노드(16 GPU, 2노드 × 8):** `--tensor-parallel-size 8 --pipeline-parallel-size 2`. TP 16 대신 TP8 × PP2인 이유: TP의 all-reduce는 매 레이어마다 일어나므로 느린 노드 간 링크에 걸지 않는다(A 덱). 네트워크 체크리스트: RDMA(InfiniBand, RoCEv2), 인터페이스 고정 `VLLM_HOST_IP`·`GLOO_SOCKET_IFNAME`·`NCCL_SOCKET_IFNAME`, IB가 없으면 `NCCL_IB_DISABLE=1`, 실행 기반은 Ray 클러스터 또는 Kubernetes LWS.
- **대형 MoE와 긴 컨텍스트:** Wide EP(DeepSeek·Kimi·GLM 계열)는 어텐션 층을 DP(GPU마다 다른 요청)로, MoE 층을 EP(GPU마다 다른 전문가)로 나눈다. `--data-parallel-size N --enable-expert-parallel`, EPLB(자주 쓰이는 전문가 복제로 부하 균형), DBO(두 마이크로배치로 통신·연산 겹침), Elastic EP(2026, 중단 최소화하며 GPU 수 조정). Context Parallel은 128K 시퀀스 하나를 시퀀스 축으로 나눈다. PCP(Prefill CP)는 긴 프롬프트의 Prefill을 나눠 TTFT를 줄이고, DCP(Decode CP)는 KV를 GPU에 나눠 저장해 TP에서 생기는 KV 중복을 줄인다(더 긴 문맥, 더 많은 동시 요청).
- **P/D 분리:** 라우터·프록시 → Prefill 풀 → KV 전송(NIXL·LMCache·Mooncake, RDMA) → Decode 풀. 장점은 Prefill 폭주가 Decode ITL을 흔들지 않는 간섭 격리와, 풀마다 GPU 종류·병렬화를 따로 고를 수 있다는 점이다. 비용은 KV 전송 시간·대역폭과 풀 사이 유휴 용량이다. 비율이 맞지 않으면 이득이 사라진다. PART 7의 같은 KV Connector API가 이번엔 노드 간 전송을 맡는다(NixlConnector, MooncakeConnector, LMCache 전송 모드(NIXL 위), MultiConnector(전송+오프로드)).

  ```bash
  --kv-transfer-config '{
    "kv_connector": "NixlConnector",
    "kv_role": "kv_both"}'
  ```

- **Kubernetes 지형:** Gateway(Gateway API Inference Extension: InferencePool, Endpoint Picker, prefix·부하 인식 라우팅) → 오케스트레이션(하나를 고르거나 조합): llm-d(레퍼런스 경로, v1.0 2026-10), production-stack(Helm·라우터·LMCache), AIBrix(LoRA 관리·오토스케일), KServe(범용 모델 서빙 CRD), NVIDIA Dynamo(분산 서빙, vLLM 백엔드) → vLLM 파드(단일 노드 Deployment, 멀티노드 LeaderWorkerSet) → GPU 노드. 오토스케일 신호는 대기 요청 수·KV 사용률·지연 SLO다. **llm-d 구조:** Envoy 기반 Inference Gateway가 아니라 Endpoint Picker가 "어느 파드로"를 결정한다(점수: prefix 적중·부하·세션, KV 캐시 이벤트 보고). Prefill/Decode 파드 사이 KV 전송은 NIXL RDMA. v1.0은 멀티테넌트 flow control, 세션 인식 라우팅, 라우터 HA, P/D 묶음 업그레이드를 넣었다.
- **메트릭(요청 단계별):** ① 큐 대기 `vllm:request_queue_time_seconds`, `vllm:num_requests_waiting` ② Prefill·첫 토큰 `vllm:time_to_first_token_seconds`, `vllm:request_prefill_time_seconds`, `vllm:prefix_cache_hits/_queries` ③ Decode `vllm:inter_token_latency_seconds`, `vllm:request_time_per_output_token_seconds`, `vllm:spec_decode_*` ④ 완료 `vllm:e2e_request_latency_seconds`, `vllm:request_success_total`. 시스템 상태(스케일링·알람 기준)는 `vllm:num_requests_running`, `vllm:kv_cache_usage_perc`, `vllm:num_preemptions`다. `/metrics` → Prometheus → Grafana, 요청 추적은 OpenTelemetry. **메트릭은 다음 마이너 버전에서 숨겨지고 그다음에 삭제되니 업그레이드 때 대시보드를 점검하라**(예: `gpu_cache_usage_perc` → `kv_cache_usage_perc`).
- **벤치마크:**

  ```bash
  vllm bench serve --model <m> \
    --dataset-name random \
    --random-input-len 2048 \
    --random-output-len 256 \
    --request-rate 8
  ```

  요청률을 바꿔 가며 반복하고(GuideLLM은 부하 스윕 자동화), SLO(예: p99 TTFT 목표) 안의 최대 요청률이 Goodput이다. 보고·기록할 것: p50·p95·p99의 TTFT·ITL·E2E, tokens/s, 비용 / 모델·하드웨어·정밀도·vLLM 버전 / 입출력 길이 분포를 실제 트래픽에 맞추기 / prefix 캐시 warm·cold, 부하 정책(도착률·동시성) / 정밀도·디코딩을 바꾸면 품질도 재평가.
- **증상별 진단:**

  | 증상 | 먼저 의심 | 확인 지표 | 조치 |
  |---|---|---|---|
  | TTFT가 높다 | 큐 대기 또는 Prefill 병목 | queue_time · num_requests_waiting | 복제·라우팅 확대, prefix 캐시, 청크 크기 |
  | ITL·TPOT가 나쁘다 | Decode 대역폭·KV 트래픽, 큰 Prefill이 끼어듦 | inter_token_latency | `max_num_batched_tokens`↓, 양자화, spec decoding |
  | 동시성에서 OOM·선점 | 가중치+KV+작업 공간 압박 | kv_cache_usage_perc · num_preemptions | `max_model_len`↓, KV fp8, TP |
  | 확장해도 안 빨라진다 | 통신·토폴로지 | 집합 통신 시간 | TP는 노드 안에서, NCCL·RDMA 설정 점검 |

  현장 사례: `Gloo connectFullMesh failed`(멀티노드에서 잘못된 인터페이스 선택 → `GLOO_SOCKET_IFNAME`으로 지정, A 덱) / Qwen 출력 이상(FlashInfer cascade attention 이슈 → `--disable-cascade-attn`, A 덱·당시 버전) / Eager + 양자화·LoRA 성능 저하(CUDA Graph 사용으로 해결, B 덱).
- **추론 엔진 비교:** vLLM(모델·하드웨어 지원 범위 최대, day-0 모델, RL 롤아웃 표준, llm-d / 옵션이 많고 변화가 빠름 / 기본 선택지), SGLang(RadixAttention 접두사 재사용, 에이전트·구조화 출력 / 접두사가 많은 멀티턴), TensorRT-LLM(NVIDIA 최고 수준 성능, v1.0부터 사전 엔진 빌드 불필요 / NVIDIA 전용, 신규 모델 지원 늦은 사례), LMDeploy(TurboMind, 양자화 배포 / 생태계 작음), TGI(2025-12부터 유지보수 모드 → 신규 도입 비권장).

#### 마무리. RL과 로드맵 (81~84쪽)

- **RL 롤아웃 엔진:** ① vLLM이 현재 정책으로 롤아웃 생성 → ② 환경·하네스가 채점(보상·샘플 구성) → ③ Trainer(FSDP·Megatron 등) 정책 업데이트 → ④ 새 가중치를 vLLM으로 동기화. 롤아웃이 학습 시간의 큰 몫을 차지한다. 네이티브 가중치 전송 `update_weights()`(전송 엔진 초기화 → 청크 단위 업데이트 → 마무리 훅, NCCL·CUDA IPC 백엔드), `POST /pause`·`/resume`(업데이트 중 진행 중 요청 유지 keep, GPU를 같이 쓰면 sleep으로 메모리 반납), `VLLM_BATCH_INVARIANT=1`(배치 크기가 바뀌어도 같은 결과 → 학습·추론 수치 불일치 감소, 베타, 처리량 비용 있음). verl·OpenRLHF·AReaL·slime·TRL·SkyRL 모두 vLLM을 롤아웃 엔진으로 쓴다.
- **사례: Agent Lightning v1.0:** 에이전트 하네스(도구·서브에이전트·컨텍스트 관리) → API Gateway 프록시(롤아웃 ID를 붙여 모든 호출 기록) → vLLM(OpenAI 호환, token ID·logprob 기록) → Trainer. **왜 token ID인가(retokenization drift):** 샘플링 당시 `h|aving`이 다시 토큰화하면 `hav|ing`이 된다. 텍스트는 같아도 토큰 경계가 달라 호출들을 이어 붙일 수 없다. vLLM이 token ID·logprob를 돌려주면 재토큰화 없이 학습한다. 보고치: SWE-bench Verified 41.8 → 56.4(Qwen3.5-9B, RL만으로, 학습 샘플 6K), 약 3,500줄의 경량 프레임워크. 하네스는 엔드포인트만 프록시로 바꾸면 된다.
- **로드맵(2026 Q4 계획, 버전은 여전히 0.x):** Core는 MRV1 완전 제거, KV 캐시 설정 빌더, CUDA Graph 리팩터링, Rust 프론트엔드 기본화 추진(Responses API 포함). 대규모 서빙은 llm-d·Dynamo와 에이전트 힌트 연동, P/D·KV 오프로드 프로덕션 레시피, EP 장애 복구, Rubin·MI455X 대응. 모델 성능은 FP4 KV cache, 디스크 기반 KV 오프로드, 신규 대형 모델(DeepSeek-V4.1, GLM-5.3, Qwen3.8 등) 최적화. Spec decoding·RL은 블록 rejection sampling 기본화, spec decoding 기본 활성(목표), RL 가중치 업데이트·학습/추론 일관성·RL용 LoRA. 출처: vLLM GitHub issue #61024(2026-10-10), RL 로드맵 #58990. "계획이며 출시된 기능이 아님."

---

### 실습 과제 / 단계

덱(Drive본) 자체에는 실습 슬라이드가 없다. 실습은 강의 저장소 `Day07/`에 있다(상세 인용은 `99-extras.md`).

1. **준비:** 저장소 루트에서 `uv sync`를 한 번 실행한 뒤(Day07에서는 하지 않는다) `cd Day07 && cp .env.example .env`. `RUNPOD_BASE_URL`(필수, 강사 공지, `https://<POD_ID>-8000.proxy.runpod.net/v1`), `EXA_API_KEY`, `OPENROUTER_API_KEY`를 채운다.
2. **호출 1:** `uv run python runpod_model_call.py`. langchain-openai `ChatOpenAI`로 GLM-5.3-Flash에 "한 줄로 자기소개 해줘."를 보낸다(`extra_body.chat_template_kwargs = {"reasoning_effort": "low", "clear_thinking": True}`, `timeout=95`).
3. **호출 2:** `uv run python runpod_openai_reasoning.py`. openai SDK로 비스트리밍과 스트리밍(`stream_options={"include_usage": True}`)을 호출하고, `reasoning`/`reasoning_content`와 `content`를 나눠 출력한다(`reasoning_effort: "max"`). 덱 PART 5의 Reasoning Parser · `chat_template_kwargs`를 직접 확인하는 실습이다.
4. **활동 1(자유):** DeepAgents 하나 만들기. 모델 GLM-5.3-Flash(RunPod), EXA API Tool 1개, 입력 "GLM-5.3-Flash 라는 모델의 분석 보고서를 작성할 것."
5. **활동 2(자유):** dcode 설치(WSL 전용, `curl -LsSf https://langch.in/dcode | bash`, OpenRouter, OpenAI·Anthropic·Google 3사 모델 불허, 테스트 모델 GLM-5.3-Flash·DeepSeek-V4.1-Flash·Qwen3.8). 과제 4개: ① Prompt Caching을 고려한 구성 ② 모델별 Harness Profile ③ 메모리 구성 확인·테스트 ④ Middleware로 Self-Improving.
6. **(Day07_new) 자유 챗봇:** 3사 주요 모델 제외 전부 허용, LLM은 200B 이하 권장, 이미지 3~4장, 비디오 X, STT·TTS 적당히. 주제는 DeepAgents 기반이면 좋지만 편한 것으로.
7. 채점 과제는 없다. 목~금 PJT용 dcode 소스는 Day08에서 제공한다.

---

### 실제 프로젝트 적용 체크리스트

에이전트 하네스가 **자체 호스팅 모델(OpenAI/Anthropic 호환 엔드포인트)**을 쓸 때를 기준으로 한 원칙이다. vLLM·LMCache 등은 예시다.

**용량·설정**
- [ ] 모델 config에서 KV 바이트/토큰을 직접 계산했다(`2 × L(full attention 층만) × H_kv × D_head × dtype 바이트`). 전체 레이어·hidden size로 과대 추정하지 않았다.
- [ ] (VRAM × 사용률 − 가중치 − 활성화) ÷ KV/토큰으로 예상 KV 토큰 수와 최대 동시성을 구했고, 기동 로그의 실제 값과 대조했다. 설정은 요청이고 로그가 응답이다.
- [ ] 최대 컨텍스트 길이를 실제 필요만큼으로 제한했다. 1개 시퀀스도 안 들어가는 길이로 띄우지 않는다.
- [ ] 목표를 먼저 정했다(처리량 vs 지연). 토큰 예산·동시 시퀀스 수·spec decoding 사용 여부를 그 목표에 맞췄다.
- [ ] 양자화(가중치·KV)를 적용했다면 같은 평가셋으로 품질을 다시 쟀다. 하드웨어가 해당 형식을 지원하는지도 확인했다.

**프롬프트·캐시 (하네스 쪽 책임)**
- [ ] 시스템 프롬프트·도구 정의·고정 지침 같은 공통·불변 부분을 프롬프트 **앞쪽**에 두고, 매번 바뀌는 내용은 뒤에 붙인다.
- [ ] 대화 이력은 **뒤에 붙이기만** 한다. 중간을 잘라내거나 순서를 바꾸는 압축은 접두사 캐시를 깨므로 비용(TTFT)과 맞바꾼다는 것을 알고 쓴다.
- [ ] 멀티테넌트라면 캐시 격리 키(테넌트별 salt, 모델·어댑터 ID)를 넣어 교차 재사용과 타이밍 공격을 막는다.
- [ ] 캐시 적중률(로컬·외부 분리)을 지표로 보고, 도입 전후 TTFT p50/p99를 비교한다.

**인터페이스·파서**
- [ ] 모델 계열에 맞는 tool-call 파서·reasoning 파서·chat template을 명시하고, 값의 출처(모델 recipe 문서)를 남겼다.
- [ ] reasoning on/off·effort 같은 옵션은 모델마다 chat template 변수 이름이 다르다는 것을 전제로, 모델별 프로필(설정 묶음)로 분리했다.
- [ ] 비표준 응답 필드(예: `reasoning` vs `reasoning_content`)는 버전별 이름 차이를 흡수하는 접근자 하나로 읽는다. 상위 SDK가 비표준 필드를 버리는지도 확인한다.
- [ ] 형식이 반드시 맞아야 하는 출력(JSON·도구 호출 강제)은 프롬프트 부탁 대신 구조화 출력(문법 제약 디코딩)으로 강제한다.
- [ ] 엔진은 stateless로 두고, 대화 상태·도구 실행 상태는 하네스(엔진 바깥)가 가진다.
- [ ] 프록시·게이트웨이의 연결 제한 시간을 알고, 클라이언트 timeout을 그보다 짧게 잡으며 긴 응답은 스트리밍으로 받는다.

**운영·관측**
- [ ] 큐 대기 / TTFT / ITL / E2E / KV 사용률 / 선점 횟수를 대시보드에 둔다. 처리량이 아니라 SLO 안의 Goodput으로 판단한다.
- [ ] 벤치마크는 실제 트래픽의 입출력 길이 분포와 도착률로 돌리고, 모델·하드웨어·정밀도·엔진 버전·캐시 warm/cold를 함께 기록한다.
- [ ] 증상 → 의심 지점 → 확인 지표 → 조치 표를 팀 런북으로 둔다(TTFT↑ = 큐/Prefill, ITL↑ = Decode/큰 Prefill 끼어듦, 선점↑ = KV 부족, 확장해도 안 빨라짐 = 통신).
- [ ] 엔진 업그레이드 때 메트릭 이름 변경·플래그 폐기를 점검한다(지원 중단 → 숨김 → 삭제 주기).
- [ ] 멀티노드는 통신이 잦은 병렬화(TP)를 노드 안에 두고, 네트워크 인터페이스를 명시적으로 고정한다.
- [ ] 외부 KV 계층(오프로드·공유 캐시)은 "재계산 vs 불러오기" 계산과 워크로드 적합성(멀티턴·긴 공통 문맥)을 먼저 확인하고 도입한다. 도입 후에는 로드·적중·정확도를 단계별로 검증한다.

**학습 연계(선택)**
- [ ] 에이전트 궤적을 학습에 재사용할 계획이면 텍스트가 아니라 엔진이 돌려준 token ID·logprob를 기록한다(재토큰화 drift 방지).

---

### 부록 — 저장소 사본 덱(`Day07/Day7_vLLM_기초와_추론_속도_최적화.pdf`) 목차

71쪽, "vLLM 기초와 추론 속도 최적화" (전현준). OT 슬라이드에 과정 지도가 있다: Agent Harness(Control Plane · Deterministic · Context Control · Code Mode · Optimization) / Local Model(TODAY: vLLM · KV Cache · Route Models · Hybrid Model Arch) / Agent Guardrail(Input · Output · Model · Code) / Coding Harness / PJT.

- Ch1 vLLM 기초(5~14쪽): 같은 VRAM의 동시 요청 수, 두 실행 형태(`LLM` / `vllm serve`), 최소 실행과 시작 로그(`vllm serve Qwen/Qwen3.8-27B --max-model-len 64000 --gpu-memory-utilization 0.85 --max-num-seqs 32 --max-num-batched-tokens 4096 --enable-prefix-caching` → `GPU KV cache size: 65,536 tokens`, `Maximum concurrency: 8.00x`, "설정 플래그는 요청이고 로그는 응답"), 요청 경로·상태 전이, 샘플링 계수, V1 Engine·MRV2, 용어
- Ch2 성능 지표(15~20쪽): Prefill/Decode, 지표 시간 축, 프로파일별 병목, CLI 파라미터 한눈에
- Ch3 Attention·KV·블록 관리(21~34쪽): KV 공식, MHA/GQA/MQA, GPU 메모리 구성, 논리·물리 블록, CoW, 블록 단위 softmax, Paged KV와 FlashAttention, 백엔드 선택
- Ch4 Batch·CUDA Graph·CPU(35~45쪽): Continuous batching, packed token·slot mapping, chunked prefill, 토큰 예산, preemption, CUDA Graph·compile, performance mode, cold start vs warm, CPU 경로 병목
- Ch5 Cache·Quant·Spec(46~56쪽): APC, 캐시 친화적 프롬프트 순서, weight/KV 양자화, FP8 KV, quality gate, hybrid attention, spec decoding(acceptance·비용 모델·방식)
- Ch6 분산·Recipe(57~71쪽): TP·PP·DP, GPU 머신별 배치 예, Dense/MoE recipe, EPLB, context parallelism, P/D 분리, offload·sleep, LoRA 운영, 구조화 출력과 E2E 지연, 모델별 runtime 개선 이력

Drive본에만 있는 것: PART 7(KV 확장: Connector API, LMCache, Mooncake, llm-d 인덱서), PART 8의 Kubernetes·진단 표·엔진 비교, Anthropic/Responses 호환·에이전트 서빙, RL·Agent Lightning·로드맵. 저장소본에만 있는 것: OT 과정 지도, 샘플링 계수, performance mode·cold start, 모델별 recipe·GPU 머신별 배치 예.
