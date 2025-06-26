import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
import math

class CompanyCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://icis.me.go.kr/pageLink.do",
            "Origin": "https://icis.me.go.kr",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
    
    def send_post_request(self, url: str, data: Dict) -> Dict:
        """POST 요청을 보내고 JSON 응답 반환"""
        try:
            res = self.session.post(url, headers=self.headers, data=data)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(f"❌ POST 요청 실패: {e}")
            return {}

    def fetch_company_page_by_material(
        self, material_name: str, year: str, page: int
    ) -> List[Dict]:
        """주어진 물질명과 연도, 페이지 번호로 업체 목록 1페이지 조회"""
        url = "https://icis.me.go.kr/iprtr/cdrInfoDetailListJson.do"
        payload = {
            "search1": year,
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
            "pageNo": str(page),
        }

        response_json = self.send_post_request(url, payload)
        return response_json.get("list", [])

    def search_companies_by_material(
        self, material_name: str, year: str = "2022", max_companies: int = 10
    ) -> List[Dict]:
        """물질명으로 업체 검색 후 max_companies 개수만큼 업체 목록 수집"""
        print(f"🚀 물질명 '{material_name}' 기반 업체정보 크롤링 시작")
        print(f"📅 검색년도: {year}, 최대 업체수: {max_companies}")
        print("-" * 60)

        companies = []
        page = 1

        while len(companies) < max_companies:
            print(f"📄 페이지 {page} 조회 중...")
            page_companies = self.fetch_company_page_by_material(material_name, year, page)
            if not page_companies:
                print("⚠️ 더 이상 조회할 업체가 없습니다.")
                break

            companies.extend(page_companies)
            if len(page_companies) == 0:
                break  # 페이지에 더 이상 데이터 없음
            page += 1

        # max_companies 이상이면 자름
        companies = companies[:max_companies]

        print(f"✅ 총 수집된 업체 수: {len(companies)}")
        return companies

    
    def get_all_chemicals(self, bplc_id: str, year: str = "2022", page_unit: int = 200) -> List[Dict]:
        base_url = "https://icis.me.go.kr/iprtr/selectListOpenMatter.do"
        all_data = []
        page_no = 1
        
        while True:
            params = {
                "searchYear": year,
                "bplcId": bplc_id,
                "downPageNo": page_no,
                "downPageUnit": page_unit,
            }
            res = self.session.get(base_url, params=params, headers=self.headers)
            res.raise_for_status()
            json_data = res.json()
            items = json_data.get("result", [])
            
            if not items:
                break
            
            all_data.extend(items)
            
            # 총 개수 기반으로 종료 판단
            total = items[0].get("TOTALCOUNT", 0)
            total_pages = math.ceil(total / page_unit)
            if page_no >= total_pages:
                break
            page_no += 1
        
        return all_data
        
    
    def get_company_details(self, bplc_id: str, year: str = "2022") -> Dict:
        """업체 ID로 상세정보 조회 (최대 3회 재시도)"""
        detail_url = 'https://icis.me.go.kr/iprtr/cdrInfoView.do'
        detail_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://icis.me.go.kr/pageLink.do'
        }
        
        detail_data = {
            'bplcId': bplc_id,
            'streNo': '',
            'searchYear': year,
        }

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                print(f"📋 업체 ID '{bplc_id}' 상세정보 조회 시도 {attempt}회차...")
                response = self.session.post(detail_url, headers=detail_headers, data=detail_data)
                response.encoding = response.apparent_encoding
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 기본 정보 테이블 찾기
                basic_table = soup.find('table', class_='view_table')
                if not basic_table:
                    basic_table = soup.find('table', class_='viewTypeA')
                if not basic_table:
                    basic_table = soup.find('table', class_='tbl_st3')
                
                result = {"bplcId": bplc_id}
                
                if basic_table:
                    tbody = basic_table.find('tbody')
                    rows = tbody.find_all('tr') if tbody else basic_table.find_all('tr')
                    
                    def extract_field(field_name):
                        for row in rows:
                            th_list = row.find_all('th')
                            td_list = row.find_all('td')
                            for th, td in zip(th_list, td_list):
                                if field_name in th.text.strip():
                                    return td.text.strip()
                        return None
                    
                    fields = [
                        '업체명', '대표자', '소재지', '대표업종',
                        '종업원수', '관할 환경청', '사업장 비상연락번호',
                        '설립년도', '자본금', '매출액', '업종분류'
                    ]
                    
                    for field in fields:
                        value = extract_field(field)
                        if value:
                            result[field] = value
                
                if '업체명' not in result or not result['업체명']:
                    company_name = soup.select_one("td.title strong")
                    if company_name:
                        result['업체명'] = company_name.text.strip()
                
                chemical_data = self.get_all_chemicals(bplc_id, year)
                if chemical_data:
                    result['화학물질정보'] = chemical_data
                    print(f"✅ 업체 '{result.get('업체명', bplc_id)}' 정보 수집 완료 (화학물질 {len(chemical_data)}개)")
                else:
                    print(f"✅ 업체 '{result.get('업체명', bplc_id)}' 기본정보 수집 완료")
                
                return result

            except Exception as e:
                print(f"❌ 업체 ID '{bplc_id}' 상세정보 조회 실패 (시도 {attempt}): {e}")
                if attempt < max_retries:
                    time.sleep(2)  # 2초 대기 후 재시도
                else:
                    print(f"❌ 최대 재시도 {max_retries}회 실패, 조회 포기")
                    return {"bplcId": bplc_id, "error": str(e)}
            
    def crawl_companies_by_material(self, material_name: str, year: str = "2022", 
                                  max_companies: int = 10, delay: float = 1.0) -> List[Dict]:
        """물질명으로 업체 검색 후 모든 업체의 상세정보 수집"""
        print(f"🚀 물질명 '{material_name}' 기반 업체정보 크롤링 시작")
        print(f"📅 검색년도: {year}, 최대 업체수: {max_companies}, 요청간격: {delay}초")
        print("-" * 60)
        
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        # 1. 업체 목록 조회
        companies = self.search_companies_by_material(material_name, year, max_companies)
        if not companies:
            return []
        
        # 2. 각 업체 상세정보 수집
        all_details = []
        for i, company in enumerate(companies, 1):
            bplc_id = company.get("bplcId")
            if not bplc_id:
                continue
                
            print(f"[{i}/{len(companies)}] ", end="")
            detail_info = self.get_company_details(bplc_id, year)
            
            # 기본 검색 결과 정보도 포함
            detail_info.update({
                "검색_순번": i,
                "원본_업체명": company.get("bplcNm", ""),
                "원본_소재지": company.get("addr", ""),
            })
            
            all_details.append(detail_info)
            
            # 요청 간격 조절 (서버 부하 방지)
            if i < len(companies):
                time.sleep(delay)
        
        print("-" * 60)
        print(f"🎉 총 {len(all_details)}개 업체 정보 수집 완료!")
        return all_details
    
    def save_to_json(self, data: List[Dict], filename: str = None) -> str:
        """결과를 JSON 파일로 저장"""
        if not filename:
            filename = f"업체정보_{int(time.time())}.json"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 결과 저장 완료: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
            return ""


def main():
    """메인 실행 함수"""
    crawler = CompanyCrawler()
    
    # 사용자 입력
    material_name = input("🔍 조회할 물질명을 입력하세요 (예: 7727-21-1): ").strip()
    if not material_name:
        print("❌ 물질명을 입력해주세요.")
        return
    
    year = input("📅 검색할 연도를 입력하세요 (기본값: 2022): ").strip() or "2022"
    
    try:
        max_companies = int(input("📊 최대 조회할 업체 수 (기본값: 10): ").strip() or "10")
    except ValueError:
        max_companies = 10
    
    try:
        delay = float(input("⏱️  요청 간격(초, 기본값: 1.0): ").strip() or "1.0")
    except ValueError:
        delay = 1.0
    
    print("\n" + "="*60)
    
    # 크롤링 실행
    results = crawler.crawl_companies_by_material(
        material_name=material_name,
        year=year,
        max_companies=max_companies,
        delay=delay
    )
    
    if results:
        # 결과 저장
        filename = f"{material_name}_{year}년_업체정보.json"
        crawler.save_to_json(results, filename)
        
        # 간단한 요약 출력
        print("\n📈 수집 결과 요약:")
        print(f"   - 총 업체 수: {len(results)}")
        successful = len([r for r in results if 'error' not in r])
        print(f"   - 성공적으로 수집된 업체: {successful}")
        if successful < len(results):
            print(f"   - 수집 실패 업체: {len(results) - successful}")
        
        # 화학물질 정보 통계
        total_chemicals = sum(len(r.get('화학물질정보', [])) for r in results)
        companies_with_chemicals = len([r for r in results if r.get('화학물질정보')])
        if total_chemicals > 0:
            print(f"   - 화학물질 정보가 있는 업체: {companies_with_chemicals}")
            print(f"   - 총 화학물질 데이터: {total_chemicals}개")
        
        # 상위 3개 업체명 출력
        print("\n📋 수집된 주요 업체:")
        for i, result in enumerate(results[:3], 1):
            company_name = result.get('업체명', result.get('원본_업체명', f"업체ID_{result.get('bplcId')}"))
            chemical_count = len(result.get('화학물질정보', []))
            chemical_info = f" (화학물질 {chemical_count}개)" if chemical_count > 0 else ""
            print(f"   {i}. {company_name}{chemical_info}")
        
        if len(results) > 3:
            print(f"   ... 외 {len(results)-3}개 업체")
    
    else:
        print("❌ 수집된 업체 정보가 없습니다.")


if __name__ == "__main__":
    main()
