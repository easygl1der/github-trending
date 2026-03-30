"""GitHub Hotspot Detector - CLI Entry Point"""
import typer
from typing import List, Optional
import yaml
from pathlib import Path

from src.fetcher import GitHubRankFetcher
from src.parser import MarkdownTableParser
from src.hotspot import HotspotDetector, HotspotConfig
from src.reporter import generate_markdown_report, generate_json_report, console_output

app = typer.Typer()


def load_config(config_path: str = "config/default_config.yaml") -> dict:
    """加载配置文件"""
    path = Path(config_path)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


@app.command()
def main(
    output_format: List[str] = typer.Option(["markdown"], "--output-format"),
    hotspot_threshold: Optional[int] = typer.Option(None, "--hotspot-threshold"),
    verbose: bool = typer.Option(False, "--verbose"),
):
    """GitHub Hotspot Detector CLI"""
    # 加载配置
    config = load_config()

    # 获取热点配置
    hotspot_config_dict = config.get('hotspot', {})
    if hotspot_threshold is not None:
        hotspot_config_dict['min_daily_growth'] = hotspot_threshold
        hotspot_config_dict['min_weekly_growth'] = hotspot_threshold * 6

    hotspot_config = HotspotConfig(
        min_daily_growth=hotspot_config_dict.get('min_daily_growth', 500),
        min_weekly_growth=hotspot_config_dict.get('min_weekly_growth', 3000),
        min_growth_percent=hotspot_config_dict.get('min_growth_percent', 0.05),
        max_rank=hotspot_config_dict.get('max_rank', 20),
    )

    output_dir = config.get('output', {}).get('directory', 'reports')

    if verbose:
        typer.echo("Fetching GitHub rankings...")

    # 1. 获取数据
    fetcher = GitHubRankFetcher()
    daily_content = fetcher.fetch_daily()
    weekly_content = fetcher.fetch_weekly()

    if verbose:
        typer.echo("Parsing rankings...")

    # 2. 解析数据
    parser = MarkdownTableParser()
    daily_entries = parser.parse_daily_rank(daily_content)
    weekly_entries = parser.parse_weekly_rank(weekly_content)

    if verbose:
        typer.echo(f"Daily entries: {len(daily_entries)}, Weekly entries: {len(weekly_entries)}")

    # 3. 检测热点
    if verbose:
        typer.echo("Detecting hotspots...")

    detector = HotspotDetector(config=hotspot_config)
    hotspots = detector.detect(daily_entries, weekly_entries)

    if verbose:
        typer.echo(f"Hotspots detected: {len(hotspots)}")

    # 4. 生成报告
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for fmt in output_format:
        fmt = fmt.lower()
        if fmt == "markdown":
            filename = output_path / f"hotspot-report-{timestamp}.md"
            generate_markdown_report(hotspots, str(filename))
            typer.echo(f"Markdown report: {filename}")
        elif fmt == "json":
            filename = output_path / f"hotspot-report-{timestamp}.json"
            generate_json_report(hotspots, str(filename))
            typer.echo(f"JSON report: {filename}")
        elif fmt == "console":
            console_output(hotspots)

    if not output_format:
        console_output(hotspots)


if __name__ == "__main__":
    app()
