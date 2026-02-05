import os, requests, pandas as pd, numpy as np, re, time
from io import BytesIO
import OpenDartReader

# 1. 환경 설정 (GitHub Secrets 활용)
DART_KEY = os.environ.get('DART_API_KEY')
dart = OpenDartReader(DART_KEY)
FILE_NAME = "신규상장기업현황.csv"

def run_automation():
    print("🚀 [START] IPO 통합 엔진 가동...")
    
    # 기존 파일 로드 (없으면 생성)
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
    else:
        df = pd.DataFrame(columns=['회사명', '액면가 (원)', '공모가 (원)', '주요제품', '유통가능주식수(주)', '비고'])
    
    df.columns = df.columns.str.strip()
    existing_corps = set(df['회사명'].astype(str).str.strip())

    # --- STEP 1: KIND 신규 종목 탐지 (맨 위로 추가) ---
    print("🔎 KIND에서 신규 상장 예정 기업 탐색 중...")
    kind_url = 'https://kind.krx.co.kr/listinvstg/pubofrprogcom.do?method=searchPubofrProgComMain'
    payload = {'method': 'searchPubofrProgComMain', 'currentPageSize': '30', 'orderMode': '1', 'orderStat': 'D'}
    
    try:
        r = requests.post(kind_url, data=payload)
        new_ipo_df = pd.read_html(BytesIO(r.content), header=0)[0]
        new_entries = []
        for _, row in new_ipo_df.iterrows():
            name = str(row['회사명']).strip()
            if name not in existing_corps and name != 'nan':
                new_entries.append({
                    '회사명': name, 
                    '주요제품': row.get('주요제품'), 
                    '비고': 'NEW_자동추가'
                })
        
        if new_entries:
            df = pd.concat([pd.DataFrame(new_entries), df], ignore_index=True)
            print(f"✅ 신규 종목 {len(new_entries)}개 추가 완료!")
    except Exception as e:
        print(f"⚠️ KIND 탐색 에러: {e}")

    # 최종 저장
    df.to_csv(FILE_NAME, index=False)
    print("✨ [ALL DONE] 데이터 업데이트 완료!")

if __name__ == "__main__":
    run_automation()
