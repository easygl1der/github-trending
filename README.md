# GitHub Hotspot Detector

自动检测 GitHub 仓库推送热点（push hotspots）的工具。通过抓取 OpenGithubs 提供的 `github-daily-rank` 和 `github-weekly-rank` 仓库的 Markdown 数据，解析出热门项目的增长指标，过滤出"热点"仓库并生成报告。

## 功能特性

- 获取 GitHub Daily/Weekly 热门排行数据
- 解析 Markdown 表格格式的排行数据
- 基于多因子评分检测热点仓库
- 生成 Markdown/JSON 格式报告
- 支持 GitHub Actions 定时执行

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
# 基本使用
python main.py

# 指定输出格式
python main.py --output-format markdown,json

# 自定义热点阈值
python main.py --hotspot-threshold 500

# 详细输出
python main.py --verbose
```

## 配置

编辑 `config/default_config.yaml` 修改热点检测阈值和其他配置。

## 许可证

MIT
