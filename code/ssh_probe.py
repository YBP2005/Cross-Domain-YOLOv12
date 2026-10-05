# -*- coding: utf-8 -*-
r"""ssh_probe.py -- 用 paramiko 在 A/B 机上跑只读侦查命令。

★ 纪律：**密码只从环境变量读**（`JUMP_PW` / `POD_PW`），**绝不写入磁盘、绝不写进本文件**。
  本会话前几次已在交接件里写明这条；本脚本是它的可执行形式。

用法（密码只在该命令的环境里出现一次）：
    JUMP_PW='...' python ssh_probe.py --host <host> --port <port> --user root --cmd "nvidia-smi -L"

不带 --cmd 时跑一组默认的只读侦查（P0 检查用）。
"""
import os
import sys
import argparse

import paramiko


def run(host, port, user, pw, cmd, timeout=120):
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(host, port=port, username=user, password=pw,
                timeout=30, banner_timeout=30, auth_timeout=30)
    stdin, stdout, stderr = cli.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', 'replace')
    err = stderr.read().decode('utf-8', 'replace')
    rc = stdout.channel.recv_exit_status()
    cli.close()
    return rc, out, err


DEFAULT = [
    ('GPU', 'nvidia-smi -L; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader'),
    ('CUDA/栈', 'python -c "import torch,ultralytics;print(\'torch\',torch.__version__);print(\'ultralytics\',ultralytics.__version__)" 2>&1 | tail -3'),
    ('训练脚本', 'ls -l /workspace/train_obj.py 2>&1; ls /workspace/*.py 2>/dev/null | head'),
    ('权重', 'ls -l /workspace/weights/dota15_pretrain.pt /workspace/weights/aitod_pretrain.pt 2>&1'),
    ('DOTA15 数据', 'ls -d /root/datasets_mask/dota15_yolo 2>&1; ls /root/datasets_mask/dota15_yolo/*.yaml 2>/dev/null | head -20'),
    ('AI-TOD 数据', 'ls -d /root/datasets/AI-TOD_yolo 2>&1; ls /root/datasets/AI-TOD_yolo/*.yaml 2>/dev/null | head -20'),
    ('POT 包', 'python -c "import ot;print(\'POT ok\', ot.__version__)" 2>&1 | tail -2'),
    ('磁盘', 'df -h /root /workspace 2>&1 | tail -3'),
    ('环境', 'echo "conda=$CONDA_PREFIX"; which python; python -V'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', required=True)
    ap.add_argument('--port', type=int, default=22)
    ap.add_argument('--user', default='root')
    ap.add_argument('--pw-env', default='POD_PW')
    ap.add_argument('--cmd', default=None)
    ap.add_argument('--timeout', type=int, default=180)
    a = ap.parse_args()

    pw = os.environ.get(a.pw_env)
    if not pw:
        sys.stderr.write('缺少环境变量 %s（密码不许写在盘上）\n' % a.pw_env)
        return 2

    tasks = [('自定义', a.cmd)] if a.cmd else DEFAULT
    for name, cmd in tasks:
        try:
            rc, out, err = run(a.host, a.port, a.user, pw, cmd, a.timeout)
        except Exception as e:
            print('=== %s ===\n  连接/执行失败: %s\n' % (name, e))
            continue
        print('=== %s === (rc=%d)' % (name, rc))
        print(out.rstrip() if out.strip() else '(无 stdout)')
        if err.strip():
            print('[stderr] ' + err.strip()[:400])
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
