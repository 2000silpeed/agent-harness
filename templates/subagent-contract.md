# 서브에이전트 계약

## 넘기는 것 (Supervisor → Worker)
```json
{"task_id": "T-001", "goal": "…", "facts": ["…"], "allowed_tools": ["Read", "Grep"], "output_path": "work/T-001/result.md"}
```

## 돌려받는 것 (Worker → Supervisor)
```json
{"status": "완료 | 미확정 | 실패", "facts": ["…"], "evidence_refs": ["path:line", "url"], "uncertainty": ["…"], "output_path": "work/T-001/result.md"}
```

## 규칙
- 나누는 기준은 페르소나가 아니라 **Context 경계**입니다. Worker에는 필요한 정보만 줍니다.
- 긴 결과는 `output_path` 파일에 쓰고, 메인에는 요약과 경로만 돌려줍니다.
- Worker끼리 직접 통신하지 않습니다. 모든 결과는 Supervisor를 거칩니다.
- 짧은 요약만 받지 말고 **사실, 근거, 불확실성**을 함께 받습니다.
- 권한은 Context 분리와 별개로 `allowed_tools`로 제한합니다.
