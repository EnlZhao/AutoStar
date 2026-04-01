# AutoStar

每天自动检查 `ZJU-LLM-Safety` 组织下的仓库：
- 已经点过 star 的仓库会跳过
- 新出现且还没 star 的仓库会自动点 star

## 使用方式（推荐：GitHub Actions）

1. 在你的仓库 `Settings -> Secrets and variables -> Actions` 中新增密钥：
   - `AUTO_STAR_TOKEN`：你的 GitHub Personal Access Token（需要有给公开仓库点 star 的权限）
2. 确保仓库里有以下文件：
   - `.github/workflows/auto-star.yml`
   - `scripts/auto_star.py`
3. 工作流会每天 UTC 02:00 自动运行一次，也可以手动触发。

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GITHUB_TOKEN=你的PAT
export TARGET_ORG=ZJU-LLM-Safety
python scripts/auto_star.py
```

## 可配置环境变量

- `GITHUB_TOKEN`（必填）
- `TARGET_ORG`（可选，默认 `ZJU-LLM-Safety`）
- `REQUEST_SLEEP_SECONDS`（可选，请求间隔秒数，默认 `0.2`）
