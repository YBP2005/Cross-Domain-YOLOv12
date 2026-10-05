# -*- coding: utf-8 -*-
"""sync_docs.py -- 把**唯一真相源**（作者侧 M3_draft）同步到放行副本，并**校验一致**。

为什么有这一件
--------------
本会话已经**两次**踩同一类事故：
  ① 页数测量用的参考文献副本没跟上 ⇒ 页数**静默少算 5 条**；
  ② 放行副本里的主稿/补材是**改稿之前**复制的 ⇒ 副本里仍是旧的 gamma 值（1.79 / 0.31 / 0.3284），
     而 `45` 守卫在副本上跑就会报 12 条 FAIL —— **那不是稿子错，是副本旧**。
⇒ 纪律：**任何"副本件"都必须有同步 + 一致性校验**，否则它迟早会变成第二个真相源。
本脚本：把两份文档从真相源复制到 `复现仓库\\M3_draft\\`，然后逐字节比对并打印 md5；
**不一致即非零退出**（不许静默通过）。
"""
import os
import io
import sys
import shutil
import hashlib

SRC_DIR = r'D:\deepseek\analysis\M3_draft'
DST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'M3_draft')
FILES = ['P1_NewDraft_v1_20260927.md', '00_SUPPLEMENTARY_v0.4.md']


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def main():
    os.makedirs(DST_DIR, exist_ok=True)
    bad = []
    for fn in FILES:
        src, dst = os.path.join(SRC_DIR, fn), os.path.join(DST_DIR, fn)
        if not os.path.exists(src):
            bad.append('真相源缺件：%s' % src)
            continue
        shutil.copy2(src, dst)
        a, b = md5(src), md5(dst)
        ok = (a == b)
        print('%-36s 源 %s  副本 %s  %s' % (fn, a[:12], b[:12], 'OK' if ok else 'MISMATCH'))
        if not ok:
            bad.append('%s 复制后 md5 不一致' % fn)
    if bad:
        print()
        for x in bad:
            print('FAIL', x)
        return 1
    print('\nOK 两份文档与真相源逐字节一致。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
