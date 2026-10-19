"""One REST request per CLI invocation, using Python's standard library."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

API_ENDPOINT = "https://copa.codyssey.kr/v1/chat/completions"


class APIError(Exception):
    """A model API error safe to show in the terminal."""


def generate_json(api_key: str, model: str, temperature: float,
                  max_tokens: int, system: str, prompt: str) -> dict:
    payload = {
        "model": model,
        "max_completion_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    # GPT-5 계열에서는 temperature를 전달하지 않음
    if not model.startswith("gpt-5"):
        payload["temperature"] = temperature

    request = urllib.request.Request(
        API_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        reason = {
            400: "요청 형식 또는 모델 파라미터를 확인하세요.",
            401: "API 키가 유효한지 확인하세요.",
            403: "모델 접근 권한을 확인하세요.",
            404: "모델 이름 또는 API 주소를 확인하세요.",
            429: "요청 한도 또는 잔여 크레딧을 확인하세요.",
        }.get(exc.code, "서비스 상태를 확인하세요.")
        raise APIError(f"HTTP {exc.code}: {reason}") from exc
    except urllib.error.URLError as exc:
        raise APIError(f"네트워크 연결 실패: {exc.reason}") from exc
    except TimeoutError as exc:
        raise APIError("API 호출 시간 초과") from exc
    except (ValueError, UnicodeError) as exc:
        raise APIError("API 응답을 JSON으로 읽지 못했습니다.") from exc

    try:
        choice = result["choices"][0]
        if choice.get("finish_reason") == "length":
            raise APIError("응답 길이 제한으로 생성이 잘렸습니다. --max-tokens를 늘려 주세요.")
        content = choice["message"]["content"]
        output = json.loads(content)
        if not isinstance(output, dict):
            raise ValueError("not a JSON object")
        return output
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise APIError("예상과 다른 API 응답입니다. 모델/출력 형식을 확인하세요.") from exc
