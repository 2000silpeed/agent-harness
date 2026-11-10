# 7일차 종합 — 모델 서빙: 양자화 · KV 캐시 · vLLM

| 파일 | 내용 |
|---|---|
| [00-deck.md](00-deck.md) | 교재: vLLM — 이론에서 추론까지 (84쪽, PART 1~8. 저장소 사본 덱과 다른 자료라 부록에 목차 비교) |
| [01-lecture1.md](01-lecture1.md) | 1강: 데이터 타입·양자화와 가중치·KV 캐시 메모리 |
| [02-lecture2.md](02-lecture2.md) | 2강: 양자화와 텐서 패럴렐 — GPU 한 장을 쥐어짜고, 못 올리면 나눈다 |
| [03-lecture3.md](03-lecture3.md) | 3강: vLLM 추론 엔진 기초 — Prefill/Decode, KV Cache, PagedAttention, 배칭, 엔진 구조 |
| [04-lecture4.md](04-lecture4.md) | 4강: vLLM 서빙 설정과 최적화 — 레시피·파서·서빙 인터페이스 |
| [05-lecture5.md](05-lecture5.md) | 5강: KV 캐시를 GPU 밖으로(계층화·LMCache), RL·증류, 자유 챗봇 실습 |
| [99-extras.md](99-extras.md) | 판서 이미지 3장(정밀도, KV 메모리 회계, 멀티 GPU 배치), 저장소 위치 표 |

## 실습 코드 위치

수업 저장소 `github.com/HyunjunJeon/sds_ax_advanced_2026` 기준이다(2026-11-10 `aad1614d`).

| 강의 | 저장소 위치 | 비고 |
|---|---|---|
| 1~4강 이론 | `Day07/Day7_vLLM_기초와_추론_속도_최적화.pdf`(71쪽) | 강의 화면 교재(드라이브 84쪽본)와 다른 덱. 주제는 겹치고 슬라이드는 다름 |
| 판서 | `Day07/Day07_01.png`~`03.png` | 전사는 `99-extras.md` |
| vLLM 호출 예제 | `Day07/runpod_model_call.py`, `runpod_openai_reasoning.py`, `Day07/README.md` | RunPod의 GLM-5.3-Flash. 강의에서 직접 열지는 않음 |
| 5강 실습 규칙 | `Day07_new/task.md`, `Day07/.env.example`(`OPENROUTER_API_KEY`) | 3사 모델 금지, 이미지 3~4장, 비디오 금지, LLM 200B 이하 |

## 하루 요약

- **왜 셀프호스팅인가.** API 비용, 보안(코드·데이터 유출), 모델 커스터마이징. 강사는 내년에 수요가 더 커진다고 봤다. 라이브러리 예제의 단건 `generate`로 서비스를 띄우지 말고 동시 요청과 KV 메모리를 관리하는 추론 엔진을 쓴다.
- **용량 = 가중치 + KV 캐시.** 가중치는 BF16 기준 파라미터 수 × 2바이트로 잡고 양자화 타입에 맞춰 나눈다. GPU에 올릴 수 있는지는 가중치만으로 판단할 수 없고, 목표 컨텍스트 길이 × 동시 요청 수만큼의 KV를 더해야 한다. 남는 메모리가 곧 동시 처리 수다. 긴 컨텍스트 API 가격이 특정 길이 이후 급등하는 이유도 이 메모리다.
- **양자화는 공짜가 아니다.** FP8·4비트로 낮추면 빠르고 작아지지만 오차가 누적돼 반복 출력 같은 품질 저하가 생긴다. 웨이트와 KV 캐시 dtype은 따로 정한다(웨이트만 줄이면 KV는 그대로). 품질은 자기 데이터로 다시 잰다.
- **못 올리면 나눈다(텐서 패럴렐).** 다만 KV는 GPU마다 들고 있어야 해서, 큰 모델은 GPU 8장으로도 100만 토큰 요청 하나를 못 받기도 한다. 그래서 업계가 KV 캐시 절감, 4비트 포맷, KV를 DRAM·NVMe로 내리는 방법(LMCache, Mooncake)에 매달린다. 오프로드는 만능이 아니라 지연과 처리량의 절충이다.
- **추론은 연산이 아니라 메모리 문제.** Prefill(입력 병렬 처리 → 첫 토큰 시간 TTFT)은 빠르고, Decode(한 토큰씩 → 토큰 간격 ITL)는 메모리 대역폭에 묶여 느리다. 우리가 조절할 수 있는 건 데이터 타입과 컨텍스트 길이뿐이다.
- **vLLM = GPU 위의 OS.** PagedAttention(블록 단위 KV), 블록 해시 기반 Prefix Caching(= 프롬프트 캐싱, TTL로 회수), Continuous Batching. GPU 8장이면 CPU도 최소 10개가 필요하다.
- **에이전트 개발자가 기억할 것:** "Prefill은 고정된 입력이어야 된다… 캐시를 깨지 말자." 프롬프트 앞부분은 고정하고 바뀌는 값은 뒤로 보낸다. 엔진은 stateless로 두고 상태는 하네스가 가진다.
- **서빙 설정은 레시피에서 시작.** vLLM 레시피 사이트의 모델 × 장비별 검증 설정(토크나이저 모드, KV dtype, TP, tool-call·reasoning 파서, auto tool choice)을 기준선으로 삼는다. 파서는 모델별 출력을 OpenAI 규격으로 바꿔 주니 직접 만들지 않는다. CUDA Graph는 테스트 외에는 끄지 않는다. 기동 로그의 KV 토큰 수·최대 동시성을 확인한다("설정은 요청, 로그는 응답").

## 확인 필요 (요약)

강의 수치와 공식 자료가 다른 곳이 많다. 각 파일의 "확인 필요"에 둘 다 적었다.
- H200 메모리: 강의 144GB, NVIDIA 공식 141GB.
- TP GPU 수: 강의 "2의 제곱수", vLLM은 attention head 수가 TP 크기로 나누어떨어지면 됨.
- 서빙에서 DP·PP: 강의 "잘 안 씀", vLLM 문서는 멀티노드 PP와 MoE용 DP 조합을 권장.
- KV FP8 효과: 강의 "30GB → 15GB", 저장소 PDF는 KV 원시 데이터만 절반이고 전체 메모리는 아니라고 설명.
- GLM-5.3 NVFP4 크기: 강의 560GB, 공식 레시피 약 465GB. MLA 도입 시점: 강의 DeepSeek V4, 논문은 V2.
- 5강 "TTFT 22배" 발언: vLLM 블로그는 CPU에서 KV를 불러올 때 TTFT가 2~22배 **줄어든다**(개선)고 함.
- 오후 실습 모델: 강의는 Qwen3.8 27B 같은 소형 모델, 저장소 README는 RunPod의 GLM-5.3-Flash.
