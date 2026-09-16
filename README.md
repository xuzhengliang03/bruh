# DATA201/422 Group Project

## Team Members

- Kaicheng Wu (Kai)
- Zhijian Zhang (Phoenix)
- Zhenliang Xu (Green)
- Xiaowen Zhu

## Deliverable 2: New Zealand Airbnb Analysis

This project uses Orange Data Mining to analyse Airbnb listings in New Zealand.

本项目使用 Orange Data Mining 分析新西兰 Airbnb 房源数据。

## Dataset

- Source: Inside Airbnb
- Website: https://beta.insideairbnb.com/get-the-data/
- Country: New Zealand
- Date: 19 June 2026
- File: `listings.csv`
- Number of listings: 50,932

The dataset is saved locally and is not uploaded to GitHub because it is a large file.

数据集保存在每位组员的电脑中，不上传到 GitHub。

## Column Descriptions

| Column | Simple Description |
|---|---|
| `id` | Unique ID of the listing（房源编号） |
| `name` | Name of the listing（房源名称） |
| `host_id` | Unique ID of the host（房东编号） |
| `host_name` | Name of the host（房东名称） |
| `neighbourhood_group` | City or district, such as Christchurch City（城市或地区） |
| `neighbourhood` | Smaller local area or neighbourhood（社区或街区） |
| `latitude` | North–south location（纬度） |
| `longitude` | East–west location（经度） |
| `room_type` | Type of room or property（房间类型） |
| `price` | Daily price in local currency（每日价格） |
| `minimum_nights` | Minimum nights required（最少入住晚数） |
| `number_of_reviews` | Total number of reviews（评论总数） |
| `last_review` | Date of the latest review（最近评论日期） |
| `reviews_per_month` | Average reviews per month（每月平均评论数） |
| `calculated_host_listings_count` | Number of listings owned by the host in this dataset（房东的房源数量） |
| `availability_365` | Available days during the next 365 days（未来一年可订天数） |
| `number_of_reviews_ltm` | Reviews received during the last 12 months（过去12个月评论数） |
| `license` | Licence or registration information（许可证信息） |

Some listing and host names contain Chinese, Korean, Māori, or other languages. These are normal values and are not encoding errors.

部分房源名称包含中文、韩文或毛利语，这是正常数据，不是乱码。

## Orange Workflow

The workflow file is:

`Deliverable_2_Orange_Workflow.ows`

### 1. New Zealand Price Distribution

We created a histogram of Airbnb prices across New Zealand.

To make the chart easier to read, we selected listings with:

`price <= 1000`

This keeps approximately 95% of listings with valid prices. The histogram uses a bin width of 50.

为了避免极端价格把图表拉得太长，我们只显示价格不超过 1000 的房源。

### 2. Christchurch Price Distribution

We selected:

`neighbourhood_group = Christchurch City`

There are 3,166 Christchurch listings with a valid price of no more than 1,000.

我们使用相同的价格范围，绘制 Christchurch City 的价格分布图。

### 3. Days Since the Last Review

We created a new variable:

`days_since_last_review`

The formula is:

`(1781827200 - last_review) / 86400`

- `1781827200` represents 19 June 2026.
- `86400` is the number of seconds in one day.

这个变量表示从最后一次评论到数据发布日期相隔多少天。

Listings without a review date were treated as missing. Negative values were removed because some review dates occurred shortly after the nominal dataset date.

没有评论日期的房源显示为空值；小于 0 的结果不用于绘图。

### 4. Top 10% by Number of Reviews

The 90th-percentile threshold is:

`number_of_reviews >= 185`

This produces 5,130 listings, which is approximately 10% of the full dataset.

评论数达到 185 或以上的房源被视为评论数量最高的前 10%。

Among these highly reviewed listings:

**343 listings are located in Christchurch City.**

其中有 **343 个房源位于 Christchurch City**。

## Important Notes

- Do not upload `listings.csv` to GitHub.
- The Orange `.ows` workflow can be uploaded.
- Each team member needs their own local copy of the dataset.

注意：CSV 数据文件不要上传到 GitHub，但 Orange workflow 可以上传。

Deliverable 3: Christchurch Airbnb Analysis

This analysis uses nine New Zealand Airbnb datasets from October 2025 to June 2026.

本次分析使用了从 2025 年 10 月到 2026 年 6 月的九个月新西兰 Airbnb 数据。

Data Processing / 数据处理

Filtered all datasets to Christchurch City only.所有数据只保留 Christchurch City 的房源。

Added month_year and scrape_date columns.添加月份年份和数据发布日期两列。

Combined nine monthly datasets into one dataset.将九个月的数据合并为一个数据集。

The combined dataset contains 28,795 rows and 21 columns.合并后的数据共有 28,795 行和 21 列。

Calculated missing values and summary statistics for all columns.计算每一列的缺失值和汇总统计数据。

Analysis Results / 分析结果

Created a Christchurch Airbnb price distribution histogram.制作了 Christchurch Airbnb 价格分布直方图。

Created a histogram showing days since the last review.计算距离最后一次评论的天数并制作直方图。

For June 2026, the top 10% review threshold was 184 reviews.在 2026 年 6 月的数据中，评论数量前 10% 的门槛是至少 184 条评论。

347 Christchurch listings were in the top 10%.共有 347 个 Christchurch 房源进入评论数量前 10%。

Files / 文件说明

Python analysis code / Python 分析代码：deliverable3.py

Local combined dataset / 本地合并数据：christchurch_2025_10_to_2026_06.csv

The large CSV datasets are stored locally and are not uploaded to GitHub.

大型 CSV 数据保存在每位组员的本地电脑中，不上传到 GitHub。


-----------------------------week7-------------------------------------------------------------
# DATA201/422 Group Project

## Team Members

- Kaicheng Wu (Kai)
- Zhijian Zhang (Phoenix)
- Zhenliang Xu (Green)
- Xiaowen Zhu

## Deliverable 2: New Zealand Airbnb Analysis

This project uses Orange Data Mining to analyse Airbnb listings in New Zealand.

本项目使用 Orange Data Mining 分析新西兰 Airbnb 房源数据。

## Dataset

- Source: Inside Airbnb
- Website: https://beta.insideairbnb.com/get-the-data/
- Country: New Zealand
- Date: 19 June 2026
- File: `listings.csv`
- Number of listings: 50,932

The dataset is saved locally and is not uploaded to GitHub because it is a large file.

数据集保存在每位组员的电脑中，不上传到 GitHub。

## Column Descriptions

| Column | Simple Description |
|---|---|
| `id` | Unique ID of the listing（房源编号） |
| `name` | Name of the listing（房源名称） |
| `host_id` | Unique ID of the host（房东编号） |
| `host_name` | Name of the host（房东名称） |
| `neighbourhood_group` | City or district, such as Christchurch City（城市或地区） |
| `neighbourhood` | Smaller local area or neighbourhood（社区或街区） |
| `latitude` | North–south location（纬度） |
| `longitude` | East–west location（经度） |
| `room_type` | Type of room or property（房间类型） |
| `price` | Daily price in local currency（每日价格） |
| `minimum_nights` | Minimum nights required（最少入住晚数） |
| `number_of_reviews` | Total number of reviews（评论总数） |
| `last_review` | Date of the latest review（最近评论日期） |
| `reviews_per_month` | Average reviews per month（每月平均评论数） |
| `calculated_host_listings_count` | Number of listings owned by the host in this dataset（房东的房源数量） |
| `availability_365` | Available days during the next 365 days（未来一年可订天数） |
| `number_of_reviews_ltm` | Reviews received during the last 12 months（过去12个月评论数） |
| `license` | Licence or registration information（许可证信息） |

Some listing and host names contain Chinese, Korean, Māori, or other languages. These are normal values and are not encoding errors.

部分房源名称包含中文、韩文或毛利语，这是正常数据，不是乱码。

## Orange Workflow

The workflow file is:

`Deliverable_2_Orange_Workflow.ows`

### 1. New Zealand Price Distribution

We created a histogram of Airbnb prices across New Zealand.

To make the chart easier to read, we selected listings with:

`price <= 1000`

This keeps approximately 95% of listings with valid prices. The histogram uses a bin width of 50.

为了避免极端价格把图表拉得太长，我们只显示价格不超过 1000 的房源。

### 2. Christchurch Price Distribution

We selected:

`neighbourhood_group = Christchurch City`

There are 3,166 Christchurch listings with a valid price of no more than 1,000.

我们使用相同的价格范围，绘制 Christchurch City 的价格分布图。

### 3. Days Since the Last Review

We created a new variable:

`days_since_last_review`

The formula is:

`(1781827200 - last_review) / 86400`

- `1781827200` represents 19 June 2026.
- `86400` is the number of seconds in one day.

这个变量表示从最后一次评论到数据发布日期相隔多少天。

Listings without a review date were treated as missing. Negative values were removed because some review dates occurred shortly after the nominal dataset date.

没有评论日期的房源显示为空值；小于 0 的结果不用于绘图。

### 4. Top 10% by Number of Reviews

The 90th-percentile threshold is:

`number_of_reviews >= 185`

This produces 5,130 listings, which is approximately 10% of the full dataset.

评论数达到 185 或以上的房源被视为评论数量最高的前 10%。

Among these highly reviewed listings:

**343 listings are located in Christchurch City.**

其中有 **343 个房源位于 Christchurch City**。

## Important Notes

- Do not upload `listings.csv` to GitHub.
- The Orange `.ows` workflow can be uploaded.
- Each team member needs their own local copy of the dataset.

注意：CSV 数据文件不要上传到 GitHub，但 Orange workflow 可以上传。

Deliverable 3: Christchurch Airbnb Analysis

This analysis uses nine New Zealand Airbnb datasets from October 2025 to June 2026.

本次分析使用了从 2025 年 10 月到 2026 年 6 月的九个月新西兰 Airbnb 数据。

Data Processing / 数据处理

Filtered all datasets to Christchurch City only.所有数据只保留 Christchurch City 的房源。

Added month_year and scrape_date columns.添加月份年份和数据发布日期两列。

Combined nine monthly datasets into one dataset.将九个月的数据合并为一个数据集。

The combined dataset contains 28,795 rows and 21 columns.合并后的数据共有 28,795 行和 21 列。

Calculated missing values and summary statistics for all columns.计算每一列的缺失值和汇总统计数据。

Analysis Results / 分析结果

Created a Christchurch Airbnb price distribution histogram.制作了 Christchurch Airbnb 价格分布直方图。

Created a histogram showing days since the last review.计算距离最后一次评论的天数并制作直方图。

For June 2026, the top 10% review threshold was 184 reviews.在 2026 年 6 月的数据中，评论数量前 10% 的门槛是至少 184 条评论。

347 Christchurch listings were in the top 10%.共有 347 个 Christchurch 房源进入评论数量前 10%。

Files / 文件说明

Python analysis code / Python 分析代码：deliverable3.py

Local combined dataset / 本地合并数据：christchurch_2025_10_to_2026_06.csv

The large CSV datasets are stored locally and are not uploaded to GitHub.

大型 CSV 数据保存在每位组员的本地电脑中，不上传到 GitHub。

-------------------------------week7----------------------------------------------

## Deliverable 4: Data Cleaning / 数据清洗

Deliverable 4 cleans the Christchurch Airbnb listing data created in Deliverable 3 and the Tenancy Services detailed quarterly rental bond data.

Deliverable 4 对 Deliverable 3 生成的 Christchurch Airbnb 房源数据和 Tenancy Services 的季度租赁押金数据进行清洗。

### Files / 文件

- Cleaning code / 清洗代码：`deliverable4.py`
- Python dependencies / Python 依赖：`requirements.txt`
- Clean datasets / 清洗后的数据：saved locally in `processed_data/` and not uploaded to GitHub / 保存在本地 `processed_data/` 文件夹，不上传至 GitHub

### Time Period / 时间范围

- Airbnb listings / Airbnb 房源：October 2025 to June 2026 / 2025 年 10 月至 2026 年 6 月
- Rental bond data / 租赁押金数据：quarter starts `2025-10-01`, `2026-01-01`, and `2026-04-01`

The three bond quarters overlap the same period as the monthly Airbnb dataset.

这三个租赁押金季度与 Airbnb 月度数据的时间范围一致。

### Christchurch Listing Cleaning / Christchurch 房源数据清洗

- Retained 28,795 rows and reduced the dataset from 21 to 12 relevant columns. / 保留 28,795 行，并将数据从 21 列精简为 12 个相关字段。
- Kept `latitude` and `longitude` for later geographic matching. / 保留 `latitude` 和 `longitude`，方便下一阶段进行地理匹配。
- Kept one row per listing and month and checked for duplicate keys. No duplicate listing-month rows were found. / 每个房源每月只保留一行；检查后未发现重复的房源—月份记录。
- Removed unrelated free-text and review fields, including listing names, host names, licence and review metrics. / 删除与下一阶段分析无关的自由文本及评论字段，包括房源名称、房东名称、许可证和评论指标。
- Added `has_price` to show whether a valid price is present. / 新增 `has_price`，明确标记房源是否有有效价格。
- Added `is_available`, defined as `availability_365 > 0`, for counting listings with at least one available day. / 新增 `is_available`；当 `availability_365 > 0` 时，表示未来一年至少有一天可以预订。
- Retained 153 prices above NZD 1,000 per night because there was no defensible rule for treating them as errors. / 保留 153 条每晚超过 1,000 新西兰元的价格，因为没有充分依据将其认定为错误。
- Did not fill missing values with estimated values. / 未使用平均数或其他估计值填补缺失数据。

The supplied source contains no price values for December 2025, January 2026 or February 2026. These months can still be used to count available listings, but they must not be used for price comparisons.

源数据中 2025 年 12 月、2026 年 1 月和 2026 年 2 月的价格全部缺失。这些月份仍可用于统计可用房源数量，但不能用于价格比较。

### Rental Bond Cleaning / 租赁押金数据清洗

- Reduced the source from 226,080 rows to 27,212 rows by keeping the three matching quarters. / 按相同时间范围保留三个季度，将数据从 226,080 行减少至 27,212 行。
- Kept `TimeFrame` and `Location Id`, as required. In the clean file their standardised names are `timeframe` and `location_id`. / 按要求保留 `TimeFrame` 和 `Location Id`；在清洗文件中统一命名为 `timeframe` 和 `location_id`。
- Added `location_id_status` to distinguish valid, missing and source-special location identifiers without guessing their meaning. / 新增 `location_id_status`，区分有效、缺失及源数据特殊地理编号，不主观猜测其含义。
- Standardised column names, date formats, count types and missing bedroom labels. / 统一列名、日期格式、计数字段类型和缺失卧室数标签。
- Preserved source missing values and did not impute rent statistics. / 保留源数据中的缺失值，不对租金统计值进行推测填补。

### Important Limitations / 重要限制

- Airbnb price is an advertised nightly short-stay price, while rental bond rent is a weekly long-term tenancy measure. Units and market differences must be explained before comparison. / Airbnb 价格是短租房源的每晚挂牌价；租赁押金数据中的租金是长期租赁的每周租金。比较前必须统一单位并说明两个市场的差异。
- `availability_365` shows calendar availability and is not the number of vacant long-term rental homes. / `availability_365` 表示 Airbnb 日历中的可订天数，不等同于长期租赁市场的空置房数量。
- Tenancy Services applies fixed random rounding to base 3 and suppresses selections with fewer than five bonds. / Tenancy Services 对数据进行以 3 为基数的固定随机取整，并抑制少于 5 个押金记录的分类结果。
- Recent bond data is provisional during migration to a new bond-management system and may be revised. / 由于租赁押金管理系统正在迁移，近期数据属于暂定数据，之后可能修订。
- Joining Airbnb coordinates to `location_id` requires an SA2-2019 boundary file or a defensible geographic crosswalk. Neighbourhood names should not be joined directly to numeric IDs. / 将 Airbnb 经纬度与 `location_id` 合并时，需要 SA2-2019 边界文件或可靠的地理对应表，不能直接用社区名称连接数字编号。

### Reproduce the Cleaning / 重新运行清洗代码

Install the dependency in `requirements.txt`, download the Tenancy Services detailed quarterly report, and run:

安装 `requirements.txt` 中的依赖，下载 Tenancy Services 的季度详细数据，然后运行：

```bash
python deliverable4.py \
  --listing-input local_data/christchurch_2025_10_to_2026_06.csv \
  --bond-input local_data/Detailed-Quarterly-Tenancy.csv \
  --output-dir processed_data
```

### Data Sources / 数据来源

- Inside Airbnb: https://insideairbnb.com/get-the-data/
- Tenancy Services rental bond data: https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/

The rental bond data is published by the Ministry of Business, Innovation and Employment under a Creative Commons Attribution 3.0 New Zealand licence.

租赁押金数据由新西兰商业、创新和就业部发布，采用 Creative Commons Attribution 3.0 New Zealand 许可协议。
------------------------week8------------------------------------------------
## Deliverable 5: SA2 matching and rental comparison / 区域匹配与租金比较

This ZIP includes the compressed prepared data, reproducible code and results. The original large downloads and the Koordinates API key are not included. / 本压缩包包含压缩后的已处理数据、可重复运行的代码和结果；不包含原始大型下载文件或 Koordinates API 密钥。

### Files / 文件

- `deliverable5_geocode.py`: queries Stats NZ SA2-2019 for each unique Airbnb coordinate, caches responses locally and saves `processed_data/christchurch_listings_with_sa2.csv.gz`. / 查询每个不同坐标的 SA2-2019 区号，并保存新增区域编号的房源数据。
- `deliverable5_analysis.py`: joins Airbnb listing-month rows to quarterly bond summaries and writes the joined file, area comparison and analysis report. / 按区域及季度连接两份数据，输出连接表、各区域比较及分析报告。
- `processed_data/airbnb_bond_joined.csv.gz`: listing-level left-join output, retaining all 28,795 Airbnb listing-month rows. / 保留全部 28,795 条房源月份记录的左连接结果。
- `processed_data/area_comparison_latest_month.csv`: June 2026 Airbnb counts, prices and active bond counts by SA2. / 按 SA2 汇总的 2026 年 6 月房源数量、价格及活跃押金数量。
- `processed_data/deliverable5_results.md`: detailed methods, findings and limitations. / 方法、结果及限制说明。

### Method and findings / 方法与结果

The bond source uses **SA2-2019** definitions, so the Koordinates layer `98970` (Statistical Area 2 2019, generalised) was used. Longitude is `x`, latitude is `y`; the single-point test returned SA2 `320800`. All 3,953 unique coordinates were queried and all 28,795 Airbnb rows received a `location_id`. / 押金数据使用 **SA2-2019** 定义，因此选用 Koordinates 图层 `98970`。`x` 为经度、`y` 为纬度；单点测试返回 `320800`。共查询 3,953 个不同坐标，28,795 条房源记录均获得区域编号。

Airbnb months were mapped to calendar quarters. The bond table contains detail and subtotal rows, so only `dwelling_type=ALL` and `number_of_beds=ALL` were joined. A many-to-one **left join** retains Airbnb rows without a bond match; missing bond results must not be treated as zero. / 将 Airbnb 月份映射至自然季度；押金表只使用两个分类均为 `ALL` 的总计行，再按 `location_id` 和季度进行多对一左连接。无押金匹配的房源仍保留，缺失值不能解释为零。

For June 2026, Christchurch Central (SA2 `326600`) has a median Airbnb asking price of **NZ$250 per night** from 117 priced listings. Among SA2 areas with at least 10 priced Airbnb listings, Holmwood (`322600`) has the largest median Airbnb-minus-bond-rent gap, **NZ$242.71 per night**, after converting weekly bond median rent to a nightly figure by dividing by seven. / 2026 年 6 月，Christchurch Central（`326600`）117 条有价格房源的挂牌价中位数为 **每晚 NZ$250**。在至少有 10 条有价格房源的区域中，Holmwood（`322600`）的短租挂牌价减去长期租赁周租金除以七所得差值中位数最大，为 **每晚 NZ$242.71**。

Airbnb asking prices and bond rents measure different markets. Bond `active_bonds` is a rounded stock measure, not an exact count of comparable properties; absent or suppressed bond records are not zeros. The generalised SA2 polygons can misclassify points near boundaries. / Airbnb 挂牌价与长期租金并非完全可比；`active_bonds` 是经过保密取整的存量指标，不是可直接对应的准确房屋数量；缺失或被抑制的押金记录不是零。简化版 SA2 边界可能影响边界附近的房源。

### Re-run / 重新运行

From the project folder, with pandas installed, run `python deliverable5_analysis.py`. It reads the two prepared compressed datasets in `processed_data/` and regenerates the joined dataset and summaries. Re-running `deliverable5_geocode.py` requires a Koordinates API key in the **session-only** `KOORDINATES_API_KEY` environment variable; the saved geocoded dataset means those queries are not required just to reproduce the analysis. Never put the key in source code, README, screenshots or Git. / 在项目目录安装 pandas 后运行 `python deliverable5_analysis.py`，即可由两份已处理压缩数据重建连接数据和分析结果。只有重新进行地理查询时才需要在当前终端设置 `KOORDINATES_API_KEY`；不要将密钥放进代码、README、截图或 Git。

Sources / 来源：[Tenancy Services rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/), [Stats NZ SA2-2019 layer](https://datafinder.stats.govt.nz/layer/98970-statistical-area-2-2019-generalised/), [Stats NZ SA2 names](https://statsnz.contentdm.oclc.org/digital/api/collection/p20045coll24/id/980/download).
