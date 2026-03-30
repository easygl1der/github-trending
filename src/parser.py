import re
from typing import List

from .models import RankEntry


class MarkdownTableParser:
    @staticmethod
    def _parse_stars(stars_str: str) -> int:
        """解析 star 字符串，如 '26.8k' -> 26800"""
        # 提取纯文本（移除 markdown 链接等）
        stars_str = re.sub(r'\[.*?\]\(.*?\)', '', stars_str)
        stars_str = stars_str.strip().lower()
        match = re.match(r'([\d.]+)([km])?', stars_str)
        if not match:
            return 0
        value = float(match.group(1))
        unit = match.group(2)
        if unit == 'k':
            return int(value * 1000)
        elif unit == 'm':
            return int(value * 1000000)
        return int(value)

    @staticmethod
    def _parse_growth(growth_str: str) -> int:
        """解析增长字符串，如 '🔺1491' -> 1491"""
        growth_str = growth_str.strip()
        # 移除emoji和加号
        growth_str = growth_str.replace('🔺', '').replace('+', '')
        # 移除逗号
        growth_str = growth_str.replace(',', '')
        try:
            return int(growth_str)
        except ValueError:
            return 0

    def _parse_growth_percent(self, percent_str: str) -> float:
        """解析增长百分比字符串，如 '12.5%' -> 12.5"""
        percent_str = percent_str.strip().replace('%', '')
        try:
            return float(percent_str)
        except ValueError:
            return 0.0

    def parse_daily_rank(self, markdown: str) -> List[RankEntry]:
        """解析日榜 Markdown"""
        return self._parse_rank(markdown, is_daily=True)

    def parse_weekly_rank(self, markdown: str) -> List[RankEntry]:
        """解析周榜 Markdown"""
        return self._parse_rank(markdown, is_daily=False)

    def _parse_rank(self, markdown: str, is_daily: bool) -> List[RankEntry]:
        """解析排行 Markdown"""
        lines = markdown.strip().split('\n')

        # 找到表格开始 - 查找包含 | 和排名数字的行
        table_start = -1
        for i, line in enumerate(lines):
            # 表格行包含 | 且下一行是分隔符（包含 ---）
            if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                # 检查是否包含排名相关的中文字符或 Star
                if '排行' in line or '排名' in line or 'Star' in line or '项目' in line:
                    table_start = i
                    break

        if table_start == -1:
            # 备用方案：直接找第一个包含 | 和数字排名的表格行
            for i, line in enumerate(lines):
                if '|' in line and re.match(r'\|\s*\d+\s*\|', line.strip()):
                    table_start = i
                    break

        if table_start == -1:
            return []

        # 跳过表头和分隔符
        data_start = table_start + 2

        entries = []
        rank = 1

        for line in lines[data_start:]:
            line = line.strip()
            if not line or not line.startswith('|'):
                continue

            # 分割表格单元格
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) < 3:
                continue

            # 直接按列索引解析（表格格式：Rank | Repo | Stars | Growth）
            # 跳过 rank 列 (cells[0])，解析 repo 列 (cells[1])
            repo_name = ''
            stars = 0
            daily_growth = 0
            weekly_growth = 0
            growth_percent = 0.0

            if len(cells) >= 2:
                # 提取 markdown 链接中的 repo 名称，如 [owner/repo](url) -> owner/repo
                repo_raw = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cells[1])
                if '/' in repo_raw:
                    repo_name = repo_raw.strip()

            if len(cells) >= 3:
                stars = self._parse_stars(cells[2])

            if len(cells) >= 4:
                growth_val = self._parse_growth(cells[3])
                if is_daily:
                    daily_growth = growth_val
                else:
                    weekly_growth = growth_val

            if len(cells) >= 5:
                growth_percent = self._parse_growth_percent(cells[4])

            if repo_name:
                entry = RankEntry(
                    repo_name=repo_name,
                    stars=stars,
                    daily_growth=daily_growth,
                    weekly_growth=weekly_growth,
                    growth_percent=growth_percent,
                    rank=rank
                )
                entries.append(entry)
                rank += 1

        return entries
