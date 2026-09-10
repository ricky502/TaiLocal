import pandas as pd

df = pd.read_excel("术语表.xlsx", usecols=[0, 1])

df.columns = ["source", "target"]

df["source"] = df["source"].astype(str).str.strip()
df["target"] = df["target"].astype(str).str.strip()

df = df.dropna(subset=["source", "target"])

df = df.drop_duplicates(subset=["source"])

df.to_csv("terms.csv", index=False, encoding="utf-8-sig")

print("terms.csv 已生成")