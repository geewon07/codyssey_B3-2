# 코디세이 B3-2 — 필수 과제 체크리스트

**과제:** 내가 수정한 코드 설명을 AI가 대신 써주는 도우미 만들기  
**프로젝트:** AI GitGen (Python CLI)  
**GitHub:** https://github.com/geewon07/codyssey_B3-2

## 1. Git 변경 사항 수집

- [x] Git 저장소의 프로젝트 루트에서 CLI 실행
- [x] `git status`를 통해 변경된 파일 목록 수집
- [x] `git diff`로 변경 내용 수집 (staged/unstaged 변경 대응)
- [x] 변경 사항이 없는 경우 안내 메시지를 출력하고 API 호출 없이 종료
- [x] 아직 `git add`하지 않은 새 파일은 diff에 포함되지 않는다는 점 안내

## 2. AI API 연동

- [x] 실제 API 키를 코드에 하드코딩하지 않고 `AI_API_KEY` 환경변수에서 읽기
- [x] 코디세이 COPA의 OpenAI 호환 REST API 호출
- [x] API 엔드포인트: `https://copa.codyssey.kr/v1/chat/completions`
- [x] 기본 모델: `gpt-5-mini`
- [x] `--model`, `--temperature`, `--max-tokens` CLI 옵션 제공
- [x] 기본 최대 생성 토큰 수: `3000`
- [x] GPT-5 계열 요청 시 지원되지 않을 수 있는 `temperature` 필드 제외
- [x] COPA에서 오류가 발생했던 `response_format` 필드를 제외하고 프롬프트로 JSON 출력을 요청한 뒤 응답 파싱
- [x] API 키 누락, 인증/요청 오류, 네트워크 문제, 비정상 응답에 대한 오류 처리
- [x] CLI 명령 1회당 AI API 최대 1회 호출 및 호출 횟수 표시
- [x] 실제 COPA API 연결 확인 (`HTTP 200`)

## 3. 커밋 메시지 자동 생성

- [x] `python3 main.py commit --safe-mode` 명령 제공
- [x] Git 변경 내용을 바탕으로 변경 요약 및 커밋 메시지 생성
- [x] 커밋 제목 1줄 포함, 본문에 변경 파일/핵심 변경 사항 정리
- [x] 제목 최대 72자 제한(50자 이내 권장) 검사
- [x] 결과를 터미널에 구분선과 헤더로 출력
- [x] **실제 COPA API 호출로 커밋 메시지 생성 성공 확인**

## 4. PR 제목·본문 자동 생성

- [x] `python3 main.py pr --safe-mode` 명령 제공
- [x] PR 제목 1줄 및 본문 초안 출력
- [x] PR 제목 최대 80자 검사
- [x] `## Why`, `## What`, `## How to Test` 섹션 포함
- [x] 각 섹션에 불릿 최소 1개 포함되도록 검증/보완
- [x] 결과를 터미널에 구분선과 헤더로 출력
- [x] **실제 COPA API 호출로 PR 초안 생성 성공 확인**

## 5. 안전성 및 문서화

- [x] `.gitignore`로 `.env`, 가상환경, 캐시 및 주요 키 파일 제외
- [x] `--safe-mode`로 대표적 민감정보 마스킹 및 diff 전송량 제한
- [x] Safe Mode의 기본 전송 제한: 최대 10개 파일 / 200줄
- [x] 생성 문구는 사용자가 검토 후 적용하도록 안내
- [x] 프로그램에서는 실제 `git commit`, `git push`, GitHub PR 등록을 자동 실행하지 않음
- [x] `README.md`에 설치·실행 방법, API 키 환경변수 설정, 명령어·출력 예시, 주의사항 작성
- [x] README를 코디세이 COPA 엔드포인트와 실제 기본 모델 설정에 맞게 수정

## 6. 테스트 및 GitHub 제출 확인

- [x] Python 문법 검사 실행 (`python3 -m py_compile ai_gitgen/ai_client.py`)
- [x] 오프라인 자동 테스트 8개 통과 (`python3 -m unittest discover -s tests -v`)
- [x] `git diff --check` 경고 수정
- [x] 실제 `commit` 명령으로 생성 결과 확인
- [x] 실제 `pr` 명령으로 생성 결과 확인
- [x] AI가 작성한 메시지의 내용을 검토하고 최종 커밋 문구에 반영
- [x] GitHub 원격 저장소 연결 및 프로젝트 push 수행
- [x] `README.md`, 소스 코드, 테스트 코드, `.gitignore`를 저장소에 포함

## 실행 명령어

```bash
# 코디세이에서 발급한 키를 현재 터미널 환경변수에 설정
export AI_API_KEY="YOUR_CODYSSEY_API_KEY"

# 커밋 메시지 생성
python3 main.py commit --safe-mode

# PR 제목과 본문 생성
python3 main.py pr --safe-mode

# 자동 테스트
python3 -m unittest discover -s tests -v
```

**주의사항:** API 키는 GitHub에 올리거나 README·소스 코드에 기록하지 않습니다. `commit` 및 `pr` 명령은 **초안만 출력**하며, 생성된 테스트 방법이나 변경 설명이 사실과 일치하는지는 사용자가 확인해야 합니다. 변경 사항이 없는 깨끗한 작업 트리에서는 생성 없이 종료하는 것이 정상입니다.
