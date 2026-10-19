# AI GitGen — Git 변경 사항 기반 커밋/PR 초안 생성기

Python 3.10 이상에서 실행하는 CLI 도구입니다. Git 변경 사항을 수집하고 OpenAI REST API를 한 번 호출해 **커밋 메시지 또는 PR 제목·본문 초안**을 터미널에 출력합니다. 실제 커밋, push, PR 등록은 하지 않습니다.

## 1. 주요 기능

- `git status --short`로 변경 파일 목록 수집
- `git diff --cached`와 `git diff`로 staged/unstaged 변경 수집
- `commit`: 변경 요약, 커밋 제목(최대 72자), 선택 본문 출력
- `pr`: 변경 요약, PR 제목(최대 80자), `Why` / `What` / `How to Test` 섹션 출력
- `--model`, `--temperature`, `--max-tokens` 옵션으로 API 요청 파라미터 변경
- `--reason`, `--requirements` 옵션으로 변경 배경·요구사항 입력
- `--safe-mode`: 키·이메일 마스킹 및 입력 diff 최대 10개 파일·200줄 제한
- API 키 미설정, 네트워크 오류, 인증 실패, 잘못된 API 응답 등 예외 처리
- 요청 횟수 출력(명령 1회당 최대 1회)

## 2. 프로젝트 구조

```text
ai-gitgen/
├── main.py                 # CLI 진입점과 실행 흐름
├── ai_gitgen/
│   ├── __init__.py
│   ├── git_tools.py        # Git 변경 정보 수집과 safe-mode 처리
│   ├── prompts.py          # 커밋/PR 프롬프트 구성
│   ├── ai_client.py        # OpenAI REST API 요청·응답·오류 처리
│   └── output.py           # 생성 결과 길이·형식 검증 및 출력
├── tests/
│   └── test_tool.py        # 오프라인 자동 테스트
├── .env.example
├── .gitignore
├── requirements.txt
├── MISSION_CHECKLIST.md
└── README.md
```

## 3. 설치 및 API 키 설정

**필요한 것:** Python 3.10+, Git, OpenAI API 키. Python 표준 라이브러리만 사용하므로 외부 패키지는 설치할 필요가 없습니다. ChatGPT Plus와 OpenAI API 결제는 별개입니다.

프로젝트 압축 파일을 풀고 **Git 저장소 루트**로 이동합니다.

```bash
cd ai-gitgen
# 아직 Git 저장소가 아니라면 최초 한 번만 실행
git init
git add .
git commit -m "chore: initial commit"
```

이후 코드나 README의 **추적 중인 파일을 한 번 수정**해야 diff가 생깁니다. 새 파일만 만들었다면 `git add 파일명`을 해야 diff에 포함됩니다.

macOS / Linux:

```bash
export AI_API_KEY="YOUR_OPENAI_API_KEY"
```

Windows PowerShell:

```powershell
$env:AI_API_KEY="YOUR_OPENAI_API_KEY"
```

API 키는 `.py`, `.env.example`, README, Git에 기록하지 마세요. 환경변수로만 입력하세요.

## 4. 사용법

```bash
# 커밋 메시지 초안 생성
python3 main.py commit --safe-mode

# PR 제목/본문 초안 생성
python3 main.py pr --safe-mode

# 요청 파라미터 지정
python3 main.py commit --model gpt-4.1-mini --temperature 0.2 --max-tokens 700 --safe-mode

# 변경 이유·요구사항 전달
python3 main.py pr --reason "에러 처리 개선" --requirements "인증 실패 안내 추가" --safe-mode

# 옵션 확인
python3 main.py --help
```

- `--model`: API 모델 이름, 기본 `gpt-4.1-mini`
- `--temperature`: 결과의 다양성에 영향을 주는 파라미터, 기본 `0.2` (0~2)
- `--max-tokens`: 최대 출력 토큰, 기본 `700` (API 요청 시 `max_completion_tokens`로 전달)
- `--safe-mode`: diff에 포함된 대표적인 이메일/토큰/비밀값을 마스킹하고, 최대 파일 10개·200줄까지만 전송

다른 모델 사용 시 모델이 JSON 형식 응답, temperature, 출력 토큰 파라미터를 지원하는지 확인해야 합니다.

## 5. 출력 예시

**커밋 생성:**

```text
[INFO] Git status 수집 완료: 2개 항목 감지
[INFO] Git diff 수집 완료: 2개 파일 패치 / 43줄
[INFO] AI API 요청 중... (모델: gpt-4.1-mini)
[INFO] API 호출 횟수: 1
[DONE] 커밋 메시지 생성 완료

--- Change Summary ---
- Git 변경 내용 수집 로직 추가

--- Commit Message ---
feat: Git 변경 기반 커밋 메시지 생성

- git_tools.py에서 변경 내용 수집
- main.py에서 CLI 옵션 처리
----------------------
```

**PR 생성:**

```text
--- Change Summary ---
- Git 변경 사항을 분석해 PR 초안을 생성

--- PR Title ---
feat: Git 변경 기반 PR 초안 생성

--- PR Body ---
## Why
- 변경 이력을 읽기 쉽게 정리할 필요가 있었습니다.

## What
- git status, git diff 결과를 API 입력에 연결했습니다.
- PR 제목과 본문 템플릿을 적용했습니다.

## How to Test
- python3 main.py pr --safe-mode 실행 후 출력 확인
- Why/What/How to Test 섹션과 불릿 구성 확인
----------------------
```

**변경 사항 없음:**

```text
[INFO] 변경 사항이 없습니다. 생성하지 않고 종료합니다.
[INFO] API 호출 횟수: 0
```

**API 키 없음:**

```text
[ERROR] AI_API_KEY 환경변수가 없습니다. 예: export AI_API_KEY="YOUR_KEY"
[INFO] API 호출 횟수: 0
```

## 6. 검증 기준과 주의사항

- 커밋 제목은 50자 이내 권장, 최대 72자이며 PR 제목은 최대 80자입니다. 초과하면 잘라내고 경고합니다.
- PR 본문에 `## Why`, `## What`, `## How to Test`가 있어야 하고 각각 불릿이 최소 1개 있어야 합니다. 누락 시 `TODO` 불릿을 넣습니다.
- 안전 모드에서도 모든 비밀을 찾을 수 있는 것은 아닙니다. 특히 회사 코드, 개인정보, 비밀번호가 포함된 diff는 외부 API 전송 전에 반드시 직접 확인해야 합니다. `.env`, 비밀 키 파일 등 알려진 민감 파일은 기본적으로 제외됩니다.
- API 요청은 명령당 최대 1회이며 자동 재시도하지 않습니다. API 사용량과 비용을 확인하세요.
- `git diff`에는 아직 `git add`하지 않은 새 파일이 포함되지 않습니다.
- 생성된 테스트 방법은 **테스트 완료를 의미하지 않습니다.** 실제로 실행해보고 내용을 확인하세요.
- 현재 작업 트리의 변경 사항을 사용하므로 **커밋하기 전에** 초안을 생성하는 방식입니다.

## 7. 자동 테스트

실제 API 통신 없이 테스트를 실행할 수 있습니다.

```bash
python3 -m unittest discover -s tests -v
```

실제 연동 검증은 API 키를 설정하고 추적 파일을 수정한 뒤 `python3 main.py commit --safe-mode` 및 `python3 main.py pr --safe-mode`를 실행합니다.

## 8. GitHub 업로드

GitHub에서 빈 저장소를 만든 다음 로컬 프로젝트 루트에서 실행하세요.

```bash
git add .
git commit -m "feat: Git 변경 기반 AI 초안 생성기 구현"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-gitgen.git
git push -u origin main
```

원격 저장소 주소는 본인 주소로 변경합니다. 이미 `origin`을 등록했다면 `git remote add origin`은 다시 실행하지 마세요. 업로드는 사람이 터미널에서 수행하며, 프로그램은 push하지 않습니다.

## 9. 설명할 수 있어야 하는 핵심

- **Git status와 Git diff의 차이:** status는 변경된 파일 목록, diff는 파일 내부에서 바뀐 줄을 보여줍니다.
- **API 호출 흐름:** 환경변수에서 키를 읽고 JSON 요청을 보내며 응답을 파싱하고 오류를 처리합니다.
- **temperature와 출력 토큰:** temperature는 생성 다양성, max-tokens는 응답 길이에 영향을 줍니다.
- **프롬프트 설계:** 변경 이유와 요구사항, Git 데이터를 함께 전달하고 커밋/PR 결과 형식을 지시합니다.
- **결과 검증:** AI 출력을 그대로 믿지 않고 제목 길이와 PR 섹션을 Python에서 확인합니다.
- **안전 모드:** 외부 API에 Git 변경 내역을 전송하기 전에 일부 민감정보를 가리고 전송량을 제한합니다.

**참고:** [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat/create) · [API 키 관리](https://platform.openai.com/api-keys)
