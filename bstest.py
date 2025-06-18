import requests
from bs4 import BeautifulSoup

def get_company_details(bplc_id: str, year: str = "2022") -> dict:
    # 1. POST 요청 준비
    url = 'https://icis.me.go.kr/iprtr/cdrInfoView.do'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://icis.me.go.kr/pageLink.do'
    }
    data = {
        'bplcId': bplc_id,
        'streNo': '',
        'searchYear': year,
        # 필요하면 다른 파라미터도 추가 가능
    }

    # 2. POST 요청
    response = requests.post(url, headers=headers, data=data)
    response.encoding = response.apparent_encoding  # 인코딩 자동 감지

    # 3. BeautifulSoup 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 4. 테이블 찾기: 우선 class='view_table' 시도 후 없으면 'viewTypeA' 사용
    table = soup.find('table', class_='view_table')
    if not table:
        table = soup.find('table', class_='viewTypeA')
    if not table:
        raise ValueError("정보가 담긴 테이블을 찾을 수 없습니다.")

    # 5. tbody 내 tr 모두 추출 (tbody가 없으면 table 바로 tr)
    tbody = table.find('tbody')
    rows = tbody.find_all('tr') if tbody else table.find_all('tr')

    # 6. 필드 추출 함수
    def extract_field(field_name):
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                if field_name in th.text.strip():
                    return td.text.strip()
        return None

    # 7. 추출할 필드 리스트 (필요에 따라 조정)
    fields = [
        '업체명', '대표자', '소재지', '대표업종',
        '종업원수', '관할 환경청', '사업장 비상연락번호'
    ]

    # 8. 각 필드별 값 딕셔너리로 수집
    result = {field: extract_field(field) for field in fields}
    return result


# 사용 예시
if __name__ == "__main__":
    bplc_id = "AAC001N"  # (주)이수페타시스 예시
    company_info = get_company_details(bplc_id, year="2022")
    for key, value in company_info.items():
        print(f"{key}: {value}")

