import requests
from tenacity import retry, stop_after_attempt, wait_exponential

class GitHubRankFetcher:
    DAILY_URL = "https://raw.githubusercontent.com/OpenGithubs/github-daily-rank/main/README.md"
    WEEKLY_URL = "https://raw.githubusercontent.com/OpenGithubs/github-weekly-rank/main/README.md"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch(self, url: str) -> str:
        """获取 URL 内容"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        # 强制使用 UTF-8 编码（raw.githubusercontent.com 返回的是 UTF-8）
        response.encoding = 'utf-8'
        return response.text

    def fetch_daily(self) -> str:
        """获取日榜"""
        return self.fetch(self.DAILY_URL)

    def fetch_weekly(self) -> str:
        """获取周榜"""
        return self.fetch(self.WEEKLY_URL)
