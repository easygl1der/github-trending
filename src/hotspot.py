from dataclasses import dataclass
from typing import List
from .models import RankEntry


@dataclass
class HotspotConfig:
    """热点检测配置"""
    min_daily_growth: int = 500      # 最小日增长
    min_weekly_growth: int = 3000    # 最小周增长
    min_growth_percent: float = 0.05 # 最小增长百分比 (5%)
    max_rank: int = 20              # 只检测前 N 名


class HotspotDetector:
    def __init__(self, config: HotspotConfig = None):
        self.config = config or HotspotConfig()

    def detect(self, daily_entries: List[RankEntry], weekly_entries: List[RankEntry]) -> List[RankEntry]:
        """检测热点仓库，返回热点列表"""
        # 创建 weekly_entries 的字典便于查找
        weekly_dict = {entry.repo_name: entry for entry in weekly_entries}

        hotspots = []
        for entry in daily_entries:
            # 只检测前 N 名
            if entry.rank > self.config.max_rank:
                continue

            # 获取周榜数据补充信息
            weekly_entry = weekly_dict.get(entry.repo_name)
            if weekly_entry:
                # 合并周榜增长数据
                entry.weekly_growth = weekly_entry.weekly_growth
                entry.growth_percent = weekly_entry.growth_percent

            # 基础条件过滤（日增长或周增长满足其一即可）
            daily_ok = entry.daily_growth >= self.config.min_daily_growth
            weekly_ok = entry.weekly_growth >= self.config.min_weekly_growth

            if not (daily_ok or weekly_ok):
                continue

            # growth_percent 检查（只有当有有效数据时才检查）
            if entry.growth_percent > 0 and entry.growth_percent < self.config.min_growth_percent:
                continue

            # 计算热点分数
            score = self.calculate_hotspot_score(entry)
            entry.hotspot_score = score

            hotspots.append(entry)

        # 按热点分数排序
        hotspots.sort(key=lambda x: x.hotspot_score, reverse=True)
        return hotspots

    @staticmethod
    def calculate_hotspot_score(entry: RankEntry) -> float:
        """计算热点分数 (0-100)

        考虑因素：
        - 日增长率（权重40%）
        - 周增长率（权重40%）
        - 增长百分比（权重20%）
        """
        # 日增长率得分 (归一化到 0-40)
        daily_score = min(entry.daily_growth / 1000 * 40, 40)

        # 周增长率得分 (归一化到 0-40)
        weekly_score = min(entry.weekly_growth / 5000 * 40, 40)

        # 增长百分比得分 (归一化到 0-20)
        percent_score = min(entry.growth_percent * 20 * 100, 20)

        return round(daily_score + weekly_score + percent_score, 2)
