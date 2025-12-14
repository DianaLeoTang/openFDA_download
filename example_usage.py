#!/usr/bin/env python3
"""
openFDA 使用示例
"""

from openfda_downloader import OpenFDADownloader
import json
import zipfile
from pathlib import Path

def example_1_list_data():
    """示例1: 查看可用数据"""
    print("="*60)
    print("示例 1: 查看所有可用数据")
    print("="*60)
    
    downloader = OpenFDADownloader()
    metadata = downloader.get_metadata()
    quarters = downloader.list_quarters(metadata)
    
    return downloader, quarters

def example_2_download_small_quarter(downloader, quarters):
    """示例2: 下载小数据集（2015 Q4 前3个文件作为测试）"""
    print("\n" + "="*60)
    print("示例 2: 下载小数据集测试")
    print("="*60)
    
    # 获取 2015 Q4 的前3个文件
    quarter_files = quarters['2015 Q4']['files'][:3]
    
    print(f"\n下载 2015 Q4 的前 3 个文件（测试用）")
    
    downloaded = []
    for file_info in quarter_files:
        filename = file_info['file'].split('/')[-1]
        filepath = downloader.download_file(file_info['file'], filename)
        downloaded.append(filepath)
    
    return downloaded

def example_3_extract_and_analyze(zip_files):
    """示例3: 解压并分析数据"""
    print("\n" + "="*60)
    print("示例 3: 解压并分析数据")
    print("="*60)
    
    extract_dir = Path("./fda_data/extracted")
    extract_dir.mkdir(exist_ok=True)
    
    for zip_file in zip_files:
        print(f"\n解压: {Path(zip_file).name}")
        
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zf.extractall(extract_dir)
        
        # 找到解压的 JSON 文件
        json_files = list(extract_dir.glob("*.json"))
        
        if json_files:
            json_file = json_files[0]
            print(f"  JSON 文件: {json_file.name}")
            
            # 读取并分析
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                if 'results' in data:
                    print(f"  记录数: {len(data['results'])}")
                    
                    # 显示第一条记录的结构
                    if data['results']:
                        first_record = data['results'][0]
                        print(f"\n  第一条记录的字段:")
                        for key in list(first_record.keys())[:10]:
                            print(f"    - {key}")

def example_4_search_specific_drug():
    """示例4: 在数据中搜索特定药物"""
    print("\n" + "="*60)
    print("示例 4: 搜索特定药物（使用 API）")
    print("="*60)
    
    # 使用查询 API 而不是下载全部数据
    search_url = "https://api.fda.gov/drug/event.json"
    
    params = {
        'search': 'patient.drug.openfda.brand_name:"Aspirin"',
        'limit': 5
    }
    
    print(f"\n搜索: {params['search']}")
    
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"找到结果数: {data['meta']['results']['total']}")
        print(f"\n前5条结果:")
        
        for i, result in enumerate(data['results'][:5], 1):
            if 'patient' in result and 'drug' in result['patient']:
                drugs = result['patient']['drug']
                print(f"\n  案例 {i}:")
                for drug in drugs[:2]:  # 只显示前2个药物
                    if 'medicinalproduct' in drug:
                        print(f"    药物: {drug['medicinalproduct']}")
    else:
        print(f"查询失败: {response.status_code}")

if __name__ == "__main__":
    import requests
    
    # 运行示例
    print("OpenFDA 完整使用示例\n")
    
    # 示例 1: 列出数据
    downloader, quarters = example_1_list_data()
    
    # 示例 2: 下载小数据集
    # downloaded_files = example_2_download_small_quarter(downloader, quarters)
    
    # 示例 3: 解压并分析
    # example_3_extract_and_analyze(downloaded_files)
    
    # 示例 4: 使用查询 API
    example_4_search_specific_drug()
    
    print("\n" + "="*60)
    print("提示: 注释掉的示例会下载真实数据，请按需取消注释")
    print("="*60)
