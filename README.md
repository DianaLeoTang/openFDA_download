# OpenFDA 药物不良事件数据使用指南

## 概述

OpenFDA 提供两种访问方式:
1. **Download API** - 批量下载历史数据（本指南重点）
2. **Query API** - 实时查询特定数据

## 数据规模

根据你提供的元数据:
- **总记录数**: 19,684,585 条药物不良事件
- **数据时间跨度**: 2010 Q3 至 2022 Q1
- **文件总数**: 数百个压缩文件
- **总大小**: 数 GB（压缩后）

### 主要季度数据示例

| 季度 | 文件数 | 大小(MB) | 记录数 |
|------|--------|----------|--------|
| 2022 Q1 | 33 | ~4,300 | 395,806 |
| 2019 Q4 | 29 | ~2,900 | 347,411 |
| 2019 Q3 | 32 | ~3,200 | 379,899 |
| 2015 Q4 | 24 | ~1,900 | 286,765 |
| 2015 Q2 | 23 | ~1,300 | 275,981 |

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 基本使用

```python
from openfda_downloader import OpenFDADownloader

# 初始化下载器
downloader = OpenFDADownloader(download_dir="./fda_data")

# 获取元数据
metadata = downloader.get_metadata()

# 列出所有季度
quarters = downloader.list_quarters(metadata)

# 下载特定季度（例如 2022 Q1）
files = downloader.download_quarter('2022 Q1', quarters)
```

### 3. 解压和处理数据

```python
import zipfile
import json
from pathlib import Path

# 解压文件
extract_dir = Path("./fda_data/extracted")
extract_dir.mkdir(exist_ok=True)

for zip_file in files:
    with zipfile.ZipFile(zip_file, 'r') as zf:
        zf.extractall(extract_dir)

# 读取 JSON 数据
json_files = list(extract_dir.glob("*.json"))
for json_file in json_files:
    with open(json_file, 'r') as f:
        data = json.load(f)
        print(f"记录数: {len(data['results'])}")
```

## 数据结构

每个 JSON 文件包含:

```json
{
  "meta": {
    "disclaimer": "...",
    "license": "..."
  },
  "results": [
    {
      "safetyreportid": "...",
      "receivedate": "20220115",
      "patient": {
        "drug": [
          {
            "medicinalproduct": "ASPIRIN",
            "drugindication": "...",
            ...
          }
        ],
        "reaction": [
          {
            "reactionmeddrapt": "NAUSEA"
          }
        ]
      },
      ...
    }
  ]
}
```

## 常见使用场景

### 场景 1: 分析特定药物的不良反应

```python
# 建议使用 Query API 而不是下载全部数据
import requests

url = "https://api.fda.gov/drug/event.json"
params = {
    'search': 'patient.drug.openfda.brand_name:"Aspirin"',
    'count': 'patient.reaction.reactionmeddrapt.exact',
    'limit': 10
}

response = requests.get(url, params=params)
data = response.json()

# 显示最常见的不良反应
for item in data['results']:
    print(f"{item['term']}: {item['count']} 次")
```

### 场景 2: 下载特定时间段数据进行离线分析

```python
# 下载 2022 年全年数据
quarters_2022 = ['2022 Q1', '2022 Q2', '2022 Q3', '2022 Q4']

for quarter in quarters_2022:
    if quarter in quarters:
        print(f"下载 {quarter}...")
        downloader.download_quarter(quarter, quarters)
```

### 场景 3: 合并多个季度数据

```python
import json

all_events = []

# 读取多个 JSON 文件
for json_file in Path("./fda_data/extracted").glob("*.json"):
    with open(json_file, 'r') as f:
        data = json.load(f)
        if 'results' in data:
            all_events.extend(data['results'])

# 保存合并后的数据
with open('merged_events.json', 'w') as f:
    json.dump({
        'total_records': len(all_events),
        'results': all_events
    }, f, indent=2)

print(f"合并完成! 总记录: {len(all_events)}")
```

## 重要提示

### 1. 数据量警告
- **单个季度可能有 100+ MB 压缩数据**
- **解压后可能超过 1 GB**
- **下载所有数据需要数十 GB 空间**

### 2. 推荐策略
✅ **小规模分析**: 使用 Query API  
✅ **特定时间段**: 下载 1-2 个季度  
✅ **大规模研究**: 分批下载和处理  
❌ **避免**: 一次性下载所有数据

### 3. 网络限制
- 添加下载延迟避免被限流
- 使用断点续传（检查文件是否已存在）

### 4. Beta 版声明
> openFDA 是研究项目，不用于临床决策

## Query API vs Download API

| 特性 | Query API | Download API |
|------|-----------|--------------|
| 用途 | 实时查询 | 批量下载 |
| 数据新鲜度 | 最新 | 按季度更新 |
| 数据量 | 按需获取 | 完整数据集 |
| 适用场景 | 特定药物/反应查询 | 大规模统计分析 |
| 网络要求 | 每次查询需联网 | 一次下载离线使用 |

## Query API 示例

```python
# 查询特定药物
search_url = "https://api.fda.gov/drug/event.json"

# 1. 搜索包含 "Aspirin" 的事件
params = {
    'search': 'patient.drug.medicinalproduct:"Aspirin"',
    'limit': 100
}

# 2. 统计最常见的不良反应
params = {
    'search': 'patient.drug.medicinalproduct:"Aspirin"',
    'count': 'patient.reaction.reactionmeddrapt.exact'
}

# 3. 按时间过滤
params = {
    'search': 'patient.drug.medicinalproduct:"Aspirin"+AND+receivedate:[20220101+TO+20221231]',
    'limit': 100
}

response = requests.get(search_url, params=params)
data = response.json()
```

## 其他可用数据集

根据元数据，还有以下数据集可用:

- **drug/shortages**: 药物短缺信息 (1,920 条记录)
- **drug/ndc**: 国家药品代码 (135,674 条记录)

```python
# 下载药物短缺数据
shortages_url = "https://download.open.fda.gov/drug/shortages/drug-shortages-0001-of-0001.json.zip"
```

## 资源链接

- 官方文档: https://open.fda.gov/apis/
- API 参考: https://open.fda.gov/apis/drug/event/
- 数据字段: https://open.fda.gov/apis/drug/event/searchable-fields/

## 许可证

数据使用需遵循: http://open.fda.gov/license

#
这是 openFDA 的 **Download API**，用于批量下载数据。让我帮你理解如何使用：

## 基本用法

### 1. 获取可下载文件列表
```bash
# 查询某个端点的可下载文件
curl "https://api.fda.gov/download.json"
```

### 2. 解析返回的 JSON
返回的数据结构：
- `meta`: 包含免责声明和最后更新时间
- `results`: 包含各个数据集的下载信息

### 3. 下载具体文件
从 `partitions` 数组中获取文件 URL，例如：
```bash
# 下载特定文件
wget "http://download.open.fda.gov/device/event/2012q2/device-event-0001-of-0001.json.zip"

# 或使用 curl
curl -O "http://download.open.fda.gov/device/event/2012q2/device-event-0001-of-0001.json.zip"
```

## Python 示例

```python
import requests
import json

# 1. 获取下载信息
response = requests.get('https://api.fda.gov/download.json')
data = response.json()

# 2. 查看设备事件数据
device_events = data['results']['device']['event']
print(f"总记录数: {device_events['total_records']}")
print(f"导出日期: {device_events['export_date']}")

# 3. 下载第一个文件
first_file = device_events['partitions'][0]
file_url = first_file['file']
print(f"下载文件: {first_file['display_name']}")
print(f"文件大小: {first_file['size_mb']} MB")
print(f"记录数: {first_file['records']}")

# 下载文件
file_response = requests.get(file_url)
with open('device-event.zip', 'wb') as f:
    f.write(file_response.content)
```

## 注意事项

1. **数据量大**: 某些端点有几十个文件，下载前检查总大小
2. **ZIP 格式**: 下载的文件是 `.json.zip`，需要解压
3. **批量处理**: 可以循环下载所有 partitions
4. **Beta 版本**: openFDA 标注为研究项目，不用于临床

这个 API 主要用于**批量下载历史数据**，如果需要实时查询，应该使用常规的查询 API（如 `https://api.fda.gov/device/event.json?search=...`）。