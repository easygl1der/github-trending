from typing import List
from datetime import datetime
from .models import RankEntry


def generate_markdown_report(hotspots: List[RankEntry], output_path: str) -> None:
    """生成 Markdown 格式报告"""
    lines = []
    lines.append("# GitHub Hotspot Report\n")
    lines.append(f"**生成时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    lines.append("\n## Hotspot Repositories\n")

    # 表头
    lines.append("| Rank | Repository | Stars | Daily Growth | Weekly Growth | Hotspot Score |")
    lines.append("|------|------------|-------|--------------|---------------|---------------|")

    # 数据行
    for i, entry in enumerate(hotspots, 1):
        stars_str = _format_stars(entry.stars)
        daily_str = f"🔺{entry.daily_growth:,}"
        weekly_str = f"🔺{entry.weekly_growth:,}"
        lines.append(f"| {i} | {entry.repo_name} | {stars_str} | {daily_str} | {weekly_str} | {entry.hotspot_score} |")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def generate_json_report(hotspots: List[RankEntry], output_path: str) -> None:
    """生成 JSON 格式报告"""
    import json

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "hotspot_count": len(hotspots),
        "hotspots": [
            {
                "rank": i + 1,
                "repo_name": entry.repo_name,
                "stars": entry.stars,
                "daily_growth": entry.daily_growth,
                "weekly_growth": entry.weekly_growth,
                "growth_percent": entry.growth_percent,
                "hotspot_score": entry.hotspot_score,
            }
            for i, entry in enumerate(hotspots)
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def console_output(hotspots: List[RankEntry]) -> None:
    """使用 rich 库在终端输出美化结果"""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        # 标题面板
        console.print(Panel("[bold blue]GitHub Hotspot Report[/bold blue]"))
        console.print(f"生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

        if not hotspots:
            console.print("[yellow]未检测到热点仓库[/yellow]")
            return

        # 创建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Repository", style="green")
        table.add_column("Stars", justify="right", width=10)
        table.add_column("Daily Growth", justify="right", width=14)
        table.add_column("Weekly Growth", justify="right", width=16)
        table.add_column("Score", justify="right", width=8)

        for i, entry in enumerate(hotspots, 1):
            stars_str = _format_stars(entry.stars)
            daily_str = f"[red]🔺[/red]{entry.daily_growth:,}"
            weekly_str = f"[red]🔺[/red]{entry.weekly_growth:,}"
            table.add_row(
                str(i),
                entry.repo_name,
                stars_str,
                daily_str,
                weekly_str,
                f"[yellow]{entry.hotspot_score}[/yellow]"
            )

        console.print(table)

    except ImportError:
        # Fallback to plain text output
        _console_output_plain(hotspots)


def _format_stars(stars: int) -> str:
    """格式化 star 数量"""
    if stars >= 1000000:
        return f"{stars / 1000000:.1f}m"
    elif stars >= 1000:
        return f"{stars / 1000:.1f}k"
    return str(stars)


def _console_output_plain(hotspots: List[RankEntry]) -> None:
    """纯文本输出（当 rich 不可用时）"""
    print("=" * 80)
    print("GitHub Hotspot Report")
    print(f"生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 80)

    if not hotspots:
        print("未检测到热点仓库")
        return

    print(f"\n{'Rank':<6}{'Repository':<40}{'Stars':<10}{'Daily':<14}{'Weekly':<16}{'Score':<8}")
    print("-" * 80)

    for i, entry in enumerate(hotspots, 1):
        stars_str = _format_stars(entry.stars)
        print(f"{i:<6}{entry.repo_name:<40}{stars_str:<10}{entry.daily_growth:<14,}{entry.weekly_growth:<16,}{entry.hotspot_score:<8.2f}")
