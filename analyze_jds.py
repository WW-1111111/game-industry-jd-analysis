"""
腾讯游戏策划岗 JD 词频分析
用法：先 pip install jieba，然后 python analyze_jds.py
"""

import pandas as pd
import jieba
import re
from collections import Counter

# ============ 1. 加载数据 ============
df = pd.read_excel("tencent_jobs_full.xlsx", dtype={"PostId": str})
print(f"加载 {len(df)} 条岗位\n")

# ============ 2. 自定义专业词汇 ============
# 防止 jieba 把"数值策划"切成"数值"+"策划"，把"虚幻引擎"切成"虚幻"+"引擎"
custom_terms = [
    # 岗位类
    "数值策划", "战斗策划", "关卡策划", "系统策划", "商业化策划",
    "游戏策划", "玩法策划", "剧情策划", "执行策划", "主策划",
    # 游戏类型
    "MOBA", "ARPG", "MMORPG", "MMO", "SLG", "FPS", "TPS", "RTS",
    "卡牌", "二次元", "开放世界", "肉鸽", "Roguelike", "自走棋",
    # 工具/技术
    "Excel", "SQL", "Python", "MATLAB", "VBA", "Tableau", "PowerBI",
    "Unity", "Unreal", "UE4", "UE5", "虚幻引擎",
    "C++", "C#", "Java", "Lua", "Javascript",
    "Photoshop", "PPT", "Office",
    # 数学/分析
    "数学建模", "数理统计", "概率论", "数据分析", "数据挖掘",
    "机器学习", "深度学习", "AI", "AB测试", "A/B测试",
    # 学历/经验
    "本科", "硕士", "博士", "应届生", "研究生",
    "项目经验", "工作经验", "实习经验",
    # 系统术语
    "数值平衡", "数值设计", "数值体系", "数值框架", "数值调优",
    "经济系统", "成长体系", "战斗系统", "养成体系", "PVP", "PVE",
    "氪金", "付费设计", "商业化", "RTM",
    # 软技能
    "沟通能力", "学习能力", "执行力", "责任心", "抗压能力", "逻辑思维",
    "团队合作", "自驱力", "主动性",
    # 玩家身份
    "热爱游戏", "深度玩家", "重度玩家", "硬核玩家", "资深玩家",
    # 知名游戏
    "王者荣耀", "和平精英", "英雄联盟", "原神", "崩坏", "魔兽世界",
    "黑神话", "DOTA", "炉石", "塞尔达", "魂系列",
]
for term in custom_terms:
    jieba.add_word(term)

# ============ 3. 停用词（无意义的词） ============
stopwords = set("""
的 是 在 和 或 及 等 中 上 下 对 为 与 以 于 其 之 了 并
我们 你 您 本 该 其他 以及 进行 拥有 具备 具有 需要 能够 可以
保证 完成 实现 提供 通过 根据 按照 基于 包括 包含 同时 协助
更 更好 良好 优秀 较强 强 一定 较好 熟悉 熟练 精通 了解 掌握
工作 项目 业务 内容 相关 方向 能力 素质 经验 背景 思维 意识
方面 能力 等等 一些 一个 这个 那个 任何 各种 所有 通用
""".split())

# ============ 4. 提取要求文本 ============
all_text = "\n".join(df["Requirement"].dropna().astype(str))
# 去掉编号 "1." "2、" 等
all_text = re.sub(r"\d+[、.\)）]\s*", "", all_text)

# ============ 5. 分词 + 过滤 ============
words = jieba.lcut(all_text)
filtered = [
    w.strip() for w in words
    if w.strip()
    and len(w.strip()) >= 2
    and w.strip() not in stopwords
    and not re.match(r"^[\d.,，。；;！!？?\s\-、（）()【】《》""'']+$", w.strip())
]

# ============ 6. 词频统计 ============
counter = Counter(filtered)

print("=" * 50)
print("任职要求 · Top 50 高频词")
print("=" * 50)
for i, (word, freq) in enumerate(counter.most_common(50), 1):
    print(f"  {i:2d}. {word:<15} {freq:>4} 次")

# 保存
freq_df = pd.DataFrame(counter.most_common(100), columns=["词", "出现次数"])
freq_df["占比%"] = (freq_df["出现次数"] / len(df) * 100).round(1)
freq_df.to_csv("word_frequency.csv", index=False, encoding="utf-8-sig")
freq_df.to_excel("word_frequency.xlsx", index=False)

# ============ 7. 附加：经验要求分布 ============
print("\n" + "=" * 50)
print("工作经验要求分布")
print("=" * 50)
exp_dist = df["RequireWorkYearsName"].value_counts()
for level, count in exp_dist.items():
    pct = count / len(df) * 100
    bar = "█" * int(pct / 2)
    print(f"  {str(level):<20} {count:>3} ({pct:>5.1f}%) {bar}")

# ============ 8. 附加：事业群分布 ============
print("\n" + "=" * 50)
print("事业群 (BG) 分布")
print("=" * 50)
bg_dist = df["BGName"].value_counts()
for bg, count in bg_dist.items():
    pct = count / len(df) * 100
    print(f"  {bg:<10} {count:>3} ({pct:>5.1f}%)")

# ============ 9. 附加：岗位地点 ============
print("\n" + "=" * 50)
print("工作地点 Top 10")
print("=" * 50)
loc_dist = df["LocationName"].value_counts().head(10)
for loc, count in loc_dist.items():
    print(f"  {loc:<10} {count:>3}")

print("\n✓ 词频已保存到 word_frequency.csv / .xlsx")