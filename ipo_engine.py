import os, pandas as pd
print("🚀 IPO 자동 엔진 가동 시작!")

# 파일이 있으면 불러오고 없으면 새로 만들기
file_name = "신규상장기업현황.csv"
if os.path.exists(file_name):
    df = pd.read_csv(file_name)
    print("📂 기존 파일을 불러왔어.")
else:
    df = pd.DataFrame(columns=['회사명', '비고'])
    print("🆕 새 파일을 생성했어.")

# 테스트 데이터 한 줄 추가
new_data = pd.DataFrame([{'회사명': '자동화테스트', '비고': '성공'}])
df = pd.concat([df, new_data], ignore_index=True)

df.to_csv(file_name, index=False)
print(f"✅ {file_name} 저장 완료!")
