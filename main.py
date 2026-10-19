"""Git 변경 내용으로 커밋 메시지 또는 PR 초안을 생성하는 CLI."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from ai_gitgen.ai_client import APIError, generate_json
from ai_gitgen.git_tools import GitError, collect_changes, prepare_context
from ai_gitgen.output import format_result
from ai_gitgen.prompts import SYSTEM_PROMPT, build_prompt


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Git 변경 내용으로 커밋 메시지/PR 초안을 생성합니다.")
    parser.add_argument("command", choices=("commit", "pr"), help="생성할 문서 종류")
    parser.add_argument("--model", default="gpt-4.1-mini", help="AI 모델 (기본: gpt-4.1-mini)")
    parser.add_argument("--temperature", type=float, default=0.2, help="0~2 (기본: 0.2)")
    parser.add_argument("--max-tokens", type=int, default=700, help="최대 생성 토큰 (기본: 700)")
    parser.add_argument("--safe-mode", action="store_true", help="민감정보 마스킹 및 diff 크기 제한")
    parser.add_argument("--reason", default="", help="변경 배경 (선택)")
    parser.add_argument("--requirements", default="", help="작업 요구사항 (선택)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    if not 0 <= args.temperature <= 2:
        parser.error("--temperature는 0~2여야 합니다.")
    if args.max_tokens < 100:
        parser.error("--max-tokens는 100 이상이어야 합니다.")

    try:
        changes = collect_changes(Path.cwd())
        if not changes.has_changes:
            print("[INFO] 변경 사항이 없습니다. 생성하지 않고 종료합니다.")
            print("[INFO] API 호출 횟수: 0")
            return 0
        print(f"[INFO] Git status 수집 완료: {len(changes.status.splitlines())}개 항목 감지")
        if changes.untracked_count:
            print(f"[WARN] 미추적 파일 {changes.untracked_count}개는 git add 전까지 diff에 포함되지 않습니다.")
        if not changes.diff.strip():
            print("[INFO] 전달할 Git diff가 없습니다. 추적 파일을 수정하거나 git add 후 재실행하세요.")
            print("[INFO] API 호출 횟수: 0")
            return 0

        context, files, lines, shortened = prepare_context(changes, args.safe_mode)
        if files == 0 or lines == 0:
            print("[INFO] 전송할 diff가 없습니다. 제외된 민감 파일을 확인하세요.")
            print("[INFO] API 호출 횟수: 0")
            return 0
        print(f"[INFO] Git diff 수집 완료: {files}개 파일 패치 / {lines}줄")
        if shortened:
            print("[WARN] 민감 파일 제외 또는 크기 제한으로 일부 diff가 생략되었습니다.")
        if not args.safe_mode:
            print("[WARN] 외부 API 전송 전 민감정보를 직접 확인하세요. --safe-mode 사용을 권장합니다.")

        api_key = os.getenv("AI_API_KEY")
        if not api_key:
            print('[ERROR] AI_API_KEY 환경변수가 없습니다. 예: export AI_API_KEY="YOUR_KEY"', file=sys.stderr)
            print("[INFO] API 호출 횟수: 0")
            return 1

        prompt = build_prompt(args.command, context, args.reason, args.requirements)
        print(f"[INFO] AI API 요청 중... (모델: {args.model})")
        try:
            generated = generate_json(api_key, args.model, args.temperature,
                                      args.max_tokens, SYSTEM_PROMPT, prompt)
        finally:
            print("[INFO] API 호출 횟수: 1")

        formatted, warnings = format_result(args.command, generated)
        for warning in warnings:
            print(f"[WARN] {warning}")
        print(f"[DONE] {'커밋 메시지' if args.command == 'commit' else 'PR 초안'} 생성 완료")
        print(formatted)
        print("[NOTE] 생성 결과를 직접 검토해 적용하세요. Git 명령으로 자동 반영하지 않습니다.")
        return 0
    except (GitError, APIError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
