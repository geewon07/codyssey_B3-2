"""Read Git working-tree changes without modifying the repository."""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitError(Exception):
    """A Git precondition or command failed."""


@dataclass(frozen=True)
class Changes:
    status: str
    diff: str
    untracked_count: int

    @property
    def has_changes(self) -> bool:
        return bool(self.status.strip())


def _git(cwd: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=cwd, check=False, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=15,
        )
    except FileNotFoundError as exc:
        raise GitError("Git이 설치되어 있지 않거나 PATH에서 찾을 수 없습니다.") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError("Git 명령 실행 시간이 초과되었습니다.") from exc
    if result.returncode != 0:
        reason = (result.stderr or result.stdout).strip().splitlines()
        raise GitError(f"git {args[0]} 실패: {reason[0] if reason else '알 수 없는 오류'}")
    return result.stdout


def collect_changes(cwd: Path) -> Changes:
    if not (cwd / ".git").exists():
        raise GitError("현재 위치가 Git 프로젝트 루트가 아닙니다. .git이 있는 디렉토리에서 실행하세요.")
    status = _git(cwd, "status", "--short", "--untracked-files=normal").strip()
    if not status:
        return Changes(status="", diff="", untracked_count=0)

    # --cached: staged; plain diff: unstaged. Untracked files have no diff until git add.
    staged = _git(cwd, "diff", "--cached", "--no-ext-diff", "--no-color", "--unified=3", "--")
    unstaged = _git(cwd, "diff", "--no-ext-diff", "--no-color", "--unified=3", "--")
    diff = "\n".join(part.rstrip() for part in (staged, unstaged) if part.strip())
    untracked_count = sum(line.startswith("??") for line in status.splitlines())
    return Changes(status=status, diff=diff, untracked_count=untracked_count)


SENSITIVE_PATH = re.compile(
    r"(?i)(?:^|[/\\])(?:\.env(?:\.[^/\\\s\"]*)?|id_rsa(?:\.pub)?|"
    r"credentials(?:\.[^/\\\s\"]*)?|secrets?(?:\.[^/\\\s\"]*)?)"
    r"(?:$|[\s\"]|\s+b/)|\.(?:pem|p12|pfx|key)(?:$|[\s\"])",
)
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
API_TOKEN = re.compile(r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{16,}|AKIA[A-Z0-9]{16})\b")
BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{8,}")
ASSIGNMENT = re.compile(
    r"(?i)(\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|"
    r"client[_-]?secret|private[_-]?key|secret)\b\s*[:=]\s*[\"']?)"
    r"([^\s,\"'}#]{4,})"
)


def mask_sensitive(text: str) -> str:
    text = API_TOKEN.sub("[MASKED_TOKEN]", text)
    text = BEARER.sub("Bearer [MASKED_TOKEN]", text)
    text = ASSIGNMENT.sub(r"\1[MASKED]", text)
    return EMAIL.sub("[MASKED_EMAIL]", text)


def prepare_context(changes: Changes, safe_mode: bool) -> tuple[str, int, int, bool]:
    """Return context, included files, included lines and whether content was reduced.

    Security: well-known sensitive paths are always excluded. Safe mode further
    masks likely secret values and limits the diff's size.
    """
    chunks = re.split(r"(?=^diff --git )", changes.diff, flags=re.MULTILINE)
    patches = [part for part in chunks if part.startswith("diff --git ")]
    selected = []
    excluded = 0
    for patch in patches:
        header = patch.splitlines()[0]
        if SENSITIVE_PATH.search(header):
            excluded += 1
            continue
        selected.append(patch)

    truncated = bool(excluded)
    if safe_mode and len(selected) > 10:
        selected = selected[:10]
        truncated = True

    diff_text = "\n".join(selected)
    lines = diff_text.splitlines()
    if safe_mode and len(lines) > 200:
        lines = lines[:200]
        truncated = True
    if safe_mode:
        # Huge one-line blobs can exceed token budgets despite the line limit.
        cropped = []
        for line in lines:
            if len(line) > 500:
                cropped.append(line[:500] + " ...[줄 길이 제한으로 생략]")
                truncated = True
            else:
                cropped.append(line)
        lines = cropped
    diff_text = "\n".join(lines)
    if safe_mode:
        diff_text = mask_sensitive(diff_text)

    # Untracked files are deliberately omitted: Git doesn't provide a patch for them.
    status_lines = [line for line in changes.status.splitlines()
                    if not line.startswith("??") and not SENSITIVE_PATH.search(line)]
    status_text = "\n".join(status_lines)
    if safe_mode:
        status_text = mask_sensitive(status_text)
    context = f"Git status (추적 파일만):\n{status_text}\n\nGit diff:\n{diff_text}"
    if truncated:
        context += "\n\n[일부 변경은 보안/길이 제한으로 생략됨. 누락된 변경을 추측하지 마세요.]"
    return context, len(selected), len(lines), truncated
