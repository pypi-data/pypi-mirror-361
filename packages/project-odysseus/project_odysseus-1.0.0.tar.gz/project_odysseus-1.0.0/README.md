# Project Odysseus - 데이터 인텔리전스 시스템

## 프로젝트 개요

프로젝트 오디세우스는 다양한 데이터 소스를 통합하여 지식 그래프를 구축하고, 이를 통해 비즈니스 인사이트를 제공하는 데이터 인텔리전스 시스템입니다.

## 시스템 아키텍처

```
project_odysseus/
├── connectors/        # 데이터 커넥터 계층
│   ├── base.py       # 추상 기본 클래스
│   └── implementations.py  # 구체적인 커넥터 구현
├── ontology/         # 온톨로지 계층
│   ├── models.py     # 온톨로지 모델 정의
│   └── engine.py     # 데이터 매핑 엔진
├── governance/       # 거버넌스 및 보안 계층
│   ├── logger.py     # 감사 로깅
│   └── access_control.py  # 접근 제어
├── applications/     # 애플리케이션 계층
│   ├── sdk.py        # 프로그래밍 SDK
│   └── workshop_app.py  # Streamlit 대시보드
├── main.py          # 메인 실행 파일
└── requirements.txt  # 의존성 패키지
```

## 주요 기능

### 1. 데이터 연결 (Connectors Layer)
- **FileConnector**: CSV, JSON 등 파일 기반 데이터 소스 연결
- **DatabaseConnector**: SQLite 등 데이터베이스 연결
- 확장 가능한 커넥터 아키텍처

### 2. 온톨로지 관리 (Ontology Layer)
- **OntologyModel**: RDF 그래프 기반 지식 모델링
- **MappingEngine**: 데이터를 온톨로지로 자동 매핑
- SPARQL 쿼리 지원

### 3. 거버넌스 (Governance Layer)
- **감사 로깅**: 모든 데이터 접근 및 수정 활동 기록
- **접근 제어**: 역할 기반 권한 관리 (RBAC)
- 보안 및 컴플라이언스 기능

### 4. 애플리케이션 (Applications Layer)
- **SDK**: 프로그래밍 방식의 온톨로지 접근
- **대시보드**: Streamlit 기반 웹 인터페이스
- SPARQL 쿼리 실행 및 시각화

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 메인 시나리오 실행
```bash
cd project_odysseus
python main.py
```

### 3. 웹 대시보드 실행
```bash
streamlit run applications/workshop_app.py
```

## 사용 예시

### 공급망 최적화 시나리오

시스템은 다음과 같은 시나리오를 통해 공급망 최적화를 시연합니다:

1. **데이터 수집**: 트럭 정보(CSV)와 주문 정보(SQLite DB) 연결
2. **온톨로지 구축**: 트럭, 주문, 관계 정보를 RDF 그래프로 변환
3. **권한 관리**: 관리자와 분석가의 역할별 접근 제어
4. **데이터 분석**: SPARQL 쿼리를 통한 비즈니스 인사이트 추출

### SPARQL 쿼리 예시

```sparql
PREFIX ods: <http://project-odysseus.com/ontology#>
SELECT ?truckId ?driverName ?currentLocation
WHERE {
    ?truck a ods:Truck .
    ?truck ods:truckId ?truckId .
    ?truck ods:driverName ?driverName .
    ?truck ods:currentLocation ?currentLocation .
}
```

## 생성되는 파일

- `knowledge_graph.ttl`: 지식 그래프 TTL 파일
- `audit_trail.log`: 거버넌스 감사 로그
- `data/trucks.csv`: 트럭 정보 CSV 파일
- `data/orders.db`: 주문 정보 SQLite 데이터베이스

## 확장 가능성

- 추가 데이터 소스 커넥터 구현
- 복잡한 비즈니스 로직 온톨로지 모델링
- 고급 보안 및 권한 관리 기능
- 실시간 데이터 스트리밍 지원
- 머신러닝 기반 인사이트 추출

## 기술 스택

- **Python**: 핵심 개발 언어
- **RDFLib**: RDF 그래프 및 SPARQL 처리
- **Pandas**: 데이터 처리 및 분석
- **Streamlit**: 웹 대시보드 구축
- **SQLite**: 경량 데이터베이스
- **Logging**: 감사 및 로깅 시스템
