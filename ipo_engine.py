import os, requests, pandas as pd, numpy as np, re, time
from io import BytesIO
import OpenDartReader

# 1. 환경 설정 (GitHub Secrets에서 키를 가져옴)
DART_KEY = os.environ.get('DART_API_KEY')
dart = OpenDartReader(DART_KEY)
FILE_NAME = "신규상장기업현황.csv"

def run_automation():
    print("🚀 [START] IPO 통합 엔진 가동...")
    
    # 기존 데이터 로드 (없으면 생성)
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
    else:
        df = pd.DataFrame(columns=['회사명', '액면가 (원)', '공모가 (원)', '주요제품', '유통가능주식수(주)', '비고'])
    
    df.columns = df.columns.str.strip()
    existing_corps = set(df['회사명'].astype(str).str.strip())

    # --- STEP 1: 신규 종목 탐지 (KIND) ---
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
                new_entries.append({'회사명': name, '주요제품': row.get('주요제품'), '비고': 'NEW_자동추가'})
        
        if new_entries:
            # 신규 종목을 맨 위로 추가
            df = pd.concat([pd.DataFrame(new_entries), df], ignore_index=True)
            print(f"✅ 신규 종목 {len(new_entries)}개 추가 완료!")
    except Exception as e: 
        print(f"⚠️ KIND 탐색 에러: {e}")

    # --- STEP 2: DART 유통물량 간단 체크 (상위 5개) ---
    print("🔎 DART 공시 확인 중...")
    target_idx = df[df['유통가능주식수(주)'].isna() | (df['유통가능주식수(주)'] == 0)].index[:5]
    for idx in target_idx:
        corp = df.at[idx, '회사명']
        try:
            clean_name = re.sub(r'\(주\)|주식회사|\s', '', str(corp))
            list_res = dart.list(clean_name, start='2024-01-01')
            if not list_res.empty:
                df.at[idx, '비고'] = "공시 확인 완료"
            time.sleep(0.5)
        except: continue

    # 최종 저장
    df.to_csv(FILE_NAME, index=False)
    print("✨ [ALL DONE] 모든 데이터 업데이트 완료!")

if __name__ == "__main__":
    run_automation()
