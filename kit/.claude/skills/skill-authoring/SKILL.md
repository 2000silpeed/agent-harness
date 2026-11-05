---
name: skill-authoring
description: 에이전트 스킬(SKILL.md)을 새로 쓰거나 기존 스킬을 고칠 때 강의 기준(What/When description, XML 구역, 5천 토큰, references/scripts/assets 분리)으로 작성하고 점검한다. 스킬 생성, 스킬 리뷰, "스킬이 잘 안 불린다", P4 단계에서 사용.
---

<structure>
```
<skill-name>/
├── SKILL.md       # frontmatter + 핵심 지시
├── scripts/       # 실행 코드 (결정적 작업, 단계 체인)
├── references/    # 필요할 때만 읽는 상세 문서
└── assets/        # 양식, 템플릿, 로고 등 고정 리소스
```
</structure>

<frontmatter_rules>
- `name`: 소문자·숫자·하이픈, 64자 이내, 폴더 이름과 같게 한다.
- `description`: **What + When(+ 아닌 경우)** 을 두세 문장으로 쓴다. What이 이름에 드러나면 When 위주로 쓴다. 반드시 불려야 하는 작업명이나 키워드를 넣는다.
- 선택 필드(`allowed-tools`, `metadata`)는 필요할 때만 넣는다.
</frontmatter_rules>

<body_rules>
- 본문은 5천 토큰 이내로 쓴다. 구역은 마크다운 헤더 대신 **XML 태그**로 나눈다(예: `<purpose>`, `<procedure>`, `<tools>`, `<anti_patterns>`).
- 본문에는 공통 지침과 안티패턴처럼 빠질 수 없는 것만 남긴다. 케이스별 상세는 `references/`로 옮기고 "X일 때 references/x.md를 읽어라"라고 안내한다.
- 긴 When to use를 본문 맨 앞에 두지 않는다. 그건 description이 할 일이다.
- 스킬이 쓰는 도구(MCP, 스크립트, 브라우저 등)마다 **어떤 작업에 어떻게 쓰는지**를 적는다.
- 순서가 중요한 다단계 절차는 "`scripts/1.sh`를 실행하라"까지만 쓴다. 각 스크립트 출력이 다음 스크립트를 안내하고 실행 시각과 "N단계 완료"를 기록하게 만든다. 안정되면 `run.sh` 하나로 합친다.
- 업무 스킬의 본문 뼈대(4일차 3강): 공통 규칙 → 베스트 프랙티스 스니펫 → 작업 방식 → 기존 코드나 자료가 있을 때 지침(먼저 읽기, 중복이면 사람에게 묻기).
</body_rules>

<review_checklist>
점검할 때 아래를 하나씩 확인하고 결과를 표로 보고한다.
1. name 형식과 폴더 이름이 일치하나
2. description에 What·When이 있고 짧은가
3. 본문이 5천 토큰 이내이고 XML로 구역이 나뉘었나
4. 상세 내용이 references로 빠졌고, 언제 읽을지 안내가 있나
5. 결정적 작업이 scripts로 빠졌나
6. 쓰는 도구의 사용법이 적혀 있나
7. 트리거 평가용 요청 예시(불려야 할 것 3개, 불리면 안 될 것 3개)가 있나 → agent-eval로 넘긴다
</review_checklist>

<always_on>
항상 로드돼야 하는 스킬은 description 트리거에 맡기지 말고 SessionStart 훅으로 강제 로드한다. 이런 스킬은 트리거 평가에서 뺀다.
</always_on>
