import requests
from bs4 import BeautifulSoup
import json

# 사용자 입력
material_name = input("조회할 물질명을 입력하세요 (예: 7727-21-1): ")
search_year = "2022"

# 요청 헤더
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "https://icis.me.go.kr/pageLink.do",
    "Origin": "https://icis.me.go.kr",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

# 1. 업체 리스트 조회
list_url = "https://icis.me.go.kr/iprtr/cdrInfoDetailListJson.do"
list_data = {
    "search1": search_year,
    "search3": "",
    "search4": "",
    "search5": "전체지역",
    "search6": "",
    "search7": "전체지역",
    "mttrGroup": "",
    "searchCategory": "03",
    "searchMttrWord": material_name,
    "irsttList": "",
    "level": "",
    "indutyCode": "",
    "indutyCode2": "",
    "indutyCode3": "",
    "indutyCode4": "",
    "pageNo": "1"
}

response = requests.post(list_url, headers=headers, data=list_data)
results = response.json()

# 상위 10개 업체 추출
companies = results.get("list", [])[:10]
print(f"{len(companies)}개 업체 조회됨")

# 2. 각 업체 상세정보 요청 및 파싱
detail_url = "https://icis.me.go.kr/iprtr/cdrInfoView.do"
all_details = []

for company in companies:
    bplcId = company.get("bplcId")
    detail_data = {
        "bplcId": bplcId,
        "searchYear": search_year,
        "searchSearchMttrWord": material_name,
        "searchSearchCategory": "03",
        "type": "detail"
    }

    detail_response = requests.post(detail_url, headers=headers, data=detail_data)
    soup = BeautifulSoup(detail_response.text, "lxml")

    # 간단한 정보만 추출 (필요에 따라 확장 가능)
    company_name = soup.select_one("td.title strong")
    tables = soup.select("table.tbl_st3")  # 정보가 담긴 주요 테이블들

    detail_info = {
        "업체명": company_name.text.strip() if company_name else "N/A",
        "bplcId": bplcId,
    }

    # 첫 번째 테이블 기준으로 주요 정보 추출 (예시)
    if tables:
        for row in tables[0].select("tr"):
            cols = row.select("th, td")
            if len(cols) == 2:
                key = cols[0].text.strip()
                val = cols[1].text.strip()
                detail_info[key] = val

    all_details.append(detail_info)

# 3. JSON 저장
with open(f"{material_name}_업체정보.json", "w", encoding="utf-8") as f:
    json.dump(all_details, f, ensure_ascii=False, indent=2)

print(f"✅ {material_name}_업체정보.json 저장 완료 ({len(all_details)}개)")

