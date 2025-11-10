# BudgetOps AI

클라우드 서비스 제공자(CSP) 리소스에 대해 Rule 기반으로 최적화 제안을 생성하고, 사용자가 승인(approve)할 수 있도록 돕는 시스템입니다. 규칙은 `.yaml` 파일로 개발자가 서비스 단위로 관리하며, 사용자는 규칙을 직접 수정할 수 없습니다.

- Repository: https://github.com/YYOAJUNG/budgetops-ai

---

## Rule

- `.yaml` 파일로 개발자가 관리한다.
- 사용자는 룰을 직접 관리할 수 없다.
- 개발자가 서비스 단위로 관리한다.
  - 예: `/aws/ec2.yml`, `/ncp/compute.yml`

## Rule Registry

- 버전 관리 메타데이터를 유지한다.
  - `rule_id`, `version`, `scope`, `description`
- YAML로 정의된 룰을 파싱하여 Registry에 반영한다.

## Rule Engine

- 최적화 서버 역할을 수행한다.
  - 조건 평가(metric)
  - scoring (절감액 계산)
    - 절감 상황 (EC2 예시)
      1) 타입 과대: 다운사이징 로직으로 적정 타입 산출 및 절감액 계산
      2) 비활성 시간 과다: `요금 * 비활성 시간` 기반 절감액 계산

### Evidence Builder (증거)

- 메트릭 스냅샷 생성
- 우선순위(Priority) 부여

## 룰 승인 단계 (Approval)

- 사용자가 최적화 제안을 검토/승인할 수 있다.
- 시스템은 제안까지만 수행하며, 실제 리소스 조작은 하지 않는다.
- CSP별 어댑터로 서비스/태그 단위 매핑을 관리한다.

## CSP Adapter

- CSP별 어댑터 구조로 룰을 바인딩한다.
  - 예: AWSAdapter(EC2 ↔ `/aws/ec2.yml`), NCPAdapter(Compute ↔ `/ncp/compute.yml`)
- 태그 기반 리소스 필터링 지원

## Rule 파일 버전 관리 자동화

- `.yaml` 변경 감지 시 자동 버전 증가 및 Registry 반영
- 변경 내역 diff 기록(`rule_change_log`)
- 관리자 알림(예: Slack 또는 콘솔)

---

## 전체 흐름

1. 개발자가 `.yaml` 파일을 작성하여 Rule 정의
2. Rule Registry가 버전별로 저장 및 관리
3. Rule Engine이 인스턴스 메트릭을 평가하고 절감액 계산
4. Evidence Builder가 근거 데이터 생성 및 우선순위 부여
5. 사용자는 제안된 룰을 승인(approve)할 수 있으며, 실제 리소스 조작은 하지 않음
6. CSP Adapter가 CSP별 메트릭 수집 및 매핑 담당

---

## 백로그 / 이슈 정리

### 📘 Epic: Rule 기반 CSP 최적화 시스템 구현

#### Feature/1 Rule Registry 설계 및 관리
- [ ] rule_registry 테이블 설계 (`rule_id`, `version`, `scope`, `description`)
- [ ] YAML 파서 구현 (`/aws/ec2.yml`, `/ncp/compute.yml` 등)
- [ ] YAML → DB 싱크 스크립트 구현 (버전 변경 감지 포함)
- [ ] Rule Registry CRUD API (내부 관리자용)
- [ ] Unit Test 작성

#### Feature/2 Rule Engine (조건 평가 및 절감액 계산)
- [ ] Rule Engine 기본 구조 설계 (`ConditionEvaluator`, `ScoringService`)
- [ ] 조건 평가 로직 구현 (CPU, Memory, 사용량 등 Metric 기반)
- [ ] 절감액 계산 로직 구현
  - 타입 과대 시: 다운사이징 로직
  - 비활성 시간 과다 시: `요금 * 비활성 시간` 계산
- [ ] 결과 JSON 스키마 정의 (score, savingAmount, reason 등)
- [ ] 단위 테스트 작성

#### Feature/3 Evidence Builder (증거 데이터 생성)
- [ ] Metric Snapshot 생성 로직 구현
- [ ] 증거 데이터 구조 설계 (`evidence_id`, `rule_id`, `metric_snapshot_id` 등)
- [ ] 우선순위 점수(Priority Score) 계산 로직 구현
- [ ] Rule Engine 결과와 Evidence 매핑
- [ ] API 응답 스키마 정의 (`rule_id`, `priority`, `evidence_link` 등)

#### Feature/4 Rule Approval (사용자 승인 단계)
- [ ] Rule Proposal API 구현 (제안 목록 조회)
- [ ] Approval API 구현 (사용자 승인/거부 상태 저장)
- [ ] 승인 상태별 처리 로직 (approved, pending, rejected)
- [ ] CSP Adapter 연결 (실제 조작은 제외, tag/service 기반 연결만)
- [ ] 승인 이력 저장 (`approval_log` 테이블)

#### Feature/5 CSP Adapter 구조화
- [ ] Adapter 인터페이스 정의 (`CspAdapter`)
- [ ] AWSAdapter, NCPAdapter 구현
- [ ] 각 Adapter에 서비스별 rule binding (예: EC2 → `aws/ec2.yml`)
- [ ] 태그 기반 리소스 필터링 로직 구현
- [ ] Adapter 테스트 코드 작성

#### Feature/6 Rule 파일 버전 관리 자동화
- [ ] Git hook 또는 CI 스크립트로 rule 파일 변경 감지
- [ ] `rule_id` 기준 버전 자동 증가 로직
- [ ] 변경 내역 diff 기록 (`rule_change_log`)
- [ ] 관리자 알림 기능 (Slack 또는 콘솔 로그)

---

## 폴더 구조 (제안)

```
budgetops-ai/
  ├─ aws/
  │   └─ ec2.yml
  ├─ ncp/
  │   └─ compute.yml
  ├─ engine/
  │   ├─ condition_evaluator/
  │   ├─ scoring/
  │   └─ evidence/
  ├─ adapters/
  │   ├─ aws_adapter/
  │   └─ ncp_adapter/
  ├─ registry/
  │   ├─ models/
  │   └─ sync/
  ├─ api/
  ├─ scripts/
  ├─ tests/
  └─ README.md
```

> 실제 구현 시 기존 프론트엔드/백엔드 레포의 구조와 컨벤션을 참고하여 조정하세요.

---

## 기여 가이드

- PR 작성 전 lint/test 통과 필수
- 룰 변경(PR)에는 반드시 변경 사유, 영향 범위, 버전 변경 포함

## 라이선스

- 추후 명시

