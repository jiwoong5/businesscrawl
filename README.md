# 🧪 화학물질 배출·이동량 정보 크롤러

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

> 환경부 화학물질 배출·이동량 정보시스템(ICIS)에서 특정 화학물질을 취급하는 업체들의 상세정보를 자동으로 수집하는 Python 크롤러입니다.

![업로드](https://github.com/jiwoong5/businesscrawl/blob/main/assets/upload.png)
![시각화](https://github.com/jiwoong5/businesscrawl/blob/main/assets/visualization.png)
![업체상세정보](https://github.com/jiwoong5/businesscrawl/blob/main/assets/company_detail.png)

## 📋 목차

- [기능](#-기능)
- [설치](#-설치)
- [사용법](#-사용법)
- [출력 데이터](#-출력-데이터)
- [대시보드](#-대시보드)
- [기여](#-기여)
- [라이선스](#-라이선스)

## ✨ 기능

### 🔍 **화학물질 기반 업체 검색**
- CAS 번호 또는 물질명으로 관련 업체 목록 자동 조회
- 지정된 연도의 데이터 검색 지원
- 최대 조회할 업체 수 설정 가능

### 📊 **업체 상세정보 수집**
- **기본정보**: 업체명, 대표자, 소재지, 대표업종, 종업원수, 관할 환경청 등
- **화학물질정보**: 물질명, CAS No., 연간입고량, 연간사용·판매량
- 동적 테이블 구조 분석으로 다양한 페이지 포맷 지원

### 🛡️ **안전한 크롤링**
- 요청 간격 조절로 서버 부하 방지
- 세션 관리로 효율적인 연결 유지
- 상세한 에러 처리 및 로깅

### 💾 **결과 저장**
- JSON 형식으로 구조화된 데이터 저장
- UTF-8 인코딩으로 한글 완벽 지원
- 타임스탬프 기반 파일명 자동 생성

## 🚀 설치

### 필수 요구사항
```bash
Python 3.6+
```

### 패키지 설치
```bash
pip install requests beautifulsoup4 lxml
```

또는 requirements.txt 사용:
```bash
pip install -r requirements.txt
```

### requirements.txt
```txt
requests>=2.25.1
beautifulsoup4>=4.9.3
lxml>=4.6.3
```

## 🎯 사용법

### 1. 대화형 실행 (권장)
```bash
python company_crawler.py
```

실행 후 다음 정보를 순서대로 입력:
- 🔍 **물질명/CAS 번호**: 예) `7727-21-1`, `과산화수소`
- 📅 **검색 연도**: 예) `2022` (기본값)
- 📊 **최대 업체 수**: 예) `10` (기본값)
- ⏱️ **요청 간격**: 예) `1.0` 초 (기본값)

### 2. 코드에서 직접 사용
```python
from company_crawler import CompanyCrawler

# 크롤러 인스턴스 생성
crawler = CompanyCrawler()

# 업체 정보 수집
results = crawler.crawl_companies_by_material(
    material_name="7727-21-1",
    year="2022",
    max_companies=10,
    delay=1.0
)

# 결과 저장
crawler.save_to_json(results, "my_results.json")
```

### 3. 실행 예시
```bash
$ python company_crawler.py
🔍 조회할 물질명을 입력하세요 (예: 7727-21-1): 7727-21-1
📅 검색할 연도를 입력하세요 (기본값: 2022): 2022
📊 최대 조회할 업체 수 (기본값: 10): 5
⏱️  요청 간격(초, 기본값: 1.0): 1.5

============================================================
🔍 물질명 '7727-21-1'으로 2022년도 업체 검색 중...
✅ 5개 업체 발견
[1/5] 📋 업체 ID 'AAC001N' 상세정보 조회 중...
✅ 업체 '○○화학(주)' 정보 수집 완료 (화학물질 3개)
[2/5] 📋 업체 ID 'AAC002N' 상세정보 조회 중...
...
```

## 📊 출력 데이터

### JSON 구조
```json
[
  {
    "bplcId": "AAC001N",
    "업체명": "○○화학(주)",
    "대표자": "홍길동",
    "소재지": "서울특별시 강남구 ...",
    "대표업종": "화학물질 제조업",
    "종업원수": "150명",
    "관할 환경청": "한강유역환경청",
    "사업장 비상연락번호": "02-1234-5678",
    "화학물질정보": [
      {
        "물질명": "과산화수소",
        "CAS_No": "7722-84-1",
        "연간입고량": "1,000 톤",
        "연간사용판매량": "800 톤"
      },
      {
        "물질명": "암모니아수",
        "CAS_No": "1336-21-6",
        "연간입고량": "500 톤",
        "연간사용판매량": "450 톤"
      }
    ],
    "검색_순번": 1,
    "원본_업체명": "○○화학(주)",
    "원본_소재지": "서울특별시 강남구"
  }
]
```

### 수집되는 정보

| 카테고리 | 필드명 | 설명 |
|---------|--------|------|
| **기본정보** | 업체명 | 회사명 |
| | 대표자 | 대표이사 이름 |
| | 소재지 | 회사 주소 |
| | 대표업종 | 주요 사업 분야 |
| | 종업원수 | 직원 수 |
| | 관할 환경청 | 관할 환경 관리 기관 |
| | 사업장 비상연락번호 | 비상시 연락처 |
| **화학물질정보** | 물질명 | 화학물질 이름 |
| | CAS_No | Chemical Abstracts Service 번호 |
| | 연간입고량 | 연간 입고된 물질의 양 |
| | 연간사용판매량 | 연간 사용/판매된 물질의 양 |

## ⚠️ 주의사항

### 법적 고지
- 본 도구는 **교육 및 연구 목적**으로만 사용하세요
- 환경부 ICIS의 **이용약관**을 준수해야 합니다
- 수집된 데이터의 상업적 이용은 관련 법규를 확인하세요

### 기술적 제한사항
- 요청 간격을 너무 짧게 설정하면 서버에서 차단될 수 있습니다
- 일부 업체의 경우 상세정보가 제한적일 수 있습니다
- 네트워크 상태에 따라 수집 시간이 달라질 수 있습니다

### 권장 사항
- 첫 실행 시에는 **소수의 업체**로 테스트해보세요
- 요청 간격은 **1초 이상**으로 설정하세요
- 대량 수집 시에는 **여러 번에 나누어** 실행하세요

## 🔧 문제 해결

### 자주 발생하는 오류

#### 1. 연결 오류
```bash
❌ 업체 목록 조회 실패: Connection error
```
**해결방법**: 네트워크 연결 확인 후 재시도

#### 2. 테이블 파싱 오류
```bash
⚠️  업체 ID 'XXX': 정보 테이블을 찾을 수 없습니다.
```
**해결방법**: 해당 업체의 페이지 구조가 다를 수 있음. 정상적인 현상입니다.

#### 3. 인코딩 오류
```bash
UnicodeDecodeError: 'utf-8' codec can't decode
```
**해결방법**: 코드에서 자동 인코딩 감지를 사용하므로 대부분 해결됩니다.

## 🚩 대시보드

### 💡 개요
본 프로젝트는 크롤링한 화학물질 배출·이동량 데이터를 보다 쉽게 확인하고 분석할 수 있도록 웹 기반 **대시보드 시각화 도구**를 제공합니다.  
업체별 환경정보, 화학물질 사용 현황, 통계 요약 및 다양한 필터 기능을 통해 데이터 탐색이 가능합니다.

### ⚙️ 주요 기능
- JSON 형식 크롤링 결과 파일 업로드 및 데이터 로딩  
- 업체 기본정보 및 화학물질별 상세 정보 테이블 조회  
- 연도별, 물질별 필터링 및 선택적 데이터 표시  
- 시각화 차트 (통계 요약, 트렌드, 분포 등) 제공  
- 반응형 UI로 PC/모바일 모두 지원

### 📥 설치 및 실행 방법

1. 대시보드 프로젝트 클론 또는 다운로드  
2. 필요한 npm 라이브러리 설치:
   ```bash
   npm install
   npm start
3. letscrawl.py 결과파일 (ex. 7727-21-1_2022년_업체정보.json) 업로드

## 🤝 기여

프로젝트 개선에 기여해주세요!

1. 이 저장소를 Fork하세요
2. 새로운 기능 브랜치를 만드세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 열어주세요

### 기여 가이드라인
- 코드 스타일: PEP 8 준수
- 커밋 메시지: 한국어 또는 영어 (일관성 유지)
- 테스트: 새로운 기능 추가 시 테스트 코드 포함

## 📝 변경 로그

### v1.0.0 (2024-XX-XX)
- ✨ 초기 릴리스
- 🔍 물질명 기반 업체 검색 기능
- 📊 업체 상세정보 크롤링
- 🧪 화학물질 정보 수집 (CAS No., 연간입고량, 사용량)
- 💾 JSON 형식 결과 저장

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 정보는 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/chemical-company-crawler&type=Date)](https://star-history.com/#yourusername/chemical-company-crawler&Date)

---

<div align="center">

**화학물질 배출·이동량 정보 크롤러**

[⬆ 맨 위로](#-화학물질-배출이동량-정보-크롤러)

</div>
