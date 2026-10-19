"""Validate and print generated drafts with human-review markers."""
from __future__ import annotations

import re


def _title(value: object, limit: int) -> tuple[str, bool]:
    first_line = str(value).splitlines()[0].strip() if value is not None and str(value) else ""
    first_line = re.sub(r"^[#\s*-]+", "", first_line)
    if not first_line:
        raise ValueError("AI가 제목을 생성하지 않았습니다.")
    too_long = len(first_line) > limit
    return first_line[:limit].rstrip() if too_long else first_line, too_long


def _bullets(value: object, fallback: str) -> list[str]:
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = value.splitlines()
    else:
        items = []
    cleaned = [re.sub(r"^\s*(?:[-*]|\d+\.)\s*", "", str(item)).strip()
               for item in items]
    cleaned = [item for item in cleaned if item]
    return cleaned[:8] or [f"TODO: {fallback}"]


def format_result(command: str, response: dict) -> tuple[str, list[str]]:
    limit = 72 if command == "commit" else 80
    title, truncated = _title(response.get("title"), limit)
    warnings = []
    if truncated:
        warnings.append(f"제목이 {limit}자를 넘어 잘랐습니다. 의미가 유지되는지 직접 확인하세요.")
    if command == "commit" and len(title) > 50:
        warnings.append("커밋 제목이 권장 길이 50자를 초과했습니다.")
    summary = _bullets(response.get("summary"), "변경 요약을 확인하세요.")
    lines = ["\n--- Change Summary ---", *[f"- {b}" for b in summary]]

    if command == "commit":
        body = _bullets(response.get("body"), "변경 모듈과 핵심 내용을 작성하세요.")
        lines.extend(["\n--- Commit Message ---", title, "", *[f"- {b}" for b in body]])
        lines.append("----------------------")
    else:
        sections = (
            ("Why", "why", "변경 배경을 확인하세요."),
            ("What", "what", "주요 변경 내용을 확인하세요."),
            ("How to Test", "how_to_test", "실제 테스트 절차를 작성하세요."),
        )
        lines.extend(["\n--- PR Title ---", title, "\n--- PR Body ---"])
        for section, key, fallback in sections:
            bullets = _bullets(response.get(key), fallback)
            lines.extend([f"## {section}", *[f"- {b}" for b in bullets], ""])
        lines.append("----------------------")
    return "\n".join(lines), warnings
