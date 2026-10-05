#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""probe_io_vs_compute.py —— 判"每轮成本"里 **I/O 与算力各占多少**。

思路（只读，不写、不改任何东西）
--------------------------------
同一台机上，`/proc/<pid>/io` 给出**每个进程累计读了多少字节**。
对训练进程**间隔采样两次**，就得到**该区间的实际读吞吐**；
同时从 `nvidia-smi` 取 GPU 利用率、从 `lscpu` 取 CPU 数。

判据（写清楚，免得事后随意解释）
------------------------------
* **I/O 受限**：训练进程读吞吐接近**磁盘顺序读上限**，且 GPU 利用率长期偏低（< 40%）。
* **算力受限**：GPU 利用率长期高位（> 80%），读吞吐远低于磁盘上限。
* **中间态**：两者都不极端 ⇒ 混合，或受 **CPU/worker** 限制（看 `%Cpu` 的 iowait 与 user）。

★ 注意：本脚本**只采样一次设备**，不给结论性推断，只把原始量摆出来。

用法：python3 probe_io_vs_compute.py [--secs 60]
"""
import os
import re
import sys
import time
import glob
import subprocess

SECS = 60
if '--secs' in sys.argv:
    SECS = int(sys.argv[sys.argv.index('--secs') + 1])


def sh(c):
    return subprocess.run(['bash', '-lc', c], capture_output=True, text=True).stdout


def train_pids():
    out = sh('pgrep -f train_obj.py | head -4')
    return [int(x) for x in out.split() if x.strip().isdigit()]


def proc_io(pid):
    """返回 (read_bytes, write_bytes, rchar)。"""
    try:
        t = open('/proc/%d/io' % pid).read()
    except Exception:
        return None
    g = lambda k: int(re.search(k + r':\s*(\d+)', t).group(1)) if re.search(k + r':\s*(\d+)', t) else 0
    return g('read_bytes'), g('write_bytes'), g('rchar')


def gpu():
    out = sh('nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader')
    return out.strip().split('\n')


def cpu_stat():
    """返回 cpu 行的 jiffies 七元组。"""
    for line in open('/proc/stat'):
        if line.startswith('cpu '):
            v = [int(x) for x in line.split()[1:8]]
            return v
    return None


def disk_dev():
    """找出 overlay 底层的块设备名（取一个最可能承载 /root 的）。"""
    return sh("lsblk -ndo NAME,TYPE 2>/dev/null | awk '$2==\"disk\"{print $1}' | head -3").split()


def dev_stat(devs):
    d = {}
    for line in open('/proc/diskstats'):
        f = line.split()
        name = f[2]
        if name in devs:
            d[name] = (int(f[5]), int(f[9]))   # sectors read, sectors written
    return d


def main():
    pids = train_pids()
    print('训练进程：%s' % (pids or '无'))
    if not pids:
        print('（当前没有训练进程在跑——可能处于 run 边界，稍后再试）')
        return 1
    devs = disk_dev()
    print('候选块设备：%s' % (devs or '（未识别，跳过 /proc/diskstats）'))
    print('CPU 核数：%s' % sh('nproc').strip())
    print('协议 workers（写死）：16')
    print()

    io0 = {p: proc_io(p) for p in pids}
    ds0 = dev_stat(devs)
    c0 = cpu_stat()
    t0 = time.time()
    print('采样 %d 秒……' % SECS)
    time.sleep(SECS)
    t1 = time.time()
    io1 = {p: proc_io(p) for p in pids}
    ds1 = dev_stat(devs)
    c1 = cpu_stat()
    dt = t1 - t0

    rb = sum((io1[p][0] - io0[p][0]) for p in pids if io0.get(p) and io1.get(p))
    rc = sum((io1[p][2] - io0[p][2]) for p in pids if io0.get(p) and io1.get(p))
    print('== 训练进程读盘 ==')
    print('  read_bytes 增量 %.1f MB ⇒ %.2f MB/s（**真正从设备读的**）' % (rb / 1e6, rb / 1e6 / dt))
    print('  rchar      增量 %.1f MB ⇒ %.2f MB/s（含页缓存命中）' % (rc / 1e6, rc / 1e6 / dt))

    if devs and ds0 and ds1:
        print('== 块设备读 ==')
        for d in devs:
            if d in ds0 and d in ds1:
                s = (ds1[d][0] - ds0[d][0]) * 512
                print('  %-8s %.2f MB/s' % (d, s / 1e6 / dt))

    if c0 and c1:
        d = [b - a for a, b in zip(c0, c1)]
        tot = sum(d) or 1
        names = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq']
        print('== CPU 时间分配（区间内 %%）==')
        for n, x in zip(names, d):
            print('  %-8s %5.1f%%' % (n, 100.0 * x / tot))

    print('== GPU ==')
    for line in gpu():
        print('  ' + line)
    print()
    print('判读提示：read_bytes 若接近设备上限、且 GPU 利用率低 ⇒ **I/O 受限**；'
          'GPU 利用率高 ⇒ **算力受限**；iowait 高 ⇒ I/O 排队。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
