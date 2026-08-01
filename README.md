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

