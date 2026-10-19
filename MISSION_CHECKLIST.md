# 코디세이 미션 필수 요구사항 체크리스트

아래는 **필수 과제만** 정리한 체크리스트입니다. 코드 구현 상태와 실제 제출 전 확인 사항을 구분했습니다.

## 코드로 구현한 기능

- [x] Git 프로젝트 루트 검사
- [x] `git status` 및 `git diff` 결과 수집
- [x] 변경 사항이 없는 경우 안내 후 종료
- [x] `AI_API_KEY` 환경변수 사용 (키 하드코딩 없음)
- [x] OpenAI REST API 요청 및 응답 파싱
- [x] 인증/네트워크/API 응답 오류 안내
- [x] `--model`, `--temperature`, `--max-tokens` 옵션
- [x] `commit`: 변경 요약과 제목/본문 출력
- [x] `pr`: 제목과 Why/What/How to Test 섹션 출력
- [x] 커밋 제목 72자·PR 제목 80자 제한, PR 섹션 불릿 검증
- [x] `--safe-mode`: 기본적인 민감정보 마스킹과 diff 전송량 제한
- [x] API 호출 횟수 로그 (1회 실행당 최대 1회)
- [x] README 설치/실행/설정/출력/주의사항 문서화
- [x] API 호출 없이 실행하는 자동 테스트

## 제출 전에 직접 확인할 사항

- [ ] OpenAI API 키 및 결제/요청 한도 준비
- [ ] 추적 중인 파일을 수정해 실제 `commit` 생성 확인
- [ ] 같은 변경 사항으로 실제 `pr` 생성 확인
- [ ] API 키 누락 및 변경 사항 없음 동작 확인
- [ ] 출력 문구와 실제 코드 변경 사항이 일치하는지 검토
- [ ] GitHub 저장소에 push 후 파일 구조/README/커밋 기록 확인

## 실행 명령 요약

```bash
export AI_API_KEY="YOUR_OPENAI_API_KEY"
python3 main.py commit --safe-mode
python3 main.py pr --safe-mode
python3 -m unittest discover -s tests -v
```

**주의:** CLI가 Git 커밋이나 PR을 원격으로 작성하지 않습니다. 생성 텍스트를 직접 검토해 사용하세요.
