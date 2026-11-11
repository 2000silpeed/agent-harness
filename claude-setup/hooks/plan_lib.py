#!/usr/bin/env python3
"""계획 게이트 공용 모듈: 계획 파일 읽기, 본문 해시, 경로 판정, 형식 검사, 승인 기록 대조.

plan_gate.py(실행 전 게이트), check_plan.py(형식 검사), approve_plan.py(사람의 승인)가
같은 규칙으로 판정하도록 한곳에 모았다. 표준 라이브러리만 쓴다(Python 3.9 이상).

용어:
    계획 파일: design/plans/<plan_id>.md. 머리말(`---` 사이의 `key: value`)과 본문으로 나뉜다.
    승인 기록: design/approvals/<plan_id>.json. approve_plan.py만 쓴다.
    본문 해시: 머리말을 뺀 본문의 SHA-256. 줄 끝 공백과 앞뒤 빈 줄은 무시한다.
    보호 경로: 계획의 수정 대상에 적혀 있어도 에이전트가 고칠 수 없는 경로.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

PLANS_DIR = "design/plans"
APPROVALS_DIR = "design/approvals"
STATUSES = ("draft", "in_review", "approved", "superseded", "done", "rejected")
RISKS = ("low", "medium", "high")

# 내장 보호 경로. 프로젝트별 추가분은 PROTECTED_LIST_FILE에 한 줄에 하나씩 적는다.
BUILTIN_PROTECTED = ("design/approvals/**", ".claude/hooks/**", ".claude/settings*.json")
PROTECTED_LIST_FILE = ".claude/hooks/protected_paths.txt"

REQUIRED_SECTIONS = (
    "요구사항", "범위", "완료 조건", "수정 대상", "작업 순서", "테스트 방법",
    "위험 표시", "가정·미결 질문", "참조 메모리·근거", "리뷰 이력",
)
MAY_BE_EMPTY = ("가정·미결 질문", "참조 메모리·근거", "리뷰 이력")
APPROVAL_KEYS = ("plan_id", "version", "plan_sha256", "reviewer_verdict", "approved_by", "approved_at")
LOCK_FILES = (
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "uv.lock",
    "Pipfile.lock", "Cargo.lock", "go.sum",
)
PLAN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class PlanError(ValueError):
    """계획 파일이나 승인 기록을 규칙대로 읽지 못했을 때 낸다."""


@dataclass(frozen=True)
class Plan:
    """읽어 들인 계획 파일 하나.

    Attributes:
        path: 계획 파일 경로.
        meta: 머리말의 key → value(문자열).
        body: 머리말 뒤의 본문.
    """

    path: Path
    meta: dict[str, str]
    body: str

    @property
    def plan_id(self) -> str:
        """머리말의 plan_id. 없으면 빈 문자열."""
        return self.meta.get("plan_id", "")

    @property
    def status(self) -> str:
        """머리말의 status. 없으면 빈 문자열."""
        return self.meta.get("status", "")

    @property
    def version(self) -> int | None:
        """머리말의 version. 1 이상의 정수가 아니면 None."""
        raw = self.meta.get("version", "")
        return int(raw) if raw.isdigit() and int(raw) >= 1 else None

    @property
    def sha256(self) -> str:
        """본문 해시."""
        return body_sha256(self.body)


# ── 프로젝트 루트 ────────────────────────────────────────────────────────────

def project_root() -> Path:
    """프로젝트 루트를 정한다.

    순서: 환경 변수 CLAUDE_PROJECT_DIR → 이 파일이 `<루트>/.claude/hooks/`에 있으면 그 루트 → 현재 폴더.

    Returns:
        심볼릭 링크를 푼 절대 경로.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve().parent
    if here.name == "hooks" and here.parent.name == ".claude":
        return here.parent.parent
    return Path.cwd().resolve()


# ── 계획 파일 읽기 ───────────────────────────────────────────────────────────

def parse_plan_text(text: str) -> tuple[dict[str, str], str]:
    """계획 파일 내용을 머리말과 본문으로 나눈다.

    Args:
        text: 계획 파일 전체 내용.

    Returns:
        (머리말 dict, 본문 문자열).

    Raises:
        PlanError: 머리말이 없거나 닫히지 않았거나, 같은 키가 두 번 나오면.
    """
    lines = text.replace("\r\n", "\n").lstrip("﻿").split("\n")
    if lines[0].strip() != "---":
        raise PlanError("첫 줄이 머리말 시작(---)이 아닙니다")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise PlanError("머리말을 닫는 --- 줄이 없습니다") from None
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        line = line.split(" #", 1)[0].strip()  # 줄 끝 주석은 버린다
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        key = key.strip()
        if not sep or not key:
            raise PlanError(f"머리말 줄을 읽지 못했습니다: {line!r}")
        if key in meta:
            raise PlanError(f"머리말에 '{key}'가 두 번 나옵니다")
        meta[key] = value.strip().strip("'\"")
    return meta, "\n".join(lines[end + 1:])


def read_plan(path: Path) -> Plan:
    """계획 파일 하나를 읽는다.

    Raises:
        PlanError: 머리말 형식이 틀리면.
        OSError: 파일을 읽지 못하면.
    """
    meta, body = parse_plan_text(path.read_text(encoding="utf-8"))
    return Plan(path=path, meta=meta, body=body)


def list_plans(root: Path) -> tuple[list[Plan], list[str]]:
    """design/plans/*.md를 모두 읽는다.

    Args:
        root: 프로젝트 루트.

    Returns:
        (읽은 계획 목록, 읽지 못한 파일 설명 목록). 읽지 못한 계획은 승인된 것으로 치지 않는다.
    """
    plans: list[Plan] = []
    unreadable: list[str] = []
    for path in sorted((root / PLANS_DIR).glob("*.md")):
        try:
            plans.append(read_plan(path))
        except PlanError as exc:
            unreadable.append(f"{path.name}({exc})")
    return plans, unreadable


def body_sha256(body: str) -> str:
    """본문 해시를 계산한다. 줄 끝 공백과 앞뒤 빈 줄 차이는 같은 본문으로 본다."""
    normalized = "\n".join(line.rstrip() for line in body.replace("\r\n", "\n").split("\n")).strip("\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def with_status(text: str, status: str) -> str:
    """계획 파일 내용에서 머리말의 status 줄만 바꾼 새 내용을 돌려준다(본문은 그대로다).

    Raises:
        PlanError: 머리말에 status 줄이 없으면.
    """
    lines = text.split("\n")
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), len(lines))
    for i in range(1, closing):
        if re.match(r"^\s*status\s*:", lines[i]):
            lines[i] = f"status: {status}"
            return "\n".join(lines)
    raise PlanError("머리말에 status 줄이 없습니다")


# ── 본문 구역 ────────────────────────────────────────────────────────────────

def section_key(title: str) -> str:
    """구역 제목을 비교용 키로 바꾼다(공백·가운뎃점 같은 기호를 뺀다)."""
    return re.sub(r"[\W_]+", "", title).lower()


def split_sections(body: str) -> dict[str, str]:
    """본문을 `## 제목` 단위로 나눈다. 코드 블록 안의 `##`는 제목으로 보지 않는다.

    Returns:
        구역 키(section_key) → 구역 내용.

    Raises:
        PlanError: 같은 구역이 두 번 나오면(어느 쪽을 믿을지 정할 수 없다).
    """
    found: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else re.match(r"^##\s+(.*\S)\s*$", line)
        if match:
            current = section_key(match.group(1))
            if current in found:
                raise PlanError(f"구역이 두 번 나옵니다: '## {match.group(1)}'")
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in found.items()}


def table_rows(section_text: str) -> list[list[str]]:
    """구역 안 마크다운 표의 데이터 행을 칸 목록으로 돌려준다(머리 행과 구분선은 뺀다)."""
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in section_text.split("\n") if line.strip().startswith("|")
    ]
    return [row for row in rows[1:] if not set("".join(row)) <= set("-: ")]


# ── 수정 대상과 보호 경로 ────────────────────────────────────────────────────

def scope_entries(body: str) -> list[str]:
    """`## 수정 대상` 표의 첫 칸(저장소 기준 상대 경로)을 모은다.

    Raises:
        PlanError: 구역이 없으면.
    """
    section = split_sections(body).get(section_key("수정 대상"))
    if section is None:
        raise PlanError("'## 수정 대상' 구역이 없습니다")
    return [row[0].strip("`").strip() for row in table_rows(section) if row and row[0].strip("`").strip()]


def scope_entry_problem(entry: str) -> str | None:
    """수정 대상 한 줄의 경로 형식을 검사한다.

    허용: 저장소 기준 상대 경로. 끝에 `/*`(폴더 바로 아래 파일) 또는 `/**`(폴더 아래 전부)를 붙일 수 있다.

    Returns:
        문제가 없으면 None, 있으면 이유.
    """
    base = _strip_wildcard(entry)
    if any(unicodedata.category(ch)[0] in "CZ" for ch in entry):
        return "공백이나 보이지 않는 문자가 들어 있습니다"
    if not base:
        return "폴더 이름 없이 와일드카드만 쓸 수 없습니다"
    if base.startswith(("/", "~")) or "\\" in base or re.match(r"^[A-Za-z]:", base):
        return "저장소 기준 상대 경로(슬래시 구분)로 적습니다"
    if any(part in ("", ".", "..") for part in base.split("/")):
        return "'.', '..', 빈 구간, 끝 슬래시는 쓸 수 없습니다(폴더 전체는 'dir/**')"
    if any(ch in base for ch in "*?[]"):
        return "와일드카드는 끝의 '/*' 또는 '/**' 하나만 쓸 수 있습니다"
    return None


def path_matches(rel: str, pattern: str) -> bool:
    """저장소 기준 경로가 패턴에 드는지 본다.

    Args:
        rel: 저장소 기준 상대 경로(슬래시 구분).
        pattern: 정확한 경로, `dir/*`(바로 아래 파일), `dir/**`(아래 전부), 그 밖에는 fnmatch 패턴.
    """
    if pattern.endswith("/**"):
        base = pattern[:-3]
        return rel == base or rel.startswith(base + "/")
    if pattern.endswith("/*"):
        base = pattern[:-2]
        return rel.startswith(base + "/") and "/" not in rel[len(base) + 1:]
    return fnmatch.fnmatchcase(rel, pattern)


def in_scope(rel: str, entries: list[str]) -> bool:
    """경로가 수정 대상 중 하나에 드는지 본다."""
    return any(path_matches(rel, entry) for entry in entries)


def protected_patterns(root: Path) -> tuple[str, ...]:
    """내장 보호 경로에 PROTECTED_LIST_FILE의 줄(빈 줄과 # 주석 제외)을 더해 돌려준다."""
    extra: list[str] = []
    listing = root / PROTECTED_LIST_FILE
    if listing.is_file():
        for line in listing.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                extra.append(line)
    return BUILTIN_PROTECTED + tuple(extra)


def is_protected(rel: str, patterns: tuple[str, ...]) -> bool:
    """경로가 보호 경로인지 본다. 대소문자를 가리지 않는 파일 시스템을 고려해 소문자로 맞춰 비교한다."""
    return any(path_matches(rel.casefold(), pattern.casefold()) for pattern in patterns)


def covers_protected(entry: str, patterns: tuple[str, ...]) -> bool:
    """수정 대상 한 줄이 보호 경로이거나 보호 경로를 품는 폴더 와일드카드인지 본다."""
    base = _strip_wildcard(entry).casefold()
    if is_protected(base, patterns):
        return True
    if base == entry.casefold():  # 와일드카드가 없는 정확한 경로
        return False
    for pattern in patterns:
        literal = re.split(r"[*?\[]", pattern.casefold(), maxsplit=1)[0].rstrip("/")
        if literal == base or literal.startswith(base + "/"):
            return True
    return False


def _strip_wildcard(entry: str) -> str:
    """끝의 `/**`, `/*`를 뗀 경로를 돌려준다."""
    for suffix in ("/**", "/*"):
        if entry.endswith(suffix):
            return entry[: -len(suffix)]
    return entry


# ── 형식 검사 ────────────────────────────────────────────────────────────────

def format_problems(plan: Plan, root: Path) -> list[str]:
    """계획의 형식을 검사한다(draft → in_review로 넘어가기 전의 형식 게이트).

    내용이 옳은지는 보지 않는다. 그것은 리뷰어와 사람의 몫이다.

    Args:
        plan: 읽은 계획.
        root: 프로젝트 루트(보호 경로 목록을 읽는 데 쓴다).

    Returns:
        문제 설명 목록. 비어 있으면 통과.
    """
    problems: list[str] = []
    problems += _meta_problems(plan)
    try:
        sections = split_sections(plan.body)
    except PlanError as exc:
        return problems + [str(exc)]

    def text_of(name: str) -> str:
        return sections.get(section_key(name), "")

    for name in REQUIRED_SECTIONS:
        if section_key(name) not in sections:
            problems.append(f"'## {name}' 구역이 없습니다")
        elif name not in MAY_BE_EMPTY and not text_of(name):
            problems.append(f"'## {name}' 구역이 비어 있습니다")

    requirements = sorted(set(re.findall(r"\bR\d+\b", text_of("요구사항"))))
    if text_of("요구사항"):
        if not re.search(r"(?m)^\s*>", text_of("요구사항")):
            problems.append("요구사항: 사용자 요청 원문 인용(> 로 시작하는 줄)이 없습니다")
        if not requirements:
            problems.append("요구사항: 번호 붙인 요구(R1, R2 …)가 없습니다")
    if text_of("범위"):
        out = re.search(r"(?is)\bout\b\W*(.*)", text_of("범위"))
        if not re.search(r"(?i)\bin\b", text_of("범위")) or not out or not out.group(1).strip():
            problems.append("범위: In과 Out이 모두 있어야 하고 Out(하지 않는 것)이 1개 이상이어야 합니다")
    if text_of("완료 조건"):
        problems += _criteria_problems(text_of("완료 조건"), requirements)
    if text_of("수정 대상"):
        problems += _scope_problems(plan, root, text_of("위험 표시"))
    if text_of("작업 순서") and not re.search(r"(?m)^\s*\d+[.)]\s+\S", text_of("작업 순서")):
        problems.append("작업 순서: 번호 목록(1. 2. …)이 없습니다")
    if text_of("테스트 방법") and "`" not in text_of("테스트 방법"):
        problems.append("테스트 방법: 실행할 명령(`명령` 또는 코드 블록)이 없습니다")
    if text_of("위험 표시") and not _says_none(text_of("위험 표시")) and plan.meta.get("risk") == "low":
        problems.append("위험 표시에 항목이 있으면 머리말 risk는 medium 이상이어야 합니다")
    if plan.status == "done" and not text_of("실행 결과"):
        problems.append("status가 done이면 '## 실행 결과'에 완료 조건별 실제 관찰이 있어야 합니다")
    return problems


def _meta_problems(plan: Plan) -> list[str]:
    """머리말 필수 키를 검사한다."""
    problems: list[str] = []
    if not PLAN_ID_PATTERN.match(plan.plan_id):
        problems.append("머리말 plan_id가 없거나 형식이 틀립니다(영문·숫자·'.', '_', '-')")
    elif plan.plan_id != plan.path.stem:
        problems.append(f"머리말 plan_id('{plan.plan_id}')가 파일 이름('{plan.path.stem}')과 다릅니다")
    if plan.version is None:
        problems.append("머리말 version은 1 이상의 정수여야 합니다")
    if plan.status not in STATUSES:
        problems.append(f"머리말 status는 {' | '.join(STATUSES)} 중 하나여야 합니다")
    if plan.meta.get("risk") not in RISKS:
        problems.append(f"머리말 risk는 {' | '.join(RISKS)} 중 하나여야 합니다")
    return problems


def _criteria_problems(section_text: str, requirements: list[str]) -> list[str]:
    """완료 조건 표를 검사한다: C번호, 확인 명령, 모든 요구(R)의 대응."""
    problems: list[str] = []
    rows = table_rows(section_text)
    if not rows:
        return ["완료 조건: 표(C번호 | 조건 | 대응 R | 확인 명령 | 기대 관찰)가 없습니다"]
    for row in rows:
        label = row[0] if row else "?"
        if not re.fullmatch(r"C\d+", label):
            problems.append(f"완료 조건: 첫 칸은 C번호여야 합니다('{label}')")
        elif len(row) < 5 or not row[3] or not row[4]:
            problems.append(f"완료 조건 {label}: 확인 명령이나 기대 관찰 칸이 비어 있습니다")
    mapped = set(re.findall(r"\bR\d+\b", section_text))
    missing = [req for req in requirements if req not in mapped]
    if missing:
        problems.append(f"완료 조건: 대응하는 조건이 없는 요구가 있습니다({', '.join(missing)})")
    return problems


def _scope_problems(plan: Plan, root: Path, risk_text: str) -> list[str]:
    """수정 대상 표를 검사한다: 경로 형식, 보호 경로, 테스트·잠금 파일의 위험 표시."""
    problems: list[str] = []
    entries = scope_entries(plan.body)
    if not entries:
        return ["수정 대상: 표(경로 | 수정·신규·삭제 | 이유)에 행이 없습니다"]
    patterns = protected_patterns(root)
    for entry in entries:
        reason = scope_entry_problem(entry)
        if reason:
            problems.append(f"수정 대상 '{entry}': {reason}")
        elif covers_protected(entry, patterns):
            problems.append(f"수정 대상 '{entry}': 보호 경로는 계획에 넣을 수 없습니다(사람이 직접 고친다)")
    sensitive = [entry for entry in entries if _is_test_or_lock(entry)]
    if sensitive and _says_none(risk_text):
        problems.append(f"수정 대상에 테스트·잠금 파일이 있는데 위험 표시가 '없음'입니다({', '.join(sensitive)})")
    return problems


def _says_none(text: str) -> bool:
    """구역 내용이 '없음' 한마디인지 본다."""
    return section_key(text) == "없음"


def _is_test_or_lock(entry: str) -> bool:
    """경로가 테스트 파일이나 의존성 잠금 파일로 보이는지 이름 규칙으로 판단한다."""
    parts = _strip_wildcard(entry).split("/")
    name = parts[-1]
    if name in LOCK_FILES:
        return True
    in_test_dir = any(part in ("test", "tests", "__tests__", "spec") for part in parts)
    return in_test_dir or name.startswith("test_") or bool(re.search(r"(_test|\.test|\.spec)\.\w+$", name))


def review_verdict(plan: Plan) -> str | None:
    """`## 리뷰 이력`에서 현재 version의 마지막 판정을 찾는다.

    줄 형식 예: `- v2: APPROVE — V5 반영(단계 3에 확인 명령 추가)`.

    Returns:
        "APPROVE", "REVISE" 또는 판정 줄이 없으면 None.
    """
    history = split_sections(plan.body).get(section_key("리뷰 이력"), "")
    verdicts = re.findall(rf"(?m)^\W*v{plan.version}\b.*?\b(APPROVE|REVISE)\b", history)
    return verdicts[-1] if verdicts else None


# ── 승인 기록 ────────────────────────────────────────────────────────────────

def approval_path(root: Path, plan_id: str) -> Path:
    """승인 기록 파일 경로."""
    return root / APPROVALS_DIR / f"{plan_id}.json"


def read_approval(root: Path, plan_id: str) -> dict | None:
    """승인 기록을 읽는다.

    Returns:
        기록 dict. 파일이 없으면 None.

    Raises:
        PlanError: JSON 객체가 아니거나 필수 키가 빠졌으면.
    """
    path = approval_path(root, plan_id)
    if not path.is_file():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        raise PlanError("승인 기록이 JSON이 아닙니다") from None
    if not isinstance(record, dict) or any(key not in record for key in APPROVAL_KEYS):
        raise PlanError(f"승인 기록에 빠진 키가 있습니다({', '.join(APPROVAL_KEYS)})")
    return record


def approval_problem(root: Path, plan: Plan) -> tuple[str, str] | None:
    """계획에 유효한 승인 기록이 있는지 대조한다.

    확인: 기록이 있다, 키가 모두 있다, plan_id·version이 같다, 기록의 해시가 지금 본문 해시와 같다,
    리뷰 판정이 APPROVE다, 승인자가 적혀 있다.

    Returns:
        유효하면 None. 아니면 (규칙 ID, 이유).
    """
    if not PLAN_ID_PATTERN.match(plan.plan_id) or plan.plan_id != plan.path.stem:
        return "plan.approval_record_invalid", "머리말 plan_id가 파일 이름과 다릅니다"
    try:
        record = read_approval(root, plan.plan_id)
    except PlanError as exc:
        return "plan.approval_record_invalid", str(exc)
    if record is None:
        return "plan.approval_record_missing", f"승인 기록({APPROVALS_DIR}/{plan.plan_id}.json)이 없습니다"
    if record["plan_id"] != plan.plan_id:
        return "plan.approval_record_invalid", "승인 기록의 plan_id가 계획과 다릅니다"
    if record["reviewer_verdict"] != "APPROVE" or not isinstance(record["approved_by"], str) or not record["approved_by"]:
        return "plan.approval_record_invalid", "승인 기록에 리뷰 판정(APPROVE)이나 승인자가 없습니다"
    if type(record["version"]) is not int or record["version"] != plan.version:
        return "plan.approval_stale", f"승인 기록은 v{record['version']}인데 계획은 v{plan.meta.get('version')}입니다"
    if record["plan_sha256"] != plan.sha256:
        return "plan.approval_stale", "승인 뒤 계획 본문이 바뀌었습니다(해시 불일치)"
    return None
