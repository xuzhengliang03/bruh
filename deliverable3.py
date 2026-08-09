from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# 数据文件夹和每个文件对应的月份
DATA_DIR = Path(__file__).parent / "local_data"

FILES = {
    "2025_10.csv": "2025-10",
    "2025_11.csv": "2025-11",
    "2025_12.csv": "2025-12",
    "2026_01.csv": "2026-01",
    "2026_02.csv": "2026-02",
    "2026_03.csv": "2026-03",
    "2026_04.csv": "2026-04",
    "2026_05.csv": "2026-05",
    "2026_06.csv": "2026-06",
}

# 每个月数据的实际发布日期
SCRAPE_DATES = {
    "2025-10": "2025-10-05",
    "2025-11": "2025-11-07",
    "2025-12": "2025-12-11",
    "2026-01": "2026-01-16",
    "2026-02": "2026-02-13",
    "2026-03": "2026-03-17",
    "2026-04": "2026-04-16",
    "2026-05": "2026-05-23",
    "2026-06": "2026-06-19",
}

# 读取每个月的数据，只保留 Christchurch City
all_months = []

for filename, month_year in FILES.items():
    file_path = DATA_DIR / filename
    df = pd.read_csv(file_path)

    christchurch = df[
        df["neighbourhood_group"] == "Christchurch City"
    ].copy()

    # 添加月份
    christchurch["month_year"] = month_year
    christchurch["scrape_date"] = SCRAPE_DATES[month_year]
    all_months.append(christchurch)

    print(filename, "Christchurch rows:", len(christchurch))

# 合并九个月的数据
combined = pd.concat(all_months, ignore_index=True)

# 计算距离最后一次评论的天数
combined["scrape_date"] = pd.to_datetime(combined["scrape_date"])
combined["last_review"] = pd.to_datetime(
    combined["last_review"],
    errors="coerce"
)

combined["days_since_last_review"] = (
    combined["scrape_date"] - combined["last_review"]
).dt.days

print("Total Christchurch rows:", len(combined))
print("Total columns:", len(combined.columns))

# 保存合并后的 CSV 文件
output_file = DATA_DIR / "christchurch_2025_10_to_2026_06.csv"
combined.to_csv(output_file, index=False, encoding="utf-8-sig")

print("Saved file:", output_file)

# 计算每一列的缺失值数量
missing_values = combined.isna().sum()

print("\nMissing values per column:")
print(missing_values)

# 数字列的统计结果
numeric_summary = combined.select_dtypes(
    include="number"
).agg(["min", "max", "mean", "std"]).T.round(2)

print("\nNumeric summary:")
print(numeric_summary)

# 文字和分类列的统计结果
categorical_summary = combined.select_dtypes(
    exclude="number"
).describe().T

print("\nCategorical summary:")
print(categorical_summary)

# Christchurch 价格直方图，只显示 0 到 1000
price_data = combined.loc[
    combined["price"].between(0, 1000),
    "price"
]

plt.figure(figsize=(8, 5))
plt.hist(
    price_data,
    bins=range(0, 1051, 50),
    edgecolor="black"
)

plt.title("Christchurch Airbnb Price Distribution")
plt.xlabel("Price (NZD)")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.show()

# 距离最后一次评论天数的直方图
review_days = combined.loc[
    combined["days_since_last_review"].between(0, 5000),
    "days_since_last_review"
].dropna()

plt.figure(figsize=(8, 5))
plt.hist(
    review_days,
    bins=range(0, 5251, 250),
    edgecolor="black"
)

plt.title("Days Since Last Review in Christchurch")
plt.xlabel("Days Since Last Review")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.show()

# 使用最新月份计算评论数量最高的前 10%
latest_month = combined[
    combined["month_year"] == "2026-06"
].copy()

review_threshold = int(
    latest_month["number_of_reviews"].quantile(
        0.90,
        interpolation="higher"
    )
)

top_10_reviews = latest_month[
    latest_month["number_of_reviews"] >= review_threshold
]

print("\nTop 10% review threshold:", review_threshold)
print("Listings in top 10%:", len(top_10_reviews))