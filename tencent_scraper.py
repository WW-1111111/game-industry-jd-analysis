"""
腾讯招聘岗位爬虫
用法：python tencent_scraper.py
"""

import requests
import pandas as pd
import time
import json

BASE_URL = "https://careers.tencent.com/tencentcareer/api/post/Query"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "referer": "https://careers.tencent.com/search.html",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
    ),
}


def fetch_page(keyword: str, page: int = 1, page_size: int = 10) -> dict:
    """请求一页岗位数据。"""
    params = {
        "timestamp": int(time.time() * 1000),
        "keyword": keyword,
        "pageIndex": page,
        "pageSize": page_size,
        "language": "zh-cn",
        "area": "cn",
    }
    r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_all(keyword: str) -> list:
    """循环翻页，把这个关键词下所有岗位捞下来。"""
    all_posts = []
    page = 1
    while True:
        data = fetch_page(keyword, page=page, page_size=10)
        if data.get("Code") != 200:
            print(f"  [错误] {keyword} 第{page}页: {data}")
            break
        
        posts = data.get("Data", {}).get("Posts", [])
        total = data.get("Data", {}).get("Count", 0)
        
        if not posts:
            break
        
        all_posts.extend(posts)
        print(f"  第{page}页: 抓到 {len(posts)} 条 (累计 {len(all_posts)}/{total})")
        
        if len(all_posts) >= total:
            break
        
        page += 1
        time.sleep(1.5)  # 礼貌延迟，别打挂腾讯
    
    return all_posts


def main():
    keywords = [
        "数值策划",
        "关卡策划",
        "战斗策划",
        "系统策划",
        "商业化策划",
        "游戏数据分析",
        "游戏策划",
    ]
    
    all_jobs = []
    for kw in keywords:
        print(f"\n=== 搜索: {kw} ===")
        try:
            jobs = fetch_all(kw)
            for job in jobs:
                job["搜索关键词"] = kw  # 标记来源
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [失败] {kw}: {e}")
        time.sleep(2)
    
    if not all_jobs:
        print("\n没抓到任何数据，可能 User-Agent 被识破，或者关键词都没结果")
        return
    
    df = pd.DataFrame(all_jobs)
    print(f"\n采集完成：共 {len(df)} 条")
    
    # 同一岗位可能被多个关键词搜到，去重
    if "PostId" in df.columns:
        df = df.drop_duplicates(subset=["PostId"])
        print(f"去重后：{len(df)} 条")
    
    # 保存
    df.to_csv("tencent_jobs.csv", index=False, encoding="utf-8-sig")
    df.to_excel("tencent_jobs.xlsx", index=False)
    print("✓ 已保存到 tencent_jobs.csv 和 tencent_jobs.xlsx")
    
    # 看看抓到了哪些字段
    print(f"\n字段列表: {list(df.columns)}")
    
    # 第一条样例
    print("\n=== 第一条数据预览 ===")
    print(json.dumps(df.iloc[0].to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()