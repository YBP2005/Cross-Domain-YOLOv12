#!/bin/sh
# push_to_github.sh —— 把本目录（放行仓库）推送到 GitHub。
# 用法：  sh push_to_github.sh "本次改动的说明"
# 目标：  YBP2005/Cross-Domain-YOLOv12  （main）
set -e
cd "$(dirname "$0")"
MSG="${1:-update release package}"
# ★ 端口 22 在本机被网络拒绝 ⇒ 固定走 GitHub 的 443
export GIT_SSH_COMMAND="ssh -p 443 -o StrictHostKeyChecking=no -o BatchMode=yes -i $HOME/.ssh/p1_deploy_ed25519"
# 忽略缓存/备份
cat > .gitignore <<'IGN'
__pycache__/
*.pyc
*.bak*
_rt*/
IGN
git add -A
if git diff --cached --quiet; then
  echo "无改动，无需提交"
else
  git commit -q -m "$MSG"
  echo "已提交: $(git rev-parse --short HEAD)  $MSG"
fi
git push -q origin main
echo "已推送 -> $(git ls-remote --heads origin main | cut -c1-12)"
