#!/usr/bin/env python3
"""
openFDA Drug Event 数据下载和处理工具
"""

import requests
import json
import zipfile
import os
from pathlib import Path
from typing import List, Dict
import time

class OpenFDADownloader:
    """openFDA 数据下载器"""
    
    def __init__(self, download_dir: str = "./fda_data"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.api_url = "https://api.fda.gov/download.json"
        
    def get_metadata(self) -> Dict:
        """获取所有可下载文件的元数据"""
        print("正在获取 FDA 数据元信息...")
        response = requests.get(self.api_url)
        response.raise_for_status()
        return response.json()
    
    def list_quarters(self, metadata: Dict) -> Dict:
        """列出所有可用的季度数据"""
        drug_events = metadata['results']['drug']['event']
        partitions = drug_events['partitions']
        
        print(f"\n总记录数: {drug_events['total_records']:,}")
        print(f"导出日期: {drug_events['export_date']}")
        print(f"总文件数: {len(partitions)}")
        
        quarters = {}
        for p in partitions:
            quarter = p['display_name'].split(' (')[0]
            if quarter not in quarters:
                quarters[quarter] = {
                    'files': [],
                    'total_size': 0,
                    'total_records': 0
                }
            quarters[quarter]['files'].append(p)
            quarters[quarter]['total_size'] += float(p['size_mb'])
            quarters[quarter]['total_records'] += p['records']
        
        return quarters
    
    def download_file(self, url: str, filename: str) -> str:
        """下载单个文件"""
        filepath = self.download_dir / filename
        
        if filepath.exists():
            print(f"  ✓ 已存在: {filename}")
            return str(filepath)
        
        print(f"  下载: {filename} ...", end=" ")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("完成")
        return str(filepath)
    
    def download_quarter(self, quarter_name: str, quarters_data: Dict):
        """下载指定季度的所有文件"""
        if quarter_name not in quarters_data:
            print(f"错误: 季度 '{quarter_name}' 不存在")
            return []
        
        quarter = quarters_data[quarter_name]
        files = quarter['files']
        
        print(f"\n下载 {quarter_name}: {len(files)} 个文件, {quarter['total_size']:.2f} MB\n")
        
        downloaded = []
        for i, file_info in enumerate(files, 1):
            print(f"[{i}/{len(files)}]", end=" ")
            filename = file_info['file'].split('/')[-1]
            try:
                filepath = self.download_file(file_info['file'], filename)
                downloaded.append(filepath)
                time.sleep(0.3)
            except Exception as e:
                print(f"失败: {e}")
        
        return downloaded

# 示例使用
if __name__ == "__main__":
    downloader = OpenFDADownloader()
    metadata = downloader.get_metadata()
    quarters = downloader.list_quarters(metadata)
    
    print("\n可用季度:")
    for q in sorted(quarters.keys(), reverse=True)[:10]:
        info = quarters[q]
        print(f"  {q:15} - {len(info['files']):2} 文件, {info['total_size']:7.2f} MB")
