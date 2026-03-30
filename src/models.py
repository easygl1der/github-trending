from dataclasses import dataclass
from typing import Optional

@dataclass
class RankEntry:
    """GitHub 排行条目"""
    repo_name: str           # 仓库名称，格式：owner/repo
    stars: int              # 当前 star 总数
    daily_growth: int        # 今日增长
    weekly_growth: int       # 本周增长
    growth_percent: float    # 增长百分比
    rank: int               # 排名
