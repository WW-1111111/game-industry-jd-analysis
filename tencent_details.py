"""
腾讯招聘岗位详情补爬
用法：先跑完 tencent_scraper.py，再跑这个
"""

import requests
import pandas as pd
import time
import json

DETAIL_URL = "https://careers.tencent.com/tencentcareer/api/post/ByPostId"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "referer": "https://careers.tencent.com/jobdesc.html",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
    ),
}


def fetch_detail(post_id: str) -> dict:
    params = {
        "timestamp": int(time.time() * 1000),
        "postId": post_id,
        "language": "zh-cn",
    }
    r = requests.get(DETAIL_URL, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def main():
    # 读取上一步的结果
    df = pd.read_csv("tencent_jobs.csv", dtype={"PostId": str})
    print(f"准备补爬 {len(df)} 个岗位的详情...\n")
    
    details = []
    failed = []
    
    for i, row in df.iterrows():
        post_id = str(row["PostId"])
        try:
            data = fetch_detail(post_id)
            if data.get("Code") == 200:
                d = data.get("Data", {})
                # 只取关键字段
                detail = {
                    "PostId": post_id,
                    "Requirement": d.get("Requirement", ""),
                    "Responsibility_full": d.get("Responsibility", ""),
                }
                details.append(detail)
                req_preview = (d.get("Requirement", "")[:30] + "...") if d.get("Requirement") else "(空)"
                print(f"  [{i+1}/{len(df)}] {row['RecruitPostName']}: {req_preview}")
            else:
                failed.append(post_id)
                print(f"  [{i+1}/{len(df)}] 失败: {data.get('Message', data)}")
        except Exception as e:
            failed.append(post_id)
            print(f"  [{i+1}/{len(df)}] 错误: {e}")
        time.sleep(1.0)  # 礼貌延迟
    
    if not details:
        print("\n❌ 一条都没爬到，可能 API 地址不对，看下下面的诊断说明")
        return
    
    detail_df = pd.DataFrame(details)
    detail_df = pd.DataFrame(details)
    detail_df.to_csv("tencent_details_only.csv", index=False, encoding="utf-8-sig")  # ← 新增这行：先保存详情，避免合并失败白爬
    
    # 合并到原表
    merged = df.merge(detail_df, on="PostId", how="left")
    
    merged.to_csv("tencent_jobs_full.csv", index=False, encoding="utf-8-sig")
    merged.to_excel("tencent_jobs_full.xlsx", index=False)
    
    print(f"\n✓ 完成！共 {len(merged)} 条")
    print(f"  其中有 Requirement 的: {merged['Requirement'].notna().sum()} 条")
    print(f"  失败: {len(failed)} 条")
    if failed:
        print(f"  失败的 PostId: {failed[:5]}{'...' if len(failed) > 5 else ''}")


if __name__ == "__main__":
    main()